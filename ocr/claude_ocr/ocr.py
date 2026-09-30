"""Double-read OCR of الحلقات المضيئات with Claude Opus (subscription, via `claude -p`).

  python ocr.py run   --vol 1 --pages 90-104   # render, crop, read twice, write report
  python ocr.py report --vol 1 --pages 90-104  # rebuild report.md from saved reads (no OCR)
  python ocr.py score --vol 1                  # after correcting volN/gold.txt
  python ocr.py test                           # self-check of the diff/score helpers

Read A = page cut in 2 slices, read B = page cut in 3 slices (independent sessions,
different line breaks). Read C = the existing full-volume transcription.
"""
import argparse
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher
from pathlib import Path

import pymupdf
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).parent
PDFS = {1: "الحلقات المضيئات - المجلد الأول 01.pdf", 2: "الحلقات المضيئات - المجلد الثاني 02.PDF"}
OLD = {1: "alhalaqat_j1_pdf1-680_ocr.txt", 2: "alhalaqat_j2_pdf1-641_ocr.txt"}
MODEL = "opus"
WORKERS = 4  # ponytail: parallel claude sessions; lower it if the subscription rate-limits
NOTES_SEP = "---NOTES---"
AR_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
HEADER_RE = re.compile(r"^=+\s*\[PDF (\d+) = ص [^\]]*\]\s*=+$", re.M)
DIACRITICS_RE = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭـ]")  # tashkeel + tatweel
DIGIT_RE = re.compile(r"[0-9٠-٩]")

PROMPT = """You are transcribing one scanned page of the Arabic book «الحلقات المضيئات من سلسلة أسانيد القراءات».
The page was cut into {n} horizontal slices at blank gaps between lines. Use the Read tool to view them, top to bottom:
{paths}

Transcribe the whole page, top to bottom, exactly as printed:
- Copy every letter, diacritic (tashkeel), number and punctuation mark exactly as printed. Do not correct, normalize or modernize anything. If the book itself contains a typo, a wrong number or a wrong name, keep it exactly as printed.
- Never fill in from memory: not Quran verses, hadith, names of people, places or books. Write only what you can see on the page.
- Read every digit carefully; the Arabic-Indic digits ٢ and ٣ are easy to confuse.
- If you are unsure of a word, write your best reading followed by [؟]. If it is unreadable, write [غير مقروء]. Never guess silently.
- One output line per printed line of text. Footnotes go at the bottom, as printed.
- Do not repeat text across slice boundaries, and do not add headers, page labels or commentary. Leave out the printed page number. If the page is blank, output only [صفحة فارغة].

Output the transcription only. Afterwards, if you have notes (suspected printing errors, uncertain spots), add a line containing exactly {sep} followed by the notes."""


# ---------- images ----------

def render(vol, page, out):
    doc = pymupdf.open(HERE / PDFS[vol])
    pix = doc[page - 1].get_pixmap(dpi=72)  # pages are 1 pt = 1 scan pixel, so 72 dpi = native scan resolution
    pix.save(out)


def cut_rows(img, parts):
    """Row indices to cut at: the emptiest row within ±8% of each even split point."""
    g = img.convert("L")
    w, h = g.size
    ink = [sum(1 for x in range(0, w, 2) if g.getpixel((x, y)) < 128) for y in range(h)]
    cuts = []
    for k in range(1, parts):
        target = h * k // parts
        lo, hi = int(target - h * 0.08), int(target + h * 0.08)
        cuts.append(min(range(lo, hi), key=lambda y: (ink[y], abs(y - target))))
    return cuts


def slice_page(png, parts, out_dir):
    img = Image.open(png)
    bounds = [0, *cut_rows(img, parts), img.height]
    paths = []
    for i in range(parts):
        p = out_dir / f"{png.stem}_{parts}{'abc'[i]}.png"
        img.crop((0, bounds[i], img.width, bounds[i + 1])).save(p)
        paths.append(p)
    return paths


# ---------- claude ----------

def claude_read(crops):
    prompt = PROMPT.format(n=len(crops), paths="\n".join(str(p.resolve()) for p in crops), sep=NOTES_SEP)
    r = subprocess.run(
        ["claude", "-p", prompt, "--model", MODEL, "--allowedTools", "Read"],
        capture_output=True, text=True, encoding="utf-8", cwd=crops[0].parent,
    )
    if r.returncode != 0 or not r.stdout.strip():
        raise RuntimeError(f"claude failed ({r.returncode}): {r.stderr.strip()[:300]}")
    return r.stdout.strip()


# ---------- page files ----------

def header(page):
    return f"=====================  [PDF {page} = ص {str(page).translate(AR_DIGITS)}]  ====================="


def split_pages(text):
    """{page_number: body} from a file in the `[PDF n = ص n]` header format."""
    parts = HEADER_RE.split(text)
    return {int(parts[i]): parts[i + 1].strip() for i in range(1, len(parts), 2)}


def join_pages(pages):
    return "\n\n".join(f"{header(p)}\n\n{body}" for p, body in sorted(pages.items())) + "\n"


def old_reading(vol, pages):
    old = split_pages((HERE / OLD[vol]).read_text(encoding="utf-8"))
    return {p: "\n".join(l for l in old.get(p, "").splitlines() if not l.startswith("[ملاحظة")).strip() for p in pages}


# ---------- compare / score ----------

def words(t):
    return t.split()


def ratio_err(ref, hyp):
    m = SequenceMatcher(None, ref, hyp, autojunk=False)
    return (1 - sum(b.size for b in m.get_matching_blocks()) / len(ref)) * 100 if ref else 0.0


def scores(ref, hyp):
    return {
        "WER": ratio_err(words(ref), words(hyp)),
        "CER": ratio_err(ref, hyp),
        "CER (no tashkeel)": ratio_err(DIACRITICS_RE.sub("", ref), DIACRITICS_RE.sub("", hyp)),
        "Digit err": ratio_err(DIGIT_RE.findall(ref), DIGIT_RE.findall(hyp)),
    }


def layout_norm(t):
    """Drop layout-only variation: tatweel/kashida (also the "١ ـ" dash) and spaces before . : ، ؛"""
    return re.sub(r"\s+([.:،؛])", r"\1", t.replace("ـ", ""))


def disagreements(base, other):
    """[(line_no_in_base, base_chunk, other_chunk, has_digit)] for every word-level difference."""
    line_of, toks = [], []
    for n, line in enumerate(base.splitlines(), 1):
        for w in layout_norm(line).split():
            toks.append(w)
            line_of.append(n)
    oth = words(layout_norm(other))
    out = []
    for tag, i1, i2, j1, j2 in SequenceMatcher(None, toks, oth, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        a, b = " ".join(toks[i1:i2]), " ".join(oth[j1:j2])
        line = line_of[min(i1, len(line_of) - 1)] if line_of else 0
        out.append((line, a, b, bool(DIGIT_RE.search(a + b))))
    return out


# ---------- timer ----------

class Timer:
    """One live status line: elapsed time, progress, what's running."""

    def __init__(self, total):
        self.t0, self.total, self.done, self.running = time.time(), total, 0, set()
        self.lock, self.stop = threading.Lock(), threading.Event()
        threading.Thread(target=self._tick, daemon=True).start()

    @staticmethod
    def fmt(s):
        return f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d}"

    def elapsed(self):
        return time.time() - self.t0

    def _line(self):
        eta = ""
        if self.done:
            eta = f" | ETA {self.fmt(self.elapsed() / self.done * (self.total - self.done))}"
        return f"\r\033[K⏱ {self.fmt(self.elapsed())} | {self.done}/{self.total} done{eta} | running: {', '.join(sorted(self.running)) or '-'}"

    def _tick(self):
        while not self.stop.wait(1):
            with self.lock:
                print(self._line(), end="", flush=True)

    def log(self, msg):
        with self.lock:
            print(f"\r\033[K[{self.fmt(self.elapsed())}] {msg}", flush=True)
            print(self._line(), end="", flush=True)

    def finish(self):
        self.stop.set()
        print(f"\r\033[K⏱ total {self.fmt(self.elapsed())}", flush=True)


# ---------- commands ----------

def run(vol, pages):
    d = HERE / f"vol{vol}"
    for sub in ("pages", "crops", "raw/a", "raw/b"):
        (d / sub).mkdir(parents=True, exist_ok=True)

    jobs = []
    for p in pages:
        png = d / "pages" / f"p{p:03d}.png"
        if not png.exists():
            render(vol, p, png)
        jobs.append((p, "a", slice_page(png, 2, d / "crops")))
        jobs.append((p, "b", slice_page(png, 3, d / "crops")))
    todo = [j for j in jobs if not (d / "raw" / j[1] / f"p{j[0]:03d}.txt").exists()]  # resume: skip finished reads
    print(f"{len(pages)} pages, {len(jobs)} reads ({len(jobs) - len(todo)} already done), model={MODEL}, workers={WORKERS}")

    timer = Timer(len(todo))
    times = {}

    def work(job):
        p, r, crops = job
        name = f"p{p}{r.upper()}"
        with timer.lock:
            timer.running.add(name)
        t = time.time()
        try:
            text = claude_read(crops)
            (d / "raw" / r / f"p{p:03d}.txt").write_text(text, encoding="utf-8")
            times[name] = time.time() - t
            timer.log(f"✓ {name} in {timer.fmt(times[name])}")
        except Exception as e:
            timer.log(f"✗ {name} FAILED after {timer.fmt(time.time() - t)}: {e}")
        finally:
            with timer.lock:
                timer.running.discard(name)
                timer.done += 1

    with ThreadPoolExecutor(WORKERS) as ex:
        list(ex.map(work, todo))
    timer.finish()

    write_outputs(d, vol, pages, times, timer.elapsed())


def load_reads(d, pages):
    reads, notes = {"a": {}, "b": {}}, {"a": {}, "b": {}}
    for r in reads:
        for p in pages:
            f = d / "raw" / r / f"p{p:03d}.txt"
            if f.exists():
                body, _, note = f.read_text(encoding="utf-8").partition(NOTES_SEP)
                reads[r][p], notes[r][p] = body.strip(), note.strip()
    return reads, notes


def write_outputs(d, vol, pages, times, total):
    # combined files cover every page read so far, not just this run's range
    pages = sorted(set(pages) | {int(f.stem[1:]) for f in (d / "raw" / "a").glob("p*.txt")})
    reads, notes = load_reads(d, pages)
    old = old_reading(vol, pages)
    (d / "read_a.txt").write_text(join_pages(reads["a"]), encoding="utf-8")
    (d / "read_b.txt").write_text(join_pages(reads["b"]), encoding="utf-8")
    (d / "read_c.txt").write_text(join_pages(old), encoding="utf-8")
    gold_f = d / "gold.txt"
    gold = split_pages(gold_f.read_text(encoding="utf-8")) if gold_f.exists() else {}
    new = {p: t for p, t in reads["a"].items() if p not in gold}  # never overwrite your corrections
    if new:
        gold_f.write_text(join_pages({**gold, **new}), encoding="utf-8")

    out = [f"# Vol {vol}, pages {pages[0]}–{pages[-1]}: disagreements", "",
           "Line numbers are lines inside that page's section of `gold.txt` (counting from the first text line).",
           "A = Opus, 2 slices · B = Opus, 3 slices · C = existing transcription. 🔢 = involves a digit.", ""]
    total_flags = 0
    for p in pages:
        a = reads["a"].get(p)
        if a is None:
            out += [f"## p{p}: read A missing (failed), rerun `run`", ""]
            continue
        out += [f"## p{p}  (image: `pages/p{p:03d}.png`)", ""]
        for label, other in (("B", reads["b"].get(p, "")), ("C", old.get(p, ""))):
            diffs = sorted(disagreements(a, other), key=lambda x: (not x[3], x[0]))
            total_flags += len(diffs)
            out.append(f"**A vs {label}: {len(diffs)}**")
            out += [f"- {'🔢 ' if dig else ''}line {ln}: A «{x}» · {label} «{y}»" for ln, x, y, dig in diffs]
            out.append("")
        for r in "ab":
            if notes[r].get(p):
                out += [f"*Notes from read {r.upper()}:* {notes[r][p]}", ""]
    if total:  # `report` rebuilds have no timings; the run's are in run.log
        out += ["## Timing", "", f"- Total wall time: {Timer.fmt(total)}"]
        out += [f"- {k}: {Timer.fmt(v)}" for k, v in sorted(times.items())]
    (d / "report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{total_flags} disagreements → {d / 'report.md'}\nCorrect {gold_f} against {d / 'pages'}, then: python ocr.py score --vol {vol}")


def score(vol):
    d = HERE / f"vol{vol}"
    gold = split_pages((d / "gold.txt").read_text(encoding="utf-8"))
    rows = []
    for label, f in (("A (Opus, 2 slices)", "read_a.txt"), ("B (Opus, 3 slices)", "read_b.txt"), ("C (existing)", "read_c.txt")):
        hyp = split_pages((d / f).read_text(encoding="utf-8"))
        ref_all = "\n".join(gold[p] for p in sorted(gold))
        hyp_all = "\n".join(hyp.get(p, "") for p in sorted(gold))
        rows.append((label, scores(ref_all, hyp_all)))
    keys = list(rows[0][1])
    lines = [f"# Vol {vol} scores vs gold ({len(gold)} pages)", "",
             "| Read | " + " | ".join(keys) + " |", "|---" * (len(keys) + 1) + "|"]
    lines += [f"| {label} | " + " | ".join(f"{s[k]:.2f}%" for k in keys) + " |" for label, s in rows]
    text = "\n".join(lines) + "\n"
    (d / "scores.md").write_text(text, encoding="utf-8")
    print(text)


def test():
    assert DIACRITICS_RE.sub("", "مُحَمَّدٌ") == "محمد"
    assert ratio_err("abc", "abc") == 0 and ratio_err(list("ab"), list("ax")) == 50
    s = scores("١٥١٥ ـ علي", "١٥١٦ ـ علي")
    assert s["WER"] > 0 and s["Digit err"] == 25
    d = disagreements("أخذ عن\n١٦١٩ ـ محمود", "أخذ عن\n١٦١٤ ـ محمود")
    assert d == [(2, "١٦١٩", "١٦١٤", True)], d
    assert disagreements("أخـذ عـن :\n١ ـ «كتاب» .", "أخذ عن:\n١ـ «كتاب».") == []
    pages = {90: "نص\nسطر", 91: "آخر"}
    assert split_pages(join_pages(pages)) == pages
    img = Image.new("L", (40, 100), 255)
    for y in (10, 30, 70):  # three "text lines"
        img.paste(0, (0, y, 40, y + 5))
    assert all(img.getpixel((0, c)) == 255 for c in cut_rows(img, 2))
    print("ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "report", "score", "test"])
    ap.add_argument("--vol", type=int, default=1, choices=[1, 2])
    ap.add_argument("--pages", default="90-104")
    a = ap.parse_args()
    if a.cmd == "test":
        return test()
    if a.cmd == "score":
        return score(a.vol)
    lo, _, hi = a.pages.partition("-")
    pages = list(range(int(lo), int(hi or lo) + 1))
    if a.cmd == "report":
        return write_outputs(HERE / f"vol{a.vol}", a.vol, pages, {}, 0)
    run(a.vol, pages)


if __name__ == "__main__":
    main()

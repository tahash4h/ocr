import ollama
import base64
import glob
import os
import re
import sys
from difflib import SequenceMatcher

# Windows consoles default to cp1252, which can't print characters like
# superscript footnote markers (e.g. ⁵) that show up in ground_text.txt
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MODEL = 'qwen3.5'
MAX_RETRIES = 3

# Aristotle (English) folders first, then Arabic folders
FOLDERS = ["aristotle1", "aristotle2", "arabic1", "arabic2"]

# Matches page1.png, page1.5.png, page.5.png, etc. and captures the page number
PAGE_RE = re.compile(r"page(\d+(?:\.\d+)?|\.\d+)\.png$", re.IGNORECASE)


def page_number(path):
    match = PAGE_RE.search(os.path.basename(path))
    return float(match.group(1)) if match else 0.0


BASE_INSTRUCTIONS = (
    'Extract all text from this page exactly as written, preserving formatting. '
    'This may be one half of a page, and is a continuation of the previous section, '
    'so do not repeat headers or restart numbering unless they genuinely appear here.'
)

ARABIC_INSTRUCTIONS = (
    'This page is in Arabic. Transcribe it letter-for-letter exactly as printed, including '
    'every diacritical mark (tashkeel/harakat: fatha, kasra, damma, sukun, shadda, tanwin) '
    'precisely where they appear. Do not normalize, modernize, correct, or translate the '
    'spelling — reproduce archaic or unusual forms exactly as shown. Preserve right-to-left '
    'word order and punctuation. If a word is ambiguous, transcribe your best literal reading '
    'of the glyphs rather than substituting a more "correct" or common word.'
)


def is_arabic_folder(folder):
    return "arabic" in folder.lower()


def ocr_page(image_path, arabic=False):
    prompt = BASE_INSTRUCTIONS + (" " + ARABIC_INSTRUCTIONS if arabic else "")
    with open(image_path, "rb") as img_file:
        image_data = base64.b64encode(img_file.read()).decode()
    for attempt in range(1, MAX_RETRIES + 1):
        response = ollama.generate(
            model=MODEL,
            prompt=prompt,
            images=[image_data],
            think=False,
            options={'num_predict': 4096, 'temperature': 0},
        )
        text = response['response'].strip()
        if text:
            return text
        print(f"    Empty response for {image_path} (attempt {attempt}/{MAX_RETRIES}), retrying...")
    print(f"    WARNING: {image_path} produced no text after {MAX_RETRIES} attempts.")
    return ""


def word_error_rate(ref, hyp):
    ref_words = ref.split()
    hyp_words = hyp.split()
    matcher = SequenceMatcher(None, ref_words, hyp_words)
    matches = sum(block.size for block in matcher.get_matching_blocks())
    total = max(len(ref_words), len(hyp_words))
    return (1 - matches / total) * 100 if total > 0 else 0


def char_error_rate(ref, hyp):
    matcher = SequenceMatcher(None, ref, hyp)
    matches = sum(block.size for block in matcher.get_matching_blocks())
    return (1 - matches / len(ref)) * 100 if len(ref) > 0 else 0


def diff_breakdown(ref, hyp):
    ref_words = ref.split()
    hyp_words = hyp.split()
    matcher = SequenceMatcher(None, ref_words, hyp_words)
    lines = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        ref_chunk = " ".join(ref_words[i1:i2])
        hyp_chunk = " ".join(hyp_words[j1:j2])
        if tag == "replace":
            lines.append(f"[REPLACE] ref[{i1}:{i2}]: \"{ref_chunk}\"  ->  hyp[{j1}:{j2}]: \"{hyp_chunk}\"")
        elif tag == "delete":
            lines.append(f"[MISSING] ref[{i1}:{i2}]: \"{ref_chunk}\" (dropped by OCR)")
        elif tag == "insert":
            lines.append(f"[EXTRA]   hyp[{j1}:{j2}]: \"{hyp_chunk}\" (added by OCR)")
    return lines


def process_folder(folder):
    print(f"\n=== Processing folder: {folder} ===")

    image_paths = sorted(glob.glob(os.path.join(folder, "page*.png")), key=page_number)
    if not image_paths:
        print(f"  No page images found in {folder}, skipping.")
        return

    ground_truth_path = os.path.join(folder, "ground_text.txt")
    if not os.path.exists(ground_truth_path):
        print(f"  No ground_text.txt found in {folder}, skipping.")
        return
    with open(ground_truth_path, "r", encoding="utf-8") as f:
        ground_truth = f.read()

    arabic = is_arabic_folder(folder)
    ocr_pages = []
    for image_path in image_paths:
        print(f"  Running OCR on {image_path}...")
        ocr_pages.append(ocr_page(image_path, arabic=arabic))
    ocr_text = "\n\n".join(ocr_pages)

    wer = word_error_rate(ground_truth, ocr_text)
    cer = char_error_rate(ground_truth, ocr_text)
    similarity = SequenceMatcher(None, ground_truth, ocr_text).ratio() * 100
    diffs = diff_breakdown(ground_truth, ocr_text)

    report_lines = []
    report_lines.append(f"=== PAGES PROCESSED ({len(image_paths)}) ===")
    report_lines.append(", ".join(os.path.basename(p) for p in image_paths))
    report_lines.append("")
    report_lines.append("=== OCR ACCURACY ===")
    report_lines.append(f"Word Error Rate: {wer:.2f}%")
    report_lines.append(f"Character Error Rate: {cer:.2f}%")
    report_lines.append(f"Overall Similarity: {similarity:.2f}%")
    report_lines.append("")
    report_lines.append(f"=== DIFFERENCES ({len(diffs)} mismatches) ===")
    if diffs:
        report_lines.extend(diffs)
    else:
        report_lines.append("No differences found.")
    report_lines.append("")
    report_lines.append("=== OCR OUTPUT ===")
    report_lines.append(ocr_text)
    report_lines.append("")
    report_lines.append("=== GROUND TRUTH ===")
    report_lines.append(ground_truth)

    report = "\n".join(report_lines)
    print(report)

    output_path = os.path.join(folder, "output.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"  Results saved to {output_path}")


def main():
    folders = sys.argv[1:] if len(sys.argv) > 1 else FOLDERS
    for folder in folders:
        if os.path.isdir(folder):
            process_folder(folder)
        else:
            print(f"\nFolder {folder} not found, skipping.")


if __name__ == "__main__":
    main()

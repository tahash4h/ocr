# Verification: `QR.Narrators` / `QR.NarratorSheikhs` against «الحلقات المضيئات»

**Date:** 2026-09-29
**Sources:** `alhalaqat_j1_pdf1-680_ocr.txt`, `alhalaqat_j2_pdf1-641_ocr.txt`
**Checked:** `DB/Data/QR/Narrators.csv` (106 rows), `DB/Data/QR/NarratorSheikhs.csv` (180 rows)

## Headline

**The `NarratorId` ↔ book entry-number correspondence holds.** All 105 real ids
(1–228; id 0 is a synthetic root, see below) resolve to the book entry of the
same number, and 94 of them match the book's own full name outright. Nothing
suggests an off-by-N or a re-numbering.

The gaps are in **completeness**, not identity: 47 teacher–student links that
the book states between two narrators already in the CSV are absent from
`NarratorSheikhs.csv`, and one link in the CSV is not supported by the book.

| Check | Result |
|---|---|
| CSV ids that exist as book entries | 105 / 105 |
| Full name matches the book | 94 / 105 |
| Full name is a truncation of the book's | 6 |
| Full name has a substantive difference | 5 |
| Short name: every word vouched for by the book | 105 / 105 |
| Sheikh links in CSV confirmed by the book | 171 / 180 |
| Sheikh links in CSV **not** supported by the book | 1 (+8 synthetic) |
| Sheikh links in the book **missing** from the CSV | 47 |

## How the book was read

The book prints 1637 numbered entries across 33 *halaqat* (generational rings),
each halaqa opening with its own range header (`من: ٥٩٣ إلى: ٦٩٠`). Those
headers sum to exactly **1637**, and the parse recovered **1637 entries, with no
duplicate and no gap** — so the extraction is complete against the book's own
count, not merely internally consistent.

Three further checks support the parse:

- The book's alphabetical name index (`الاسم | رقم الترجمة`) yielded exactly
  **1637 rows, one per entry number**, independently confirming the numbering.
- The `أخذ عن` (took from) and `أخذ عنه` (taught) lists are printed separately
  for every entry, so each relationship is stated twice. **99.2 %** of the 4482
  links stated in one direction are mirrored in the other — misattributed list
  items would have destroyed that agreement.
- No relationship references a non-existent entry number (0 of 4506).

The one hard problem was telling an entry heading from a reference inside a
`أخذ عن` list, since both read `<number> ـ <name>` and a well-known narrator is
referenced from dozens of other entries (al-Kisāʾī, entry 112, appears 23
times). The book vocalises entry headings fully and prints list references bare,
so each candidate was scored by the fraction of its letters carrying a strong
haraka and the *most-vocalised* candidate within each halaqa's own span was
elected. A fixed threshold does not work in either direction: a few references
carry partial vowels (~0.41) and a few genuine headings are diluted by long
unvocalised place-names (~0.15).

## 1. Full names — substantive differences (5)

Both the entry heading and the book's index agree against the CSV in every case
below.

| id | Field | Value |
|---|---|---|
| **5** | CSV | …بن قارن بن **مخروم** بن صاهلة… |
| | Book | …بن قارن بن **مخزوم** بن صاهلة… |
| | | Letter transposition in the CSV. مخزوم is also the historically attested form. |
| **36** | CSV | …بن أحمد **أيو** إسحاق السبيعي… |
| | Book | …بن أحمد **أبو** إسحاق السبيعي… |
| | | Typo: `أيو` for `أبو`. |
| **57** | CSV | ابن كثير عبد الله أبو معبد المكي |
| | Book | عبد الله بن كثير بن عمرو بن عبد الله بن هرمز أبو معبد الكناني الداري الإمام المكي |
| | | The `NarratorFullName` holds a short form, not the full name. Worth fixing — this is Ibn Kathīr, one of the seven. |
| **93** | CSV | أبان بن يزيد بن **محمد** أبو يزيد العطار البصري |
| | Book | أبان بن يزيد بن **أحمد** أبو يزيد العطار البصري |
| | | Grandfather's name differs. |
| **155** | CSV | خلاد بن خالد الشيباني الصيرفي الكوفي |
| | Book | خلاد بن خالد **أبو عيسى** الشيباني الصيرفي الكوفي راوي الإمام حمزة |
| | | The kunya أبو عيسى is dropped from the middle of the name. |

## 2. Full names — CSV truncates the book (6)

The CSV value is a clean prefix of the book's; the book adds a trailing epithet.
Harmless as identifiers, but incomplete.

| id | Dropped from the end |
|---|---|
| 14 | المدني |
| 79 | راوي الإمام عاصم |
| 80 | راوي الإمام عاصم |
| 156 | راوي الكسائي |
| 157 | راوي الإمام يعقوب |
| **166** | **المعروف برويس** راوي الإمام يعقوب |

id 166 is the one to look at: the CSV's `NarratorFullName` omits
**المعروف برويس**, and Ruways is the name this narrator is universally known by.
(The CSV's `NarratorShortName` does carry رويس.)

## 3. Short names — no discrepancies

All 105 short names check out. Every word in every `NarratorShortName` is
vouched for by the book's own text for that narrator (heading, index, or the
labels other entries use when referring to him).

They are *not* literal copies, because the two follow different conventions:

| | |
|---|---|
| CSV | `قنبل محمد بن عبد الرحمن المكي` — laqab + given name + nisba |
| Book | `قنبل راوي الإمام ابن كثير` — laqab + role in the chain |

The CSV form is the more useful of the two as a display name, since the book's
reference form frequently omits the given name entirely (`حفص راوي الإمام عاصم`,
`الدوري راوي الإمام أبي عمرو`). **No change recommended** — this is a convention
difference, not an error. It does mean short names cannot be regenerated from
the book mechanically.

## 4. Sheikh links in the CSV not supported by the book (1)

| Narrator | Sheikh | Status |
|---|---|---|
| 111 إسماعيل بن جعفر الأنصاري | 49 شيبة بن نصاح | **Not in the book** |

Entry 111 (j2 p307) lists exactly three sheikhs — **69** نافع, **90** ابن وردان,
**91** ابن جماز — and entry 49 (j2 p365) lists exactly four students — 69, 72,
90, 91. Neither side mentions the other. This link should be re-sourced or
removed.

The other 8 unmatched CSV rows are `(1..8) → 0`, the eight Companions taking
from the Prophet ﷺ. Id 0 is a synthetic root with no book entry, and the book's
halaqa 1 is precisely those eight Companions, so these are **correct by design**.

## 5. Sheikh links stated by the book but missing from the CSV (47)

Every row below is a relationship the book states between two narrators that are
*both already in `Narrators.csv`*, so each is addable without adding a narrator.
"Stated at" gives the page of the narrator's entry and of the sheikh's entry;
all 47 are stated in both the `أخذ عن` and `أخذ عنه` lists.

| Narrator | Sheikh | Stated at |
|---|---|---|
| 18 رفيع بن مهران أبو العالية | 9 عبد الله بن عباس | p384 / p379 |
| 20 عمران بن تميم أبو رجاء | 9 عبد الله بن عباس | p385 / p379 |
| 21 عبيد بن نضلة الخزاعي | 17 علقمة بن قيس النخعي | p386 / p384 |
| 40 يحيى بن يعمر العدواني | 9 عبد الله بن عباس | p360 / p379 |
| 45 مجاهد بن جبر المكي | 14 عبد الله بن السائب | p363 / p382 |
| 56 سليمان بن مهران الأعمش | 43 عاصم بن أبي النجود | p368 / p361 |
| 56 سليمان بن مهران الأعمش | 45 مجاهد بن جبر المكي | p368 / p363 |
| 57 ابن كثير المكي | 45 مجاهد بن جبر المكي | p369 / p363 |
| 72 أبو عمرو بن العلاء | 18 أبو العالية الرياحي | p333 / p384 |
| 72 أبو عمرو بن العلاء | 37 يزيد بن القعقاع | p333 / p358 |
| 72 أبو عمرو بن العلاء | 43 عاصم بن أبي النجود | p333 / p361 |
| 72 أبو عمرو بن العلاء | 49 شيبة بن نصاح | p333 / p365 |
| 72 أبو عمرو بن العلاء | 57 ابن كثير المكي | p333 / p369 |
| 72 أبو عمرو بن العلاء | 66 يزيد بن رومان | p333 / p374 |
| 74 يحيى بن الحارث الذماري | 69 نافع بن عبد الرحمن | p334 / p331 |
| 82 محمد بن عبد الرحمن بن أبي ليلى | 56 سليمان الأعمش | p339 / p368 |
| 84 إسماعيل بن عبد الله بن قسطنطين | 76 معروف بن مشكان | p340 / p335 |
| 84 إسماعيل بن عبد الله بن قسطنطين | 81 شبل بن عباد | p340 / p338 |
| 89 حمزة بن حبيب الكوفي | 82 ابن أبي ليلى | p343 / p339 |
| 90 ابن وردان المدني | 49 شيبة بن نصاح | p344 / p365 |
| 90 ابن وردان المدني | 69 نافع بن عبد الرحمن | p344 / p331 |
| 91 ابن جماز المدني | 49 شيبة بن نصاح | p344 / p365 |
| 91 ابن جماز المدني | 69 نافع بن عبد الرحمن | p344 / p331 |
| 94 المفضل بن محمد الضبي | 36 أبو إسحاق السبيعي | p346 / p357 |
| 100 هارون بن موسى العتكي | 72 أبو عمرو بن العلاء | p349 / p333 |
| 100 هارون بن موسى العتكي | 83 عيسى بن عمر الثقفي | p349 / p340 |
| 108 عيسى بن عمر الهمداني | 43 عاصم بن أبي النجود | p353 / p361 |
| 108 عيسى بن عمر الهمداني | 72 أبو عمرو بن العلاء | p353 / p333 |
| 111 إسماعيل بن جعفر الأنصاري | 69 نافع بن عبد الرحمن | p307 / p331 |
| 111 إسماعيل بن جعفر الأنصاري | 90 ابن وردان المدني | p307 / p344 |
| 111 إسماعيل بن جعفر الأنصاري | 91 ابن جماز المدني | p307 / p344 |
| 112 الكسائي | 79 شعبة بن عياش | p308 / p337 |
| 112 الكسائي | 89 حمزة بن حبيب الكوفي | p308 / p343 |
| 113 قالون | 90 ابن وردان المدني | p309 / p344 |
| 116 يحيى بن المبارك اليزيدي | 89 حمزة بن حبيب الكوفي | p311 / p343 |
| 122 يعقوب الحضرمي | 72 أبو عمرو بن العلاء | p314 / p333 |
| 122 يعقوب الحضرمي | 112 الكسائي | p314 / p308 |
| 125 يحيى بن آدم الصلحي | 112 الكسائي | p316 / p308 |
| 131 ابن ذكوان | 112 الكسائي | p319 / p308 |
| 131 ابن ذكوان | 128 إسحاق المسيبي | p319 / p318 |
| 148 خلف بن هشام البزار | 111 إسماعيل بن جعفر | p271 / p307 |
| 155 خلاد بن خالد الصيرفي | 79 شعبة بن عياش | p275 / p337 |
| 156 الليث بن خالد أبو الحارث | 116 يحيى اليزيدي | p276 / p311 |
| 168 الدوري | 111 إسماعيل بن جعفر | p281 / p307 |
| 168 الدوري | 121 سليم بن عيسى الكوفي | p281 / p314 |
| 210 البزي | 159 أحمد بن علقمة القواس | p303 / p277 |
| 214 قنبل | 210 البزي | p214 / p303 |

All page numbers are in volume ج٢ (`alhalaqat_j2_pdf1-641_ocr.txt`); printed page
equals PDF page in that file.

Several of these are load-bearing for the twenty chains — **112 ← 89**
(al-Kisāʾī from Ḥamza), **214 ← 210** (Qunbul from al-Bazzī), **122 ← 112**
(Yaʿqūb from al-Kisāʾī), **131 ← 112**, **156 ← 116** — so the DAG built from
`NarratorSheikhs` is currently missing well-attested edges.

Thirty of the 105 narrators have fewer sheikhs in the CSV than the book gives
them. The largest gaps: id 72 (أبو عمرو بن العلاء) has 8 in the CSV vs 14 in the
book; id 56 (الأعمش) 3 vs 5; id 112 (الكسائي) 5 vs 7; id 168 (الدوري) 2 vs 4.

## 6. Book-internal inconsistencies touching these narrators (4)

Not CSV problems — the book's entry heading and its own name index disagree.
Recorded so the CSV is not "corrected" toward the wrong witness.

| id | Heading | Index | Note |
|---|---|---|---|
| 5 | …بن شم**خ** بن قارن بن مخزوم… | …بن شم**س** أبو عبد الرحمن… | Index both shortens the lineage and reads شمس. CSV follows the heading. |
| 9 | …بن هاشم … أبو العباس الهاشمي | …أبو العباس بن هاشم | Reordering only. |
| **20** | عمران بن **تيم** بن ملحان | عمران بن **تميم** بن ملحان | **The CSV follows the index (تميم); the entry heading reads تيم.** Needs a human decision. |
| 57 | …الكناني **الداري** الإمام المكي | …الكنانى **الدارمى** الإمام المكى | الداري is the expected form for Ibn Kathīr. |

Separately, at j2 p359 the book prints `١٢٠ ـ محمد بن سالم الطبلاوي` in entry
1205's student list where it means `١٢٠٦`. This was already caught and verified
against the page image by the transcribers (`alhalaqat_j1_DISCREPANCIES.md` §1
row 5). It produces a spurious link from entry 120 (Warsh) and is a **book**
misprint, not an OCR error. It does not affect the CSV, since 1205 is not in it.

## Caveats

- This compares the CSV against the **OCR transcription**, not against the
  printed pages. Where transcription and print were known to differ, the
  transcribers' own logs (`alhalaqat_j*_DISCREPANCIES.md`) were consulted; the
  one relevant case is the §6 note above.
- Name matching folds Arabic diacritics, alif/yāʾ/tāʾ-marbūṭa variants and
  open/closed compounds (`عبد الله` ↔ `عبدالله`). Two names differing only in
  those respects are treated as equal.
- Nothing here has been run against a live database; it is a comparison of the
  CSV files as committed.

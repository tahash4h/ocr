# الحلقات المضيئات, Volume 1, pages 90–200: new OCR vs existing transcription

**Compared:**

- **Existing:** the full-volume transcription made earlier (`alhalaqat_j1_pdf1-680_ocr.txt`).
- **New:** two independent Claude Opus readings of every page, A and B. Each reading ran in a separate session and cut the page into different slices, with a strict instruction to copy exactly what is printed.

**Scope:** 111 pages (PDF 90–200). Differences were counted word by word, ignoring kashida (letter-stretching), dashes, and spaces before punctuation.

## Summary

| | Count |
|---|---|
| Pages compared | 111 |
| Differences, new reading A vs existing | 231 |
| Differences, reading A vs reading B | 253 |
| Real text differences (not formatting or diacritics) | 6 |
| Misread digits | 0 |

## What the differences between new and existing are

| Type | Count | Cause |
|---|---|---|
| Diacritics only | 132 | Small vowel marks on the bold entry headings, e.g. `عَلِيِّ` vs `عَلِيٍّ`, `إبْرَاهِيمُ` vs `إِبْرَاهِيمُ`. They are tiny in the scan, so readings vary. |
| Punctuation, spacing, separators | 93 | Formatting choices: `١٤١٨ هـ` vs `١٤١٨هـ`, the poem half-verse separator (`***` existing, `...` new), and two-column lists joined with a tab in the new reading. |
| Alif / hamza / yaa spelling | 6 | One side copied the print and the other normalised it, e.g. `فى` vs `في`, `الإبياري` vs `الأَبْيَارِيُّ`. |
| Different words | 23 | Mostly false alarms. The existing file joins lines into paragraphs and orders two-column lists differently, so the comparison pairs the wrong words. About 5 are real (below). |

## Real discrepancies

### Errors in the new reading

| Page | Existing | New A | New B | Printed | Cause |
|---|---|---|---|---|---|
| 174 | العرقوسوسي | **العرقوسي** | العرقوسوسي | العرقوسوسي (checked against the image) | Reading A "corrected" the book's spelling. The normal spelling appears two lines above on the same page. |
| 127 | عَلِيِّ بنِ مُحَمَّدِ بنِ مُحَمَّدِ مَعِين | **عَلِيِّ بنِ مُحَمَّدِ مَعِين** | same as existing | – | Reading A skipped a repeated phrase («محمد بن محمد»). |
| 182 | أَحْمَدُ بنُ مُحَمَّدِ بنِ مُحَمَّدِ بنِ عَلِيٍّ | **أَحْمَدُ بنُ مُحَمَّدِ بنِ عَلِيٍّ** | same as existing | – | Same slip: a repeated phrase was skipped. |

| 128 | العرقوسوسي | العرقوسوسي | **العرقوسي** | العرقوسوسي (checked against the image) | Same name and same "correction", this time in reading B. |

In every case the other independent reading had it right. The unusual name «العرقوسوسي» was "corrected" once by each reading, on different pages. That makes it the clearest example of a model normalising a name towards its common form.

### Errors in the existing transcription

| Page | Existing | New A and B | Cause |
|---|---|---|---|
| 197 | **محمد** | محمت | Both new readings copied «محمت» (a Mauritanian spelling) and noted it as printed. The existing transcription normalised it. |
| 177 | **القراءت** | القراءات | Likely a typing slip in the existing transcription (not yet checked against the image). |

### Unresolved: order of volume and page numbers

| Page | Existing | New A | New B |
|---|---|---|---|
| 127 | ١٩٨/١ | ١/ ١٩٨ | – |
| 200 | ٤/ ٨ | ٨/٤ | ٤/ ٨ |

The digits are identical and only their order differs. This is a right-to-left ordering question in footnote references, not a misreading. It needs one agreed convention.

## Printing errors in the book, noted by the new readings

The new readings were told to copy the book's errors as printed and report them separately. They reported, among others:

- **p. 92:** reference numbers 1614 and 1619 swapped in «أخذ عنه» under entry 1606. This was already confirmed in the existing discrepancy log, and both new readings kept it as printed.
- **p. 92:** «١٦١٤عبدالرافع» printed with no dash.
- **p. 94:** «بنِ بعَبْدِالله», with a doubled ب.
- **pp. 91 and 92:** missing opening quotation marks «.
- **p. 101:** «الشرفي» and «الشرقي» on the same page.
- **p. 103:** the same teacher written in two different name orders in consecutive entries.

## Conclusions

1. **Numbers are reliable in this range:** there were no misread digits across 111 pages in either the existing or the new transcription. This is worth stating because the existing transcription of **Volume 2** did have a known digit problem. Its discrepancy log (`alhalaqat_j2_DISCREPANCIES.md`, §9) confirms three places where ٢ and ٣ were confused, all in cross-reference numbers on **printed** pages, not handwritten ones:

- «١٣٣» for the printed «١٢٣» (p. 272, entry 150)
- «٣٦١» for «٢٦١» (p. 218, entry 222)
- «٧٣٠» for «٧٢٠» (p. 21, entry 617)

Two further suspected cases (entries 238 and 565) turned out, on checking the page images, to be errors in the printed book itself, not in the transcription. The log's summary line still says "five", counting those two. All three real cases had already been corrected in the existing transcription before this comparison. The same confusion did not recur anywhere in Volume 1, pp. 90–200.
2. **The two sources agree on almost all of the text.** The remaining differences are mostly diacritics on the headings and formatting.
3. **Each source has its own kind of error:**
   - The existing transcription sometimes normalises unusual spellings (محمت → محمد).
   - A single new reading occasionally "corrects" the book or skips a repeated phrase.
4. **Reading each page twice independently works:** every error in one new reading was caught by the other.

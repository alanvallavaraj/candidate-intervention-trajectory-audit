# PLOS ONE manuscript package

This folder follows the supplied PLOS LaTeX template (version 3.8, April 2026). The paper is a research article about the observed delayed harm of one-step candidate replacement. It reports negative and null outcomes transparently and does not claim a new state-of-the-art optimizer.

| File | Submission role |
|---|---|
| `main.pdf` | Upload as the **manuscript PDF**. It contains title page, abstract, body, tables, figure captions and references, with no embedded figures. |
| `Fig1.tif` | Upload separately as Fig 1. |
| `Fig2.tif` | Upload separately as Fig 2. |
| `main.tex`, `references.bib`, `plos2025.bst` | Retain as the PLOS source; supply if the journal requests LaTeX files. |
| `SUBMISSION_METADATA.md` | Text for the data availability field and a short list of author-supplied declarations. |

The two TIFF files are RGB, LZW compressed, 300 dpi, 2220 pixels wide, and below 10 MB each. Their plots are regenerated from the released CSVs with `python ../../code/make_fork_figure.py --plos` and `python ../../code/plot_injection.py --plos`, run from `data/processed/` (use `../../code` there). They have no figure number or caption in the image; each caption is directly in the manuscript.

To compile from this directory:

```bash
pdflatex -halt-on-error main.tex
bibtex main
pdflatex -halt-on-error main.tex
pdflatex -halt-on-error main.tex
```

PLOS asks for the PDF as the manuscript, with TIFFs as separate uploads. The references use the template's `plos2025.bst`. Do not include the attached `latexdiff.zip` in an initial submission; it is useful only if a tracked revised PDF is requested later.

Before submission, confirm the corresponding author email and affiliation, review the AI-tool disclosure and scientific claims, and complete the separate funding, competing-interest, CRediT, and data availability fields in the submission system. The title page intentionally leaves the email to be confirmed; a guessed address should not be published.

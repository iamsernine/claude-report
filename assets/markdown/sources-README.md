# sources/

Drop documents here when the report needs something the repository cannot
provide and `BRIEF.md` does not yet contain.

**What to put here**

- The company / department presentation deck (PDF)
- Results exports, benchmark outputs, evaluation tables
- Meeting notes, requirement documents, specifications
- A previous report or your supervisor's written remarks
- Anything else holding a fact the draft currently marks `[[TODO]]`

**Formats read directly:** `.md`, `.txt`, `.csv`, `.rst`
**Read after conversion:** `.pdf` (needs `pdftotext` or `pip install pypdf`)
**Convert first:** `.docx`, `.pptx`, `.xlsx` — save as PDF or Markdown

**Never put credentials here.** Files named like `.env`, `*.pem`, `*.key` or
`credentials.json` are detected and skipped without being read, but the safest
thing is not to place them here at all.

## How it is used

`/report:draft` reads every readable file in this folder and treats its contents
exactly like the brief: usable, quotable, never invented. PDFs are converted to
text in `.extracted/`, which is generated output — do not edit it, and do not
commit it.

Run `/report:status` or `python3 …/cli.py gaps reports_docs` to see what is still
missing, then drop the document that closes it here and draft again.

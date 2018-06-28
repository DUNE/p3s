# P3S Documentation

---
## If you are looking for the p3s introduction and tutorial...
Please read the document "JOB.pdf" found in the pdf directory.

## What's in here?
The *documents* folder contains definitive documentation for the protoDUNE prompt processing system (p3s). There are
three subfolders:
- **src**: the source files in the "markdown" format (_md_)
- **pdf**: the final product, files in the PDF format obtained by converting the _md_ files
- **graphics**: some illustrative visual materials, but these images are not necessarily a part of any other document

A PDF version of this "README" is included in the pdf directory.

---

## Content

The OVERVIEW document contains a concise description of the system design
and components.

Documentation covering p3s clients is organized into separate
files to make it easier for the user to find the right reference.
Of primary interest to the end user is the **JOB** document.

Expert-level documentation about the server maintenance will be created
at a later time

---

## Creating PDFs
In case anyone would want to rebuild a PDF (perhaps from a fresher -md_ source) -

```
pandoc -s -o README.pdf README.md
```


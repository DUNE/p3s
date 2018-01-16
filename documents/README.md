# P3S Documentation
## Content
This folder contains definitive documentation for the protoDUNE prompt processing system (p3s).
- the "src" subdirectory contains the source files are stored (in the "markdown" format)
- the "pdf" subdirectory contains the final product, files in the PDF format
- the "graphics" subdirectory contains some illustrative visual materials, but these images are not necessarily a part of any other document.

Documentation covering p3s clients is split into separate files for convenience.
Of primary interest to the end user is the _JOB_ document.

A PDF version of this "README" is included in the pdf directory.

## Creating PDFs
In case anyone want to rebuild a PDF (perhaps from a fresher **md** source) -

```
pandoc -s -o README.pdf README.md
```


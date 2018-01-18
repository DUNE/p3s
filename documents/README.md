# P3S Documentation
## What's in here?
The *documents* folder contains definitive documentation for the protoDUNE prompt processing system (p3s). There are
three subfolders:
- the "src" subdirectory contains the source files are stored (in the "markdown" format)
- the "pdf" subdirectory contains the final product, files in the PDF format
- the "graphics" subdirectory contains some illustrative visual materials, but these images are not necessarily a part of any other document.

A PDF version of this "README" is included in the pdf directory.

## Content

p3s is based on the client-server paradigm.
Documentation covering p3s clients is organized into separate
files to make it easier for the user to find the right reference.
Of primary interest to the end user is the **JOB** document.


## Creating PDFs
In case anyone want to rebuild a PDF (perhaps from a fresher **md** source) -

```
pandoc -s -o README.pdf README.md
```


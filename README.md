# ProtoDUNE Prompt Processing System (p3s)
## About the system
**p3s** stands for the ProtoDUNE Prompt Processing System.

It was initially developed as a lightweight and easy-to-deploy tool for
managing prompt processing workflows in the protoDUNE experiment at CERN.
However, p3s does not contain any special logic or dependency related specifically
to protoDUNE. It is content-agnostic and can be utilized for
many other purposes.

The design of p3s was inspired by pilot-based frameworks such as PanDA and
Dirac, but p3s is a clean sheet development and prioritizes simplicity
and component reuse over most other factors.

## Content
Important subdirectories:
- **documents**: documentation
- **promptproc**: the Web application server code
- **clients**: the p3s client code
- **inputs**:  useful examples of actual job description both for local testing and for the real operating environment
- **configuration**: templates of the p3s environment, which will likely be site-dependent

Misc:
- **display**: the Web application which is a companion of p3s, used to display results
of calculations specific to protoDUNE data quality management


## Documentation
Please consult the **documents** subdirectory for documentation concerning
- system overview
- installation of p3s and its software dependencies
- p3s client interface (important for operators and shifters)
- advanced part of the design such as workflow functionality etc

The documents are best viewed and/or printed out in the PDF format. These
files are kept in **documents/pdf** folder.

In addition, don't forget that most p3s clients are fairly well self-documented via
the use of "-h" option which prints out useful synopsis for each command.

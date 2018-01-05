# ProtoDUNE Prompt Processing System (p3s)
## About the system
**p3s** stands for the ProtoDUNE Prompt Processing System, as it was developed as a
lightweight and easy-to-deploy tool for managing prompt processing workflows
in the protoDUNE experiment at CERN. However, p3s does not contain any special logic
or dependency related to protoDUNE. It is content-agnostic and can be utilized for
many other purposes. It design is inspired by the pilot-based frameworks such as PanDA and
Dirac, but p3s is a clean sheet development and prioritizes simplicity
and component reuse over most other factors.

## Content
More important of the subdirectories are
- **promptproc** which contains the Web application server code
- **clients** which contains the client code
- **inputs** with useful examples of actual job description both for local testing and for the real operating environment

## Documentation
Please consult the *documents* subdirectory for documentation concerning
- installation
- p3s client interface (important for operators and shifters)
- advanced part of the design such as workflow functionality etc

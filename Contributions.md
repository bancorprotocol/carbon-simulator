# Contributions

We welcome contributions. We generally operate as follows

- All new contributions should be developed as feature branches on top of `main` or `beta`, and ideally be periodically rebased during development

- Finished branches should be rebased on `beta` and submitted as pull request (or pushed into the repo if you have acces)

- New code should usually contain

    - Up-to-date docstrings, at least on all user-facing functions

    - A test Jupyter notebook that demonstrates the use of the new feature, in the root area of the project from where it can run without installation (see `resources/examples` for example sheets)

    - One or multiple test cases to be included into `carbon/tests`

We will then merge the code into `beta` and eventually into `main`.
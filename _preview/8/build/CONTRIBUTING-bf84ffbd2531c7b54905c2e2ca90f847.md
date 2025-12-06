# Contributor's Guide
<br>

We welcome contributions of all kinds. If you spot a bug, please [raise an issue here](https://github.com/ASFOpenSARlab/NISAR_GCOV_Cookbook/issues). We encourage Pull Requests to address issues or add new features and data recipes.
<br>

This project uses the standard **fork → branch → pull request** workflow.

## 1. View current issues and engage in discussions
See if the issue or feature you plan to work on is already under discussion or, if it's not, start a discussion by raising an [issue](https://github.com/ASFOpenSARlab/NISAR_GCOV_Cookbook/issues).

## 2. Fork the repository
Click the **Fork** button at the top-right of the [NISAR_GCOV_Cookbook GitHub page](https://github.com/ASFOpenSARlab/NISAR_GCOV_Cookbook) to create your own copy of the repo.

## 3. Clone your fork
```bash
git clone https://github.com/<your-username>/NISAR_GCOV_Cookbook.git
cd NISAR_GCOV_Cookbook
```

## 4. Create a feature branch
```bash
git checkout -b feature/my-change
```

## 5. Add the upstream remote
This lets you pull updates from the main project.
```bash
git remote add upstream https://github.com/ASFOpenSARlab/NISAR_GCOV_Cookbook.git
git remote -v
```

## 6. Add new utility scripts (as necessary)

Add new utility scripts to the `util` directory. Favor descriptive filenames (avoid `util.py`). <!-- TODO: Include instructions related to tests for scripts -->

## 7. Add new images to render in notebooks or Markdown documents (as necessary)

Add new images to the `assets` directory.

## 8. Add new Notebooks or Markdown

Add new notebooks and Markdown docs to the `notebooks` directory

:::{tip} A note about MyST Markdown

This cookbook is built with MyST Markdown-backed [Jupyter Book 2](https://jupyterbook.org/stable/). This is an actively developing space, and while MyST opens up many exciting new capabilities for Markdown in Jupyter, these are the early days, and there are still some holes in the ecosystem. Not all of the MyST features available in a rendered HTML Jupyter Book are available when viewing the Markdown in Jupyter Lab with the [jupyterlab-myst](https://github.com/jupyter-book/jupyterlab-myst) renderer.

**Our goal is to provide a Cookbook that renders correctly as a published Jupyter Book website, as well as in Jupyter Lab.**
As you develop notebooks and documentation, please verify that your Markdown renders correctly when published as as a website as well as when viewed in Jupyter Lab with `jupyterlab-myst` installed.
:::

To maintain a consistent format for the Jupyter Book, we have provided a [Notebook template](notebooks/notebook-template.ipynb) that we encourage you to use a starting point.

## 9. Add any new dependencies to a new or existing Pixi environment
If you add dependencies, you will need to [add them to an existing or new Pixi environment](https://rse-guidelines.readthedocs.io/en/latest/fundamentals/computing-development-environments/pixi/#:~:text=packages%20go%20here-,3.%20Adding%20Dependencies,-Add%20conda%20packages).

Adds steps to install any new enviornments to the [software environment installation notebook](create_software_environment.ipynb).

## 10. Add and commit your changes
Commit in small, focused steps.
```bash
git add path/to/file1 path/to/file2
git commit -m "Describe your change"
```

## 11. Keep your branch up to date with the upstream cookbook
```bash
git fetch upstream
git merge upstream/main
# or
git rebase upstream/main
```

## 12. Push your branch
```bash
git push origin feature/my-change
```

## 13. Open a Pull Request
Go to your fork on GitHub and click **Compare & pull request**.

Please include a detailed description of your updates and the motivation behind them.

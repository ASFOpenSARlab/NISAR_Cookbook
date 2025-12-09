# Getting Started with the NISAR GCOV Cookbook

## ALERT: This Jupyter Book is under active development and currently uses pre-launch test data


[![Jupyter Book](https://img.shields.io/badge/Open-NISAR%20GCOV%20Cookbook-brightgreen?logo=jupyter)](https://asfopensarlab.github.io/NISAR_GCOV_Cookbook/)[![nightly-build](https://github.com/ProjectPythia/cookbook-template/actions/workflows/nightly-build.yaml/badge.svg)](https://github.com/ProjectPythia/cookbook-template/actions/workflows/nightly-build.yaml)
[![Binder](https://binder.projectpythia.org/badge_logo.svg)](https://binder.projectpythia.org/v2/gh/ProjectPythia/cookbook-template/main?labpath=notebooks)
[![DOI](https://zenodo.org/badge/475509405.svg)](https://zenodo.org/badge/latestdoi/475509405)

_See the [Cookbook Contributor's Guide](https://projectpythia.org/cookbook-guide) for step-by-step instructions on how to create your new Cookbook and get it hosted on the [Pythia Cookbook Gallery](https://cookbooks.projectpythia.org)!_

NISAR GCOV, is a primary data product from the NISAR mission. GCOV, or Geocoded Polarimetric Covariance, provides calibrated, L-band radar data on a standardized grid, making it straightforward to load, analyze and explore in Python. 

After learning to access and visualize GCOV data in this cookbook, you will be ready to begin applying NISAR imagery to a wide range of Earth science applications, including ecosystem monitoring, hydrology, cryosphere studies, natural hazards, and surface change analysis.


## Motivation

The NISAR mission will provide one of the most comprehensive global radar datasets ever collected, offering new opportunities to study the dynamic Earth. This cookbook is designed to help a wide range of users, including students, researchers, and communities, to begin working with NISAR’s GCOV products.

By introducing clear, hands-on examples, we hope to make the mission’s powerful data resources simple, approachable and usable. Our goal is to help you build the skills needed to explore GCOV data with confidence and apply NISAR’s capabilities to your own scientific, environmental, or community-focused questions.

## Authors

Lewandowski, Alex. White, Julia. (Several others will be added as we produce notebooks)

## Structure

### Section 1: Accessing NISAR GCOV Products
Learn where GCOV files come from, how to download them, and how to open them in Python.

### Section 2: Understanding GCOV Contents
Explore the structure of GCOV files and the meaning of key layers.

### Section 3: Visualizing GCOV Data
Create basic plots and maps using NISAR GCOV data.

### Section 4: Building Simple Analyses
Apply GCOV data to introductory examples from ecosystems, hydrology, hazards, and the cryosphere.

## Running the Notebooks

You can either run the notebook using [Binder](https://binder.projectpythia.org/) or on your local machine.

### Running on Binder

The simplest way to interact with a Jupyter Notebook is through
[Binder](https://binder.projectpythia.org/), which enables the execution of a
[Jupyter Book](https://jupyterbook.org) in the cloud. The details of how this works are not
important for now. All you need to know is how to launch a Pythia
Cookbooks chapter via Binder. Simply navigate your mouse to
the top right corner of the book chapter you are viewing and click
on the rocket ship icon, (see figure below), and be sure to select
“launch Binder”. After a moment you should be presented with a
notebook that you can interact with. I.e. you’ll be able to execute
and even change the example programs. You’ll see that the code cells
have no output at first, until you execute them by pressing
{kbd}`Shift`\+{kbd}`Enter`. Complete details on how to interact with
a live Jupyter notebook are described in [Getting Started with
Jupyter](https://foundations.projectpythia.org/foundations/getting-started-jupyter).

Note, not all Cookbook chapters are executable. If you do not see
the rocket ship icon, such as on this page, you are not viewing an
executable book chapter.


### Running on Your Own Machine

If you are interested in running this material locally on your computer, you will need to follow this workflow:

(Replace "cookbook-example" with the title of your cookbooks)

1. Clone the `https://github.com/ProjectPythia/cookbook-example` repository:

   ```bash
    git clone https://github.com/ProjectPythia/cookbook-example.git
   ```

1. Move into the `cookbook-example` directory
   ```bash
   cd cookbook-example
   ```
1. Create and activate your conda environment from the `environment.yml` file
   ```bash
   conda env create -f environment.yml
   conda activate cookbook-example
   ```
1. Move into the `notebooks` directory and start up Jupyterlab
   ```bash
   cd notebooks/
   jupyter lab
   ```

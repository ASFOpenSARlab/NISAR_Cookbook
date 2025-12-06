# Getting Started with the NISAR GCOV Cookbook
<br>

[![Jupyter Book](https://img.shields.io/badge/Open-NISAR%20GCOV%20Cookbook-brightgreen?logo=jupyter)](https://asfopensarlab.github.io/NISAR_GCOV_Cookbook/)[![nightly-build](https://github.com/ProjectPythia/cookbook-template/actions/workflows/nightly-build.yaml/badge.svg)](https://github.com/ProjectPythia/cookbook-template/actions/workflows/nightly-build.yaml)
[![Binder](https://binder.projectpythia.org/badge_logo.svg)](https://binder.projectpythia.org/v2/gh/ProjectPythia/cookbook-template/main?labpath=notebooks)

:::{figure} assets/3_PAR_SARImaging.gif
:alt: NISAR Imaging Animation

*NISAR Imaging Animation: https://assets.science.nasa.gov/content/dam/science/missions/nisar/nisar-jpl/multimedia/3_PAR_SARImaging.mp4*
:::

:::{warning} This Cookbook is pre-release and under active development

As of writing (2025-12-04), NISAR L2 GCOV data are not yet available. The workflows in this Cookbook were created using proxy NISAR test data, available here:
[https://science.nasa.gov/mission/nisar/sample-data/](https://science.nasa.gov/mission/nisar/sample-data/)
:::

NISAR GCOV, is a Level-2 data product from the NISAR mission. GCOV, or Geocoded Polarimetric Covariance, provides calibrated, L-band radar data on a standardized grid, making it straightforward to load, analyze and explore in Python. 

After learning to access and visualize GCOV data in this cookbook, you will be ready to begin applying NISAR imagery to a wide range of Earth science applications, including ecosystem monitoring, hydrology, cryosphere studies, natural hazards, and surface change analysis.


## Motivation

The NISAR mission will provide one of the most comprehensive global radar datasets ever collected, offering new opportunities to study the dynamic Earth. This cookbook is designed to help a wide range of users, including students, researchers, and communities, to begin working with NISAR’s GCOV products.

By introducing clear, hands-on examples, we hope to make the mission’s powerful data resources simple, approachable and usable. Our goal is to help you build the skills needed to explore GCOV data with confidence and apply NISAR’s capabilities to your own scientific, environmental, or community-focused questions.

## Authors

Lewandowski, Alex. White, Julia.

<a href="https://github.com/ASFOpenSARlab/NISAR_GCOV_Cookbook/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=ASFOpenSARlab/NISAR_GCOV_Cookbook" />
</a>

## Contribute!

This project is open source and developed in the open. Use, improve, and contribute to the NISAR GCOV Cookbook! See our [contributor's guide]() to learn how.

## Structure

### Section 1: About NISAR GCOV Data
Learn about NISAR GCOV data, its HDF5 structure, and its applications.

### Section 2: Tutorial Set Up
Gain access to the data and set up required software environments for the included workflows.

### Section 3: Data Access
Learn how to search, download GCOV data

### Section 4: Data Loading, Manipulation, and Visualization
Learn how to load, work with, and create visualizations of GCOV data in Python.

### Section 3: Backscatter Tutorials
Notebooks focusing on NISAR GCOV backscatter channels.

### Section 4: PolSAR Tutorials
Notebooks focusing on NISAR GCOV covariance channels.

## Running the Notebooks

You can run the notebooks on a Jupyter Hub such as [OpenSARLab](https://opensciencelab.asf.alaska.edu/) or on your local machine.

### Running on Your Own Machine

If you are interested in running this material locally on your computer, you will need to follow this workflow:

1. Clone the `https://github.com/ProjectPythia/cookbook-example` repository:

   ```bash
    git clone https://github.com/ASFOpenSARlab/NISAR_GCOV_Cookbook.git
   ```

1. Move into the `NISAR_GCOV_Cookbook` directory
   ```bash
   cd NISAR_GCOV_Cookbook
   ```
1. Move into the `notebooks` directory and start up Jupyterlab (requires that Jupyter Lab is installed)
   ```bash
   cd notebooks/
   jupyter lab
   ```
1. Run the `create_software_environment.ipynb` notebook to install the software environment needed to run the remaining notebooks in the cookbook.
1. Run additional cookbook notebooks. 

# NISAR Cookbook
<br>

[![Jupyter Book](https://img.shields.io/badge/Open-NISAR%20GCOV%20Cookbook-brightgreen?logo=jupyter)](https://asfopensarlab.github.io/NISAR_Cookbook/)[![nightly-build](https://github.com/ProjectPythia/cookbook-template/actions/workflows/nightly-build.yaml/badge.svg)](https://github.com/ProjectPythia/cookbook-template/actions/workflows/nightly-build.yaml)
[![Binder](https://binder.projectpythia.org/badge_logo.svg)](https://binder.projectpythia.org/v2/gh/ProjectPythia/cookbook-template/main?labpath=notebooks)

:::{figure} assets/3_PAR_SARImaging.gif
:alt: NISAR Imaging Animation

*NISAR Imaging Animation: https://assets.science.nasa.gov/content/dam/science/missions/nisar/nisar-jpl/multimedia/3_PAR_SARImaging.mp4*
:::

:::{warning} This Cookbook is under active development

The workflows in this Cookbook were initially created using proxy NISAR test data, available here:
[https://science.nasa.gov/mission/nisar/sample-data/](https://science.nasa.gov/mission/nisar/sample-data/)

Some workflows have been updated to use newly available production NISAR data, others have not. Those still needing work have been temporarily removed from the table of contents but remain in the repository.

Upcoming cookbook goals include:
- more GCOV backscatter notebooks
- GCOV PolSAR notebooks
- GSLC notebooks (custom InSAR generation)
- GUNW notebooks

We welcome [community contributions](contribute)!
:::

NISAR (NASA-ISRO Synthetic Aperture Radar) is a satellite mission designed to observe Earth's dynamic processes using microwave remote sensing. It's L-band and S-band measurements provide consistent global observations, regardless of cloud cover or daylight. 

After learning to access and visualize NISAR L-band data in this cookbook, you will be ready to begin applying NISAR imagery to a wide range of Earth science applications, including ecosystem monitoring, hydrology, cryosphere studies, natural hazards, and surface change analysis.

## Motivation

The NISAR mission will provide one of the most comprehensive global radar datasets ever collected, offering new opportunities to study the dynamic Earth. This cookbook is designed to help a wide range of users, including students, researchers, and communities, to begin working with NISAR’s multiple products.

By introducing clear, hands-on examples, we hope to make the mission’s powerful data resources simple, approachable and usable. Our goal is to help you build the skills needed to explore NISAR data with confidence and apply NISAR’s capabilities to your own scientific, environmental, or community-focused questions.

## Authors

Lewandowski, Alex. White, Julia.

<a href="https://github.com/ASFOpenSARlab/NISAR_GCOV_Cookbook/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=ASFOpenSARlab/NISAR_GCOV_Cookbook" />
</a>

(contribute)=
## Contribute!

This project is open source and open development. See the [contributor's guide](CONTRIBUTING.md) to learn how to join the project and make your first contribution.

## Structure

### Section 1: Cookbook Set Up
Gain access to the data and set up required software environments for the included workflows.

### Section 2: GCOV
Learn how to search, access, and work with GCOV data.

#### Section 2a: GCOV Data Access
Learn how to search and download GCOV data.

#### Section 2b: GCOV Data Loading, Manipulation, and Visualization
Learn how to load, work with, and create visualizations with GCOV data.

#### Section 2c: GCOV Backscatter Tutorials
Notebooks focusing on NISAR GCOV backscatter.

### Section 3: Additional NISAR Resources
Links to additional NISAR and NISAR GCOV resources.

### Section 4: Contibute to the NISAR Cookbook
We welcome contributions! Learn how to raise issues, make updates, and add content to this cookbook.

## Running the Notebooks

You can run the notebooks on a Jupyter Hub such as [OpenSARLab](https://opensciencelab.asf.alaska.edu/) or on your local machine.

### Running on Your Own Machine

If you are interested in running this material locally on your computer, you will need to follow this workflow:

1. Clone the `https://github.com/ProjectPythia/cookbook-example` repository:

   ```bash
    git clone https://github.com/ASFOpenSARlab/NISAR_Cookbook.git
   ```

1. Move into the `NISAR_Cookbook` directory
   ```bash
   cd NISAR_Cookbook
   ```
1. Move into the `notebooks` directory and start up Jupyterlab (requires that Jupyter Lab is installed)
   ```bash
   cd notebooks/
   jupyter lab
   ```
1. Run the `create_software_environment.ipynb` notebook to install the software environment needed to run the remaining notebooks in the cookbook.
1. Run additional cookbook notebooks. 

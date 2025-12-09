# An Introduction to NISAR Level-2 GCOV data
<br/>

:::{note} All possible covariance channels: linear (H/V) + circular/linear (RH/RV) polarizations
:::{math}
\begin{aligned}
&\left[
\begin{array}{cccc|cc}
\color{green}\langle HH\,HH^* \rangle
  & \langle HH\,HV^* \rangle
  & \langle HH\,VH^* \rangle
  & \langle HH\,VV^* \rangle
  &
  &
\\[6pt]
{\color{lightgray}\langle HV\,HH^* \rangle}
  & \color{green}\langle HV\,HV^* \rangle
  & \langle HV\,VH^* \rangle
  & \langle HV\,VV^* \rangle
  &
  &
\\[6pt]
{\color{lightgray}\langle VH\,HH^* \rangle}
  & {\color{lightgray}\langle VH\,HV^* \rangle}
  & \color{green}\langle VH\,VH^* \rangle
  & \langle VH\,VV^* \rangle
  &
  &
\\[6pt]
{\color{lightgray}\langle VV\,HH^* \rangle}
  & {\color{lightgray}\langle VV\,HV^* \rangle}
  & {\color{lightgray}\langle VV\,VH^* \rangle}
  & \color{green}\langle VV\,VV^* \rangle
  &
  &
\\ \hline
&
&
&
&
\color{green}\langle RH\,RH^* \rangle
  & \langle RH\,RV^* \rangle
\\[6pt]
&
&
&
&
{\color{lightgray}\langle RV\,RH^* \rangle}
  & \color{green}\langle RV\,RV^* \rangle
\end{array}
\right]
&
\end{aligned}
\\[12pt]
\textcolor{black}{\text{Black}}:\ \text{Included off-diagonal covariance terms}\\
\textcolor{green}{\text{Green}}:\ \text{Included diagonal terms (backscatter)}\\
\textcolor{lightgray}{\text{Light gray}}:\ \text{Conjugate off-diagonal terms (not included)}
:::


## What is NISAR GCOV data?

:::{dropdown} Explain to me like a scientist who is new to SAR

GCOV is one of NISAR’s data science products. GCOV takes radar signals collected from NISAR and process them into images that are: 
- **<span title="Data is placed onto a map using latitude/longitude, or another coordinate system, so each pixel matches a real location on Earth.">Geocoded</span>**, meaning they are assigned to their corresponding place on the Earth.
- **<span title="Data is adjusted using elevation data so hills, mountains, and valleys do not distort where features appear in the image.">Terrain corrected</span>**, meaning mountains, hills, and other slopes will not distort the radar data.
:::

:::{dropdown} Explain it to me like an experienced SAR scientist

GCOV is one of NISAR’s main Level-2 products. GCOV data are **<span title="Data is adjusted using elevation data to correct geometric and radiometric effects from topography.">radiometrically terrain-corrected (RTC)</span>** and **<span title="Data is placed onto a map using latitude/longitude, or another coordinate system, so each pixel matches a real location on Earth.">geocoded</span>**. Through RTC and a fixed map projection, GCOV removes topographic radiometric distortions and places all layers onto a consistent geographic grid.
:::

<hr/>

## What are the applications for GCOV data?

:::{dropdown} Explain to me like a scientist who is new to SAR

GCOV is useful because it removes many of the complexities that create challenges in a radar analysis. Given that GCOV data  is already corrected for terrain and mapped to a coordinate system, one can immediately analyze patterns on the ground without needing to correct viewing angles, slopes, or satellite geometry. It gives you consistent, ready-to-use data across space and time.

 Some of its many uses include: 
-Tracking snow, ice, and freeze–thaw patterns

- Monitoring forests, vegetation, and land cover change

- Studying wetlands and surface water

- Mapping agricultural fields and soil moisture

- Detecting flooding, landslides, or burn severity

- General Earth surface monitoring where backscatter is needed

GCOV provides reliable, consistent, analysis-ready imagery for science, mapping, and environmental monitoring.
:::

:::{dropdown} Explain it to me like an experienced SAR scientist
GCOV data are **<span title="Data is adjusted using elevation data so hills, mountains, and valleys do not distort where features appear in the image.">terrain-corrected</span>** and **<span title="Data is placed onto a map using latitude/longitude, or another coordinate system, so each pixel matches a real location on Earth.">geocoded</span>**, so you can immediately analyze patterns on the ground without needing to correct viewing angles, slopes, or satellite geometry. It gives you consistent, ready-to-use data across space and time.

 Some of its many uses include: 
-Tracking snow, ice, and freeze–thaw patterns

- Monitoring forests, vegetation, and land cover change

- Studying wetlands and surface water

- Mapping agricultural fields and soil moisture

- Detecting flooding, landslides, or burn severity

- General Earth surface monitoring where backscatter is needed

GCOV offers an analysis-ready representation of surface scattering behavior that avoids the complexities of RSLC-level geometry.
:::

<hr/>

## What data layers are included with a GCOV product?

:::{dropdown} Explain to me like a scientist who is new to SAR

A GCOV file contains:

- Radar images that have already been corrected for hills, slopes, and terrain **<span title="A data matrix that describes how different radar polarizations (such as HH, HV, VH, VV) relate to each other.">polarimetric covariance</span>**

- Location information that tells you exactly where each pixel is on the map **<span title="The coordinates and reference system that inform where each pixel is located on Earth.">geolocation information</span>**

- Basic details about the data, such as when it was collected and which radar settings were used at the time of collection **<span title="Additional information stored with a dataset that explains what the data is, how it was made, and how to use it correctly.">metadata</span>**

- Different frequency sections, depending on how the satellite was operating when the data was collected **<span title="Sections of the HDF5 file that organize data by radar frequency, keeping each band’s measurements separate.">frequency group</span>**

All of this is stored in an **<span title="A scientific file format that stores many datasets and metadata together in one organized structure, like folders inside a file.">HDF5 file</span>**, which is similar to a folder that contains organized, labeled pieces of data.
:::

:::{dropdown} Explain it to me like an experienced SAR scientist

A GCOV granule includes:

- **Terrain-corrected <span title="A data matrix that describes how different radar polarizations (such as HH, HV, VH, VV) relate to each other.">polarimetric covariance</span> layers** derived from RSLC data

- **<span title="The coordinates and reference system that inform where each pixel is located on Earth.">Geolocation datasets</span>** (projection definition, coordinate vectors, pixel spacing)

- **<span title="Additional information stored with a dataset that explains what the data is, how it was made, and how to use it correctly.">Metadata</span>** describing acquisition timing, frequencies, polarization combinations, and processing parameters

- **<span title="Sections of the HDF5 file that organize data by radar frequency, keeping each band’s measurements separate.">Frequency-specific groups</span>** (frequencyA and/or frequencyB depending on acquisition mode)

Everything is organized hierarchically within an **<span title="A scientific file format that stores many datasets and metadata together in one organized structure, like folders inside a file.">HDF5 structure</span>** with groups, datasets, and attributes.
:::

## What's Next?

:::{dropdown} ASF Notebooks

These notebooks offer systematic, step-by-step guidance for:

- Opening GCOV files

- Reading different layers

- Understanding the file structure

- Plotting geocoded data

- Connecting GCOV to science questions
:::

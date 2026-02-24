# Understanding HDF5 Files
<br/>


## What is HDF5?
NISAR GCOV products are delivered in HDF5, or Hierarchical Data Format version 5. HDF5 is a file format designed to efficiently store, organize, and access large scientific datasets. GCOV uses HDF5 to systematically organize radar data and metadata in a way that is both efficient and easy to read, share, and analyze.

HDF was originally developed by the National Center for Supercomputing Applications (NCSA) at the University of Illinois to support data sharing within the scientific community. HDF5 represents a significant redesign compared to earlier versions of HDF, with a more flexible and powerful internal structure. For additional details, users can consult the official HDF documentation at
<https://portal.hdfgroup.org/display/HDF5/HDF5>.


At a high level, an HDF5 file functions as a container that organizes data into a hierarchy of objects, such as **{abbr}`Groups(A folder within an HDF5 file)`**, **{abbr}`Datasets(The actual data values stored in an HDF5 file)`**, and **{abbr}`Datatypes(The type and format of data)`**. In general, radar layers are organized **{abbr}`frequencyA(Lower portion of the radar bandwidth)`**/ and (potentially) **{abbr}`frequencyB(Higher portion of the radar signal)`**/. Note that nothing stored at the root `/`.


:::{dropdown} Groups
An HDF5 **{abbr}`group(A folder within an HDF5 file)`** is a folder within an HDF5 file. Groups can hold datasets, datatypes and other groups (subfolders). In essence, groups act like directories on computers. Path navigation is identical to that or Unix path navigation: `/`.
:::
:::{dropdown} Datasets
An HDF5 **{abbr}`Dataset(A collection of data values stored in an HDF5 file)`** is where the actual data lives. This might be an array or table stored within the HDF5 file. Each dataset will include the data, a **{abbr}`dataspace(Describing the shape of the data)`**, a **{abbr}`datatype(What values are: integers, floats, etc)`**, and other optional attributes such as units, range, time, and other descriptions. 
:::

:::{dropdown} Attributes
An HDF5 **attribute** is a small piece of information that describes a **{abbr}`group(A folder within an HDF5 file)`** or **{abbr}`dataset(A collection of data values stored in an HDF5 file)`** rather than storing the data itself. Attributes provide important context that helps correctly interpret values within a dataset. Common examples include:
- Units of measurement
- Descriptions of what the data represent
- Valid ranges, dates of acquisition
- Processing details.
Storing this information with the data helps ensure that datasets can be understood and used correctly without relying on external documentation.
:::

::: {dropdown} Datatypes

An HDF5 datatype describes the kind of data that is being stored. A datatype explains how to interpret a dataset and how it is stored. Datatypes are categorized into three types: **{abbr}`Atomic Datatypes(Basic building blocks)`**, **{abbr}`Composite Datatypes(Combinations of atomic types)`**, and **{abbr}`Named Datatypes(Ways of storing and sharing datatypes)`**. 
    
``` {dropdown} Atomic Datatypes
**{abbr}`Atomic Datatypes(Basic building blocks)`** are typically the simplest datatypes. They serve as building blocks for more complex datatypes. Common atomic datatypes include:
- Time
- Bitfield
- String
- Reference
- Opaque
- Integer
- Float

**{abbr}`Derived Datatypes(Customized versions of atomic datatypes)`** in most cases, are custom versions of Atomic types. Derived datatypes are ideal for custom N-bit integers and floating-point numbers. They are useful for storing nonstandard data in optimal ways.

Derived datatypes are useful becasue they: 
- Allow ustom storage with specific numbers of bits
- Save values that don't follow standard number formats
- Match the way the data was originally recorded

The HDF5 atomic datatypes used in NISAR GCOV products are summarized in Table 3-1.
```{figure} NISAR_GCOV_Cookbook/assets/Table3.1_GCOV_Guide.png
:alt: Table 3-1 listing HDF5 atomic datatypes used in NISAR products
:name: table-3-1-hdf5-datatypes
:width: 650px
**Table 3-1.** HDF5 Atomic Datatypes used in NISAR GCOV products.  
*Source: NISAR GCOV Product Guide, NASA Jet Propulsion Laboratory (JPL).*
```

```{dropdown} Composite Datatypes
**{abbr}`Composite Datatypes(Combinations of atomic types)`** combine multiple atomic datatypes in a more complex manner. Common types of composite datatypes include: 
- **{abbr}`Array Datatypes(Fixed-size, multi-dimensional arrays treated as a single unit)`**
- **{abbr}`Variable-length datatypes(One-dimensional arrays whose length can vary between elements)`**
- **{abbr}`Compound datatypes(Collections of named fields, each with its own datatype)`**
- **{abbr}`Enumeration datatypes(Map integer values to named labels)`**
```

``` {dropdown} Named Datatypes
**{abbr}`Named Datatypes(Ways of storing and sharing datatypes)`** are stored as objects within an HDF5 file. These are ideal for reusability and sharing. 

Any datatype (atomic, derived, or composite) can be named.
Naming allows datatypes to be:
- Shared across datasets and attributes
- Reused consistently throughout a file
```
:::

## Layout of a GCOV HDF5 file
SOURCE: This is based off the NISAR L2 GCOV Guide

:::{dropdown} **Group Organization**
All GCOV content resides inside `/science/LSAR/GCOV/`. Within the HDF5 file, all GCOV data reside under /science/, and data from the L-SAR and S-SAR instruments are kept in separate groups: `/science/LSAR/` and `/science/SSAR/`. S-SAR and L-SAR data will be stored separately, regearldess of whether they cover the same geographic area. This notebook will only work with `/science/LSAR/` data.
:::

:::{dropdown} Metadata
Several kinds of metadata exist within a GCOV HDF5 file. Metadata provids contextual information that deescribes the data and how it was produced, which helps correctly interpret data. In GCOV products, both **{abbr}`File Metadata(Metadata that describes the entire file)`** and **{abbr}`Variable Metadata(Metadata that describes individual datasets)`** are provided.

```{dropdown} File Metadata 
 **{abbr}`File Metadata(Metadata that describes the entire file)`** in GCOV products are stored as global attributes that describe the product as a whole. These attributes define the data conventions, product title, mission name, producing institution, reference documentation, and contact information. **Granule-specific metadata** are stored separately in the `/science/LSAR/identification/` group and are described in later sections.
```

```{dropdown} Variable Metadata
**{abbr}`Variable metadata(Metadata specific to one acquisition)`** describe individual datasets within a GCOV HDF5 file. This metadata provides the information needed to understand what each dataset represents, how its values should be interpreted, and what values are considered valid. In GCOV products, variable metadata are stored as HDF5 attributes and are attached directly to each dataset.

#### Attributes
Each GCOV HDF5 dataset includes a set of **{abbr}`attributes(Metadata that describes a group or dataset)`** that describe the data within a dataset. These attributes provide descriptive and contextual information, such as how missing values are represented, what the data measure, and the units of the data values. Common variable attributes in an HDF5 file include: 
- `_FillValue`, describing the value used to represent missing or undefined data
- `description`, providing additional information about the dataset or how it was generated
- `long_name`, giving a human-readable, descriptive name for the dataset
- `standard_name`, providing a standardized, case-sensitive name used to identify the dataset consistently
- `units`, describing the units of the dataset’s data values
- `valid_max`, indicating the maximum theoretical valid value of the dataset
- `valid_min`, indicating the minimum theoretical valid value of the dataset

Some datasets also include statistical attributes that summarize the data values. For real-valued datasets, these may include:
- `min_value`, the minimum value in the dataset
- `mean_value`, the mean value of the dataset
- `max_value`, the maximum value of the dataset
- `sample_stddev`, the sample standard deviation of the dataset

For complex-valued datasets, similar statistics may be provided separately for the real and imaginary components. Common attributes include: 
- `min_real_value`, the minimum value of the real component
- `mean_real_value`, the mean value of the real component
- `max_real_value`, the maximum value of the real component
- `sample_stddev_real`, the sample standard deviation of the real component
- `min_imag_value`, the minimum value of the imaginary component
- `mean_imag_value`, the mean value of the imaginary component
- `max_imag_value`, the maximum value of the imaginary component
- `sample_stddev_imag`, the sample standard deviation of the imaginary component

Not all GCOV datasets include statistical attributes. The presence of these attributes depends on the dataset type. The datasets listed below are examples of GCOV datasets that may be populated with statistical attributes, grouped by whether they contain real-valued or complex-valued data. Availability of various frequencies will depend upon NISAR acquisition mode at the time of collection.

Real-valued datasets:
- `/science/LSAR/GCOV/grids/frequency[A|B]/HHHH`
- `/science/LSAR/GCOV/grids/frequency[A|B]/HVHV`
- `/science/LSAR/GCOV/grids/frequency[A|B]/VHVH`
- `/science/LSAR/GCOV/grids/frequency[A|B]/VVVV`
- `/science/LSAR/GCOV/grids/frequency[A|B]/RHRH`
- `/science/LSAR/GCOV/grids/frequency[A|B]/RVRV`
- `/science/LSAR/GCOV/grids/frequency[A|B]/numberOfLooks`
- `/science/LSAR/GCOV/grids/frequency[A|B]/rtcGammaToSigmaFactor`

Complex-valued datasets:
- `/science/LSAR/GCOV/grids/frequency[A|B]/HHHV`
- `/science/LSAR/GCOV/grids/frequency[A|B]/HHVH`
- `/science/LSAR/GCOV/grids/frequency[A|B]/HHVV`
- `/science/LSAR/GCOV/grids/frequency[A|B]/HVVH`
- `/science/LSAR/GCOV/grids/frequency[A|B]/HVVV`
- `/science/LSAR/GCOV/grids/frequency[A|B]/VHVV`
- `/science/LSAR/GCOV/grids/frequency[A|B]/RHRV`

[Source: GCOV Product Guide, Table 3-5, 3-6, 3-7, and 3-8]

#### Datasets
GCOV datasets represent radar-derived measurements organized by **{abbr}`frequency band(A specific range of radar frequencies)`** and **{abbr}`polarization(The orientation of the radar signal)`**. The datasets available in a GCOV file depend on the LSAR acquisition mode during the time of acquisition.

Data acquired from different portions of the radar bandwidth are stored in separate frequency groups. Datasets collected from the lower portion of the spectrum are stored in the **{abbr}`frequencyA(Lower portion of the radar bandwidth)`** group, while datasets from the higher portion of the spectrum are stored in the **{abbr}`frequencyB(Higher portion of the radar signal)`** group. A GCOV product may contain data from only frequencA, or both frequencyA and frequencyB.

Within each frequency group, LSAR datasets are further organized by polarization combinations, such as HH, HV, VH, and VV. As a result, the exact set of datasets included in a GCOV file can vary between products, indicative of  acquisition configuration rather than missing data.

Below is a copy of Figure 3-1 from the GCOV Product Guide, providing a visualiziation of possible LSAR acquisition modes. 

```{figure} NISAR_GCOV_Cookbook/assets/Figure3.1_GCOV_ProductGuide.png
:alt: Table 3-1 listing possible NISAR L-Band Acquisition Modes
:width: 650px
**Figure 3-1.** Possible LSAR Aquisition Modes.  
*Source: NISAR GCOV Product Guide, NASA Jet Propulsion Laboratory (JPL).*

```
:::

::: {dropdown} Georeferenced Datasets
All GCOV products include **{abbr}`georeferenced(Linked to real locations on Earth)`** HDF5 datasets, meaning each dataset is associated with a real-world location on Earth. The georeferencing information follows **{abbr}`Climate and Forecast (CF) 1.7(Standards for describing geospatial data)`** conventions, which provide standardized rules for describing spatial coordinates and map projections in Earth science data products. 
``` {dropdown} Grid Mapping
Under **{abbr}`CF conventions(Standards for describing geospatial data)`**, each georeferenced dataset must reference a **{abbr}`grid mapping(Information defining the map projection)`** dataset that informs the coordinate system used to assign the data to specific places on the Earth. In NISAR Level-2 products, this grid mapping is provided by a dataset named `projection`, which is stored in the same group as the georeferenced dataset it describes.

Each georeferenced dataset includes an attribute called `grid_mapping`, whose value is always set to "projection". This attribute links the dataset to the corresponding projection dataset that contains the coordinate reference information.
```
``` {dropdown} Coordinate Information
Spatial coordinates for georeferenced datasets are provided using HDF5 dimension scales, which associate coordinate values with each data dimension. GCOV products use one-dimensional coordinate datasets for the horizontal X and Y directions, and for elevation where applicable. These coordinates represent the center location of each pixel in the georeferenced grid.
```
``` {dropdown} Dataset Types
While most GCOV datasets are two-dimensional, some will be three-dimensional. 3D datasets are stored in the `radarGrid` group and provide geometric metadata regarding radar geometry instead of measured values. 
```
``` {dropdown} Attributes of Projection datasets
The `projection` dataset includes the following attributes:
- `ellipsoid`, describing the mathematical shape used to model the Earth
- `epsg_code`, identifying the map projection using a numeric EPSG code
- `false_easting`, describing the value added to all X coordinates to avoid negative values
- `false_northing`, describing the value added to all Y coordinates to avoid negative values
- `grid_mapping_name`, specifying the name of the grid mapping definition
- `inverse_flattening`, describing the flattening of the Earth’s ellipsoid
- `latitude_of_projection_origin`, defining the latitude used as the projection origin
- `longitude_of_projection_origin`, defining the longitude used as the projection origin
- `semi_major_axis`, describing the Earth’s equatorial radius used by the projection
- `spatial_ref`, providing a text description of the spatial reference system
- `utm_zone_number`, identifying the UTM zone used for the projection

<br/>
Source: Table 3-10, GCOV Product Guide
```
``` {dropdown} Georeferenced HDF5 Datasets
The following georeferenced datasets may be present in a GCOV product.

#### Two-dimensional datasets:
- `/science/LSAR/GCOV/grids/frequency[A|B]/HHHH`
- `/science/LSAR/GCOV/grids/frequency[A|B]/HHHV`
- `/science/LSAR/GCOV/grids/frequency[A|B]/HHVH`
- `/science/LSAR/GCOV/grids/frequency[A|B]/HHVV`
- `/science/LSAR/GCOV/grids/frequency[A|B]/HVHV`
- `/science/LSAR/GCOV/grids/frequency[A|B]/HVVH`
- `/science/LSAR/GCOV/grids/frequency[A|B]/HVVV`
- `/science/LSAR/GCOV/grids/frequency[A|B]/VHVH`
- `/science/LSAR/GCOV/grids/frequency[A|B]/VHVV`
- `/science/LSAR/GCOV/grids/frequency[A|B]/VVVV`
- `/science/LSAR/GCOV/grids/frequency[A|B]/RHRH`
- `/science/LSAR/GCOV/grids/frequency[A|B]/RHRV`
- `/science/LSAR/GCOV/grids/frequency[A|B]/RVRV`
- `/science/LSAR/GCOV/grids/frequency[A|B]/numberOfLooks`
- `/science/LSAR/GCOV/grids/frequency[A|B]/rtcGammaToSigmaFactor`

#### Three-dimensional datasets: 
- `slantRange`, describing the distance from the radar to the target
- `zeroDopplerAzimuthTime`, describing the time when the radar is closest to the target
- `incidenceAngle`, describing the angle between the radar beam and the ground
- `losUnitVectorX`, describing the X component of the radar line-of-sight direction
- `losUnitVectorY`, describing the Y component of the radar line-of-sight direction
- `alongTrackUnitVectorX`, describing the X component of the satellite motion direction
- `alongTrackUnitVectorY`, describing the Y component of the satellite motion direction
- `elevationAngle`, describing the elevation angle of the radar beam
- `groundTrackVelocity`, describing the satellite velocity along its ground track

<br/>
Source: Table 3-11, GCOV Guide
```
:::

:::{dropdown} Granules 
A GCOV **{abbr}`granule(A single data file covering a specific area on Earth)`** represents a single, spatially defined data product that follows the **{abbr}`Tiling Scheme(A system for dividing the Earth into fixed data tiles)`** designed for the NISAR mission. A single granule will cover a ground area of approximately 240 km × 240 km. Exact **{abbr}`footprints(The area on Earth covered by the data)`** may vary depending on frame location.

All GCOV granules are provided on a fixed, geocoded output grid, meaning the data are mapped to consistent geographic coordinates rather than the original radar acquisition geometry. This ensures that GCOV products are spatially aligned and easy to compare across regions and acquisition times.
:::

::: {dropdown} GCOV File Naming
Each field in the filename represents a specific property of the GCOV product. Below is the general file naming structure for GCOV data: 

<span style="color:forrest;">NISAR_IL_PT_GCOV_</span><span style="color:green;">CYL_REL_P_FRM_</span><span style="color:lightgreen;">MODE_POLE_</span><span style="color:teal;">S_StartDateTime_EndDateTime_</span><span style="color:blue;">CRID_A_C_LOC_CTR.EXT</span>

Each field in the filename represents a specific property of the GCOV product. Below is the general file naming structure for GCOV data: `NISAR_IL_PT_PROD_CYL_REL_P_FRM_MODE_POLE_S_StartDateTime_EndDateTime_CRID_A_C_LOC_CTR.EXT`


---
#### Mission, instrument, and product type
- `NISAR` — Mission name  
- `I` — Instrument (`L` for L-SAR, `S` for S-SAR)  
- `L` — Processing level (e.g., Level-2)  
- `PT` — Processing type  
  - `PR` = Production  
  - `UR` = Urgent Response  
  - `OD` = Science On-Demand  
- `GCOV` — Product identifier (Geocoded Covariance)
---
#### Orbit and acquisition geometry
- `CYL` — Mission cycle number (12-day cycles, zero-padded)  
- `REL` — Relative orbit track number within the cycle  
- `P` — Orbit direction  
  - `A` = Ascending  
  - `D` = Descending  
- `FRM` — Frame number along the orbit track
---
#### Radar configuration
- `MODE` — Bandwidth mode of the primary and secondary bands  
- `POLE` — Polarization configuration for each band  
Common polarization codes include:
- `SH` = HH (single polarization, H transmit/receive)  
- `SV` = VV (single polarization, V transmit/receive)  
- `DH` = HH/HV (dual polarization, H transmit)  
- `DV` = VV/VH (dual polarization, V transmit)  
- `QP` = HH/HV/VV/VH (quad polarization)  
- `NA` = Band not present  
---
#### Time coverage and data source

- `S` — Source of data  
  - `A` = Acquired from a single mode  
  - `M` = Mixed acquisition modes  
- `StartDateTime` — Radar start time in UTC  
- `EndDateTime` — Radar end time in UTC  

#### Time format:
`YYYYMMDDTHHMMSS`
---
### Product versioning and bookkeeping
- `CRID` — Composite Release Identifier  
- `A` — Orbit and pointing accuracy indicator  
- `C` — Coverage indicator (`F` = Full, `P` = Partial)  
- `LOC` — Processing location (e.g., `J` for JPL)  
- `CTR` — Product counter (zero-padded)  
- `EXT` — File extension (`.h5`, `.met`, `.log`)

<span style="color:red;">NISAR_IL_PT_GCOV</span>

:::



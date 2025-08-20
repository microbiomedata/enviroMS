# Table of Contents  
- Introduction
  - [EnviroMS](#EnviroMS)  
  - [Version](#current-version)  
  - [Data Input](#data-input-formats)  
  - [Data Output](#data-output-formats)  
  - [Data Structure](#data-structure-types)  
  - [Features](#molecular-formulae-search-and-assignment)  
  - [Code Documentation](https://emsl-computing.github.io/EnviroMS/)  
- Installation
  - [PyPi](#enviroms-installation)  
- Execution:  
  - [CLI](#running-the-workflow)  
  - [MiniWDL](#MiniWDL)  
  - [Docker Container](#enviroms-docker)  

# EnviroMS

**EnviroMS** is a workflow for natural organic matter data processing and annotation

## Current Version

### `5.0.0`

### Data input formats

- Generic mass list in profile and centroid mode (include all delimiters types and Excel formats)
- Intrument raw files - Thermo(.raw) and Bruker(.d) 

### Data output

The primary output consists of a molecular formula table with several columns representing specific measurements and attributes related to the mass spectrometry data. All molecular formula candidates are shown for each m/z measurement that is possible within the molecular search space defined by the user. Below is a description of each column and its significance:

  - Index: A unique identifier for each row in the dataset.

  - m/z: The mass-to-charge ratio of the detected ions. This is a fundamental measurement in mass spectrometry.

  - Calibrated m/z: The calibrated mass-to-charge ratio, adjusted for any instrumental deviations.

  - Calculated m/z: The theoretical mass-to-charge ratio calculated based on the chemical formula.

  - Peak Height: The intensity of the detected ion peak, representing the abundance of the ion.

  - Resolving Power: The measurement that represents how narrow a mass spectral peak is.

  - S/N: Signal-to-noise ratio, indicating the quality of the detected signal.

  - Ion Charge: The charge state of the ion.

  - m/z Error (ppm): The error in the measured m/z value expressed in parts per million.

  - m/z Error Score: A score representing the accuracy of the m/z measurement.

  - Mass Defect: The difference between the exact mass of an ion and its nominal mass.

  - Isotope Distribution: Information about the distribution of isotopes within the detected ion.

  - Ion Type: The type of ion detected (e.g., protonated, de-protonated).

  - Is Isotopologue: A flag indicating if the ion is an isotopologue (a molecule that differs only in the isotopic composition).

  - Mono Isotopic Index: The index of the monoisotopic peak in the isotope distribution.

  - Molecular Formula: The chemical formula of the detected ion.

  - C: Number of carbon atoms in the molecular formula.

  - H: Number of hydrogen atoms in the molecular formula.

  - O: Number of oxygen atoms in the molecular formula.

  - 13C: Number of carbon-13 isotopes in the molecular formula.

  - 18O: Number of oxygen-18 isotopes in the molecular formula.

  - 17O: Number of oxygen-17 isotopes in the molecular formula.

  - Any other atoms that is part of at least one molecular formula

In addition to the data table, diagrams are provided to serve as quick quality checks, including:

1. Mass Error Plot: Distribution of mass errors.

2. Van Krevelen Diagram: H/C vs. O/C plot, categorized by heteroatomic classes.

3. Carbon Number vs. DBE: Plot of carbon number against double bound equivalents, categorized by heteroatomic classes.

#### Data Formats
- Pandas data frame (can be saved using pickle, h5, etc)
- Text Files (.csv, tab separated .txt, etc)
- Microsoft Excel (xlsx)
- JSON for workflow metadata

### Data structure types

- FT-ICR MS
- LC-FT-ICR MS

### Molecular formulae search and assignment

- Automatic local (SQLite) or external (PostgreSQL) database check, generation, and search
- Automatic molecular formulae assignments algorithm for ESI(-) MS for natural organic matter analysis
- Automatic fine isotopic structure calculation and search for all isotopes
- Flexible Kendrick normalization base
- Kendrick filter using density-based clustering
- Kendrick classification
- Hetero atoms classification and visualization


## EnviroMS Installation

Make sure you have python 3.9.13 installed before continue

- PyPi:     
```bash
pip3 install enviroms
```

- From source:
 ```bash
pip3 install --editable .
```

To be able to open thermo raw files a installation of pythonnet is needed:
- Windows: 
    ```bash
    pip3 install pythonnet
    ```

- Mac and Linux:
    ```bash
    brew install mono
    pip3 install pythonnet   
    ```

## Running the workflow

```bash
enviroMS dump-corems-enviroms-template enviroms.toml
```
```bash
enviroMS dump-corems-template corems.toml
```

 Modify the enviroms.toml and corems.toml accordingly to your dataset and workflow parameters
make sure to include corems.toml path inside the enviroms.toml: "corems_toml_path": "path_to_corems.toml" 

```bash
enviroMS run-di configuration/enviroms.json
```

## MiniWDL 

Make sure you have python 3.9.13 installed before continue

MiniWDL uses the microbiome/enviroMS image so there is not need to install enviroMS

- Change wdl/enviroms_input.json to specify the data location

- Change configuration/corems.toml to specify the workflow parameters

Install miniWDL:
```bash
pip3 install miniwdl
```

For Direct Infusion Workflow:
```bash
miniwdl run wdl/di_fticr_ms.wdl -i wdl/di_fticr_wdl_input.json --verbose --no-cache --copy-input-files
```
For Liquid Chromatography Workflow:
```bash
miniwdl run wdl/lc_fticr_ms.wdl -i wdl/lc_fticr_wdl_input.json --verbose --no-cache --copy-input-files
```

WARNING ** Current mode only allows for multiprocessing in a single node and it defaults to one job at a time. 
To use multiprocessing mode modify the parameter "runDirectInfusion.jobs_count" in the enviroMS.wdl and modify the parameter "MolecularFormulaSearch.url_database" on corems.toml to point to a Postgresql url. The default is set to use SQLite and it will fail on multiprocessing mode.

## EnviroMS Docker 

You will need docker and docker compose: 

If you don't have it installed, the easiest way is to [install docker for desktop](https://www.docker.com/products/docker-desktop/)

A docker image containing the EnviroMS command line as code entry-point

- Pull from Docker Registry:

    ```bash
    docker pull microbiome/enviroms:latest
    
    ```

- Or to build the image from source (after cloning microbiomedata/enviroMS github repo):

    ```bash
    docker build -t microbiomedata/enviroms:latest .
    ```
- Run Workflow from Container:

    $(data_dir) = dir_containing the FT-ICR MS data
    $(configuration_dir) = dir_containing the enviroms.toml, corems.toml and nmdc_metadata.json
    
    ```bash
    docker run -v $(data_dir):/enviroms/data \
               -v $(configuration_dir):/enviroms/configuration \
                  microbiomedata/enviroms:latest enviroMS run-di /enviroms/configuration/enviroms.toml    
    ```

- Save a new parameters file template:
    
    ```bash
    docker run -v $(data_dir):/enviroms/data \
               -v $(configuration_dir):/enviroms/configuration \
                microbiomedata/enviroms:latest enviroMS dump_di_template /enviroms/configuration/enviroms.toml    
    ```
    
    ```bash
    docker run -v $(data_dir):/enviroms/data \
               -v $(configuration):/enviroms/configuration \
                microbiomedata/enviroms:latest enviroMS dump_corems_template /enviroms/configuration/corems.toml
    ```

## Disclaimer

This material was prepared as an account of work sponsored by an agency of the
United States Government.  Neither the United States Government nor the United
States Department of Energy, nor Battelle, nor any of their employees, nor any
jurisdiction or organization that has cooperated in the development of these
materials, makes any warranty, express or implied, or assumes any legal
liability or responsibility for the accuracy, completeness, or usefulness or
any information, apparatus, product, software, or process disclosed, or
represents that its use would not infringe privately owned rights.

Reference herein to any specific commercial product, process, or service by
trade name, trademark, manufacturer, or otherwise does not necessarily
constitute or imply its endorsement, recommendation, or favoring by the United
States Government or any agency thereof, or Battelle Memorial Institute. The
views and opinions of authors expressed herein do not necessarily state or
reflect those of the United States Government or any agency thereof.

                 PACIFIC NORTHWEST NATIONAL LABORATORY
                              operated by
                                BATTELLE
                                for the
                   UNITED STATES DEPARTMENT OF ENERGY
                    under Contract DE-AC05-76RL01830
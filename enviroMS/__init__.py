__version__ = "4.2.1"
__doc__ = '''
# Table of Contents  
- Introduction
  - [EnviroMS](#EnviroMS)  
  - [Version](#current-version)  
  - [Data Input](#data-input-formats)  
  - [Data Output](#data-output-formats)  
  - [Data Structure](#data-structure-types)  
  - [Features](#molecular-formulae-search-and-assignment)  
- Installation
  - [PyPi](#enviroms-installation)  
- Execution:  
  - [CLI](#running-the-workflow)  
  - [MiniWDL](#MiniWDL)  
  - [Docker Container](#enviroms-docker)  
  

# EnviroMS

**EnviroMS** is a workflow for natural organic matter data processing and annotation

## Current Version

### `4.1.1`

### Data input formats

- Generic mass list in profile and centroid mode (include all delimiters types and Excel formats)

### Data output formats

- Pandas data frame (can be saved using pickle, h5, etc)
- Text Files (.csv, tab separated .txt, etc)
- Microsoft Excel (xlsx)
- Automatic JSON for workflow metadata
- Self-containing Hierarchical Data Format (.hdf5) including raw data and ime-series data-point for processed data-sets with all associated workflow metadata (JSON)

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
enviroMS dump-corems-enviroms-template EnviromsFile.json
```
```bash
enviroMS dump-corems-template CoremsFile.json
```

 Modify the EnviromsFile.json and CoremsFile.json accordingly to your dataset and workflow parameters
make sure to include CoremsFile.json path inside the EnviromsFile.json: "corems_json_path": "path_to_CoremsFile.json" 

```bash
enviroMS run-di path_to_MetamsFile.json
```

## MiniWDL 
- Change wdl/enviroms_input.json to specify the data location

- Change data/CoremsFile.json to specify the workflow parameters

Install miniWDL:
```bash
pip3 install miniwdl
```

Call:
```bash
miniwdl run wdl/enviroMS.wdl -i wdl/enviroms_input.json --verbose --no-cache --copy-input-files
```

WARNING ** Current mode only allows for multiprocessing in a single node and it defaults to one job at a time. 
To use multiprocessing mode modify the parameter "runDirectInfusion.jobs_count" in the enviroMS.wdl and modify the parameter "MolecularFormulaSearch.url_database" on CoremsFile.json to point to a Postgresql url. The default is set to use SQLite and it will fail on multiprocessing mode.

## EnviroMS Docker 

A docker image containing the EnviroMS command line as code entry-point

If you don't have docker installed, the easiest way is to [install docker for desktop](https://hub.docker.com/?overlay=onboarding)

- Pull from Docker Registry:

    ```bash
    docker pull corilo/enviroms:latest
    
    ```

- Or to build the image from source:

    ```bash
    docker build -t enviroms:latest .
    ```
- Run Workflow from Container:

    $(data_dir) = dir_containing the FT-ICR MS data, EnviromsFile.json and CoremsFile.json
    
    ```bash
    docker run -v $(data_dir):/enviroms/data corilo/enviroms:latest enviroMS run-di /enviroms/data/EnviromsFile.json    
    ```

- Save a new parameters file template:
    
    ```bash
    docker run -v $(data_dir):/enviroms/data corilo/enviroms:latest enviroMS dump_json_template /enviroms/data/EnviromsFile.json    
    ```
    
    ```bash
    docker run -v $(data_dir):/metaB/data corilo/enviroms:latest enviroMS dump_corems_json_template /metaB/data/CoremsFile.json
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
'''
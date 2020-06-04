# EnviroMS

**EnviroMS** is a workflow for natural organic matter data processing and annotation

## Current Version

### `1.2.1`

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
enviroMS dump_json_template EnviromsFile.json
```
```bash
enviroMS dump_corems_json_template CoremsFile.json
```

 Modify the EnviromsFile.json and CoremsFile.json accordingly to your dataset and workflow parameters
make sure to include CoremsFile.json path inside the EnviromsFile.json: "corems_json_path": "path_to_CoremsFile.json" 

```bash
enviroMS run-di path_to_MetamsFile.json
```

## EnviroMS Docker 

A docker image containing the EnviroMS command line as code entry-point

If you don't have docker installed, the easiest way is to [install docker for desktop](https://hub.docker.com/?overlay=onboarding)

- Pull from Docker Registry:

    ```bash
    docker pull corilo/enviroms:latest
    
    ```

- Build the image from source:

    ```bash
    docker build -t enviroms:latest .
    ```
- Run Workflow from Container:

    $(data_dir) = dir_containing the FT-ICR MS data, EnviromsFile.json and CoremsFile.json
    
    ```bash
    docker run -v $(data_dir):/metaB/data corilo/enviroms:latest run-di /metaB/data/EnviromsFile.json    
    ```

- Get the parameters templates:
    
    ```bash
    docker run -v $(data_dir):/metaB/data corilo/enviroms:latest dump_json_template /metaB/data/EnviromsFile.json    
    ```
    
    ```bash
    docker run -v $(data_dir):/metaB/data corilo/enviroms:latest dump_corems_json_template /metaB/data/CoremsFile.json
    ```
    
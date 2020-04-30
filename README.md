# EnviroMS

**EnviroMS** is a workflow for natural organic matter data processing and annotation

## Current Version

### `1.0.0`

### Data input formats

- CoreMS self-containing Hierarchical Data Format (.hdf5)

### Data output formats

- Pandas data frame (can be saved using pickle, h5, etc)
- Text Files (.csv, tab separated .txt, etc)
- Microsoft Excel (xlsx)
- JSON for workflow metadata
- Self-containing Hierarchical Data Format (.hdf5) including raw data and ime-series data-point for processed data-sets with all associated metadata stored as json attributes

### Data structure types

- FT-ICR MS
- LC-FT-ICR MS

## Available features

### Signal Processing

- Baseline detection, subtraction, smoothing 
- Manual and automatic noise threshold calculation
- First and second derivatives peak picking methods
- Peak Area Calculation
- EIC Chromatogram deconvolution(TODO)

### Calibration

- Ledford
- Linear
- Quadratic

### Compound Identification

- Automatic local (SQLite) or external (PostgreSQL) database check, generation, and search
- Automatic molecular match algorithm

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

## Usage

```bash
enviroMS dump_json_template EnviromsFile.json
```
```bash
enviroMS dump_corems_json_template CoremsFile.json
```

 Modify the EnviromsFile.json and CoremsFile.json accordingly to your dataset and workflow parameters
make sure to include CoremsFile.json path inside the EnviromsFile.json: "corems_json_path": "path_to_CoremsFile.json" 

```bash
enviroMS run-gcms-workflow path_to_MetamsFile.json
```

## EnviroMS Docker 

A docker image containing the EnviroMS command line as the entry point

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

    $(data_dir) = dir_containing the gcms data, EnviromsFile.json and CoremsFile.json
    
    ```bash
    docker run -v $(data_dir):/metaB/data corilo/enviroms:latest run-gcms-workflow /metaB/data/EnviromsFile.json    
    ```

- Getting the parameters templates:
    
    ```bash
    docker run -v $(data_dir):/metaB/data corilo/enviroms:latest dump_json_template /metaB/data/EnviromsFile.json    
    ```
    
    ```bash
    docker run -v $(data_dir):/metaB/data corilo/enviroms:latest dump_corems_json_template /metaB/data/CoremsFile.json
    ```
    
from dataclasses import dataclass

@dataclass
class DiWorkflowParameters:
    
    file_paths: tuple = ('data/...', 'data/...')
    output_directory: str = 'data/...'
    output_filename: str = 'data/...'
    output_type: str = 'csv'
    corems_json_path: str = 'data/coremsFile.json'
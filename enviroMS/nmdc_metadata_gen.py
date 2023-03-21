from dataclasses import dataclass, field, asdict
from datetime import datetime
import hashlib
from json import dumps
from enum import Enum
from pathlib import Path
import yaml
import oauthlib

import nmdc_schema.nmdc as nmdc
import requests_oauthlib

@dataclass
class NomAnalysisActivity:
    codebase_url:str = "https://github.com/microbiomedata/enviroMS"
    cluster_name:str = "EMSL-RZR"
    nom_21T_instrument_name: str = "21T Agilent"

@dataclass
class OmicsProcessing:
    nom_omics_processing_type:str = "Organic Matter Characterization"
    nom_omics_processing_description:str = "High resolution MS spectra only"
    nom_21T_instrument_name: str = "21T Agilent"

@dataclass
class DataObject:
    nom_raw_data_object_type:str = "Direct Infusion FT ICR-MS Raw Data"
    nom_raw_data_object_description:str = "Raw 21T Direct Infusion Data"
    nom_dp_data_object_type:str = "FT ICR-MS Analysis Results"
    nom_dp_data_object_description:str = "EnviroMS FT ICR-MS natural organic matter workflow molecular formula assignment output details",
    
@dataclass
class NMDC_Types: 
    
    BioSample:str = "nmdc:BioSample"
    OmicsProcessing:str = "nmdc:OmicsProcessingActivity"
    NomAnalysisActivity:str = "nmdc:NomAnalysisActivity"
    DataObject:str = "nmdc:DataObject"

@dataclass
class NMDC_Mint:
    
    schema_class: dict = field(default_factory= lambda: {
        'schema': None,
    })
    how_many:int = 1

    @property
    def __dict__(self):
        return asdict(self)

    @property
    def json(self):
        return dumps(self.__dict__)

def mint_nmdc_id(type:NMDC_Types, how_many:int = 1): 
    
    config = yaml.safe_load(open('./config.yaml','r'))
    client = oauthlib.oauth2.BackendApplicationClient(client_id=config['client_id'])
    oauth = requests_oauthlib.OAuth2Session(client=client)
    
    token = oauth.fetch_token(token_url='https://api.microbiomedata.org/token',
                              client_id=config['client_id'], 
                              client_secret=config['client_secret'])

    nmdc_mint_url = "https://api.microbiomedata.org/pids/mint"
    
    payload = NMDC_Mint(type, how_many)
    
    #response = s.post(nmdc_mint_url, data=payload.json, )
    #list_ids = response.json()
    print(payload.json)
    response = oauth.post(nmdc_mint_url, data=payload.json)
    list_ids = response.json()

    return list_ids

def get_data_object(file_path:Path, base_url:str, was_generated_by:str,
                data_object_type:str, description:str):
    base_url = "https://nmdcdemo.emsl.pnnl.gov/nom/raw/"
    
    nmdc_id = mint_nmdc_id({'id': NMDC_Types.DataObject.value})[0]

    data_dict = {
                'id': nmdc_id,
                "name": file_path.name,
                "file_size_bytes": file_path.stat().st_size,
                "md5_checksum": hashlib.md5(file_path.open('rb').read()).hexdigest(),
                "url": base_url + str(file_path.name),
                "was_generated_by": was_generated_by,
                "data_object_type": data_object_type,
                "description": description,
                "type": "nmdc:DataObject"
                } 

    data_object = nmdc.DataObject(**data_dict)

    return data_object

def get_omics_processing(file_path:Path, instrument_name:str, sample_id:str,
                raw_data_id:str, omics_type:str,  description:str, project_id:str):
    
    nmdc_id = mint_nmdc_id({'id': NMDC_Types.OmicsProcessing.value})[0]
    
    data_dict = {
                'id': nmdc_id,
                "name": file_path.stem,
                "instrument_name": instrument_name,
                "has_input": sample_id,
                "has_output": raw_data_id,
                "omics_type": {"has_raw_value": omics_type},
                "part_of": project_id,
                "processing_institution": "Environmental Molecular Science Laboratory",
                "description": description,
                "type": "nmdc:OmicsProcessing"
                } 

    omicsProcessing = nmdc.OmicsProcessing(**data_dict)

    return omicsProcessing

def get_nom_analysis_activity(cluster_name:str, code_repository_url, 
                          raw_data_id:str, data_product_id:str, 
                          has_calibration:bool,  omics_processing_id, 
                          instrument_name:str):
    
    nmdc_id = mint_nmdc_id({'id': NMDC_Types.NomAnalysisActivity.value})[0]
    
    data_dict = {
                'id': nmdc_id,
                "execution_resource": cluster_name,
                "git_url": code_repository_url,
                "has_input": [raw_data_id],
                "has_output": [data_product_id],
                "has_calibration": has_calibration,
                "ended_at_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "started_at_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "used": instrument_name,
                "was_informed_by": omics_processing_id,
                "type": "nmdc:NomAnalysisActivity"
                } 

    nomAnalysisActivity = nmdc.NomAnalysisActivity(**data_dict)

    return nomAnalysisActivity

def create_nmdc_metadata(raw_data_path:Path, base_url:str,
                         nmdc_study_id:str, 
                         create_biosample=False):

    if create_biosample:
        biosample_id = mint_nmdc_id({'id': NMDC_Types.BioSample.value})[0]
        bioSample =  nmdc.BioSample(id=biosample_id)

    omicsProcessing = get_omics_processing(raw_data_path,
                                           OmicsProcessing.nom_21T_instrument_name,
                                           bioSample.id, None, 
                                           OmicsProcessing.nom_omics_processing_type,
                                           OmicsProcessing.nom_omics_processing_description,
                                           nmdc_study_id
                                           )
    
    rawDataObject = get_data_object(raw_data_path, base_url + 'nom/raw/', 
                                    was_generated_by=omicsProcessing.id, 
                                    data_object_type =DataObject.nom_raw_data_object_type,
                                    description =DataObject.nom_raw_data_object_description)
    
    nomAnalysisActivity = get_nom_analysis_activity(NomAnalysisActivity.cluster_name,
                                                NomAnalysisActivity.codebase_url,
                                                rawDataObject.id, None, False, 
                                                omicsProcessing.id,
                                                NomAnalysisActivity.nom_21T_instrument_name)

    dataProductDataObject = get_data_object(raw_data_path, base_url + 'nom/results/', 
                                    was_generated_by=nomAnalysisActivity.id, 
                                    data_object_type =DataObject.nom_dp_data_object_type,
                                    data_object_type =DataObject.nom_dp_data_object_description)
    
    #circular dependencies : great! 
    nomAnalysisActivity.has_input = rawDataObject.id
    nomAnalysisActivity.has_output = dataProductDataObject.id
    omicsProcessing.has_output = rawDataObject.id
    
'''

def run_nom_nmdc_data_processing():

    file_ext = '.raw'  # '.d' 
    data_dir = Path("/Users/eber373/OneDrive - PNNL/Documents/Data/FT_ICR_MS/Spruce_Data/")
    dms_file_path = Path("/Users/eber373/OneDrive - PNNL/Documents/Data/FT_ICR_MS/Spruce_Data/SPRUCE_FTICR_Peat.xlsx")

    results_dir = Path("results/")
    registration_path = results_dir / "spruce_ftms_nom_data_products.json"
    failed_files = results_dir / "nom_failed_files.json"
    pos_files = results_dir / "pos_files.json"

    field_strength = 21
    cores = 4
    ref_calibration_path = False

    # file_paths = get_dirnames()
    ref_calibration_path = Path("db/Hawkes_neg.ref")

    dms_mapping = DMS_Mapping(dms_file_path)
    selected_files = dms_mapping.get_selected_sample_list()

    failed_list = []
    pos_list = []

    '''

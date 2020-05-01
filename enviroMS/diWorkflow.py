from dataclasses import dataclass, asdict

import multiprocessing
from pathlib import Path
import os
import cProfile

from corems.mass_spectrum.input.massList import ReadMassList
from corems.mass_spectrum.factory.classification import HeteroatomsClassification
from corems.molecular_id.search.priorityAssignment import OxygenPriorityAssignment
from corems.molecular_id.search.molecularFormulaSearch import SearchMolecularFormulas
from corems.transient.input.brukerSolarix import ReadBrukerSolarix

import json
import click
from multiprocessing import Pool
from corems.molecular_id.factory.MolecularLookupTable import MolecularCombinations
from corems.encapsulation.factory.processingSetting import MolecularFormulaSearchSettings
from corems.encapsulation.input.parameter_from_json import load_and_set_parameters_class

@dataclass
class DiWorkflowParameters:
    
    file_paths: tuple = ('data/...', 'data/...')
    input_type: str = 'masslist'
    output_directory: str = 'data/...'
    output_filename: str = 'data/...'
    output_type: str = 'csv'
    corems_json_path: str = 'data/coremsFile.json'

    def to_json(self):
        return json.dumps(asdict(self))

def run_bruker(file_location, corems_params_path):
    
    with ReadBrukerSolarix(file_location) as transient:

        transient.set_parameter_from_json(corems_params_path) 
        mass_spectrum = transient.get_mass_spectrum(plot_result=False, auto_process=True)
        
        return mass_spectrum

def get_masslist(file_location, corems_params_path, polarity):

    reader = ReadMassList(file_location)
    reader.set_parameter_from_json(parameters_path=corems_params_path)
    return(reader.get_mass_spectrum(polarity=-1))


def run_assignment(file_location, workflow_params_json_str):
    
    
    workflow_params = DiWorkflowParameters(**json.loads(workflow_params_json_str))
    
    if workflow_params.input_type == 'bruker':
    
       mass_spectrum = run_bruker(file_location, workflow_params.corems_json_path)
    
    elif workflow_params.input_type == 'masslist':
    
       mass_spectrum = get_masslist(file_location, workflow_params.corems_json_path, polarity=-1)

    mass_spectrum.set_parameter_from_json(workflow_params.corems_json_path)
    
    #force it to one job. daemon child can not have child process 
    mass_spectrum.molecular_search_settings.db_jobs = 1

    mass_spectrum.filter_by_max_resolving_power(15, 2)
 
    SearchMolecularFormulas(mass_spectrum, first_hit=True).run_worker_mass_spectrum()
    
    print(mass_spectrum.percentile_assigned())

    mass_spectrum_by_classes = HeteroatomsClassification(mass_spectrum, choose_molecular_formula=True)
    
    return mass_spectrum

def generate_database(corems_parameters_file, jobs):
    
    '''corems_parameters_file: Path for CoreMS JSON Parameters file
       --jobs: Number of processes to run   
    '''
    click.echo('Loading Searching Settings from %s' % corems_parameters_file)

    molecular_search_settings = load_and_set_parameters_class('MolecularSearch', MolecularFormulaSearchSettings(), parameters_path=corems_parameters_file)

    molecular_search_settings.db_jobs = jobs

    MolecularCombinations().runworker(molecular_search_settings)


def read_workflow_parameter(di_workflow_paramaters_json_file):
    
    with open(di_workflow_paramaters_json_file, 'r') as infile:
        return DiWorkflowParameters(**json.load(infile))    

def workflow_worker(args):
    
    file_location, workflow_params_json_str = args
    
    mass_spec = run_assignment(file_location, workflow_params_json_str)

    return mass_spec, os.getpid()

def cprofile_worker(file_location, workflow_params_json_str):

    cProfile.runctx('run_assignment(file_location, workflow_params)', globals(), locals(), 'di-fticr-di.prof')
    #stats = pstats.Stats("topics.prof")
    #stats.strip_dirs().sort_stats("time").print_stats() 

def run_direct_infusion_workflow(workflow_params_file, jobs, replicas):
    
    click.echo('Loading Searching Settings from %s' % workflow_params_file)

    workflow_params = read_workflow_parameter(workflow_params_file)
    
    dirloc = Path(workflow_params.output_directory)
    dirloc.mkdir(exist_ok=True)
    
    worker_args = replicas*[(file_path, workflow_params.to_json()) for file_path in workflow_params.file_paths]
    
    cores = jobs
    pool = Pool(cores)
    
    for i, results in enumerate(pool.imap_unordered(workflow_worker, worker_args), 1):
        
        mass_spectrum, job_id =results

        output_path = '{DIR}/{NAME}_{ID}'.format(DIR=workflow_params.output_directory, NAME=workflow_params.output_filename, ID=job_id)
    
        eval('mass_spectrum.to_{OUT_TYPE}(output_path)'.format(OUT_TYPE=workflow_params.output_type))

        mass_spectrum.to_dataframe()["Ion Type"]

    pool.close()
    pool.join()
    
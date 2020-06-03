

import cProfile
from dataclasses import dataclass, asdict
import json
from multiprocessing import Pool
import os
from pathlib import Path

import click

from corems.mass_spectrum.calc.Calibration import MzDomainCalibration
from corems.mass_spectrum.factory.classification import HeteroatomsClassification
from corems.mass_spectrum.input.massList import ReadMassList

from corems.molecular_id.search.priorityAssignment import OxygenPriorityAssignment
from corems.molecular_id.search.molecularFormulaSearch import SearchMolecularFormulas
from corems.transient.input.brukerSolarix import ReadBrukerSolarix

from corems.molecular_id.factory.MolecularLookupTable import MolecularCombinations
from corems.encapsulation.factory.processingSetting import MolecularFormulaSearchSettings
from corems.encapsulation.input.parameter_from_json import load_and_set_parameters_class


@dataclass
class DiWorkflowParameters:
    
    #input type: masslist, bruker_transient, thermo_reduced_profile
    input_type: str = 'masslist'
    
    #scans to sum for thermo raw data, reduce profile
    start_scan:int = 1
    final_scan:int = 7

    #input output paths 
    file_paths: tuple = ('data/...', 'data/...')
    output_directory: str = 'data/...'
    output_filename: str = '...'
    output_type: str = 'csv'
    
    #polarity for masslist input
    polarity: int = -1
    
    #corems settings 
    corems_json_path: str = 'data/CoremsFile.json'
    
    #calibration
    calibrate: bool = True
    calibration_ref_filepath: str = 'data/SRFA.ref'
    
    def to_json(self):
        return json.dumps(asdict(self))

def run_thermo_reduce_profile(file_location, corems_params_path):
    
    from corems.mass_spectra.input import rawFileReader
    mass_spectrum = rawFileReader.ImportLCMSThermoMSFileReader(file_location).get_summed_mass_spectrum(1,7)
    return mass_spectrum

def run_bruker_transient(file_location, corems_params_path):
    
    with ReadBrukerSolarix(file_location) as transient:

        transient.set_parameter_from_json(corems_params_path) 
        mass_spectrum = transient.get_mass_spectrum(plot_result=False, auto_process=True)
        
        return mass_spectrum

def get_masslist(file_location, corems_params_path, polarity):

    reader = ReadMassList(file_location)
    reader.set_parameter_from_json(parameters_path=corems_params_path)

    return(reader.get_mass_spectrum(polarity=polarity))

def run_assignment(file_location, workflow_params):
    
    if workflow_params.input_type == 'thermo_reduced_profile':
    
       mass_spectrum = run_thermo_reduce_profile(file_location, workflow_params)

    if workflow_params.input_type == 'bruker_transient':
    
       mass_spectrum = run_bruker_transient(file_location, workflow_params.corems_json_path)
    
    elif workflow_params.input_type == 'masslist':
    
       mass_spectrum = get_masslist(file_location, workflow_params.corems_json_path, polarity=workflow_params.polarity)

    mass_spectrum.set_parameter_from_json(workflow_params.corems_json_path)
    
    if workflow_params.calibrate:
        
        ref_file_location = Path(workflow_params.calibration_ref_filepath) 

        MzDomainCalibration(mass_spectrum, ref_file_location).run()

    #force it to one job. daemon child can not have child process 
    mass_spectrum.molecular_search_settings.db_jobs = 1

    SearchMolecularFormulas(mass_spectrum, first_hit=False).run_worker_mass_spectrum()
    
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
    
    workflow_params = DiWorkflowParameters(**json.loads(workflow_params_json_str))

    mass_spec = run_assignment(file_location, workflow_params)

    dirloc = Path(workflow_params.output_directory)
    
    dirloc.mkdir(exist_ok=True)

    output_path = '{DIR}/{NAME}_{ID}'.format(DIR=workflow_params.output_directory, NAME=workflow_params.output_filename, ID= os.getpid())
    
    eval('mass_spec.to_{OUT_TYPE}(output_path)'.format(OUT_TYPE=workflow_params.output_type))

    return 'Success' + str(os.getpid())

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
        
        pass

    pool.close()
    pool.join()

def run_di_mpi(workflow_params_file, tasks, replicas):
    
    import os, sys
    from mpi4py import MPI
    #from mpi4py.futures import MPIPoolExecutor
    sys.path.append(os.getcwd()) 
    
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    
    workflow_params = read_workflow_parameter(workflow_params_file)
    all_worker_args = replicas*[(file_path, workflow_params.to_json()) for file_path in workflow_params.file_paths]
    
    #worker_args = comm.scatter(all_worker_args, root=0)
    
    # will only run tasks up to the number of files paths selected in the EnviroMS File
    if len(all_worker_args) <= size:

        workflow_worker(all_worker_args[0])
    else:

        print("Tasks needs to be the same size of the input data count, , until you find time to come and help to code this section :D")
        
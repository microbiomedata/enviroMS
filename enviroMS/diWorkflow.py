import cProfile
from dataclasses import dataclass, asdict
import json
from multiprocessing import Pool
import os
from pathlib import Path

import click
from tqdm import tqdm

from matplotlib import pyplot as plt
from corems.mass_spectrum.calc.Calibration import MzDomainCalibration
from corems.molecular_id.factory.classification import HeteroatomsClassification
from corems.mass_spectrum.input.massList import ReadMassList

from corems.molecular_id.search.priorityAssignment import OxygenPriorityAssignment
from corems.molecular_id.search.molecularFormulaSearch import SearchMolecularFormulas
from corems.transient.input.brukerSolarix import ReadBrukerSolarix

from corems.molecular_id.factory.MolecularLookupTable import MolecularCombinations
from corems.encapsulation.factory.processingSetting import MolecularFormulaSearchSettings
from corems.encapsulation.input.parameter_from_json import load_and_set_parameters_class

@dataclass
class DiWorkflowParameters:

    # input type: masslist, bruker_transient, thermo_reduced_profile
    
    # scans to sum for thermo raw data, reduce profile
    raw_file_start_scan: int = 1
    raw_file_final_scan: int = 7

    # input output paths
    file_paths: tuple = ('data/...', 'data/...')
    output_directory: str = 'data/...'
    output_group_name: str = '...'
    output_type: str = 'csv'

    # polarity for masslist input
    polarity: int = -1
    is_centroid:bool = False
    # corems settings
    corems_json_path: str = 'data/CoremsFile.json'

    # calibration
    calibrate: bool = True
    calibration_ref_file_path: str = 'data/SRFA.ref'

    # plots
    plot_mz_error: bool = True
    plot_ms_assigned_unassigned: bool = True

    plot_c_dbe: bool = True
    plot_van_krevelen: bool = True
    plot_ms_classes: bool = True
    plot_mz_error_classes: bool = True

    def to_json(self):
        return json.dumps(asdict(self))

def run_thermo_reduce_profile(file_location, corems_params_path, first_scan, last_scan):

    from corems.mass_spectra.input import rawFileReader
    parser =  rawFileReader.ImportMassSpectraThermoMSFileReader(file_location)
    
    mass_spectrum = parser.get_average_mass_spectrum_in_scan_range(first_scan=1, last_scan=5)
    return mass_spectrum

def run_bruker_transient(file_location, corems_params_path):

    with ReadBrukerSolarix(file_location) as transient:

        transient.set_parameter_from_json(corems_params_path) 
        mass_spectrum = transient.get_mass_spectrum(plot_result=False, auto_process=True)
    
    return mass_spectrum

def get_masslist(file_location, corems_params_path, polarity, is_centroid):

    if is_centroid:
        reader = ReadMassList(file_location)
    else:
       reader = ReadMassList(file_location, header_lines=7, isCentroid=False, isThermoProfile=True)
    
    reader.set_parameter_from_json(parameters_path=corems_params_path)

    return(reader.get_mass_spectrum(polarity=polarity))

def run_assignment(file_location, workflow_params):

    file_path = Path(file_location)
    
    if file_path.suffix == '.raw':
    
        first_scan, last_scan = workflow_params.raw_file_start_scan, workflow_params.raw_file_final_scan    
        mass_spectrum = run_thermo_reduce_profile(file_location, workflow_params, first_scan, last_scan)

    elif file_path.suffix == '.d':

        mass_spectrum = run_bruker_transient(file_location, workflow_params.corems_json_path)

    
    elif file_path.suffix == '.txt' or file_path.suffix == 'csv' or file_path.suffix == '.tsv':
        
        mass_spectrum = get_masslist(file_location, workflow_params.corems_json_path, 
                        polarity=workflow_params.polarity, is_centroid=workflow_params.is_centroid)


    mass_spectrum.set_parameter_from_json(workflow_params.corems_json_path)
    
    if workflow_params.calibrate:

        ref_file_location = Path(workflow_params.calibration_ref_file_path)

        MzDomainCalibration(mass_spectrum, ref_file_location).run()

    # force it to one job. daemon child can not have child process 
    mass_spectrum.molecular_search_settings.db_jobs = 1

    SearchMolecularFormulas(mass_spectrum, first_hit=False).run_worker_mass_spectrum()

    
    return mass_spectrum

def generate_database(corems_parameters_file, jobs):

    '''corems_parameters_file: Path for CoreMS JSON Parameters file
       --jobs: Number of processes to run   
    '''
    click.echo('Loading Searching Settings from %s' % corems_parameters_file)

    molecular_search_settings = load_and_set_parameters_class('MolecularSearch', MolecularFormulaSearchSettings(), parameters_path=corems_parameters_file)
    molecular_search_settings.db_jobs = jobs
    molecular_search_settings.url_database = None
    MolecularCombinations().runworker(molecular_search_settings)

def read_workflow_parameter(di_workflow_paramaters_json_file):

    with open(di_workflow_paramaters_json_file, 'r') as infile:
        return DiWorkflowParameters(**json.load(infile))

def create_plots(mass_spectrum, workflow_params, dirloc):

    ms_by_classes = HeteroatomsClassification(mass_spectrum, choose_molecular_formula=False)

    if workflow_params.plot_ms_assigned_unassigned:
        print("Plotting assigned vs. unassigned mass spectrum")
        ax_ms = ms_by_classes.plot_ms_assigned_unassigned()
        plt.savefig(dirloc / "assigned_unassigned.png", bbox_inches='tight')
        plt.clf()

    if workflow_params.plot_mz_error:
        print("Plotting mz_error")
        ax_ms = ms_by_classes.plot_mz_error()
        plt.savefig(dirloc / "mz_error.png", bbox_inches='tight')
        plt.clf()

    if workflow_params.plot_van_krevelen:
        van_krevelen_dirloc = dirloc / "van_krevelen"
        van_krevelen_dirloc.mkdir(exist_ok=True, parents=True)  

    if workflow_params.plot_c_dbe:
        c_dbe_dirloc = dirloc / "dbe_vs_c"
        c_dbe_dirloc.mkdir(exist_ok=True, parents=True)      

    if workflow_params.plot_ms_classes:
        ms_class_dirloc = dirloc / "ms_class"
        ms_class_dirloc.mkdir(exist_ok=True, parents=True)  

    if workflow_params.plot_mz_error_classes:
        mz_error_class_dirloc = dirloc / "mz_error_class"
        mz_error_class_dirloc.mkdir(exist_ok=True, parents=True)  

    pbar = tqdm(ms_by_classes.get_classes())

    for classe in pbar:

        pbar.set_description_str(desc="Plotting results for class {}".format(classe), refresh=True)

        if workflow_params.plot_van_krevelen:
            ax_c = ms_by_classes.plot_van_krevelen(classe)
            plt.savefig(van_krevelen_dirloc / "{}.png".format(classe), bbox_inches='tight')
            plt.clf()

        if workflow_params.plot_mz_error_classes:
            ax_c = ms_by_classes.plot_mz_error_class(classe)
            plt.savefig(mz_error_class_dirloc / "{}.png".format(classe), bbox_inches='tight')
            plt.clf()

        if workflow_params.plot_ms_classes:
            ax_c = ms_by_classes.plot_ms_class(classe)
            plt.savefig(ms_class_dirloc / "{}.png".format(classe), bbox_inches='tight')
            plt.clf()

        if workflow_params.plot_c_dbe:
            ax_c = ms_by_classes.plot_dbe_vs_carbon_number(classe)
            plt.savefig(c_dbe_dirloc / "{}.png".format(classe), bbox_inches='tight')
            plt.clf()

def workflow_worker(args):

    file_location, workflow_params_json_str = args

    workflow_params = DiWorkflowParameters(**json.loads(workflow_params_json_str))
    
    mass_spec = run_assignment(file_location, workflow_params)

    dirloc = Path(workflow_params.output_directory) / mass_spec.sample_name

    dirloc.mkdir(exist_ok=True, parents=True)

    output_path = dirloc / mass_spec.sample_name

    eval('mass_spec.to_{OUT_TYPE}(output_path)'.format(OUT_TYPE=workflow_params.output_type))

    create_plots(mass_spec, workflow_params, dirloc)

    return 'Success' + str(os.getpid())

def cprofile_worker(file_location, workflow_params_json_str):

    cProfile.runctx('run_assignment(file_location, workflow_params)', globals(), locals(), 'di-fticr-di.prof')
    # stats = pstats.Stats("topics.prof")
    # stats.strip_dirs().sort_stats("time").print_stats() 

def run_wdl_direct_infusion_workflow(*args, **kwargs):
    
    cores = kwargs.get('jobs')
    del kwargs['jobs']
    kwargs["polarity"] = -1 if kwargs.get('polarity') == 'negative' else 1
    
    workflow_params = DiWorkflowParameters(**kwargs)
    workflow_params.file_paths = workflow_params.file_paths.split(",")
    # workflow_params.output_directory = kwargs.get['output_directory']
    # workflow_params.output_type = kwargs.get['output_type']
    # workflow_params.corems_json_path = kwargs.get['corems_json_path']
    # workflow_params.polarity = -1 if kwargs.get['polarity'] == 'negative' else 1
    # workflow_params.raw_file_start_scan = kwargs.get['raw_file_start_scan']
    # workflow_params.raw_file_final_scan = kwargs.get['raw_file_final_scan']
    # workflow_params.is_centroid = kwargs.get['is_centroid']
    # workflow_params.calibration_ref_file_path = kwargs.get['calibration_ref_file_path']

    # workflow_params.calibrate = kwargs.get['calibrate']
    # workflow_params.calibrate = kwargs.get['plot_mz_error']
    # workflow_params.calibrate = kwargs.get['plot_ms_assigned_unassigned']
    # workflow_params.calibrate = kwargs.get['plot_c_dbe']
    # workflow_params.calibrate = kwargs.get['plot_van_krevelen']
    # workflow_params.calibrate = kwargs.get['plot_ms_classes']
    # workflow_params.calibrate = kwargs.get['plot_mz_error_classes']
    # workflow_params.calibrate = kwargs.get['calibrate']

    dirloc = Path(workflow_params.output_directory)
    dirloc.mkdir(exist_ok=True)

    pool = Pool(cores)

    worker_args = [(file_path, workflow_params.to_json()) for file_path in workflow_params.file_paths]
    file_path = Path(worker_args[0][0])
    #for worker_arg in worker_args:
    #    workflow_worker(worker_arg)
    
    for i, results in enumerate(pool.imap_unordered(workflow_worker, worker_args), 1):
        pass
    pool.close()
    pool.join()

def run_direct_infusion_workflow(workflow_params_file, jobs, replicas):

    click.echo('Loading Searching Settings from %s' % workflow_params_file)

    workflow_params = read_workflow_parameter(workflow_params_file)

    dirloc = Path(workflow_params.output_directory)
    dirloc.mkdir(exist_ok=True)

    worker_args = replicas * [(file_path, workflow_params.to_json()) for file_path in workflow_params.file_paths]

    cores = jobs
    pool = Pool(cores)

    for worker_arg in worker_args:
        workflow_worker(worker_arg)
    # for i, results in enumerate(pool.imap_unordered(workflow_worker, worker_args), 1):

    #    pass

    pool.close()
    pool.join()

def run_di_mpi(workflow_params_file, tasks, replicas):

    import os, sys
    from mpi4py import MPI
    # from mpi4py.futures import MPIPoolExecutor
    sys.path.append(os.getcwd())

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    workflow_params = read_workflow_parameter(workflow_params_file)
    all_worker_args = replicas * [(file_path, workflow_params.to_json()) for file_path in workflow_params.file_paths]

    # worker_args = comm.scatter(all_worker_args, root=0)

    # will only run tasks up to the number of files paths selected in the EnviroMS File
    if len(all_worker_args) <= size:

        workflow_worker(all_worker_args[0])

    else:

        print("Tasks needs to be the same size of the input data count, , until you find time to come and help to code this section :D")

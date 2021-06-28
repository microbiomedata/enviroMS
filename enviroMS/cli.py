
from pathlib import Path
import json
import sys

import click

from enviroMS.singleMzSearch import run_molecular_formula_search
from enviroMS.diWorkflow import DiWorkflowParameters, generate_database, run_di_mpi, run_direct_infusion_workflow, run_wdl_direct_infusion_workflow
from corems.molecular_id.search.molecularFormulaSearch import SearchMolecularFormulas
from corems.encapsulation.output.parameter_to_json import dump_ms_settings_json, dump_all_settings_json

class Config:
    def __init__(self):
        self.verbose = False
        
pass_config = click.make_pass_decorator(Config, ensure=True)

@click.group()
@click.option('--verbose', is_flag=True, help='print out the results')
@pass_config
def cli(config, verbose):
    
    config.verbose = verbose

@cli.command()
@click.argument('mz', required=True, type=float, )
@click.argument('corems_parameters_filepath', required=True, type=click.Path())
@click.argument('out', required=False, type=click.File('w'), default='-')
@click.option('-e', '--error', 'ppm_error', default=1.0,  help='the marging of mass error (ppm)')
@click.option('-r', '--radical', 'isRadical', default=True, type=bool, help='include radical ion type') 
@click.option('-p', '--protonated', 'isProtonated', default=True, type=bool, help='include (de)-protonated ion type')
@click.option('-a', '--adduct', 'isAdduct', default=False, type=bool, help='include adduct ion type')

@pass_config
def run_search_formula(config, mz, ppm_error, isRadical, isProtonated, isAdduct,out, corems_parameters_filepath):#settings_filepath
    
    '''Search for molecular formula candidates to a given m/z value \n
       corems_parameters_filepath =' CoreMS Parameters File (JSON)' 
       MZ = m/z value FLOAT\n
       out = filename to store results TEXT\n
    '''
    
    #if config.verbose:
    click.echo('', file=out)
    #dump_search_settings_yaml()    
    
    click.echo('Searching formulas for %.5f' % mz, file=out)
    
    click.echo('', file=out)
    
    click.echo('Loading Searching Settings from %s' % corems_parameters_filepath, file=out)
    
    click.echo('',file=out)

    run_molecular_formula_search(mz, out, corems_parameters_filepath)

@cli.command()
@click.argument('corems_parameters_file', required=True, type=str)
@click.option('--jobs','-j', default=4, help="'cpu's'")
def create_database(corems_parameters_file, jobs):
    '''corems_parameters_file: Path for CoreMS JSON Parameters file\n
       jobs: Number of processes to run\n
       "postgresql://postgres:labthomson0102@172.22.113.27:5432/",
    '''
    generate_database(corems_parameters_file, jobs)

@cli.command()
@click.argument('file_paths', required=True, type=str)
@click.argument('output_directory', required=True, type=str)
@click.argument('output_type', required=True, type=str)
@click.argument('corems_json_path', required=True, type=str)
@click.argument('polarity', required=True, type=str)
@click.argument('raw_file_start_scan', required=True, type=int)
@click.argument('raw_file_final_scan', required=True, type=int)
@click.argument('is_centroid', required=True, type=bool)
@click.argument('calibration_ref_file_path', required=False, type=str)
@click.option('--calibrate','-c', default=True)
@click.option('--plot_mz_error', '-e', default=True)
@click.option('--plot_ms_assigned_unassigned','-a', default=True)
@click.option('--plot_c_dbe', '-cb', default=True)
@click.option('--plot_van_krevelen', '-vk', default=True)
@click.option('--plot_ms_classes', '-mc', default=True)
@click.option('--plot_mz_error_classes', '-ec',  default=True)
@click.option('--jobs','-j', default=4, help="'cpu's'")
def run_di_wdl(*args, **kwargs):
    '''Run the Direct Infusion Workflow using wdl'''
    
    run_wdl_direct_infusion_workflow(*args, **kwargs)


@cli.command()
@click.argument('di_workflow_paramaters_file', required=True, type=str)
@click.option('--jobs','-j', default=4, help="'cpu's'")
@click.option('--replicas','-r', default=1, help="data replicas")
@click.option('--tasks','-t', default=4, help="mpi tasks")
@click.option('--mpi','-m', is_flag=True, help="run mpi version")
def run_di(di_workflow_paramaters_file, jobs, replicas, tasks, mpi):
    '''Run the Direct Infusion Workflow\n
       workflow_paramaters_file = json file with workflow parameters\n
       output_types = csv, excel, pandas, json set on the parameter file\n
       corems_json_path = json file with corems parameters\n
       --jobs = number of processes to run in parallel\n 
       --mpi = run on hpc, if omitted will run python's multiprocessing and will duplicate runs on nodes\n
    '''
    if mpi:
        
        run_di_mpi(di_workflow_paramaters_file, tasks, replicas)

    else:    

        run_direct_infusion_workflow(di_workflow_paramaters_file, jobs, replicas)

@cli.command()
@click.argument('lcms_workflow_paramaters_file', required=True, type=str)
@click.option('--jobs','-j', default=4, help="'cpu's'")
@pass_config
def run_lcms(workflow_paramaters_file, jobs):
    #implement a mz search inside the mass spectrum, then run a search for molecular formula and the isotopologues
    pass       

@cli.command()
@click.argument('json_file_name', required=True, type=click.Path())
def dump_corems_template(json_file_name):
    '''Dumps a CoreMS json file template
        to be used as the workflow parameters input 
    '''
    path_obj = Path(json_file_name).with_suffix('.json')
    dump_all_settings_json(file_path=path_obj)

@cli.command()
@click.argument('json_file_name', required=True, type=click.Path())
def dump_corems_enviroms_template(json_file_name):
    '''Dumps a CoreMS json file template
        to be used as the workflow parameters input 
    '''
    path_obj = Path(json_file_name).with_suffix('.json')
    dump_ms_settings_json(file_path=path_obj)

@cli.command()
@click.argument('json_file_name', required=True, type=click.Path())
def dump_di_template(json_file_name):
    '''Dumps a json file template
        to be used as the workflow parameters input
    '''
    ref_lib_path = Path(json_file_name).with_suffix('.json')
    with open(ref_lib_path, 'w') as workflow_param:
    
        json.dump(DiWorkflowParameters().__dict__, workflow_param, indent=4)
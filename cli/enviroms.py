import click

import sys
sys.path.append("..//CoreMS")

from corems.molecular_id.search.molecularFormulaSearch import SearchMolecularFormulas
from corems.encapsulation.settings.io import settings_parsers  

from corems.mass_spectrum.input.numpyArray import ms_from_array_centroid
from tabulate import tabulate

class Config(object):
    def __init__(self):
        self.verbose = False
        self.home_directory = '.'   
        self.settings_filepath =  'SearchConfig.json'

pass_config = click.make_pass_decorator(Config, ensure=True)   

@click.group()
@click.option('--verbose', is_flag=True,  help='print out the results')
@click.option('--home_directory', type=click.Path())
@click.option('-s', '--settings', 'settings_filepath', type=click.Path(),  default='SearchConfig.json',  help='JSOS File with the molecular formula search settings')

@pass_config

def cli(config, verbose, home_directory, settings_filepath):
    
    config.verbose = verbose
    config.home_directory = home_directory
    config.settings_filepath = settings_filepath
    
@cli.command()
@click.argument('mz', required=True, type=float, )
@click.argument('out', required=False, type=click.File('w'), default='-')
@click.option('-e', '--error', 'mz_error', default=1.0,  help='the marging of mass error (ppm)')
@click.option('-r', '--radical', 'isRadical', default=True, type=bool, help='include radical ion type') 
@click.option('-p', '--protonated', 'isProtonated', default=True, type=bool, help='include (de)-protonated ion type')
@click.option('-a', '--adduct', 'isAdduct', default=False, type=bool, help='include adduct ion type')
@pass_config

def search_formula(config, mz, mz_error, isRadical, isProtonated, isAdduct,out):#settings_filepath
    '''Search for molecular formula candidates to a given m/z value \n
       MZ = m/z value FLOAT\n
       out = filename to store results TEXT\n
    '''
    #if config.verbose:
    
    click.echo('', file=out)
    #dump_search_settings_yaml()    
    
    click.echo('Searching formulas for %.5f' % mz, file=out)
    
    click.echo('', file=out)
    
    click.echo('Loading Searching Settings from %s' % config.settings_filepath, file=out)
    
    click.echo('',file=out)

    settings_parsers.load_search_setting_json(settings_path=config.settings_filepath)
    
    run_molecular_formula_search(mz, out)

    
@cli.command()
@click.argument('mz', required=True, type=float, )
@click.argument('out', required=False, type=click.File('w'), default='-')
@click.option('-e', '--error', 'mz_error', default=1.0,  help='the marging of mass error (ppm)')
@click.option('-r', '--radical', 'isRadical', default=True, type=bool, help='include radical ion type') 
@click.option('-p', '--protonated', 'isProtonated', default=True, type=bool, help='include (de)-protonated ion type')
@click.option('-a', '--adduct', 'isAdduct', default=False, type=bool, help='include adduct ion type')

@pass_config
def search_mspeak_formula(config, mz, mz_error, isRadical, isProtonated, isAdduct,out):#settings_filepath
    
    '''Search for mass spectrum peak in the mass spectrum and \n
        search for a molecular formula candidates to a given m/z value \n
        MZ = m/z value FLOAT\n
        out = filename to store results TEXT\n
    '''
    #if config.verbose:
    
    click.echo('', file=out)

def run_molecular_formula_search_massspectrum(mz, out, filelocation, mspeak_index=None):
    
    #implement a mz search inside the mass spectrum, then run a search for molecular formula and the isotopologues
    
    mz = [mz]
    abundance = [1]
    rp, s2n = [1,1]
    dataname = out
    
    mass_spectrum_obj = ms_from_array_centroid(mz, abundance, rp, s2n, dataname)

    click.echo('Searching for molecular formulas within %.3f - %.3f ppm' % (mass_spectrum_obj.molecular_search_settings.min_mz_error, mass_spectrum_obj.molecular_search_settings.max_mz_error))

    SearchMolecularFormulas(mass_spectrum_obj, find_isotopologues=True).run_worker_ms_peak(mass_spectrum_obj[0])
    
    ms_peak = mass_spectrum_obj[0]
    
    if ms_peak.is_assigned:
        
        header = ['Molecular Formula',  'Calculated m/z', 'Mass Error', 'DBE', 'Ion Type', 'Expected Isotopologue Count', 'Found Isotopologue Count']
        
        results = []
        
        for formula in ms_peak:
            results.append([formula.to_string, formula.mz_theor, formula.mz_error, formula.dbe, formula.ion_type, len(formula.expected_isotopologues), len(formula.mspeak_indexes_isotopologues)])
              
        
        click.echo(tabulate(results, headers=header, floatfmt=("s", ".5f", ".5f", ".1f", "s"  )), file=out)
        click.echo('', file=out)        
        
    else:        
        
        click.echo("Could not find a possible molecular formula match for the m/z %.5f" % mz[0], file=out)
        click.echo('', file=out)

def run_molecular_formula_search(mz, out):
    
    mz = [mz]
    abundance = [1]
    rp, s2n = [1,1]
    dataname = out
    
    mass_spectrum_obj = ms_from_array_centroid(mz, abundance, rp, s2n, dataname)
    
    click.echo('Searching for molecular formulas within %.3f and %.3f ppm' % (mass_spectrum_obj.molecular_search_settings.min_mz_error, mass_spectrum_obj.molecular_search_settings.max_mz_error))

    SearchMolecularFormulas(mass_spectrum_obj, find_isotopologues=True).run_worker_ms_peak(mass_spectrum_obj[0], mass_spectrum_obj)
    
    ms_peak = mass_spectrum_obj[0]
    
    if ms_peak.is_assigned:
        
        header = ['Molecular Formula',  'Calculated m/z', 'Mass Error', 'DBE', 'Ion Type']
        
        results = []
        
        for formula in ms_peak:
            
            results.append([formula.to_string, formula.mz_theor, formula.mz_error, formula.dbe, formula.ion_type])
              
        
        click.echo(tabulate(results, headers=header, floatfmt=("s", ".5f", ".5f", ".1f", "s"  )), file=out)
        click.echo('', file=out)        
        
    else:        
        
        click.echo("Could not find a possible molecular formula match for the m/z %.5f" % mz[0], file=out)
        click.echo('', file=out)
        
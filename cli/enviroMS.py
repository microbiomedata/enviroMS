import click
from corems.molecular_id.search.MolecularFormulaSearch import SearchMolecularFormulas
from corems.mass_spectrum.input.fromData import ms_from_array_centroid
from tabulate import tabulate

class Config(object):
    def __init__(self):
        self.verbose = False
        self.home_directory = '.'   
pass_config = click.make_pass_decorator(Config, ensure=True)   

@click.group()
@click.option('--verbose', is_flag=True,  help='print out the results')
@click.option('--home_directory', type=click.Path())

@pass_config
def cli(config, verbose, home_directory):
    config.verbose = verbose
    config.home_directory = home_directory
    
@cli.command()
@click.argument('mz', required=True, type=float, )
@click.argument('out', required=False, type=click.File('w'), default='-')
@click.option('-e', '--error', 'mz_error', default=1.0,  help='the marging of mass error (ppm)')
@click.option('-r', '--radical', 'isRadical', default=True, type=bool, help='include radical ion type') 
@click.option('-p', '--protonated', 'isProtonated', default=True, type=bool, help='include (de)-protonated ion type')
@click.option('-a', '--adduct', 'isAdduct', default=False, type=bool, help='include adduct ion type')

@pass_config
def search_formula(config, mz, mz_error, isRadical, isProtonated, isAdduct,out):
    '''Search for molecular formula candidates to a given m/z value \n
       MZ = m/z value FLOAT\n
       out = filename to store results TEXT\n
    '''
    #if config.verbose:
    click.echo('',file=out)
    click.echo('Searching formulas for %.5f' % mz, file=out)
    click.echo('',file=out)
    run_molecular_formula_search(mz, out)

def run_molecular_formula_search(mz, out):
    
    mz = [mz]
    abundance = [1]
    rp, s2n = [1,1]
    dataname = out
    mass_spectrum_obj = ms_from_array_centroid(mz, abundance, rp, s2n, dataname)
    SearchMolecularFormulas().run_worker_ms_peak(mass_spectrum_obj[0], mass_spectrum_obj)
    ms_peak = mass_spectrum_obj[0]
    
    if ms_peak.is_assigned:
        
        header = ['Calculated m/z', 'Mass Error', 'Molecular Formula', 'DBE', 'Ion Type']
        
        results = []
        
        for formula in ms_peak:
            results.append([formula.to_string_formated, round(formula.mz_theor,7), round(formula.mz_error,3), round(formula.dbe,1), formula.ion_type])
        
        click.echo(tabulate(results, headers=header), file=out)
        click.echo('', file=out)        
    
    else:        
        
        click.echo("Could not find a possible molecular formula match for the m/z %.5f" % mz[0], file=out)
        click.echo('', file=out)
        
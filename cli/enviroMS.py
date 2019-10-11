import click

class Config(object):
    def __init__(self):
        self.verbose = False

pass_config = click.make_pass_decorator(Config, ensure=True)   

@click.group()
@click.option('--verbose', is_flag=True,  help='print out the results')
@click.option('--home_directory', type=click.Path())

@pass_config
def cli(config, verbose, home_directory):
    config.verbose = verbose
    if home_directory is None:
        home_directory = '.'    
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
    if config.verbose:
        click.echo('Searching formulas for %.5f' % mz, file=out)
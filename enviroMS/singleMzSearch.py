
import click
from tabulate import tabulate
from pathlib import Path
from corems.mass_spectrum.input.numpyArray import ms_from_array_centroid
from corems.encapsulation.input import parameter_from_json
from corems.molecular_id.search.molecularFormulaSearch import SearchMolecularFormulas


def run_molecular_formula_search(mz, out, parameters_filepath):
    
    mz = [mz]
    abundance = [1]
    rp, s2n = [[1],[1]]
    dataname = Path(str(out))
    
    mass_spectrum_obj = ms_from_array_centroid(mz, abundance, rp, s2n, dataname)
    
    parameter_from_json.load_and_set_parameters_ms(mass_spectrum_obj, parameters_path=parameters_filepath)

    mass_spectrum_obj.molecular_search_settings.use_min_peaks_filter = False
    mass_spectrum_obj.molecular_search_settings.use_min_peaks_filter = 10
    mass_spectrum_obj.molecular_search_settings.use_isotopologue_filter = False

    click.echo('Searching for molecular formulas within %.3f and %.3f ppm' % (mass_spectrum_obj.molecular_search_settings.min_ppm_error, mass_spectrum_obj.molecular_search_settings.max_ppm_error))

    SearchMolecularFormulas(mass_spectrum_obj, find_isotopologues=True).run_worker_ms_peaks([mass_spectrum_obj[0]])
    
    ms_peak = mass_spectrum_obj[0]
    
    if ms_peak:
        
        header = ['Molecular Formula',  'Calculated m/z', 'Mass Error', 'DBE', 'Ion Type']
        
        results = []
        
        for formula in ms_peak:
            
            results.append([formula.to_string, formula.mz_calc, formula.mz_error, formula.dbe, formula.ion_type])
              
        
        click.echo(tabulate(results, headers=header, floatfmt=("s", ".5f", ".5f", ".1f", "s"  )), file=out)
        click.echo('', file=out)        
        
    else:        
        
        click.echo("Could not find a possible molecular formula match for the m/z %.5f" % mz[0], file=out)
        click.echo('', file=out)
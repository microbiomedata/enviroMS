from dataclasses import asdict
from pathlib import Path

import click
import toml
from corems.encapsulation.output.parameter_to_json import (
    dump_all_settings_toml,
    dump_ms_settings_toml,
)
from corems.molecular_id.search.molecularFormulaSearch import SearchMolecularFormulas

from enviroMS.diWorkflow import (
    DiWorkflowParameters,
    generate_database,
    run_di_mpi,
    run_direct_infusion_workflow,
    run_wdl_direct_infusion_workflow,
)

from enviroMS.LC_FTICR_workflow import (
    LC_FTICR_WorkflowParameters,
    run_LC_FTICR_workflow,
    run_LC_FTICR_workflow_wdl,
)
from enviroMS.singleMzSearch import run_molecular_formula_search


@click.group()
def cli():
    pass


@cli.command(name="run_search_formula")
@click.argument(
    "mz",
    required=True,
    type=float,
)
@click.argument("corems_parameters_filepath", required=True, type=click.Path())
@click.argument("out", required=False, type=click.File("w"), default="-")
@click.option(
    "-e", "--error", "ppm_error", default=1.0, help="the marging of mass error (ppm)"
)
@click.option(
    "-r",
    "--radical",
    "isRadical",
    default=True,
    type=bool,
    help="include radical ion type",
)
@click.option(
    "-p",
    "--protonated",
    "isProtonated",
    default=True,
    type=bool,
    help="include (de)-protonated ion type",
)
@click.option(
    "-a",
    "--adduct",
    "isAdduct",
    default=False,
    type=bool,
    help="include adduct ion type",
)

def run_search_formula(
    config,
    mz,
    ppm_error,
    isRadical,
    isProtonated,
    isAdduct,
    out,
    corems_parameters_filepath,
):  # settings_filepath
    """Search for molecular formula candidates to a given m/z value \n
    corems_parameters_filepath =' CoreMS Parameters File (TOML)'
    MZ = m/z value FLOAT\n
    out = filename to store results TEXT\n
    """

    # if config.verbose:
    click.echo("", file=out)
    # dump_search_settings_yaml()

    click.echo("Searching formulas for %.5f" % mz, file=out)

    click.echo("", file=out)

    click.echo(
        "Loading Searching Settings from %s" % corems_parameters_filepath, file=out
    )

    click.echo("", file=out)

    run_molecular_formula_search(mz, out, corems_parameters_filepath)


@cli.command(name="create_database")
@click.argument("corems_parameters_file", required=True, type=str)
@click.option("--jobs", "-j", default=4, help="'cpu's'")
def create_database(corems_parameters_file, jobs):
    """Create molecular formula database.
    corems_parameters_file: Path for CoreMS TOML Parameters file\n
    jobs: Number of processes to run\n
    """
    generate_database(corems_parameters_file, jobs)


@cli.command(name="run_di_wdl")
@click.argument("file_paths", required=True, type=str)
@click.argument("output_directory", required=True, type=str)
@click.argument("output_type", required=True, type=str)
@click.argument("corems_toml_path", required=True, type=str)
@click.argument("nmdc_metadata_path", required=True, type=str)
@click.argument("polarity", required=True, type=str)
@click.argument("raw_file_start_scan", required=True, type=int)
@click.argument("raw_file_final_scan", required=True, type=int)
@click.argument("is_centroid", required=True, type=bool)
@click.argument("calibration_ref_file_path", required=False, type=str)
@click.option("--calibrate", "-c", default=True, help="Calibrate the raw files")
@click.option("--plot_mz_error", "-e", default=True, help="Plot m/z error")
@click.option("--plot_ms_assigned_unassigned", "-a", default=True, help="Plot MS assigned and unassigned")
@click.option("--plot_c_dbe", "-cb", default=True, help="Plot C vs DBE")
@click.option("--plot_van_krevelen", "-vk", default=True, help="Plot Van Krevelen diagram")
@click.option("--plot_ms_classes", "-mc", default=True, help="Plot MS classes")
@click.option("--plot_mz_error_classes", "-ec", default=True, help="Plot m/z error classes")
@click.option("--jobs", "-j", default=4, help="'cpu's'")
def run_di_wdl(*args, **kwargs):
    """Run the Direct Infusion Workflow using wdl"""

    run_wdl_direct_infusion_workflow(*args, **kwargs)


@cli.command(name="run_di")
@click.argument("di_workflow_paramaters_file", required=True, type=str)
@click.option("--jobs", "-j", default=4, help="'cpu's'")
@click.option("--replicas", "-r", default=1, help="data replicas")
@click.option("--tasks", "-t", default=4, help="mpi tasks")
@click.option("--mpi", "-m", is_flag=True, help="run mpi version")
def run_di(di_workflow_paramaters_file, jobs, replicas, tasks, mpi):
    """Run the Direct Infusion Workflow\n
    workflow_paramaters_file = toml file with workflow parameters\n
    output_types = csv, excel, pandas, json set on the parameter file\n
    corems_toml_path = toml file with corems parameters\n
    --jobs = number of processes to run in parallel\n
    --mpi = run on hpc, if omitted will run python's multiprocessing and will duplicate runs on nodes\n
    """
    if mpi:
        run_di_mpi(di_workflow_paramaters_file, tasks, replicas)

    else:
        run_direct_infusion_workflow(di_workflow_paramaters_file, jobs, replicas)



@cli.command(name="run_lc_fticr")
@click.argument("lc_fticr_workflow_paramaters_file", required=True, type=str)
def run_lc_fticr(lc_fticr_workflow_paramaters_file):
    """Run the LC FTICR MS workflow

    Parameters
    ----------
    full_input_file_path : str
        The path to the toml file with the workflow parameters
    start_time : int
        The paths to the input files, separated by commas as one string
    end_time : int
        The directory where the output files will be stored
    time_block : int
        The path corems parameters toml file
    refmasslist_neg : str
        The path to the sqlite database for spectra searching
    output_directory : str
        The path to the scan translator file
    output_file_name : str
        The number of cores to use for processing
    output_file_type : str
        The number of cores to use for processing
    lc_fticr_toml_path : str
        The number of cores to use for processing
    corems_toml_path : str
        The number of cores to use for processing
    do_plot_van_krevelen_all_ids : bool
        The number of cores to use for processing
    do_plot_van_krevelen_individual : bool
        The number of cores to use for processing
    do_plot_properties : bool
        The number of cores to use for processing

    """

    run_LC_FTICR_workflow(lc_fticr_workflow_paramaters_file)


@cli.command(name="run_lc_fticr_wdl")
@click.argument("full_input_file_path", required=True, type=str)
@click.argument("start_time", required=True, type=float)
@click.argument("end_time", required=True, type=float)
@click.argument("time_block", required=True, type=float)
@click.argument("refmasslist_neg", required=True, type=str)
@click.argument("output_directory", required=True, type=str)
@click.argument("output_file_name", required=True, type=str)
@click.argument("output_file_type", required=True, type=str)
@click.argument("lc_fticr_toml_path", required=True, type=str)
@click.argument("corems_toml_path", required=True, type=str)
@click.option("--do_plot_van_krevelen_all_ids", "-a", default=True, help="Creates Van Krevelen plots for all ids.")
@click.option("--do_plot_van_krevelen_individual", "-i", default=True, help="Creates Van Krevelen plots for all ids individually.")
@click.option("--do_plot_properties", "-p", default=True, help="Creates plots of properties for run.")
def run_lc_fticr_wdl(
    full_input_file_path,
    start_time,
    end_time,
    time_block,
    refmasslist_neg,
    output_directory,
    output_file_name,
    output_file_type,
    lc_fticr_toml_path,
    corems_toml_path,
    do_plot_van_krevelen_all_ids,
    do_plot_van_krevelen_individual,
    do_plot_properties,
):
    """
    Run the LC FTICR MS workflow using WDL.

    Parameters
    ----------
    full_input_file_path : str
        The path to the input file containing LC-FTICR data
    start_time : float
        The start time for the LC-FTICR analysis
    end_time : float
        The end time for the LC-FTICR analysis
    time_block : float
        The time block for processing the LC-FTICR data
    refmasslist_neg : str
        The path to the reference mass list for negative ion mode
    output_directory : str
        The directory where the output files will be stored
    output_file_name : str
        The name of the output file to be generated
    output_file_type : str
        The type of the output file (e.g., csv, json)
    lc_fticr_toml_path : str
        The path to the LC-FTICR workflow parameters file in TOML format
    corems_toml_path : str
        The path to the CoreMS parameters file in TOML format
    do_plot_van_krevelen_all_ids : bool
        Whether to create Van Krevelen plots for all IDs
    do_plot_van_krevelen_individual : bool
        Whether to create individual Van Krevelen plots for each ID
    do_plot_properties : bool
        Whether to create plots of properties for the run
    """
    click.echo("Running lc-fticr workflow")
    run_LC_FTICR_workflow_wdl(
        full_input_file_path = full_input_file_path,
        start_time = start_time,
        end_time = end_time,
        time_block = time_block,
        refmasslist_neg = refmasslist_neg,
        output_directory = output_directory,
        output_file_name = output_file_name,
        output_file_type = output_file_type,
        lc_fticr_toml_path = lc_fticr_toml_path,
        corems_toml_path = corems_toml_path,
        do_plot_van_krevelen_all_ids = do_plot_van_krevelen_all_ids,
        do_plot_van_krevelen_individual = do_plot_van_krevelen_individual,
        do_plot_properties = do_plot_properties,
    )


### toml template commands ###
@cli.command(name="dump_corems_template")
@click.argument("toml_file_name", required=True, type=click.Path())
def dump_corems_template(toml_file_name):
    """Dumps a CoreMS toml file template
    to be used as the workflow parameters input
    """
    path_obj = Path(toml_file_name).with_suffix(".toml")
    dump_all_settings_toml(file_path=path_obj)


@cli.command()
@click.argument("toml_file_name", required=True, type=click.Path())
def dump_corems_enviroms_template(toml_file_name):
    """Dumps a CoreMS toml file template
    to be used as the workflow parameters input
    """
    path_obj = Path(toml_file_name).with_suffix(".toml")
    dump_ms_settings_toml(file_path=path_obj)


@cli.command()
@click.argument("toml_file_name", required=True, type=click.Path())
def dump_di_template(toml_file_name):
    """Dumps a toml file template
    to be used as the workflow parameters input
    """
    ref_lib_path = Path(toml_file_name).with_suffix(".toml")
    with open(ref_lib_path, "w") as workflow_param:
        workflow = DiWorkflowParameters()

        toml.dump(asdict(workflow), workflow_param)

@cli.command()
@click.argument("toml_file_name", required=True, type=click.Path())
def dump_lc_fticr_template(toml_file_name):
    """Dumps a toml file template
    to be used as lc fticr workflow parameters input
    """
    ref_lib_path = Path(toml_file_name).with_suffix(".toml")
    with open(ref_lib_path, "w") as workflow_param:
        workflow = LC_FTICR_WorkflowParameters()

        toml.dump(asdict(workflow), workflow_param)
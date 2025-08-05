# Import packages
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as patches
sns.set_context('talk')
import os
import numpy as np
from tqdm import tqdm
from dataclasses import dataclass
import toml

# Import CoreMS functions
from corems.encapsulation.factory.parameters import MSParameters, LCMSParameters, MassSpectrumSetting, MassSpecPeakSetting
from corems.mass_spectra.input.rawFileReader import ImportMassSpectraThermoMSFileReader
from corems.molecular_id.search.molecularFormulaSearch import SearchMolecularFormulas
from corems.mass_spectrum.calc.Calibration import MzDomainCalibration
from corems.encapsulation.factory.parameters import hush_output
from corems.encapsulation.input.parameter_from_json import load_and_set_toml_parameters_class, load_and_set_toml_parameters_ms

################################### LC-FTICR OBJECT AND OBJECT'S METHODS ###################################
@dataclass
class LC_FTICR_WorkflowParameters:
    # Time Block Parameters:
    start_time: int # minutes
    end_time: int # minutes
    time_block: int #seconds
    # removed original values (check if I should do that)
    # Reference mass list:
    refmasslist_neg: str = "data/referencec/Hawkes_neg.ref"
    # input output paths
    full_input_file_path: str = "data/raw_data/..."
    input_file_directory: str = "data/raw_data/..."
    input_file_name: str = "..."
    output_directory: str = "data/..."
    output_file_name: str = "..."
    output_file_type: str = ".csv"
    # corems and MF search settings
    lc_fticr_toml_path:str = "configuration/lc_fticr/lc_fticr_corems_enviroms.toml"
    ms_toml_path: str = "configuration/lc_fticr/lc_fticr_corems_massspectrum.toml"
    mspeak_toml_path: str = "configuration/lc_fticr/lc_fticr_corems_mspeak.toml"
    mfsearch_toml_path: str = "configuration/lc_fticr/lc_fticr_corems_mfsearch.toml"
    # plot settings
    plot_van_krevelen_all_ids: bool = True
    plot_van_krevelen_individual: bool = True
    plot_properties: bool = True


    def to_toml(self):
        return toml.dumps(asdict(self))


    ### function that init parser and get data
    def init_parser_extract_data(self) -> pd.DataFrame:
        # Define datafile location
        file_in = self.full_input_file_path

        # Start with all scans
        LCMSParameters.lc_ms.scans = (-1, -1) # this needs to be read in
        # the (-1, -1) tells software to choose all scans that exist

        # Init parser object
        print(file_in)
        parser = ImportMassSpectraThermoMSFileReader(file_in)

        # Get the TIC data, scan ids, etc
        # TIC = Total Ion Chromatogram
        tic_data = parser.get_tic(ms_type=None, peak_detection=False, smooth=False, plot=False, trace_type='TIC')[0]
        tic_df = pd.DataFrame(index=tic_data.scans, columns=['scans', 'tic', 'time'])
        tic_df['scans'] = tic_data.scans
        tic_df['tic'] = tic_data.tic
        tic_df['time'] = tic_data.time

        return(tic_df)


    ### process timeblocks
    # Process the time block mass spectrum
    def proc_time_block_inner(self, msreader, datafile, block):
        # scans = list(subset_df['scan'])

        # load_and_set_toml_parameters_ms(MSParameters, self.corems_toml_path)
        with open(self.ms_toml_path, "r") as infile:
            MSParameters.mass_spectrum = MassSpectrumSetting(**toml.load(infile))
        with open(self.mspeak_toml_path, "r") as infile:
            MSParameters.ms_peak = MassSpecPeakSetting(**toml.load(infile))
        msobj = msreader.get_average_mass_spectrum(spectrum_mode = 'profile',auto_process=True)

        #msobj.clear_molecular_formulas()
        MzDomainCalibration(msobj, self.refmasslist_neg).run()

        #set_mf_settings(msobj)
        load_and_set_toml_parameters_class("MolecularFormulaSearch", msobj.molecular_search_settings, parameters_path=self.mfsearch_toml_path)

        SearchMolecularFormulas(msobj).run_worker_mass_spectrum()


        msdf = msobj.to_dataframe()
        msdf['datafile'] = datafile
        msdf['block'] = block
        msdf['tic'] = msobj.tic

        statdict = {datafile:{
            'filename':datafile,
            'block':block,
            'peaks':len(msdf),
            'calibpts':msobj.calibration_points,
            'calibrms':msobj.calibration_RMS,
            'calibrawmedian':msobj.calibration_raw_error_median,
            'calibrawstd':msobj.calibration_raw_error_stdev,
            'tic':msobj.tic,
            'baseline_noise':msobj.baseline_noise,
            'baseline_noise_std':msobj.baseline_noise_std,
            'rms_mz_error_ppm': (msdf['m/z Error (ppm)'] ** 2).mean() ** 0.5
            }}

        return(msdf, statdict)

    def process_with_time_block(self, tic_df):
        # Strip out the time where there's no useful data
        file_in = self.full_input_file_path
        tic_df = tic_df[(tic_df['time'] > self.start_time) & (tic_df['time'] < self.end_time)]

        # Block the scans into 30-second blocks, for signal averaging.
        tic_df['time_block'] = ((tic_df['time'] * 60) // self.time_block) + 1

        # Get a list of the groups
        groupblocks = list(set(tic_df['time_block']))

        # Now let's process each time block
        all_msdfs_in_file = []
        all_statdics = []
        for block in tqdm(groupblocks,desc='blocks',leave=False):
            subset_df = tic_df[tic_df['time_block'] == block].copy()
            scans_to_proc = list(subset_df['scans'])
            scans_to_proc = [int(x) for x in scans_to_proc]
            scan_tuple = (min(scans_to_proc), max(scans_to_proc))

            # Start with all scans
            LCMSParameters.lc_ms.scans = (scan_tuple)
            # Init parser object
            parser = ImportMassSpectraThermoMSFileReader(file_in)

            msdf, statdict = self.proc_time_block_inner(parser, file_in, block)  ### i'm not sure about this self.function()
            all_msdfs_in_file.append(msdf)
            all_statdics.append(statdict)

        all_msdfs = pd.concat(all_msdfs_in_file)
        all_msdfs.reset_index(inplace=True, drop=True)
        all_msdfs.to_csv(self.output_directory + self.output_file_name + self.output_file_type)
        return(all_msdfs, all_statdics)


    def create_summary(self, all_statdics):
        # Flatten the list of dictionaries
        flat_list = [inner_dict for outer_dict in all_statdics for inner_dict in outer_dict.values()]
        # Create a DataFrame
        summary_df = pd.DataFrame(flat_list)
        summary_df.to_csv(self.output_directory + self.output_file_name +"-statdicts.csv")
        return(summary_df)


################################### LC-FTICR PLOTS ###################################


## for creating plots
def filter_out_common_background(df):
    formula_block_counts = df.pivot_table(index='Molecular Formula', columns='block', aggfunc='size', fill_value=0)

    # Filter to get 'Molecular Formula' entries that appear in all blocks
    common_formulas = formula_block_counts[formula_block_counts.gt(0).sum(axis=1) == len(df['block'].unique())].index

    # Step 2: Further filter based on similar 'Peak Height' values (using a threshold)
    # Create a function to check if 'Peak Height' values are within a tolerance
    def peak_height_similar(df, tolerance=0.99):  # 10% tolerance
        peak_heights = df['Peak Height']
        return peak_heights.max() - peak_heights.min() <= tolerance * peak_heights.mean()

    # Group the dataframe by 'Molecular Formula' and apply the peak height similarity check
    similar_peak_height_formulas = df.groupby('Molecular Formula').filter(lambda x: peak_height_similar(x))['Molecular Formula'].unique()

    # Combine both conditions
    formulas_to_remove = set(common_formulas).intersection(similar_peak_height_formulas)

    # Step 3: Remove these entries from the dataframe
    filtered_df = df[~df['Molecular Formula'].isin(formulas_to_remove)]
    return filtered_df

### create plots
def plot_van_krevelen_all_ids(all_msdfs_path, output_dir):
    if isinstance(all_msdfs_path,str):
        all_msdfs_df = pd.read_csv(all_msdfs_path)
    else:
        all_msdfs_df = all_msdfs_path
    all_msdfs_annotated = all_msdfs_df[all_msdfs_df['Heteroatom Class']!='unassigned'].copy()

    filtered_df = filter_out_common_background(all_msdfs_annotated)
    all_msdfs_annotated = filtered_df


    all_msdfs_annotated.sort_values(by='m/z',ascending=True,inplace=True)

    fig,ax  = plt.subplots(figsize=(10,10))
    ax.scatter(all_msdfs_annotated['O/C'],
            all_msdfs_annotated['H/C'],
            s=all_msdfs_annotated['S/N']/10,
            c=all_msdfs_annotated['O'])

    ax.set_xlabel('O/C')
    ax.set_ylabel('H/C')
    ax.set_xlim(0,1.25)
    ax.set_ylim(0.25,2.25)
    fig.savefig(output_dir+'van_kreelen_AllIDs.png',dpi=300,bbox_inches='tight')
    plt.show()

def plot_van_krevelen_individual(all_msdfs_path, output_dir):
    if isinstance(all_msdfs_path,str):
        all_msdfs_df = pd.read_csv(all_msdfs_path)
    else:
        all_msdfs_df = all_msdfs_path
        all_msdfs_annotated = all_msdfs_df[all_msdfs_df['Heteroatom Class']!='unassigned'].copy()
    # Get unique blocks and sort them
    blocks = sorted(all_msdfs_annotated['block'].unique())
    number_of_blocks = len(blocks)

    # Determine the grid size for the subplots
    cols = int(np.ceil(np.sqrt(number_of_blocks)))
    rows = int(np.ceil(number_of_blocks / cols))

    # Create the figure and axes
    fig, axes = plt.subplots(rows, cols, figsize=(cols*7, rows*5), constrained_layout=True,
                            sharex=True,sharey=True)
    axes = axes.flatten()

    # Plot data for each block
    for i, block in enumerate(blocks):
        ax = axes[i]
        block_data = all_msdfs_annotated[all_msdfs_annotated['block'] == block]
        ax.scatter(block_data['O/C'], block_data['H/C'],
                s=block_data['S/N']/10, c=block_data['O'])
        ax.set_title(f'Block {block}')
        ax.set_xlabel('O/C')
        ax.set_ylabel('H/C')
        #ax.set_aspect('equal', 'box')  # Set aspect ratio to be square

    # Hide any unused subplots (in case the grid has more axes than blocks)
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    # Show the plot
    plt.show()
    fig.savefig(output_dir+'TimeBlockIDs.png',dpi=300,bbox_inches='tight')

def plot_properties(summary_df_path,output_dir):
    if isinstance(summary_df_path,str):
        summary_df = pd.read_csv(summary_df_path)
    else:
        summary_df = summary_df_path

    # List of properties to plot
    properties = ['peaks', 'calibpts', 'calibrms', 'tic','rms_mz_error_ppm']

    # Number of properties
    num_properties = len(properties)

    # Create subplots for trends and distributions side by side
    fig, axes = plt.subplots(num_properties, 2, figsize=(15, 5 * num_properties))

    # Plot each property
    for i, prop in enumerate(properties):
        # Trend plot
        sns.lineplot(x='block', y=prop, data=summary_df, marker='o', ax=axes[i, 0])
        axes[i, 0].set_title(f'Trend of {prop} by Block')
        axes[i, 0].set_xlabel('Block')
        axes[i, 0].set_ylabel(prop)

        # Distribution plot
        sns.histplot(summary_df[prop], kde=True, ax=axes[i, 1], bins=10, color='skyblue')
        axes[i, 1].set_title(f'Distribution of {prop}')
        axes[i, 1].set_xlabel(prop)
        axes[i, 1].set_ylabel('Frequency')

    # Adjust layout
    plt.tight_layout()
    fig.savefig(output_dir+'property_plots.png',dpi=300,bbox_inches='tight')
    plt.show()

################################### RUN LC-FTICR WORKFLOW ###################################

def run_LC_FTICR_workflow(lc_fticr_workflow_paramaters_toml_file):
    # read in LC_WorkflowParameters from toml file
    with open(lc_fticr_workflow_paramaters_toml_file, "r") as infile:
        lc_object = LC_FTICR_WorkflowParameters(**toml.load(infile))
    # call functions
    tic_df = lc_object.init_parser_extract_data()
    all_msdfs_df, all_statdics_df = lc_object.process_with_time_block(tic_df)
    summary_df = lc_object.create_summary(all_statdics=all_statdics_df)
    if lc_object.plot_van_krevelen_all_ids:
        plot_van_krevelen_all_ids(all_msdfs_df, lc_object.output_directory)
    if lc_object.plot_van_krevelen_individual:
        plot_van_krevelen_individual(all_msdfs_df, lc_object.output_directory)
    if lc_object.plot_properties:
        plot_properties(summary_df, lc_object.output_directory)
    return()

def run_LC_FTICR_workflow_wdl(
    start_time,
    end_time,
    time_block,
    refmasslist_neg,
    full_input_file_path,
    input_file_directory,
    input_file_name,
    output_directory,
    output_file_name,
    output_file_type,
    lc_fticr_toml_path,
    ms_toml_path,
    mspeak_toml_path,
    mfsearch_toml_path,
    plot_van_krevelen_all_ids,
    plot_van_krevelen_individual,
    plot_properties,
):
    # read in LC_WorkflowParameters from wdl inputs
    lc_object = LC_FTICR_WorkflowParameters(start_time = start_time,
                                            end_time = end_time,
                                            time_block = time_block,
                                            refmasslist_neg = refmasslist_neg,
                                            full_input_file_path = full_input_file_path,
                                            input_file_directory = input_file_directory,
                                            input_file_name = input_file_name,
                                            output_directory = output_directory,
                                            output_file_name = output_file_name,
                                            output_file_type = output_file_type,
                                            lc_fticr_toml_path = lc_fticr_toml_path,
                                            ms_toml_path = ms_toml_path,
                                            mspeak_toml_path = mspeak_toml_path,
                                            mfsearch_toml_path = mfsearch_toml_path,
                                            plot_van_krevelen_all_ids = plot_van_krevelen_all_ids,
                                            plot_van_krevelen_individual = plot_van_krevelen_individual,
                                            plot_properties = plot_properties)
    # call functions
    tic_df = lc_object.init_parser_extract_data()
    all_msdfs_df, all_statdics_df = lc_object.process_with_time_block(tic_df)
    summary_df = lc_object.create_summary(all_statdics=all_statdics_df)
    if lc_object.plot_van_krevelen_all_ids:
        plot_van_krevelen_all_ids(all_msdfs_df, lc_object.output_directory)
    if lc_object.plot_van_krevelen_individual:
        plot_van_krevelen_individual(all_msdfs_df, lc_object.output_directory)
    if lc_object.plot_properties:
        plot_properties(summary_df, lc_object.output_directory)
    return()
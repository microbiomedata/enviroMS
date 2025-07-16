version 1.0

workflow lc_ft_icr_ms {
    call run_LCFTICR

    output {
        String out = run_LCFTICR.out
        Array[File] output_files = run_LCFTICR.output_files
        Array[File] plots = run_LCFTICR.plots
    }
}

task run_LCFTICR {
    input {
        Float start_time
        Float end_time
        Float time_block
        String refmasslist_neg
        String input_file_path
        String input_file_name
        String output_directory
        String output_file_name
        String output_file_type
        String ms_toml_path
        String mspeak_toml_path
        String mfsearch_toml_path
        Boolean plot_van_krevelen_all_ids
        Boolean plot_van_krevelen_individual
        Boolean plot_properties
    }

    command {
        enviroMS run_lc_fticr_wdl \
            ${start_time} \ 
            ${end_time} \ 
            ${time_block} \ 
            ${refmasslist_neg} \ 
            ${input_file_path} \ 
            ${input_file_name} \ 
            ${output_directory} \ 
            ${output_file_name} \ 
            ${output_file_type} \ 
            ${ms_toml_path} \ 
            ${mspeak_toml_path} \ 
            ${mfsearch_toml_path} \ 
            -a ${plot_van_krevelen_all_ids} \ 
            -i ${plot_van_krevelen_individual} \ 
            -p ${plot_properties}
    }

    output {
        String out = read_string(stdout())
        Array[File] output_files = glob('${output_directory}/*.csv')
        Array[File] plots = glob('${output_directory}/*.png')
    }

    runtime {
        docker: "microbiomedata/enviroms:latest"
    }
}
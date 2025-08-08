version 1.0

workflow lc_ft_icr_ms {
    input {
        String? docker_image  # Optional input for Docker image
    }
    call run_LCFTICR {
        input:
            docker_image = docker_image
    }

    output {
        String out = run_LCFTICR.out
        Array[File] output_files = run_LCFTICR.output_files
        Array[File] plots = run_LCFTICR.plots
    }
}

task run_LCFTICR {
    input {
        Array[File] full_input_file_path
        Float start_time
        Float end_time
        Float time_block
        File refmasslist_neg
        String output_directory
        String output_file_name
        String output_file_type
        File lc_fticr_toml_path
        File corems_toml_path
        Boolean do_plot_van_krevelen_all_ids
        Boolean do_plot_van_krevelen_individual
        Boolean do_plot_properties
        String? docker_image
    }

    command {
        mkdir -p data

        enviroMS run_lc_fticr_wdl \
            ${sep=',' full_input_file_path} \
            ${start_time} \
            ${end_time} \
            ${time_block} \
            ${refmasslist_neg} \
            ${output_directory} \
            ${output_file_name} \
            ${output_file_type} \
            ${lc_fticr_toml_path} \
            ${corems_toml_path} \
            -a ${do_plot_van_krevelen_all_ids} \
            -i ${do_plot_van_krevelen_individual } \
            -p ${do_plot_properties}


    }

    output {
        String out = read_string(stdout())
        Array[File] output_files = glob('${output_directory}/*.csv')
        Array[File] plots = glob('${output_directory}/*.png')
    }

    runtime {
        docker: "~{if defined(docker_image) then docker_image else 'microbiomedata/enviroms:latest'}"
    }
}
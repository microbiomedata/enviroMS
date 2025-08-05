app_name = enviroms
parameters_path = data/enviroms.toml
# change the path to your data path /Users/eber373/Desenvolvimento/enviroms
data_dir = /Users/eber373/Development/enviroms/data
configuration_dir = /Users/eber373/Development/enviroms/configuration
version := $(shell cat .bumpversion.cfg | grep current_version | cut -d= -f2 | tr -d ' ')
stage := $(shell cat .bumpversion.cfg | grep optional_value | cut -d= -f2 | tr -d ' ') 

cpu: 
	pyprof2calltree -k -i $(file)

mem: 

	mprof run --multiprocess $(script)
	mprof plot

major:
	
	@bumpversion major --allow-dirty

minor:
	
	@bumpversion minor --allow-dirty

patch:
	
	@bumpversion patch --allow-dirty

install:
	
	venv/bin/pip3 install --editable .
	
run:
	
	venv/bin/pip3/enviroMS run_di_workflow $(parameters_path)

pypi:
	@python3 setup.py sdist
	@twine upload dist/*

docker-push:
	
	@echo corilo/enviroms:$(version)
	@docker build --no-cache -t corilo/enviroms:$(version) .
	@docker push corilo/enviroms:$(version)
	
	@docker image tag corilo/enviroms:$(version) corilo/enviroms:latest
	@docker push corilo/enviroms:latest


docker-push-im:
	@echo alexandriai168/enviroms:$(version)
	@docker build --no-cache -t alexandriai168/enviroms:$(version) .
	@docker push alexandriai168/enviroms:$(version)
	
	@docker image tag alexandriai168/enviroms:$(version) alexandriai168/enviroms:latest
	@docker push alexandriai168/enviroms:latest


docker-nmdc:
	@echo microbiomedata/enviroms:$(version)
	@docker buildx create --use
	@docker buildx build --platform linux/amd64,linux/arm64 --no-cache -t microbiomedata/enviroms:$(version) --push .
	@docker buildx imagetools create microbiomedata/enviroms:$(version) -t microbiomedata/enviroms:latest
	@docker buildx imagetools inspect microbiomedata/enviroms:latest
	
	
docker-build:

	docker build -t enviroms:local .


docker-build-local:

	docker build -t local-enviroms:latest .


docker-run-di:

	@echo $(data_dir)
	@echo $(configuration_dir)
	docker run -v $(data_dir):/enviroms/data -v $(configuration_dir):/enviroms/configuration microbiomedata/enviroms:latest run-di /enviroms/configuration/enviroms.toml

docker-run-lc:

	@echo $(data_dir)
	@echo $(configuration_dir)
	docker run -v $(data_dir):/enviroms/data -v $(configuration_dir):/enviroms/configuration microbiomedata/enviroms:latest run_lc_fticr /enviroms/configuration/lc_fticr/lc_fticr_enviroms.toml

cascade-run:

	srun -A mscms -t 240 -N 1 -n time enviroMS run-di -r 2 --mpi  /dtemp/mscms/enviroms/data/configuration/enviroms.toml

wdl-run-di :
 	 
	miniwdl run wdl/di_fticr_ms.wdl -i wdl/di_fticr_wdl_input.json --verbose --no-cache --copy-input-files

wdl-run-lc :
 	 
	miniwdl run wdl/lc_fticr_ms.wdl -i wdl/lc_fticr_wdl_input.json --verbose --no-cache --copy-input-files

get-lcms-fticr-test-data:

	@echo "Downloading test files for LC-MS FT-ICR workflow"

	# download configs
	@echo "Downloading configuration files"
	@mkdir -p configuration/lc_fticr
	@if [ ! -f ./configuration/lc_fticr/lc_fticr_corems_massspectrum.toml || ! -f ./configuration/lc_fticr/lc_fticr_corems_mfsearch.toml || ! -f ./configuration/lc_fticr/lc_fticr_corems_mspeak.toml || ! -f ./configuration/lc_fticr/lc_fticr_enviroms.toml ]; \
	then echo "Some or all config files do not exist, downloading"; \
	curl -L -o configuration/lc_fticr/lcms_fticr_test_configs.zip https://nmdcdemo.emsl.pnl.gov/nom/test_data/enviroms_lcms_nom_test/lcms_fticr_test_configs.zip; \
	unzip -j configuration/lc_fticr/lcms_fticr_test_configs.zip -d configuration/lc_fticr/; \
	rm configuration/lc_fticr/lcms_fticr_test_configs.zip; \
	else echo "Configuration files downloaded and unzipped"

	# download data
	@echo "Checking if test data file exists"
	@if [ ! -f ./data/raw_data/lc_fticr/20231109_60885_SRFA_50ppm_5uL_LC_PolarAdv-001262_231109183242.raw ]; \
	then echo "Test data file does not exist, downloading"; \
	curl -L -O --output-dir data/raw_data/lc_fticr/ https://nmdcdemo.emsl.pnl.gov/nom/test_data/enviroms_lcms_nom_test/20231109_60885_SRFA_50ppm_5uL_LC_PolarAdv-001262_231109183242.raw; \
	else echo "Test data file exists"; fi

	# download ref
	@echo "Checking if reference file exists"
	@if [ ! -f ./data/reference/Hawkes_neg.ref ]; then echo "Reference file does not exist, downloading"; \
	curl -L -O --output-dir data/reference/ https://nmdcdemo.emsl.pnl.gov/nom/test_data/enviroms_lcms_nom_test/Hawkes_neg.ref; \
	else echo "Reference file exists"; fi
	@echo "LC-MS FT-ICR test files complete"

wdl-run-lc-local:

	miniwdl run wdl/lc_fticr_ms.wdl -i wdl/lc_fticr_wdl_input_local_docker.json --verbose --no-cache --copy-input-files

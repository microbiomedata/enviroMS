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

	@docker image tag corilo/enviroms:$(version) microbiomedata/enviroms:$(version)
	@docker push microbiomedata/enviroms:$(version)

	@docker image tag corilo/enviroms:$(version) microbiomedata/enviroms:latest
	@docker push microbiomedata/enviroms:latest

docker-nmdc:
	@echo microbiomedata/enviroms:$(version)
	@docker buildx create --use
	@docker buildx build --platform linux/amd64,linux/arm64 --no-cache -t microbiomedata/enviroms:$(version) --push .
	@docker buildx imagetools create microbiomedata/enviroms:$(version) -t microbiomedata/enviroms:latest
	@docker buildx imagetools inspect microbiomedata/enviroms:latest
	
	
docker-build:

	docker build -t enviroms:local .

docker-run:

	docker run -v $(data_dir):/enviroms/data -v $(configuration_dir):/enviroms/configuration microbiomedata/enviroms:latest run-di /enviroms/configuration/enviroms.toml

cascade-run:

	srun -A mscms -t 240 -N 1 -n time enviroMS run-di -r 2 --mpi  /dtemp/mscms/enviroms/data/configuration/enviroms.toml

wdl-run-di :
 	 
	miniwdl run wdl/di_fticr_ms.wdl -i wdl/di_fticr_wdl_input.json --verbose --no-cache --copy-input-files

wdl-run-lc :
 	 
	miniwdl run wdl/lc_fticr_ms.wdl -i wdl/lc_fticr_wdl_input.json --verbose --no-cache --copy-input-files

get-lcms-fticr-test-data:
	@echo "Downloading test files for LC-MS FTICR workflow"

# download configs 
	@echo "Downloading configuration files"
	@mkdir -p configuration/lc_fticr
	@curl -L -o configuration/lc_fticr/lcms_fticr_test_configs.zip https://nmdcdemo.emsl.pnl.gov/nom/test_data/enviroms_lcms_nom_test/lcms_fticr_test_configs.zip
	@unzip configuration/lc_fticr/lcms_fticr_test_configs.zip -d configuration/lc_fticr/
	@rm configuration/lc_fticr/lcms_fticr_test_configs.zip
	@echo "Configuration files downloaded and unzipped"

# download data
	@echo "Downloading test data"
	@mkdir -p data/raw_data/lc_fticr
	@curl -L -O --output-dir data/raw_data/lc_fticr/ https://nmdcdemo.emsl.pnl.gov/nom/test_data/enviroms_lcms_nom_test/20231109_60885_SRFA_50ppm_5uL_LC_PolarAdv-001262_231109183242.raw
	@echo "Test data downloaded"

# download ref
	@echo "Checking if reference file exists"
ifeq ($(data/reference/Hawkes_neg.ref), "")
	@echo "Reference file not present, downloading"
    @curl -L -O --output-dir data/raw_data/lc_fticr/ https://nmdcdemo.emsl.pnl.gov/nom/test_data/enviroms_lcms_nom_test/20231109_60885_SRFA_50ppm_5uL_LC_PolarAdv-001262_231109183242.raw
	@echo "Reference file downloaded"
else
	@echo "Reference file exists"
endif
	@echo "Test files complete"
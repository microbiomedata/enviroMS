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
	@docker buildx imagetools inspect microbiomedata/enviromså:latest
	
	
docker-build:

	docker build -t enviroms:local .

docker-run:

	docker run -v $(data_dir):/enviroms/data -v $(configuration_dir):/enviroms/configuration microbiomedata/enviroms:latest run-di /enviroms/configuration/enviroms.toml

cascade-run:

	srun -A mscms -t 240 -N 1 -n time enviroMS run-di -r 2 --mpi  /dtemp/mscms/enviroms/data/configuration/enviroms.toml

wdl-run :
 	 
	 miniwdl run wdl/enviroMS.wdl -i wdl/enviroms_input.json --verbose --no-cache --copy-input-files
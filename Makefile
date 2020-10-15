app_name = enviroms
parameters_path = data/EnviromsFile.json
# change the path to your data path /Users/eber373/Desenvolvimento/enviroms
data_dir = /Users/eber373/Desenvolvimento/enviroms/data/
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
	
	@echo corilo/enviroms:$(version).$(stage)
	@docker build --no-cache -t corilo/enviroms:$(version).$(stage) .
	@docker push corilo/enviroms:$(version).$(stage)
	@docker image tag corilo/enviroms:$(version).$(stage) corilo/enviroms:latest
	@docker push corilo/enviroms:latest

docker-build:

	docker build -t enviroms:local .

docker-run:

	docker run -v $(data_dir):/enviroms/data enviroms:local run-di-workflow /enviroms/data/EnviromsFile.json

cascade-run:

	srun -A mscms -t 240 -N 1 -n time enviroMS run-di-workflow -r 2 --mpi  /dtemp/mscms/enviroms/data/EnviromsFile.json
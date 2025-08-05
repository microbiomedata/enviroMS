# FROM jcarr87/corems-base-py3.10
# WORKDIR /enviroms

# COPY enviroMS/ /enviroms/enviroMS/
# COPY README.md disclaimer.txt Makefile requirements.txt setup.py /enviroms/
# RUN pip3 install -U pip
# RUN pip3 install --editable .

# Python base image
FROM python:3.11.1-bullseye

# Mono: 6.12
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF \
  && echo "deb http://download.mono-project.com/repo/debian buster/snapshots/6.12 main" > /etc/apt/sources.list.d/mono-official.list \
  && apt-get update \
  && apt-get install -y clang \
  && apt-get install -y mono-devel=6.12\* \
  && rm -rf /var/lib/apt/lists/* /tmp/*

# Pythonnet: 3.0.1 (from PyPI)
# Note: pycparser must be installed before pythonnet can be built
RUN pip install pycparser \
  && pip install pythonnet==3.0.1

# Copy EnviroMS contents
WORKDIR /enviroms
COPY enviroMS/ /enviroms/enviroMS/
COPY README.md disclaimer.txt Makefile requirements.txt setup.py /enviroms/
COPY data/raw_data/lc_fticr /enviroms/data/raw_data/lc_fticr
COPY data/reference/Hawkes_neg.ref /enviroms/data/reference/Hawkes_neg.ref
COPY configuration/lc_fticr /enviroms/configuration/lc_fticr


# Install the correct version of CoreMS from github
RUN pip install git+https://github.com/EMSL-Computing/CoreMS.git@v3.6.0

# Install the MetaMS package in editable mode
RUN pip3 install -U pip
RUN pip3 install --editable .

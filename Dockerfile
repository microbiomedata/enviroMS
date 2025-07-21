# FROM jcarr87/corems-base-py3.10
# WORKDIR /enviroms

# COPY enviroMS/ /enviroms/enviroMS/
# COPY README.md disclaimer.txt Makefile requirements.txt setup.py /enviroms/
# RUN pip3 install -U pip
# RUN pip3 install --editable .

# Python base image
FROM python:3.11.1-bullseye

# Pythonnet: 3.0.1 (from PyPI)
# Note: pycparser must be installed before pythonnet can be built
RUN pip install pycparser \
  && pip install pythonnet==3.0.1

# Copy EnviroMS contents
WORKDIR /enviroms
COPY enviroMS/ /enviroms/enviroMS/
COPY README.md disclaimer.txt Makefile requirements.txt setup.py /enviroms/

# Install the correct version of CoreMS from github
RUN pip install git+https://github.com/EMSL-Computing/CoreMS.git@v3.6.0

# Install the MetaMS package in editable mode
RUN pip3 install -U pip
RUN pip3 install --editable .

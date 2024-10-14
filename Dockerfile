FROM jcarr87/corems-base-py3.10
WORKDIR /enviroms

COPY enviroMS/ /enviroms/enviroMS/
COPY README.md disclaimer.txt Makefile requirements.txt setup.py /enviroms/
RUN pip3 install -U pip
RUN pip3 install --editable .

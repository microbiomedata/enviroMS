FROM corilo/corems:base-mono-pythonnet
WORKDIR /enviroms

COPY enviroMS/ /enviroms/enviroMS/
COPY README.md disclaimer.txt Makefile requirements.txt setup.py /enviroms/
COPY db/ /enviroms/db/
RUN pip3 install --editable .
ENTRYPOINT ["enviroMS"]

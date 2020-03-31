FROM gitlab.pnnl.gov:4567/mass-spectrometry/corems:latest

WORKDIR /home/EnviroMS

COPY cli/ /home/EnviroMS/cli
COPY requirements.txt LICENSE README.md setup.py /home/CoreMS/
RUN python3 setup.py install 
RUN pip install --editable .

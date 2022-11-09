FROM python:3.10-slim

RUN apt-get -y update

RUN apt-get -y install git

WORKDIR ./code/app/

RUN git clone https://github.com/raresradua/ASET-post-quantic-cryptography.git

WORKDIR ./ASET-post-quantic-cryptography/proj/

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "deploy.py"]
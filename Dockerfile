From ubuntu:latest

RUN apt-get update
RUN apt-get install python3 python3-pip -y

# https://stackoverflow.com/questions/75608323/how-do-i-solve-error-externally-managed-environment-every-time-i-use-pip-3
# https://veronneau.org/python-311-pip-and-breaking-system-packages.html
ENV PIP_BREAK_SYSTEM_PACKAGES 1


##################################################
# Ubuntu setup
##################################################

RUN  apt-get update \
  && apt-get install -y wget \
  && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get -y upgrade \
  && apt-get install -y --no-install-recommends \
    unzip \
    nano \
    git \ 
    g++ \
    gcc \
    htop \
    zip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

##################################################
# ODTP setup
##################################################

RUN mkdir /app
COPY . /saving-willy
RUN pip3 install --upgrade setuptools
RUN pip3 install -r /saving-willy/requirements.txt

WORKDIR /saving-willy

ENTRYPOINT bash
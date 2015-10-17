FROM buildpack-deps:jessie

MAINTAINER Cristóbal Ganter

RUN apt-get -y update && apt-get -y upgrade
RUN apt-get -y update && apt-get install -y python3 python3-pip

RUN mkdir /src
WORKDIR /src

COPY calculator_api.py requirements.txt test_calculator_api.py ./
RUN pip3 install -r requirements.txt

EXPOSE 8888

CMD ["./calculator_api.py"]

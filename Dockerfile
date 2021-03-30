FROM ubuntu:18.04

#create a Ubuntu User
RUN \
  groupadd -g 12574 ubuntu && \
  useradd -u 12574 -g 12574 -m -N -s /bin/bash ubuntu && \

  apt-get update -y && \
  apt-get -y install software-properties-common && \
  apt-get -y upgrade

RUN mkdir /opt/ilyde
COPY . /opt/ilyde
RUN chown -R ubuntu:ubuntu /opt/ilyde

USER ubuntu
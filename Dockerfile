FROM gitlab.hopenly.com:4567/ilyde/base-images/minimal-py37:1.0.rc

RUN mkdir /opt/ilyde
COPY . /opt/ilyde
RUN chown -R ubuntu:ubuntu /opt/ilyde

CMD ["tail -f /dev/null"]

USER ubuntu
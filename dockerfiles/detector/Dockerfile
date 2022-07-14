#  docker build -t detector .
# 入侵偵測
FROM ubuntu:20.04
WORKDIR /app

RUN cd /app &&\
    apt-get  update   &&\
    apt-get install -y python3-dev python3-pip &&\
    pip3 install --upgrade pip &&\
    pip3 install --upgrade tensorflow-cpu &&\
    pip3 install Flask &&\
    pip3 install pycryptodome==3.13.0 &&\
    pip3 install sqlalchemy==1.4.31 &&\
    pip3 install requests==2.27.1 &&\
    pip3 install itsdangerous==2.0.1 &&\
    pip3 install flask-cors

CMD ["/bin/bash"]
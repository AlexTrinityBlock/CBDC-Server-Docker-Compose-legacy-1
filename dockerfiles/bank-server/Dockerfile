# 銀行端虛擬機
FROM python:3.9
WORKDIR /app

RUN cd /app &&\
    pip3 install Flask &&\
    pip3 install pycryptodome==3.13.0 &&\
    pip3 install sqlalchemy==1.4.31 &&\
    pip3 install requests==2.27.1 &&\
    pip3 install itsdangerous==2.0.1 &&\
    pip3 install flask-cors

CMD ["/bin/bash"]
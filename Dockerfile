FROM python:3.6-slim
LABEL maintainer="hiennguyen83@gmail.com"
USER root
WORKDIR /app
ADD . /app
RUN apt-get update && apt-get install -y default-libmysqlclient-dev build-essential gcc
#ENV LDFLAGS "-I/usr/local/opt/openssl/include -L/usr/local/opt/openssl/lib"
RUN pip install --trusted-host pypi.python.org -r requirements.txt
EXPOSE 5000
ENV FLASK_APP app.py
CMD ["python", "app.py"]

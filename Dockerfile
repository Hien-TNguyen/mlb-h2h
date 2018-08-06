FROM python:3.6-slim
LABEL maintainer="hiennguyen83@gmail.com"
USER root
WORKDIR /app
ADD . /app 
RUN pip install --trusted-host pypi.python.org -r requirements.txt
EXPOSE 5000
ENV FLASK_APP app.py
CMD ["python", "app.py"] 



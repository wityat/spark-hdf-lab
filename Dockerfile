FROM bitnami/spark:latest

USER root

RUN apt update -y && apt upgrade -y && apt install -y python3-pip
COPY ./requirements.txt /requirements.txt
COPY ./app/app.py /opt/bitnami/spark/app.py
RUN pip install -r /requirements.txt

USER 1001

CMD ["bin/spark-class", "org.apache.spark.deploy.master.Master"]
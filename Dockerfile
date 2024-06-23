FROM bitnami/spark:latest

USER root

RUN apt update -y && apt upgrade -y && apt install -y python3-pip

RUN pip install -r requirements.txt

USER 1001

CMD ["bin/spark-class", "org.apache.spark.deploy.master.Master"]
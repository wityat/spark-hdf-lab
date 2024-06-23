docker compose up -d

docker exec -it namenode hdfs dfs -put /taxi_fare/test.csv /

docker exec -it spark-master spark-submit --master spark://spark-master:7077 app.py --data_path hdfs://namenode:9000/test.csv --datanodes 1
docker exec -it spark-master spark-submit --master spark://spark-master:7077 app.py --data_path hdfs://namenode:9000/test.csv --datanodes 1 --optimal true


docker compose up -f docker-compose-with-3-datanodes.yml -d

docker exec -it namenode hdfs dfs -put /taxi_fare/test.csv /

docker exec -it spark-master spark-submit --master spark://spark-master:7077 app.py --data_path hdfs://namenode:9000/test.csv --datanodes 3
docker exec -it spark-master spark-submit --master spark://spark-master:7077 app.py --data_path hdfs://namenode:9000/test.csv --datanodes 3 --optimal true

docker compose up -d

docker exec -it namenode hdfs dfs -mkdir -p /input
docker exec -it namenode hdfs dfs -put /taxi_fare/test.csv /input

docker exec -it master park-submit --master spark://spark-master:7077 app.py --data_path hdfs://namenode:9000/taxi_fare/test.csv --datanodes 1 --optimal false
docker exec -it master park-submit --master spark://spark-master:7077 app.py --data_path hdfs://namenode:9000/taxi_fare/test.csv --datanodes 3 --optimal false
docker exec -it master park-submit --master spark://spark-master:7077 app.py --data_path hdfs://namenode:9000/taxi_fare/test.csv --datanodes 1 --optimal true
docker exec -it master park-submit --master spark://spark-master:7077 app.py --data_path hdfs://namenode:9000/taxi_fare/test.csv --datanodes 3 --optimal true
sleep(40000)
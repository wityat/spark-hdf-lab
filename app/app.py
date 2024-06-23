import argparse
import os
import time

import seaborn as sns
import requests
from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from pyspark.sql import SparkSession
from tqdm import tqdm


def save_as_graph(total_time, total_RAM, path):
    plt.figure(figsize=(14, 6))

    # Set the style
    sns.set_style("whitegrid")

    # Histogram for total_time
    plt.subplot(1, 2, 1)
    sns.histplot(total_time, bins=30, kde=True, color='skyblue')
    plt.xlabel('Time (s)', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.title(f'Time Distribution of {path}', fontsize=14)
    plt.grid(True)

    # Histogram for total_RAM
    plt.subplot(1, 2, 2)
    sns.histplot(total_RAM, bins=30, kde=True, color='salmon')
    plt.xlabel('RAM (MB)', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.title(f'RAM Distribution of {path}', fontsize=14)
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(path+".png")
    plt.close()


def get_total_executor_memory_usage():
    spark_master_url = os.getenv("SPARK_MASTER_URL")
    total_memory_used = 0
    response = requests.get(f'{spark_master_url}/api/v1/applications')
    if response.status_code == 200:
        applications = response.json()
        for app in applications:
            app_id = app['id']
            app_detail_response = requests.get(f'{spark_master_url}/api/v1/applications/{app_id}/executors')
            if app_detail_response.status_code == 200:
                executors = app_detail_response.json()
                for executor in executors:
                    total_memory_used += executor['memoryUsed']
    else:
        print("Failed to get applications list")
    return total_memory_used


def train(train_data):
    X = train_data[['distance_traveled', 'num_of_passengers']]
    y = train_data['fare']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = make_pipeline(StandardScaler(), LinearRegression())  # Train the model
    model.fit(X_train, y_train)

    # Make predictions on the test set
    predictions = model.predict(X_test)

    # Evaluate the model
    mse = mean_squared_error(y_test, predictions)
    return mse


def main(data_path, datanodes, is_optimal):
    spark = (
        SparkSession
        .builder
        .appName('default')
        .getOrCreate()
    )

    sc = spark.sparkContext
    logger = sc._jvm.org.apache.log4j
    logger.LogManager.getLogger("org").setLevel(logger.Level.ERROR)

    time_spend = []
    RAM_used = []

    for i in tqdm(range(100)):
        start_time = time.perf_counter()

        if is_optimal:
            spark.sparkContext.parallelize(range(50)).map(train)
        else:
            train_data = spark.read.csv(data_path, header=True)
            train(train_data)

        end_time = time.perf_counter()
        time_spend.append(end_time - start_time)
        RAM_used.append(get_total_executor_memory_usage())

    save_as_graph(time_spend, RAM_used, f'./{"" if is_optimal else "not_"}optimal_spark_with_{datanodes}_datanodes')

    spark.stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str)
    parser.add_argument('--datanodes', type=int, default=1)
    parser.add_argument('--optimal', type=bool, default=False)
    args = parser.parse_args()
    main(args.data_path, args.datanodes, args.optimal)
    print('Done')

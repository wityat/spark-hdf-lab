import argparse
import time
from pyspark.ml.feature import VectorAssembler, StandardScaler
import seaborn as sns
from matplotlib import pyplot as plt
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator

from pyspark.sql import SparkSession
from tqdm import tqdm
import psutil

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
    plt.savefig(path + ".png")
    plt.close()


def get_total_executor_memory():
    total_used_memory = psutil.virtual_memory().used / (1024 * 1024)  # Convert bytes to MB
    return total_used_memory


def train(train_data):
    # Assemble features into a single vector
    feature_columns = ['distance_traveled', 'num_of_passengers']
    assembler = VectorAssembler(inputCols=feature_columns, outputCol='features')
    assembled_data = assembler.transform(train_data)

    # Standardize features
    scaler = StandardScaler(inputCol='features', outputCol='scaled_features')
    scaler_model = scaler.fit(assembled_data)
    scaled_data = scaler_model.transform(assembled_data)

    # Split the data into training and test sets
    train_data, test_data = scaled_data.randomSplit([0.8, 0.2], seed=42)

    # Train the model
    lr = LinearRegression(featuresCol='scaled_features', labelCol='fare')
    lr_model = lr.fit(train_data)

    # Make predictions on the test set
    predictions = lr_model.transform(test_data)

    # Evaluate the model
    evaluator = RegressionEvaluator(labelCol='fare', predictionCol='prediction', metricName='mse')
    mse = evaluator.evaluate(predictions)
    return mse


def main(data_path, datanodes, is_optimal):
    spark = (
        SparkSession
        .builder
        .appName('default')
        .getOrCreate()
    )

    time_spend = []
    RAM_used = []

    train_data = spark.read.csv(data_path, header=True, inferSchema=True)

    if is_optimal:
        # Repartition to ensure data is evenly distributed
        train_data = train_data.repartition(datanodes)

        # Cache the DataFrame to avoid recomputing
        train_data = train_data.cache()

    for i in tqdm(range(100)):
        start_time = time.perf_counter()

        mse = train(train_data)

        end_time = time.perf_counter()
        time_spend.append(end_time - start_time)
        RAM_used.append(get_total_executor_memory())

    save_as_graph(time_spend, RAM_used, f'./images/{"" if is_optimal else "not_"}optimal_spark_with_{datanodes}_datanodes')

    spark.stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str)
    parser.add_argument('--datanodes', type=int, default=1)
    parser.add_argument('--optimal', type=bool, default=False)
    args = parser.parse_args()
    main(args.data_path, args.datanodes, args.optimal)
    print('Done')

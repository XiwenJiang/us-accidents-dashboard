
import os
from pathlib import Path
from pyspark.sql import SparkSession

def get_spark(app_name: str = "us-accidents"):
    """
    Create a SparkSession with:
    - Fixed JAVA_HOME (JDK 17)
    - Isolated Hadoop/YARN configs
    - Stable S3A configuration
    """

    # ---------- 1. Java environment (必须最先) ----------
    java_home = "/Library/Java/JavaVirtualMachines/openjdk-17.jdk/Contents/Home"
    os.environ["JAVA_HOME"] = java_home
    os.environ["PATH"] = f"{java_home}/bin:" + os.environ.get("PATH", "")

    # ---------- 2. 隔离本机 Hadoop / YARN 配置 ----------
    os.environ.pop("HADOOP_CONF_DIR", None)
    os.environ.pop("YARN_CONF_DIR", None)
    os.environ["HADOOP_USER_NAME"] = os.environ.get("HADOOP_USER_NAME", "local")

    # ---------- 3. Ivy cache（避免重复下载依赖） ----------
    ivy_dir = str(Path.home() / ".ivy2_spark")
    Path(ivy_dir).mkdir(parents=True, exist_ok=True)

    # ---------- 4. Spark + S3A 启动参数 ----------
    os.environ["PYSPARK_SUBMIT_ARGS"] = (
        "--packages org.apache.hadoop:hadoop-aws:3.3.6,"
        "com.amazonaws:aws-java-sdk-bundle:1.12.367 "
        f"--conf spark.jars.ivy={ivy_dir} "
        "--conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem "
        "--conf spark.hadoop.fs.s3a.aws.credentials.provider="
        "com.amazonaws.auth.DefaultAWSCredentialsProviderChain "
        # 所有时间参数 → 纯数字（毫秒）
        "--conf spark.hadoop.fs.s3a.threads.keepalivetime=60000 "
        "--conf spark.hadoop.fs.s3a.multipart.purge.age=86400000 "
        "--conf spark.hadoop.fs.s3a.retry.interval=500 "
        "--conf spark.hadoop.fs.s3a.retry.throttle.interval=100 "
        "--conf spark.hadoop.fs.s3a.connection.ttl=300000 "
        "--conf spark.hadoop.fs.s3a.connection.establish.timeout=60000 "
        "--conf spark.hadoop.fs.s3a.connection.timeout=60000 "
        "--conf spark.hadoop.fs.s3a.socket.timeout=60000 "
        "pyspark-shell"
    )

    # ---------- 5. Create SparkSession ----------
    spark = (
        SparkSession.builder
        .master("local[*]")
        .appName(app_name)
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")
    return spark

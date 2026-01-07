def get_spark(app_name: str = "us-accidents"):
    from pyspark.sql import SparkSession

    packages = ",".join([
        "org.apache.hadoop:hadoop-aws:3.4.2",
        "com.amazonaws:aws-java-sdk-bundle:1.12.367",
    ])

    spark = (
        SparkSession.builder
        .appName(app_name)
        .config("spark.jars.packages", packages)
        .config("spark.jars.ivy", "/Users/josiejiang/.ivy2_spark")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.aws.credentials.provider",
                "com.amazonaws.auth.DefaultAWSCredentialsProviderChain")

        # 毫秒整数，避免 NumberFormatException
        .config("spark.hadoop.fs.s3a.threads.keepalivetime", "60000")
        .config("spark.hadoop.fs.s3a.multipart.purge.age", "86400000")
        .config("spark.hadoop.fs.s3a.retry.interval", "500")
        .config("spark.hadoop.fs.s3a.retry.throttle.interval", "100")
        .config("spark.hadoop.fs.s3a.connection.ttl", "300000")
        .config("spark.hadoop.fs.s3a.connection.establish.timeout", "60000")
        .config("spark.hadoop.fs.s3a.connection.timeout", "60000")
        .config("spark.hadoop.fs.s3a.socket.timeout", "60000")

        # 先保守关闭，确保稳定（后面性能优化再考虑打开）
        .config("spark.hadoop.fs.s3a.vectored.read.enabled", "false")
        .config("spark.hadoop.parquet.read.vectored.io.enabled", "false")

        .getOrCreate()
    )
    return spark

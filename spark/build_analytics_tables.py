from pyspark.sql import functions as F
from spark.session_start import get_spark

# -------------------------
# Config
# -------------------------
spark = get_spark("us-accidents-build-analytics")

raw_path = "s3a://us-accidents-dashboard-1445/US_Accidents_March23_sampled_500k.csv"
out_prefix = "s3a://us-accidents-dashboard-1445/analytics"

# -------------------------
# Load raw
# -------------------------
df = spark.read.csv(raw_path, header=True, inferSchema=True)

# Normalize time once (reused by multiple tables)
df2 = (
    df
    .withColumn("Start_Time_ts", F.to_timestamp("Start_Time"))
    .filter(F.col("Start_Time_ts").isNotNull())
)

def write_parquet(df_out, name: str, coalesce_one: bool = True):
    out_path = f"{out_prefix}/{name}"
    w = df_out.coalesce(1) if coalesce_one else df_out
    w.write.mode("overwrite").parquet(out_path)
    return out_path

def validate_parquet(path: str, n: int = 10):
    chk = spark.read.parquet(path)
    chk.show(n, truncate=False)
    chk.printSchema()
    print("rows:", chk.count())
    return chk

# ============================================================
# 1) analytics/state_counts  (for Regional/Severity)
# ============================================================
state_counts = (
    df2
    .filter(F.col("State").isNotNull())
    .groupBy("State")
    .agg(F.count("*").alias("accident_count"))
    .orderBy(F.desc("accident_count"))
)

path_state_counts = write_parquet(state_counts, "state_counts")
print("\n=== state_counts ===")
validate_parquet(path_state_counts, 10)

# ============================================================
# 2) analytics/severity_counts  (for Severity)
# ============================================================
severity_counts = (
    df2
    .filter(F.col("Severity").isNotNull())
    .groupBy("Severity")
    .agg(F.count("*").alias("accident_count"))
    .orderBy("Severity")
)

path_severity_counts = write_parquet(severity_counts, "severity_counts")
print("\n=== severity_counts ===")
validate_parquet(path_severity_counts, 10)

# ============================================================
# 3) analytics/weather_severity_counts  (for Weather/Severity)
#    Output: Weather_Condition, Severity, accident_count
# ============================================================
weather_severity_counts = (
    df2
    .filter(F.col("Weather_Condition").isNotNull())
    .filter(F.col("Severity").isNotNull())
    .groupBy("Weather_Condition", "Severity")
    .agg(F.count("*").alias("accident_count"))
    .orderBy(F.desc("accident_count"))
)

path_weather_sev = write_parquet(weather_severity_counts, "weather_severity_counts")
print("\n=== weather_severity_counts ===")
validate_parquet(path_weather_sev, 10)

# ============================================================
# 4) analytics/state_yearly_counts  (for Regional)
#    Output: State, year, accident_count
# ============================================================
state_yearly_counts = (
    df2
    .filter(F.col("State").isNotNull())
    .withColumn("year", F.year("Start_Time_ts"))
    .groupBy("State", "year")
    .agg(F.count("*").alias("accident_count"))
    .orderBy("State", "year")
)

path_state_yearly = write_parquet(state_yearly_counts, "state_yearly_counts")
print("\n=== state_yearly_counts ===")
validate_parquet(path_state_yearly, 10)

# ============================================================
# 5) analytics/city_counts_topN  (for Regional)
#    Output: City, State(optional), accident_count
#    Note: Some datasets have City, some have City + State. We keep both if available.
# ============================================================
# If City column doesn't exist in your schema, this will fail; in that case tell me your actual column name.
city_cols = [c for c in ["City", "State"] if c in df2.columns]

city_base = df2
for c in city_cols:
    city_base = city_base.filter(F.col(c).isNotNull())

city_counts = (
    city_base
    .groupBy(*city_cols)
    .agg(F.count("*").alias("accident_count"))
    .orderBy(F.desc("accident_count"))
)

TOP_N_CITIES = 200  # enough for dashboard; adjust as needed
city_counts_topN = city_counts.limit(TOP_N_CITIES)

path_city_topN = write_parquet(city_counts_topN, "city_counts_topN")
print("\n=== city_counts_topN ===")
validate_parquet(path_city_topN, 10)

# ============================================================
# 6) analytics/top_states_by_quarter  (for Temporal racing bar)
#    Output: year, quarter, State, accident_count (Top 10 per quarter)
# ============================================================
state_quarter_counts = (
    df2
    .filter(F.col("State").isNotNull())
    .withColumn("year", F.year("Start_Time_ts"))
    .withColumn("quarter", F.quarter("Start_Time_ts"))
    .groupBy("year", "quarter", "State")
    .agg(F.count("*").alias("accident_count"))
)

from pyspark.sql.window import Window

w = Window.partitionBy("year", "quarter").orderBy(F.desc("accident_count"))
top_states_by_quarter = (
    state_quarter_counts
    .withColumn("rank", F.row_number().over(w))
    .filter(F.col("rank") <= 10)
    .drop("rank")
    .orderBy("year", "quarter", F.desc("accident_count"))
)

path_top_states_quarter = write_parquet(top_states_by_quarter, "top_states_by_quarter")
print("\n=== top_states_by_quarter ===")
validate_parquet(path_top_states_quarter, 20)

print("\nAll analytics tables generated under:", out_prefix)

"""Gold merchant totals on Databricks: bronze Delta table in, gold Delta table out, all work on the cluster."""
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


class InputCheckFailed(Exception):
    """Raised before the write, so a partial or stale bronze never replaces a correct gold table."""


def check_input(bronze, min_rows: int, max_age_hours: float) -> None:
    # one small aggregate on the cluster; .first() brings back a single row, not the data
    row = bronze.agg(
        F.count("*").alias("rows"),
        ((F.unix_timestamp(F.current_timestamp()) - F.unix_timestamp(F.max("ingested_at"))) / 3600).alias("age_h"),
    ).first()
    if row["rows"] < min_rows:
        raise InputCheckFailed(f"bronze.transactions has {row['rows']} rows, expected at least {min_rows}")
    if row["age_h"] is None or row["age_h"] > max_age_hours:
        raise InputCheckFailed(f"bronze.transactions is stale: newest ingested_at is {row['age_h']} hours old")


def build(spark: SparkSession, min_rows: int = 1_000_000, max_age_hours: float = 26) -> None:
    bronze = spark.read.table("bronze.transactions")
    check_input(bronze, min_rows, max_age_hours)   # blocking: nothing is written if this raises
    (
        bronze
        .filter(F.col("amount") > 0)
        .groupBy("merchant")
        .agg(F.sum("amount").alias("total"))
        .write.format("delta")
        .mode("overwrite")
        .saveAsTable("gold.merchant_totals")
    )


if __name__ == "__main__":
    build(SparkSession.builder.getOrCreate())

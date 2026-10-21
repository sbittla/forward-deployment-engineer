"""Gold merchant totals on Databricks: one day of bronze in, that day's gold partition out, all work on the cluster."""
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


class InputCheckFailed(Exception):
    """Raised before the write, so a partial or stale batch never replaces a correct gold partition."""


def check_input(bronze, batch_date: str, max_age_hours: float, min_ratio: float, history_days: int) -> None:
    # Completeness is relative: the batch's row count against the median of the trailing days' counts (the same rule
    # as check_batch_complete in Part A). An absolute floor such as 1,000,000 rows passes a 1.1M-row truncated day.
    daily = (bronze
             .filter((F.col("event_date") < F.lit(batch_date))
                     & (F.col("event_date") >= F.date_sub(F.lit(batch_date), history_days)))
             .groupBy("event_date").count())
    median = daily.agg(F.percentile_approx("count", 0.5).alias("median")).first()["median"]
    # one small aggregate on the cluster; .first() brings back a single row, not the data
    row = bronze.filter(F.col("event_date") == F.lit(batch_date)).agg(
        F.count("*").alias("rows"),
        ((F.unix_timestamp(F.current_timestamp()) - F.unix_timestamp(F.max("ingested_at"))) / 3600).alias("age_h"),
    ).first()
    if median is None:
        raise InputCheckFailed(f"no trailing daily counts before {batch_date} to compare against")
    if row["rows"] < min_ratio * median:
        raise InputCheckFailed(f"bronze.transactions has {row['rows']} rows for {batch_date}, "
                               f"below {min_ratio:.0%} of the trailing median {median}")
    if row["age_h"] is None or row["age_h"] > max_age_hours:
        raise InputCheckFailed(f"bronze.transactions is stale: newest ingested_at is {row['age_h']} hours old")


def build(spark: SparkSession, batch_date: str, max_age_hours: float = 26, min_ratio: float = 0.5,
          history_days: int = 7) -> None:
    bronze = spark.read.table("bronze.transactions")
    check_input(bronze, batch_date, max_age_hours, min_ratio, history_days)   # blocking: nothing written if it raises
    (
        bronze
        .filter((F.col("event_date") == F.lit(batch_date)) & (F.col("amount") > 0))
        .groupBy("event_date", "merchant")
        .agg(F.sum("amount").alias("total"))
        .write.format("delta")
        .mode("overwrite")
        .option("replaceWhere", f"event_date = '{batch_date}'")    # rebuild only this batch's partition
        .saveAsTable("gold.merchant_totals")
    )


if __name__ == "__main__":
    import sys
    build(SparkSession.builder.getOrCreate(), sys.argv[1])

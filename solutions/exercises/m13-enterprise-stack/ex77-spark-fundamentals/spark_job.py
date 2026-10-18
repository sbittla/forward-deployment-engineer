"""Gold merchant totals on Databricks: bronze Delta table in, gold Delta table out, all work on the cluster."""
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def build(spark: SparkSession) -> None:
    (
        spark.read.table("bronze.transactions")
        .filter(F.col("amount") > 0)
        .groupBy("merchant")
        .agg(F.sum("amount").alias("total"))
        .write.format("delta")
        .mode("overwrite")
        .saveAsTable("gold.merchant_totals")
    )


if __name__ == "__main__":
    build(SparkSession.builder.getOrCreate())

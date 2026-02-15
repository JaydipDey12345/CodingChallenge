# Spark + Jupyter Troubleshooting Guide

## ✅ Issue Fixed

The Jupyter notebook was not connecting to the Spark cluster because the SparkSession builder was missing the **master URL**.

### What Changed

**Before (broken):**
```python
spark = SparkSession.builder \
    .appName("pyspark-assesment") \
    .getOrCreate()  # ❌ Defaults to local mode
```

**After (fixed):**
```python
spark = SparkSession.builder \
    .appName("pyspark-assesment") \
    .master("spark://master:7077") \  # ✅ Explicitly connect to cluster
    .getOrCreate()
```

## ✅ Current Status

| Component | Status |
|-----------|--------|
| Spark Master | ✅ Running on `spark://master:7077` |
| Worker 1 | ✅ Connected (2 cores) |
| Worker 2 | ✅ Connected (2 cores) |
| Jupyter | ✅ Running at `http://localhost:8888` |
| Connectivity | ✅ Verified |

## How to Use Jupyter with Spark Cluster

### 1. Access Jupyter
```
http://localhost:8888
```

### 2. Create a new cell with:
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("my-app") \
    .master("spark://master:7077") \
    .getOrCreate()

print(f"Connected to: {spark.sparkContext.master}")
print(f"App ID: {spark.sparkContext.applicationId}")
```

### 3. Run your PySpark code
```python
# Example: Load data
df = spark.read.csv("/dataset/nyc-jobs.csv", header=True)
df.show()

# Example: Transform data
result = df.groupBy("Agency").count().show()
```

### 4. Monitor jobs
- **Jupyter output**: Shows Spark job progress
- **Spark Master UI**: http://localhost:8080 (see running jobs)
- **Worker UIs**: http://localhost:8081 and http://localhost:8082

## Key Configuration Details

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `master` | `spark://master:7077` | Connect to cluster (required) |
| `appName` | Your app name | Identifies job in Spark UI |
| Dataset path | `/dataset/nyc-jobs.csv` | CSV file inside container |

## Verify Connection

Run this in Jupyter to test:
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("test") \
    .master("spark://master:7077") \
    .getOrCreate()

# Test DataFrame creation
test_df = spark.createDataFrame([(1, "test")], ["id", "value"])
print(f"✓ Connection verified: {test_df.count()} row(s) created")
```

## If Jobs Still Don't Execute

Run these checks:

**1. Check Jupyter kernel is running:**
```bash
docker logs jupyter | tail -20
```

**2. Verify Spark cluster is healthy:**
```bash
curl http://localhost:8080/
```

**3. Check worker connectivity:**
```bash
docker logs worker1 | grep -i "connected\|registered"
docker logs worker2 | grep -i "connected\|registered"
```

**4. Restart all services:**
```bash
docker compose down
docker compose up -d
sleep 30  # Give Spark time to start
```

## Notes

- Always specify `.master("spark://master:7077")` in SparkSession builder
- Jupyter notebook now has the correct configuration
- All data paths inside containers use `/dataset/` and `/app/`
- Jobs will show up in Spark Master UI at http://localhost:8080

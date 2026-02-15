# Execute Spark Code from VS Code

## Quick Start (2 Steps)

### Step 1: Start Docker Containers
Open terminal in VS Code (Ctrl+`) and run:
```bash
docker compose up -d
```

Wait 30 seconds for Spark to initialize.

### Step 2: Execute Your Code

Choose one of these methods based on your preference:

---

## Method 1: Run PySpark Interactive Shell ⭐ (RECOMMENDED)

Fastest way to test code interactively.

**In VS Code terminal:**
```bash
docker exec -it master /opt/spark/bin/pyspark --master spark://master:7077
```

You'll see:
```
>>>
```

Now paste your Python code:
```python
df = spark.read.csv("/dataset/nyc-jobs.csv", header=True)
print(f"Loaded {df.count()} records")
df.show(5)
```

**Advantages:**
- Interactive, see results immediately
- No file creation needed
- Good for testing/debugging

---

## Method 2: Create Python Script & Submit via spark-submit ⭐ (FOR SERIOUS WORK)

Best for actual analysis and reproducibility.

### Step 1: Create Analysis Script in VS Code

Create a new file in your project: `my_analysis.py`

```python
#!/usr/bin/env python3
"""My Spark Analysis"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import count, desc

# Initialize Spark
spark = SparkSession.builder \
    .appName("my-analysis") \
    .master("spark://master:7077") \
    .getOrCreate()

print("=" * 60)
print("NYC JOBS ANALYSIS")
print("=" * 60)

# Load data
df = spark.read.csv("/dataset/nyc-jobs.csv", header=True, inferSchema=True)
print(f"\n✓ Loaded {df.count()} records")

# Show schema
print("\nColumns:")
df.printSchema()

# Sample data
print("\nFirst 3 records:")
df.show(3, truncate=False)

# Your analysis here
print("\nTop 5 Agencies:")
if "Agency" in df.columns:
    df.groupBy("Agency") \
        .agg(count("*").alias("count")) \
        .orderBy(desc("count")) \
        .limit(5) \
        .show()

spark.stop()
print("\n✓ Analysis complete")
```

### Step 2: Execute from VS Code Terminal

```bash
# Copy script to Spark master container
docker cp my_analysis.py master:/tmp/

# Execute
docker exec master /opt/spark/bin/spark-submit \
  --master spark://master:7077 \
  /tmp/my_analysis.py
```

**Output:**
```
============================================================
NYC JOBS ANALYSIS
============================================================

✓ Loaded 2946 records

Columns:
root
 |-- Job ID: integer
 |-- Agency: string
 ...

First 3 records:
...

Top 5 Agencies:
+------------------------------+-----+
|Agency                        |count|
+------------------------------+-----+
|DEPT OF ENVIRONMENT PROTECTION|655  |
|NYC HOUSING AUTHORITY         |231  |
...
```

---

## Method 3: Run Python Script in Code Directory

If you put scripts in the `code/` folder, they're auto-mounted.

### Step 1: Create Script in `code/` folder

Create: `code/analysis.py`
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("analysis") \
    .master("spark://master:7077") \
    .getOrCreate()

df = spark.read.csv("/dataset/nyc-jobs.csv", header=True)
df.show()
```

### Step 2: Execute from VS Code Terminal

```bash
docker exec master /opt/spark/bin/spark-submit \
  --master spark://master:7077 \
  /app/analysis.py
```

(Note: `/app` is the container path for `code/` folder)

---

## Method 4: Run Jupyter Notebook (⚠️ Workaround for ARM64)

**Note:** Jupyter doesn't work directly on ARM64, but you can use it for non-Spark code.

Access at: http://localhost:8888

Use it ONLY for:
- Pandas analysis (small data)
- Visualization
- Data exploration (NOT Spark operations)

For Spark work, use Methods 1-3 above.

---

## Quick Commands Reference

| Task | Command |
|------|---------|
| Start containers | `docker compose up -d` |
| Stop containers | `docker compose down` |
| Interactive Spark shell | `docker exec -it master /opt/spark/bin/pyspark --master spark://master:7077` |
| Submit script | `docker exec master /opt/spark/bin/spark-submit --master spark://master:7077 /tmp/script.py` |
| View logs | `docker logs -f master` |
| Monitor jobs | http://localhost:8080 |
| Check running containers | `docker compose ps` |

---

## Workflow: Write Code in VS Code, Execute in Docker

```
1. Write your Python script in VS Code
   ↓
2. Save as: my_script.py
   ↓
3. Open VS Code terminal (Ctrl+`)
   ↓
4. Run: docker cp my_script.py master:/tmp/
   ↓
5. Run: docker exec master /opt/spark/bin/spark-submit \
         --master spark://master:7077 /tmp/my_script.py
   ↓
6. See results in terminal
   ↓
7. Monitor in Spark UI: http://localhost:8080
```

---

## Example: Complete Workflow

**Step 1:** In VS Code, create `analysis.py`:
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("test") \
    .master("spark://master:7077") \
    .getOrCreate()

df = spark.read.csv("/dataset/nyc-jobs.csv", header=True, inferSchema=True)
print(f"Total jobs: {df.count()}")
print(f"Agencies: {df.select('Agency').distinct().count()}")

spark.stop()
```

**Step 2:** In VS Code terminal:
```bash
docker cp analysis.py master:/tmp/
docker exec master /opt/spark/bin/spark-submit --master spark://master:7077 /tmp/analysis.py
```

**Step 3:** See output:
```
Total jobs: 2946
Agencies: 52
```

---

## Troubleshooting

### "Command not found: docker"
- Docker is not installed or not in PATH
- Restart VS Code after installing Docker

### "Cannot connect to master:7077"
- Spark cluster not running: `docker compose up -d`
- Wait 30 seconds and try again

### "File not found" error
- Ensure you copied file: `docker cp my_file.py master:/tmp/`
- Or put it in `code/` folder (auto-mounted as `/app`)

### Script hangs indefinitely
- You're on ARM64 with Jupyter (don't use Method 4)
- Use spark-submit (Methods 1-3) instead

### Want to see Spark logs?
```bash
docker logs -f master | grep -i "application\|error"
```

---

## Next Steps

1. **Try Method 1** (pyspark shell) first to test interactively
2. **Create your analysis.py** script
3. **Execute via spark-submit** (Method 2)
4. **Monitor** at http://localhost:8080
5. **Iterate** and refine your code

Good luck! Let me know if you need help with any specific analysis.

# VS Code Quick Start Card

## 🚀 Get Running in 60 Seconds

### Terminal 1: Start Docker
```bash
docker compose up -d
```
Wait 30 seconds.

### Terminal 2: Run Analysis
```bash
docker cp my_analysis.py master:/tmp/
docker exec master /opt/spark/bin/spark-submit --master spark://master:7077 /tmp/my_analysis.py
```

**Done!** Results show in terminal.

---

## 📝 Three Ways to Execute Code

### Way 1️⃣: Interactive Shell (Best for Testing)
```bash
docker exec -it master /opt/spark/bin/pyspark --master spark://master:7077
```
Then type Python code directly:
```python
>>> df = spark.read.csv("/dataset/nyc-jobs.csv", header=True)
>>> df.show()
```

### Way 2️⃣: Python Script (Best for Real Work)
```bash
# Edit my_analysis.py, then:
docker cp my_analysis.py master:/tmp/
docker exec master /opt/spark/bin/spark-submit --master spark://master:7077 /tmp/my_analysis.py
```

### Way 3️⃣: Script in code/ Folder (Auto-Mounted)
```bash
# Put script in: code/my_script.py
docker exec master /opt/spark/bin/spark-submit --master spark://master:7077 /app/my_script.py
```

---

## 🛠️ Essential Commands

| Command | What it does |
|---------|------------|
| `docker compose up -d` | Start all containers |
| `docker compose down` | Stop all containers |
| `docker compose ps` | Check status |
| `docker logs -f master` | Watch Spark logs |
| `docker logs jupyter` | Check Jupyter logs |

---

## 🌐 Web Interfaces

| Service | URL |
|---------|-----|
| Spark Master | http://localhost:8080 |
| Spark Worker 1 | http://localhost:8081 |
| Spark Worker 2 | http://localhost:8082 |
| Jupyter (⚠️ ARM64 issue) | http://localhost:8888 |
| Documentation | http://localhost |

---

## 📚 Your Files

- `my_analysis.py` - Template script (copy & modify this)
- `code/` - Auto-mounted to `/app` in containers
- `dataset/nyc-jobs.csv` - Data file (auto-mounted to `/dataset`)

---

## ⚡ Typical Workflow

```
1. Edit my_analysis.py in VS Code
2. Save (Ctrl+S)
3. Open terminal (Ctrl+`)
4. Run: docker cp my_analysis.py master:/tmp/
5. Run: docker exec master /opt/spark/bin/spark-submit --master spark://master:7077 /tmp/my_analysis.py
6. See results in terminal
7. Go to step 1 to iterate
```

---

## 🔍 Debugging

**Script won't run?**
```bash
# Check if containers are running
docker compose ps

# Start them if not
docker compose up -d

# Check logs
docker logs master
```

**Want to see what Spark is doing?**
- Open http://localhost:8080 in browser
- Click on your application name
- See tasks, stages, and performance metrics

**Script is slow?**
- Check Spark Master UI to see if tasks are distributed across workers
- If all tasks on one executor, your data might be too small to parallelize

---

## 💡 Pro Tips

1. **Copy full code output:**
   ```bash
   docker exec master /opt/spark/bin/spark-submit ... > output.txt 2>&1
   ```

2. **Run multiple times quickly:**
   - Keep the same terminal open
   - Edit script, then rerun command

3. **Debug in interactive mode:**
   ```bash
   docker exec -it master /opt/spark/bin/pyspark
   # Test code line by line
   ```

4. **Access data files:**
   - CSV: `/dataset/nyc-jobs.csv`
   - Code: `/app/` (same as `code/` folder)
   - Temp: `/tmp/`

---

## ✅ Verify Everything Works

```bash
# Run template analysis
docker cp my_analysis.py master:/tmp/
docker exec master /opt/spark/bin/spark-submit --master spark://master:7077 /tmp/my_analysis.py
```

**Expected output:**
```
✓ Loaded 2,946 records
... [data analysis results] ...
✓ ANALYSIS COMPLETE
```

If you see this, you're good to go!

---

Need more help? Check `EXECUTE_FROM_VSCODE.md` for detailed instructions.

#!/usr/bin/env python3
"""
NYC Jobs Data Analysis Template
Author: Jaydip Dey
Date: 2026-02-15

HOW TO RUN:
-----------
1. In VS Code terminal, run:
   
   docker cp my_analysis.py master:/tmp/
   docker exec master /opt/spark/bin/spark-submit --master spark://master:7077 /tmp/my_analysis.py
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, avg, desc, max as spark_max, 
    min as spark_min, when, isnan, lower, dense_rank, year
)
from pyspark.sql.types import *
from pyspark.sql.window import Window
import matplotlib.pyplot as plt
import sys

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("NYC-Jobs-Analysis") \
    .master("spark://master:7077") \
    .config("spark.executor.memory", "1g") \
    .config("spark.driver.memory", "1g") \
    .getOrCreate()

print("\n" + "=" * 80)
print("NYC JOBS DATA ANALYSIS")
print("=" * 80)

def dataframe_decription(df):
    print("Total Records: ",df.count())
    print("Total Columns: ",len(df.columns))
    print("Data Schema: ")
    df.printSchema()
    print("Data Sample: \n")
    df.describe().show()

    numeric_columns = []
    categorical_columns = []
    date_columns = []
    others = []
    for f in df.schema.fields:
        if type(f.dataType) in [IntegerType,DoubleType,FloatType]: numeric_columns.append(f.name)
        elif type(f.dataType) in [StringType]: categorical_columns.append(f.name)
        elif type(f.dataType) in [DateType,TimestampType]: date_columns.append(f.name)
        else: others.append(f.name)

    if len(numeric_columns) > 0: print("Numeric Columns: ", numeric_columns)
    if len(categorical_columns) > 0: print("Category Columns: ", categorical_columns)
    if len(date_columns) > 0: print("Date Columns: ", date_columns)
    if len(others) > 0: print("Non Categorized Columns: ", others)
    return

def writeDataframe(df, path):
    print("Writing the Dataframe into: ", path)
    df.coalesce(1).write.mode("overwrite").option("header", "true").csv(path)
    return

try:
    # ========== STEP 1: LOAD DATA ==========
    df = spark.read.format("csv") \
                    .option("header", "true") \
                    .option("inferSchema", "true") \
                    .option("multiLine", "true") \
                    .option("escape", '"') \
                    .option("quote", '"') \
                    .load("/dataset/nyc-jobs.csv")
    df = df.distinct() # REMOVE DUPLICATES 
    df.cache()
    dataframe_decription(df)

    df = df.withColumn('Skill', when(lower(df['Preferred Skills']).contains('python'),"python")\
                                .when(lower(df['Preferred Skills']).contains('sql'),"sql")\
                                .when(lower(df['Preferred Skills']).contains('excel'),"excel")\
                                .when(lower(df['Preferred Skills']).contains('linux'),"linux")\
                                .when(lower(df['Preferred Skills']).contains('housing'),"contractor")\
                                .when(lower(df['Preferred Skills']).contains('engineering'),"engineering")\
                                .when(lower(df['Preferred Skills']).contains('manager'),"manager")\
                                .when(lower(df['Preferred Skills']).contains('driver'),"driver")\
                                .when((lower(df['Preferred Skills']).contains('legal')) | 
                                      (lower(df['Preferred Skills']).contains('law')) |
                                      (lower(df['Preferred Skills']).contains('prosecutor')) |
                                      (lower(df['Preferred Skills']).contains('investigator')) |
                                      (lower(df['Preferred Skills']).contains('advocacy')),"legal")\
                                .when(lower(df['Preferred Skills']).contains('construction'),"civil")\
                                .when(lower(df['Preferred Skills']).contains('communication'),"civil")\
                                .when(df['Preferred Skills'].isNull(),"Not Provided")
                                .otherwise('Not Mapped'))


    df = df.withColumn('Degree', when(lower(df['Minimum Qual Requirements']).contains('phd'), "PhD")\
                                .when(lower(df['Minimum Qual Requirements']).contains('master'), "Master")\
                                .when((lower(df['Minimum Qual Requirements']).contains('baccalaureate')) |
                                      (lower(df['Minimum Qual Requirements']).contains('engineer')) |
                                      (lower(df['Minimum Qual Requirements']).contains('bachelorâ€™s')) |
                                      (lower(df['Minimum Qual Requirements']).contains('four years of recent full-time')) |
                                      (lower(df['Minimum Qual Requirements']).contains('graduation')) | 
                                      (lower(df['Minimum Qual Requirements']).contains('legal')), "Bachelor")\
                                .when((lower(df['Minimum Qual Requirements']).contains('high school')) |
                                      (lower(df['Minimum Qual Requirements']).contains('matriculation')), "High School")\
                                .otherwise("Not Required"))
    
    print("\n" + "-" * 80)
    print("CATEGORY WISE JOB COUNT -> TOP 10")
    print("-" * 80)

    # TOP 10 JOB COUNT HAS BEEN PROVIDED BASED ON JOB CATEGORY COLUMN AVAILABLE IN THE DATA

    jobCount_categorywise = df.groupBy('Job Category').agg({'Job ID':'count'}).withColumnRenamed('count(Job ID)','JobCount')
    jobCount_categorywise = jobCount_categorywise.sort(desc('JobCount'))
    jobCount_categorywise.limit(10).show(truncate=False)
    writeDataframe(jobCount_categorywise, "/app/jobCount_categorywise.csv")

    print("\n" + "-" * 80)
    print("CATEGORY WISE SALARY DISTRIBUTION")
    print("-" * 80)

    # ============== SALARY DISTRIBUTION BASED ON 22 WORKING DAYS IN A MONTH & 8 WORKING HOURS IN A DAY ====================

    salarydist_categorywise1 = df.withColumn('RangeStart', when(df['Salary Frequency']=='Hourly', df['Salary Range From']*8*22)\
                                                            .when(df['Salary Frequency']=='Daily', df['Salary Range From']*22)\
                                                            .when(df['Salary Frequency']=='Annual', df['Salary Range From'])\
                                                            .otherwise(df['Salary Range From']))\
                                .withColumn('RangeEnd', when(df['Salary Frequency']=='Hourly', df['Salary Range To']*8*22)\
                                                            .when(df['Salary Frequency']=='Daily', df['Salary Range To']*22)\
                                                            .when(df['Salary Frequency']=='Annual', df['Salary Range To'])\
                                                            .otherwise(df['Salary Range To']))
    salarydist_categorywise = salarydist_categorywise1.groupBy('Job Category').agg({'RangeStart':'min','RangeEnd':'max'})\
                                                        .withColumnRenamed('min(RangeStart)','Min_Salary')\
                                                        .withColumnRenamed('max(RangeEnd)','Max_Salary')
    salarydist_categorywise.select('Job Category','Min_Salary','Max_Salary').show(40)
    writeDataframe(salarydist_categorywise, "/app/salarydist_categorywise.csv")

    print("\n" + "-" * 80)
    print("RELATION BETWEEN DEGREE & SALARY")
    print("-" * 80)

    # DEGREE HAS BEEN MAPPED MANUALLYF FROM THE DATA, BASED ON THAT DEGREE WISE AVERAGE SALARY HAS BEEN PROVIDED IN DESCENDING ORDER

    salarydist_categorywise1 = salarydist_categorywise1.withColumn('Salary_avg', (col('RangeStart')+col('RangeEnd'))/2)
    salarydist_categorywise1 = salarydist_categorywise1.withColumn('PostingYear', year(col('Posting Date')))
    salarydist_titlewise = salarydist_categorywise1.groupBy('Degree').agg({'RangeStart':'min','RangeEnd':'max','Salary_avg':'avg'})\
                                                        .withColumnRenamed('avg(Salary_avg)','Avg_Salary')\
                                                        .sort(desc('Avg_Salary'))
    salarydist_titlewise.select('Degree','Avg_Salary').show(40)
    writeDataframe(salarydist_titlewise, "/app/salarydist_titlewise.csv")

    print("\n" + "-" * 80)
    print("JOB POSTINGS HAVING HIGHEST SALARY PER AGENCY")
    print("-" * 80)

    # FULL DATA HAS BEEN PROVIDED, WITH FILTERED ONLY JOBS OFFERING HIGHEST SALARY PER AGENCY

    highestSalary = salarydist_categorywise1.withColumn('SalaryRank', dense_rank().over(Window.partitionBy('Agency').orderBy(col('RangeEnd').desc())))
    highestSalary_agencywise = highestSalary.filter(col('SalaryRank')==1)
    highestSalary_agencywise.show()
    writeDataframe(highestSalary_agencywise, "/app/highestSalary_agencywise.csv")

    print("\n" + "-" * 80)
    print("JOB POSTINGS AVERAGE SALARY PER AGENCY FOR THE LAST 2 YEARS")
    print("-" * 80)

    # YEAR & AGENCY WISE AVERAGE HAS BEEN PROVIDED, USED PIVOT FOR BETTER VISAULIZATION
    
    salaryavg_agencywise = salarydist_categorywise1.withColumn('YearRank', dense_rank().over(Window.partitionBy('Agency').orderBy(col('PostingYear').desc())))
    salaryavg_agencywise = salaryavg_agencywise.filter(col('YearRank')<=2).groupBy('Agency', 'PostingYear').agg({'Salary_avg':'avg'}).withColumnRenamed('avg(Salary_avg)','Salary_avg')
    salaryavg_agencywise = salaryavg_agencywise.groupBy('Agency').pivot('PostingYear').agg({'Salary_avg':'first'})
    salaryavg_agencywise.sort('Agency').show()
    writeDataframe(salaryavg_agencywise, "/app/salaryavg_agencywise.csv")

    print("\n" + "-" * 80)
    print("HIGHEST PAID SKILLS IN THE US MARKET")
    print("-" * 80)

    # SKILL WISE RANKING BASED ON HIGHEST SALARY HAS BEEN PROVIDED

    highestSalary_skillwise = salarydist_categorywise1.filter(~(col('Skill').isin(['Not Mapped','Not Provided'])))  # DATA FILTERED FOR THE DATA QUALITY ISSUES
    highestSalary_skillwise = highestSalary_skillwise.groupBy('Skill').agg({'RangeEnd':'max'}).withColumnRenamed('max(RangeEnd)','Salary')\
                                                    .withColumn('Rank',dense_rank().over(Window.partitionBy().orderBy(col('Salary').desc())))
    highestSalary_skillwise.show()
    writeDataframe(highestSalary_skillwise, "/app/highestSalary_skillwise.csv")

    salary_pd = highestSalary_skillwise.select("Skill", "Salary").toPandas()
    plt.figure()
    plt.bar(salary_pd["Skill"], salary_pd["Salary"])
    plt.title("Salary Distribution per Skill")
    plt.xticks(rotation=45)
    plt.xlabel("Skill")
    plt.ylabel("Salary")
    plt.tight_layout()
    plt.savefig("/app/skillwise_salary.png")
    
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("PLEASE FIND ALL THE OUTPUT FILES IN /code OF THE PROJECT")
    print("=" * 80)

except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    raise

finally:
    spark.stop()

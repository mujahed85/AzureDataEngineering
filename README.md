

---

# **FULL END-TO-END DATA LAKEHOUSE PIPELINE**

### **1. Bronze → Silver → Gold Processing (Industry Standard)**

✔ **1.1** Bronze = Raw

✔ **1.2** Silver = Cleaned

✔ **1.3** Gold = Aggregated / Analytics Ready


Everything will be done in **ONE GO**:

**1.4** Create sample datasets

**1.5** Create Azure resources (CLI)

**1.6** Upload RAW → Bronze

**1.7** Process Bronze → Silver (Python)

**1.8** Process Silver → Gold (Python)

**1.9** Upload all results back into Azure

**1.10** Verify structure

**1.11** Clean local files and folders

**1.12** Clean Azure resources

This is EXACTLY what Azure Data Engineers do in real projects.

---

# 🚀 **BRONZE → SILVER → GOLD (Full Workflow in One Go)**

Azure CLI + Python ● Windows 11 ● Azure Free Trial

---

# =============================================

# **2. PART 1 — CREATE LOCAL DATASETS (Raw)**

### **2.1** Folder for all work

```cmd
mkdir DL_Python_Pipeline
```

### **2.2** Create RAW (Bronze) file

📄 **DL_Python_Pipeline\customers_raw.csv**

```
id,name,city,age,salary
1,Rohit,Mumbai,28,50000
2,Neha,Pune,31,62000
3,Amit,Delhi,24,45000
4,,Bangalore,29,55000
5,Meera,Mumbai,30,70000
6,Ajay,Mumbai,35,80000
```

---

# =============================================

# **3. PART 2 — CREATE AZURE RESOURCES (CLI)**

### **3.1** Login

```cmd
az login --use-device-code
```

### **3.2** Create Resource Group

```cmd
az group create --name ADE-Pipeline-RG --location eastus
```

### **3.3** Create ADLS Gen2 Account

```cmd
az storage account create ^
 --name adepipeline110 ^
 --resource-group ADE-Pipeline-RG ^
 --location eastus ^
 --sku Standard_LRS ^
 --kind StorageV2 ^
 --hns true
```

### **3.4** Get account key

```cmd
az storage account keys list --account-name adepipeline110 --resource-group ADE-Pipeline-RG
```

Copy **key1**

---

# =============================================

# **4. PART 3 — CREATE BRONZE / SILVER / GOLD CONTAINERS**

```cmd
az storage container create --name bronze --account-name adepipeline110 --account-key <KEY>
az storage container create --name silver --account-name adepipeline110 --account-key <KEY>
az storage container create --name gold   --account-name adepipeline110 --account-key <KEY>
```

Create folders:

```cmd
az storage fs directory create -f bronze -n "customers" --account-name adepipeline110
az storage fs directory create -f silver -n "customers" --account-name adepipeline110
az storage fs directory create -f gold   -n "customers" --account-name adepipeline110
```

---

# =============================================

# **5. PART 4 — UPLOAD RAW FILE INTO BRONZE**

```cmd
az storage fs file upload ^
 --account-name adepipeline110 ^
 --file-system bronze ^
 --path "customers/customers_raw.csv" ^
 --source "customers_raw.csv"
```

---

# =============================================

# **6. PART 5 — DOWNLOAD BRONZE AND PROCESS INTO SILVER**

## **6.1** Step 1: List bronze file

```cmd
az storage fs file list ^
  --account-key "3i....YOUR...KEY....==" ^
  --account-name adepipeline110 ^
  --file-system bronze
```

## **6.2** Step 2: Create Folder to Land data

```cmd
    mkdir bronze_files
```

## **6.3** Step 3: Download bronze file

```cmd
az storage fs file download ^
 --account-name adepipeline110 ^
 --file-system bronze ^
 --path "customers/customers_raw.csv" ^
 --dest "bronze_files/customers_bronze.csv" ^
 --account-key "3i....YOUR...KEY....=="
```

---

# =============================================

# **7. PART 6 — PYTHON PROCESSING: BRONZE → SILVER**

### **7.1** Install Virtualenv

In your command prompt, install `virtualenv` using pip:

```cmd
pip install virtualenv
```

### **7.2** Create a New Virtual Environment

```cmd
virtualenv venv
```

### **7.3** Activate Virtual Environment

Activate the virtual environment.

* On Windows:

```cmd
.\venv\Scripts\activate
```

* On macOS/Linux:

```bash
source venv/bin/activate
```

Once activated, your command prompt will change to show the virtual environment name (like `(venv)`).

### **7.4** Install Required Libraries

```cmd
pip install -r requirements.txt
```

---

## **7.5** Create Python script:

📄 **bronze_to_silver.py**

```python
import pandas as pd

# Load bronze data
df = pd.read_csv("./bronze_files/customers_bronze.csv")

print("\n--- BRONZE DATA ---")
print(df)

# 1. Remove missing names
df = df.dropna(subset=["name"])

# 2. Convert name to Proper Case
df["name"] = df["name"].str.title()

# 3. Remove rows where salary < 50000 (example cleaning rule)
df = df[df["salary"] >= 50000]

# 4. Remove duplicates
df = df.drop_duplicates()

# Save as Silver CSV and Parquet
df.to_csv("./silver_files/customers_silver.csv", index=False)
df.to_parquet("./silver_files/customers_silver.parquet", engine="pyarrow")

print("\n--- SILVER DATA (Cleaned) ---")
print(df)
```

---

## **7.6** Run script:

```cmd
python ./bronze_to_silver.py
```

Silver dataset now created.

---

# =============================================

# **8. PART 7 — UPLOAD SILVER → ADLS SILVER CONTAINER**

### **8.1** Upload CSV

```cmd
az storage fs file upload ^
 --account-name adepipeline110 ^
 --file-system silver ^
 --path "customers/customers_silver.csv" ^
 --source "silver_files\customers_silver.csv"
```

### **8.2** Upload Parquet

```cmd
az storage fs file upload ^
 --account-name adepipeline110 ^
 --file-system silver ^
 --path "customers/customers_silver.parquet" ^
 --source "silver_files\customers_silver.parquet"
```

---

# =============================================

# **9. PART 8 — PYTHON TRANSFORMATION: SILVER → GOLD**

Gold layer = aggregated, analytics-ready
Example transformation:

✔ **9.1** Average salary by city
✔ **9.2** Count of customers
✔ **9.3** Highest salary per city

---

📄 **silver_to_gold.py**

```python
import pandas as pd

# Load silver layer
df = pd.read_parquet("./silver_files/customers_silver.parquet")

print("\n--- SILVER CLEANED DATA ---")
print(df)

# --- GOLD LEVEL AGGREGATION ---

# 1. Aggregation: Salary summary per city
gold_df = df.groupby("city").agg(
    avg_salary=("salary", "mean"),
    max_salary=("salary", "max"),
    customer_count=("id", "count")
).reset_index()

# Save gold output
gold_df.to_csv("./gold_files/customers_gold.csv", index=False)
gold_df.to_parquet("./gold_files/customers_gold.parquet", engine="pyarrow")

print("\n--- GOLD AGGREGATED DATA ---")
print(gold_df)
```

---

## **9.4** Run Script

```cmd
python silver_to_gold.py
```

---

# =============================================

# **10. PART 9 — UPLOAD GOLD → ADLS GOLD CONTAINER**

### **10.1** Upload CSV

```cmd
az storage fs file upload ^
 --account-name adepipeline110 ^
 --file-system gold ^
 --path "customers/customers_gold.csv" ^
 --source "gold_files\customers_gold.csv"
```

### **10.2** Upload Parquet

```cmd
az storage fs file upload ^
 --account-name adepipeline110 ^
 --file-system gold ^
 --path "customers/customers_gold.parquet" ^
 --source "gold_files\customers_gold.parquet"
```

---

# =============================================

# 🔥 PART 10 — VERIFY BRONZE, SILVER, GOLD STRUCTURE

# =============================================

### Bronze

```cmd
az storage fs file list --account-name adepipeline110 --file-system bronze --path customers
```

```json
[
  {
    "contentLength": 165,
    "creationTime": "2025-11-14T16:11:35.105715+00:00",
    "encryptionScope": null,
    "etag": "0x8DE239894B37FED",
    "expiryTime": null,
    "group": "$superuser",
    "isDirectory": false,
    "lastModified": "2025-11-14T16:12:16",
    "name": "customers/customers_raw.csv",
    "owner": "$superuser",
    "permissions": "rw-r-----"
  }
]
```

### Silver

```cmd
az storage fs file list --account-name adepipeline110 --file-system silver --path customers
```

```json
[
  {
    "contentLength": 121,
    "creationTime": "2025-11-14T16:45:54.906271+00:00",
    "encryptionScope": null,
    "etag": "0x8DE239D47D13C05",
    "expiryTime": null,
    "group": "$superuser",
    "isDirectory": false,
    "lastModified": "2025-11-14T16:45:55",
    "name": "customers/customers_silver.csv",
    "owner": "$superuser",
    "permissions": "rw-r-----"
  },
  {
    "contentLength": 4249,
    "creationTime": "2025-11-14T16:47:00.783413+00:00",
    "encryptionScope": null,
    "etag": "0x8DE239D6F138639",
    "expiryTime": null,
    "group": "$superuser",
    "isDirectory": false,
    "lastModified": "2025-11-14T16:47:01",
    "name": "customers/customers_silver.parquet",
    "owner": "$superuser",
    "permissions": "rw-r-----"
  }
]
```

### Gold

```cmd
az storage fs file list --account-name adepipeline110 --file-system gold --path customers
```
```json
[
  {
    "contentLength": 99,
    "creationTime": "2025-11-14T16:49:22.258361+00:00",
    "encryptionScope": null,
    "etag": "0x8DE239DC35BC329",
    "expiryTime": null,
    "group": "$superuser",
    "isDirectory": false,
    "lastModified": "2025-11-14T16:49:22",
    "name": "customers/customers_gold.csv",
    "owner": "$superuser",
    "permissions": "rw-r-----"
  },
  {
    "contentLength": 3395,
    "creationTime": "2025-11-14T16:49:36.178602+00:00",
    "encryptionScope": null,
    "etag": "0x8DE239DCBA3B2DD",
    "expiryTime": null,
    "group": "$superuser",
    "isDirectory": false,
    "lastModified": "2025-11-14T16:49:36",
    "name": "customers/customers_gold.parquet",
    "owner": "$superuser",
    "permissions": "rw-r-----"
  }
]
```

Expected folder structure:


```
bronze/customers/customers_raw.csv  
silver/customers/customers_silver.csv  
silver/customers/customers_silver.parquet  
gold/customers/customers_gold.csv  
gold/customers/customers_gold.parquet  
```

---

# **12. PART 11 — CLEANING LOCAL FILES AND FOLDERS**

### **12.1** Delete local silver files

```cmd
for /f "delims=" %f in ('dir /b /a-d silver_files') do (
    if /i not "%f"==".gitignore" del /q "silver_files\%f"
)
```

### **12.2** Delete local gold files

```cmd
for /f "delims=" %f in ('dir /b /a-d gold_files') do (
    if /i not "%f"==".gitignore" del /q "gold_files\%f"
)
```

### **12.3** Delete temporary folders

```cmd
for /f "delims=" %f in ('dir /b /a-d bronze_files') do (
    if /i not "%f"==".gitignore" del /q "bronze_files\%f"
)
```

---

# **13. PART 12 — CLEANING AZURE RESOURCES**

### **13.1** Delete containers

```cmd
az storage container delete --name bronze --account-name adepipeline110 --account-key <KEY>
az storage container delete --name silver --account-name adepipeline110 --account-key <KEY>
az storage container delete --name gold --account-name adepipeline110 --account-key <KEY>
```

### **13.2** Delete storage account

```cmd
az storage account delete --name adepipeline110 --resource-group ADE-Pipeline-RG
```


---

# 🎉 **YOU HAVE BUILT A COMPLETE LAKEHOUSE PIPELINE!**

This is the **full professional workflow**:

### **12.1** Bronze Layer (RAW):

* Unprocessed
* Stored as uploaded

### **12.2** Silver Layer (Cleaned):

* Cleaned
* Filtered
* Normalized
* Format-converted

### **12.3** Gold Layer (Aggregated):

* Aggregations
* Business metrics
* Analytics-ready

This is EXACTLY how Azure Data Engineers build modern data pipelines.

---

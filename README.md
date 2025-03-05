# Large File Processing API with FastAPI, PostgreSQL & RabbitMQ

## 📌 Overview
This project efficiently processes large `.csv` files using **FastAPI**, **PostgreSQL**, **RabbitMQ**, and **Pandas** for high-performance data ingestion and retrieval.

---

## 🛠️ Installation Guide

### ** Prerequisites**
Ensure you have the following installed:
- Python 3.x
- PostgreSQL
- RabbitMQ
- Git

---

### ** 1. Clone the Repository**
```bash
git clone https://github.com/sparate/assignment_1.git
cd assignment_1
```

---

### ** 2. Set Up Environment Variables**
Create a `.env` file:
```bash
cp .env.sanjay .env
nano .env
```
Modify the values accordingly:
```env
AWS_REGION=us-east-1
AWS_SECRET_NAME=my_database_secret
RABBITMQ_HOST=localhost
QUEUE_NAME=file_queue
```

---

### ** 3. Run the Installation Script**
The `install.sh` script is already provided in the repository. Run:
```bash
chmod +x install.sh
./install.sh
```
This will:
- Install dependencies
- Set up the PostgreSQL database
- Start RabbitMQ

---

### ** 4. Start the FastAPI Server**
Run the FastAPI server using Uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

### ** 5. Start the RabbitMQ Consumer**
Run the consumer script to process messages:
```bash
python3 consumer.py
```

---

## 📂 Database Setup  
The `schema.sql` file is already provided in the repository. If needed, manually set up the database using:
```bash
psql -U my_user -d my_database -f schema.sql
```

---

## 🌐 API Endpoints  
| **Method** | **Endpoint** | **Description** |
|-----------|-------------|-----------------|
| `GET` | `/data?page_no=1&pagesize=10&name=John` | Fetch paginated user data |

---

## 📡 Processing Large CSV Files  
To process large `.csv` files, run:  
```bash
python3 main.py --file data.csv
```

---

## 🚀 Deployment  
Run the server and consumer in the background:  
```bash
nohup uvicorn main:app --host 0.0.0.0 --port 8000 &  
nohup python3 consumer.py &
```

---

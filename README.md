# Large File Processing API with FastAPI, PostgreSQL & RabbitMQ

##  Overview
This project efficiently processes large `.csv` files using **FastAPI**, **PostgreSQL**, **RabbitMQ**, and **Pandas**.

## 🛠️ Installation Guide

### ** Prerequisites**
Ensure you have the following installed:
- Python 3.x
- PostgreSQL
- RabbitMQ
- Git

### ** 1. Clone the Repository**
```bash```
git clone https://github.com/sparate/assignment_1.git

### ** 2. Set Up Environment Variables
Create a .env file:
cp .env.example .env
nano .env

Modify the values accordingly:

AWS_REGION=us-east-1
AWS_SECRET_NAME=my_database_secret
RABBITMQ_HOST=localhost
QUEUE_NAME=file_queue

### ** 3. Run the Installation Script
chmod +x install.sh
./install.sh
This will Install dependencies
 - Set up PostgreSQL database
 - Start RabbitMQ

### ** 4. Start the FastAPI Server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

### ** 5. Start the RabbitMQ Consumer
python3 consumer.py

### * Database Setup
The schema.sql file defines the database structure.

Manual Setup (if needed)
psql -U my_user -d my_database -f schema.sql


### * API Endpoints:
Method	: GET  	                            
Endpoint	: /data?page_no=1&pagesize=10&name=John	
Description : Fetch paginated user data


Processing Large CSV Files
To process large CSV files:
python3 main.py --file data.csv


### * Deployment
Run in the background:

nohup uvicorn main:app --host 0.0.0.0 --port 8000 &
nohup python3 consumer.py &




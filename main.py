import os
import json
import boto3
import pika
import psycopg2
import pandas as pd
from psycopg2 import pool, extras
from contextlib import closing
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
SECRET_NAME = os.getenv("AWS_SECRET_NAME", "my_database_secret")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
QUEUE_NAME = os.getenv("QUEUE_NAME", "file_queue")
FILE_BATCH_SIZE = 5000  # Increased batch size for efficiency

# Gender allowed values
VALID_GENDERS = {"MALE", "FEMALE", "OTHER"}


def get_secret():
    """Retrieve database credentials securely from AWS Secrets Manager."""
    try:
        client = boto3.client("secretsmanager", region_name=AWS_REGION)
        response = client.get_secret_value(SecretId=SECRET_NAME)
        return json.loads(response["SecretString"])
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        return {}


# Fetch secrets securely
secrets = get_secret()
DB_CREDENTIALS = {
    "host": secrets.get("host", "localhost"),
    "dbname": secrets.get("dbname", "your_db"),
    "user": secrets.get("username", "your_user"),
    "password": secrets.get("password", "your_password"),
}

# Initialize database connection pool
try:
    db_pool = psycopg2.pool.SimpleConnectionPool(1, 20, **DB_CREDENTIALS)
except Exception as e:
    raise RuntimeError(f"Database connection pool initialization failed: {e}")

app = FastAPI()


class Data(BaseModel):
    """Data validation for input records."""

    name: str = Field(..., max_length=255)
    email: str = Field(..., max_length=320)
    mobile: str = Field(..., max_length=15)
    gender: str
    age: int = Field(..., ge=0, le=120)
    designation: str = Field(..., max_length=255)
    city: str = Field(..., max_length=50)
    pin: str = Field(..., regex="^[0-9]{6}$")  # Enforce exactly 6-digit PIN
    fav_food: str = Field(..., max_length=100)
    fav_movie: str

    @validator("gender")
    def validate_gender(cls, value):
        """Ensure gender is one of the allowed values."""
        if value.upper() not in VALID_GENDERS:
            raise ValueError("Gender must be MALE, FEMALE, or OTHER")
        return value.upper()


def get_db_connection():
    """Get a database connection from the pool."""
    try:
        return db_pool.getconn()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {e}")


def release_db_connection(conn):
    """Release a database connection back to the pool."""
    db_pool.putconn(conn)


def store_data_in_db(data_batch):
    """Bulk insert data into PostgreSQL for efficiency."""
    if not data_batch:
        return
    conn = get_db_connection()
    try:
        with closing(conn.cursor()) as cursor:
            insert_query = """
                INSERT INTO users (name, email, mobile, gender, age, designation, city, pin, fav_food, fav_movie)
                VALUES %s
            """
            extras.execute_values(cursor, insert_query, data_batch)
            conn.commit()
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        release_db_connection(conn)


def callback(ch, method, properties, body):
    """RabbitMQ consumer callback function with batch processing."""
    try:
        data_batch = json.loads(body.decode())
        store_data_in_db(data_batch)
    except Exception as e:
        print(f"Message Processing Error: {e}")


def start_consumer():
    """Start consuming messages from RabbitMQ with better error handling."""
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME)
        channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
        print("Waiting for messages...")
        channel.start_consuming()
    except Exception as e:
        print(f"RabbitMQ Consumer Error: {e}")


def publish_file_data(file_path: str):
    """Efficiently read and publish file data in bulk to RabbitMQ."""
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME)

        for chunk in pd.read_csv(file_path, chunksize=FILE_BATCH_SIZE, dtype=str):
            batch = chunk.to_dict(orient="records")  # Convert DataFrame to list of dictionaries
            channel.basic_publish(
                exchange="", routing_key=QUEUE_NAME, body=json.dumps(batch)
            )
            print(f"Published {len(batch)} records")

        connection.close()
    except Exception as e:
        print(f"File publishing error: {e}")


@app.get("/data")
def get_data(page_no: int = Query(1, ge=1), pagesize: int = Query(10, gt=0), name: str = None):
    """Fetch data securely with pagination and optional filtering."""
    offset = (page_no - 1) * pagesize
    conn = get_db_connection()
    try:
        with closing(conn.cursor()) as cursor:
            query = "SELECT * FROM users"
            params = []
            if name:
                query += " WHERE name ILIKE %s"
                params.append(f"%{name}%")
            query += " LIMIT %s OFFSET %s"
            params.extend([pagesize, offset])

            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return {"data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {e}")
    finally:
        release_db_connection(conn)

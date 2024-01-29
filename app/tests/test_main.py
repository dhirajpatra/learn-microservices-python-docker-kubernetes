# app/tests/test_main.py
import json
import sys
import os
from telnetlib import STATUS
from urllib import response
from dotenv import load_dotenv
sys.path.append('../app')

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from main import app

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Define the base class for SQLAlchemy models
Base = declarative_base()

# Use a different test database URL
DB_URI = os.getenv('DB_URI')

# Use the original engine and sessionmaker with CREATE DATABASE handled
engine = create_engine(DB_URI, pool_pre_ping=True)  # Added pool_pre_ping for health check
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the test database if it does not exist
Base.metadata.create_all(bind=engine)

# Define a fixture for the test client with module scope
@pytest.fixture(scope="module")
def test_client():
    return TestClient(app)

# Define a fixture for the database session with function scope
@pytest.fixture(scope="function")
def db_session(request):
    # Create an instance of the TestingSessionLocal class
    db = TestingSessionLocal()

    # Return the database session instance
    return db

# Test case: Ensure the main endpoint returns a valid response
def test_read_main(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World, health check"}

# Test case: Ensure file upload endpoint works correctly
def test_upload_file(test_client, db_session):
    response = test_client.post("/products/upload", files={"file": ("test.csv")})
    assert response.status_code == 201
    assert response.json() == {"message": "File uploaded successfully"}

# Test case: Ensure the products endpoint returns a valid response
def test_read_products(test_client, db_session):
    response = test_client.get("/products")
    assert response.status_code == 200
    assert len(response.json()) >= 0
    
# graphql based test
def test_query(test_client, db_session):
    query = '''
    {
        products(skip: 0, limit: 10) {
            id
            partNumber
            branchId
        }
    }
    '''
    response = test_client.post('/graphql', json={'query': query})
    assert response.status_code == 200
    assert 'data' in response.json()


# Microservices CSV Processing with Docker, FastAPI, Celery, PgSql, GraphQL, Rabbitmq, Redis

This a representation level template application to show how can we use microservices application using non blocking architecture.

## Problem Overview

A new branch of a company needs to import product data from a CSV file into the database. Each line in the CSV file represents a steel product with specific attributes. The goal is to create an endpoint that allows users to upload the CSV file, and the application should update existing products or add new products to the database. The CSV file has the following columns:

PART_NUMBER: Identifier for a product.
BRANCH_ID: Short code of a Kloeckber branch that produces the product (e.g., TUC - Tucson, CIN - Cincinnati).
PART_PRICE: Price of the product in USD.
SHORT_DESC: Short description text about the product.

### Requirements

Users should be able to upload the CSV file multiple times, and each upload should update corresponding products.
The uploaded data should be shown in a list.

Bonus Feature (Optional): Products that are not present in the uploaded CSV should be deleted from the database.

Implementation:
The application uses FastAPI for creating the API endpoint (/upload) to handle file uploads.
SQLAlchemy is used for database interactions, and Alembic is used for database migrations.
The database model (Product) represents the products with relevant attributes.
The upload_file endpoint reads the uploaded CSV file, updates existing products, and adds new products to the database.

### How to Run

1. Ensure you have Docker installed on your machine.

[https://docs.docker.com/images/get-started/overview.png](https://docs.docker.com/get-started/overview/)

Clone the repository and rename env.example to .env

2. Build the Docker image:

   `docker-compose build`
   `docker-compose up`

   Wait for few minute [firest time]/seconds to see like following output in terminal to know all services are ready.

   ```
   celery    | [2024-01-17 04:38:27,604: INFO/MainProcess] mingle: all alone
   celery    | [2024-01-17 04:38:27,647: INFO/MainProcess] celery@f68fa4112c22 ready.
   ```

3. Access the POST API at <http://127.0.0.1:8000/upload> to upload the CSV file can upload from postman.

curl --location '<http://127.0.0.1:8000/upload>' \
--form 'file=@"/senior-python-ai-integration-mjxfji/data/data.csv"'

Also can check the GET API at <http://127.0.0.1:8000/products> to check the products already uploaded.

4. To check the container eg. db

`docker exec -it db bash`
`psql -U admin -d myapp -c '\dt'`
or
`psql -h localhost -U admin -d myapp`
`select * from products;`

```
myapp=# select * from products;
 id |   part_number   | branch_id | part_price |                       short_desc
----+-----------------+-----------+------------+--------------------------------------------------------
  1 | 0121F00548      | TUC       |       3.14 | GALV x FAB x 0121F00548 x 16093 x .026 x 29.88 x 17.56
  2 | 0121G00047P     | TUC       |       42.5 | GALV x FAB x .026 x 29.88 x 17.56
  3 | 0121G00509      | CIN       |       3.14 | GALV x FAB x 0121F00548 x 16093 x .026 x 29.88 x 17.56
  4 | 0163D00006-T006 | CIN       |       3.14 | GALV x FAB x 0121F00548
  5 | 0163D00007      | CIN       |       3.14 | GALV x FAB x 0121F00548
  6 | 05700-001-16-88 | TUC       |       3.14 | GALV x FAB x 0121F00548
  7 | 05700-002-11-15 | TUC       |       3.14 | GALV x FAB x 0121F00548
  8 | 102430          | TUC       |       3.14 | GALV x FAB x 0121F00548
  9 | 0163D00007      | CIN       |       4.27 | GALV x FAB x 0121F00548
(9 rows)
```

`\d products`

```
myapp=# \d products;
                                      Table "public.products"
   Column    |          Type          | Collation | Nullable |               Default
-------------+------------------------+-----------+----------+--------------------------------------
 id          | integer                |           | not null | nextval('products_id_seq'::regclass)
 part_number | character varying(100) |           | not null |
 branch_id   | character varying(100) |           |          |
 part_price  | double precision       |           | not null |
 short_desc  | character varying(255) |           |          |
Indexes:
    "products_pkey" PRIMARY KEY, btree (id)
    "ix_products_id" btree (id)
```

\products API will return

```
[
    {
        "part_number": "0121F00548",
        "part_price": 3.14,
        "branch_id": "TUC",
        "id": 1,
        "short_desc": "GALV x FAB x 0121F00548 x 16093 x .026 x 29.88 x 17.56"
    },
    {
        "part_number": "0121G00047P",
        "part_price": 42.5,
        "branch_id": "TUC",
        "id": 2,
        "short_desc": "GALV x FAB x .026 x 29.88 x 17.56"
    },
    {
        "part_number": "0121G00509",
        "part_price": 3.14,
        "branch_id": "CIN",
        "id": 3,
        "short_desc": "GALV x FAB x 0121F00548 x 16093 x .026 x 29.88 x 17.56"
    },
    {
        "part_number": "0163D00006-T006",
        "part_price": 3.14,
        "branch_id": "CIN",
        "id": 4,
        "short_desc": "GALV x FAB x 0121F00548"
    },
    {
        "part_number": "0163D00007",
        "part_price": 3.14,
        "branch_id": "CIN",
        "id": 5,
        "short_desc": "GALV x FAB x 0121F00548"
    }
    .
    .
    .
]
```

5. Bonus Feature:

The bonus feature, if enabled, deletes products from the database that are not present in the uploaded CSV file. This ensures that the database only contains products from the latest CSV upload.

Now, with Docker, you can run your FastAPI application inside a container, making it easy to manage dependencies and isolate the environment.

### Testing

To run tests inside a Docker container, you can follow these steps:

1. Access the Docker Container:

After starting the Docker container using docker-compose up, open a new terminal window.

2. Run Tests Inside the Container:

Execute the following command to run tests inside the Docker container:
`docker-compose run web python -m pytest tests/`

### Future Improvement

There are many we can, from putting all into .env or more secure place. Also make full Alembic version wise update the DB. Make celery code repo seperate, write more testes, proper logging system, elasticache for serching. More optimize Dockerfile for both web and celery.

### To check if Celery is saving results to the Redis container, you can perform the following steps

1. Access the Redis Container:**

   ```
   docker exec -it redis bash
   ```

2. Open the Redis CLI:**

   ```
   redis-cli
   ```

3. Check for Result Keys:**

   ```
   keys *
   ```

   This command will show you all the keys present in the Redis database. If Celery is saving results to Redis, you should see some keys related to task results.
4. Inspect a Result Key:**
   If you find a key that seems related to Celery results, you can inspect its value:

   ```
   get <your-result-key>
   ```

   Replace `<your-result-key>` with the actual key you want to inspect.

### GraphQl

http://localhost:8000/graphql

Then write the query to get the result
```
{
    products {
        id
        partNumber
        branchId
    }
}
```
reponse
```
{
  "data": {
    "products": [
      {
        "id": 9,
        "partNumber": "0163D00007",
        "branchId": "CIN"
      },
      {
        "id": 1,
        "partNumber": "0121F00548",
        "branchId": "TUC"
      },
      {
        "id": 2,
        "partNumber": "0121G00047P",
        "branchId": "TUC"
      },
      .
      .
      .
  }
}

or you can call for specific product

{
    products(partNumber: "0121F00548", branchId: "TUC") {
        id
        partNumber
        branchId
    }
}

```

### Folder and File Tree

```
.
├── README.md
├── app
│   ├── Dockerfile.celery
│   ├── Dockerfile.web
│   ├── __init__.py
│   ├── __pycache__
│   │   └── models.cpython-311.pyc
│   ├── alembic
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions
│   ├── alembic.ini
│   ├── celery_config.py
│   ├── celery_tasks
│   ├── celery_tasks.py
│   ├── crud.py
│   ├── database.py
│   ├── entrypoint.sh
│   ├── main.py
│   ├── models.py
│   ├── product.py
│   ├── requirements.txt
│   ├── schemas.py
│   └── tests
│       ├── test.csv
│       └── test_main.py
├── data
│   └── data.csv
├── docker-compose.yml
└── init-db.sql
```

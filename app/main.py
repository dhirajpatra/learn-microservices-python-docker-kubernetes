import logging
from logging.handlers import TimedRotatingFileHandler

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette_graphene3 import GraphQLApp, make_graphiql_handler
from elasticsearch import Elasticsearch

from database import Base, engine
import product

# Configure logging with a rotating file handler
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
handler = TimedRotatingFileHandler('web.log', when='midnight', interval=1, backupCount=5, encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# FastAPI app
app = FastAPI()

# Elasticsearch
es = Elasticsearch(hosts=["http://elasticsearch:9200"])

# Create "products" index
index_name = "products"

# Create database tables
Base.metadata.create_all(bind=engine)

# CORS setup
origins = [
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust based on your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include product router
app.include_router(product.router)

# Add GraphQL route using add_route method
app.add_route("/graphql", GraphQLApp(
    schema=product.Schema(query=product.Query),
    on_get=make_graphiql_handler()
))

# Health check endpoint
@app.get("/")
async def live():
    try:
        return {"message": "Hello World, health check"}
    except Exception as e:
        logger.error("Error processing live check: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Elasticsearch check endpoint
@app.get("/search")
async def search():
    try:
        return {"message": "Elasticsearch activated"}
    except Exception as e:
        logger.error("Error processing Elasticsearch check: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

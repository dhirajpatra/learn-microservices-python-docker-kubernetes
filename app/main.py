# main.py
import product
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
# from alembic.env import run_migrations_online
import logging
from logging.handlers import TimedRotatingFileHandler
from starlette_graphene3 import GraphQLApp, make_graphiql_handler


# Configure logging with a rotating file handler
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
handler = TimedRotatingFileHandler('web.log', when='midnight', interval=1, backupCount=5, encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

app = FastAPI()

Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(product.router)

# Add GraphQL route using add_route method
app.add_route("/graphql", GraphQLApp(
    schema=product.Schema(query=product.Query), 
    on_get=make_graphiql_handler()
)) 

@app.get("/")
async def live():
    try:
        return {"message": "Hello World, health check"}
    except Exception as e:
        logger.error("Error processing live check: %s", str(e)) 
        raise HTTPException(status_code=500, detail=str(e))

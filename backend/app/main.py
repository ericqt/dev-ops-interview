from typing import Union
# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
import os 

from fastapi import FastAPI
from bs4 import BeautifulSoup


app = FastAPI()


# DATABASE_URL = "postgres://postgres:postgres@" + os.environ['DB_HOST'] + "/" + os.environ['DB_NAME']

# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
from typing import Union
import sqlalchemy as db
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
import os 
from fastapi import FastAPI, File, UploadFile
from bs4 import BeautifulSoup
from bs4.element import Comment
import re
from sqlalchemy.dialects.mysql import LONGTEXT, TIMESTAMP, INTEGER
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pinecone import Pinecone
from pydantic import BaseModel


### Constants 
PINECONE_NAME_SPACE="search"
# Chunking hyperparameters 
OVERLAP= 10
CHUNKSIZE = 80
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@" + os.environ['DB_HOST'] + ":5432" + "/" + os.environ['DB_NAME']

### Singltons 
pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])
index = pc.Index("hebbia-search")
app = FastAPI()
engine = db.create_engine(DATABASE_URL)
connection = engine.connect()
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()
metadata = db.MetaData()
# TODO: lazy load if possible or download model dur
model = SentenceTransformer('sentence-transformers/msmarco-MiniLM-L-6-v3')


# TODO Move to models dir 
class Chunks(Base):
    __tablename__ = 'chunks'
    id = db.Column('id', INTEGER(display_width=11), primary_key=True, nullable=False, autoincrement=True)
    content = db.Column('content', LONGTEXT)
    created_at = db.Column('created_at', TIMESTAMP, nullable=False, server_default=func.now())
    __table_args__ = {'schema': 'core'}


# TODO: MOVE TO UTIL LATER
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)

def chunks_from_html(doc_body):
    raw_text = text_from_html(doc_body)
    # replace white space with space char
    raw_text  = re.sub(r"\s+", ' ', raw_text)

    words = raw_text.split(" ")

    chunks = [" ".join(words[chunkStart -OVERLAP: chunkStart + OVERLAP + CHUNKSIZE]) for chunkStart in range(OVERLAP, len(words), CHUNKSIZE)]
    return chunks

def get_chunk_embeddings(chunks):
    embeddings = model.encode(chunks)

    print("finished embeddings", len(embeddings), len(embeddings[0]))
    return embeddings

def write(chunks, embeddings):
    vectors = []
    for idx in range(len(chunks)):
        content = chunks[idx].replace("’", "'").replace("'", "\'").replace("\\", "\\\\")
        print(content)
        newChunkRow = Chunks(content = content)
        session.add(newChunkRow)
        session.commit()
        print(newChunkRow.id)
        vectors.append({"id": str(newChunkRow.id), "values": embeddings[idx], "metadata": {}})
    
    print(vectors)
    index.upsert(vectors,namespace= PINECONE_NAME_SPACE)
    

@app.get("/")
def read_root():
    
    return "Hello world :)"

@app.post("/upload")
def upload(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        chunks = chunks_from_html(contents)
        embeddings = get_chunk_embeddings(chunks)
        write(chunks, embeddings)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded {file.filename}"}

class SearchQuery(BaseModel):
   search_term: str 

@app.post("/search")
def read_item(query: SearchQuery):

    search_vector = get_chunk_embeddings([query.search_term])
    search_results  = index.query(
        namespace=PINECONE_NAME_SPACE,
        vector=search_vector[0].tolist(),
        top_k=2,
        include_values=False,
        include_metadata=True,
    )    
    matchIds = [int(match["id"]) for match in search_results["matches"]]
    matchChunks = session.query(Chunks).filter(Chunks.id.in_(matchIds)).all()

    return matchChunks
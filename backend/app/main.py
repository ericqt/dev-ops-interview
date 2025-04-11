from typing import Optional
import sqlalchemy as db
import os 
from fastapi import FastAPI, File, UploadFile
from bs4 import BeautifulSoup
from bs4.element import Comment
import re
from sqlalchemy.dialects.mysql import LONGTEXT, TEXT, TIMESTAMP, INTEGER
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pinecone import Pinecone
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


### Constants 
PINECONE_NAME_SPACE="searchV2"
# Chunking hyperparameters 
OVERLAP= 10
CHUNKSIZE = 80
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@" + os.environ['DB_HOST'] + ":5432" + "/" + os.environ['DB_NAME']

### Singltons 
pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])
index = pc.Index("corpus-search")
app = FastAPI()
engine = db.create_engine(DATABASE_URL)
connection = engine.connect()
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()
metadata = db.MetaData()
# TODO: lazy load if possible or download model dur
model = SentenceTransformer('sentence-transformers/msmarco-MiniLM-L-6-v3')

# CORS policy 
origins = [
    "http://localhost",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Chunks(Base):
    __tablename__ = 'chunks'
    __table_args__ = {'schema': 'core'}
    id = db.Column('id', INTEGER(display_width=11), primary_key=True, nullable=False, autoincrement=True)
    content = db.Column('content', LONGTEXT, nullable=False)
    company_name = db.Column('company_name', TEXT, nullable=True)
    created_at = db.Column('created_at', TIMESTAMP, nullable=False, server_default=func.now())


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

def write(filename, chunks, embeddings):
    # extract company name from filename
    company_name = filename[0:filename.find(" |")]
    print(company_name)
    vectors = []
    for idx in range(len(chunks)):
        content = chunks[idx].replace("’", "'").replace("'", "\'").replace("\\", "\\\\")
        newChunkRow = Chunks(content = content, company_name=company_name)
        session.add(newChunkRow)
        session.commit()
        vectors.append({"id": str(newChunkRow.id), "values": embeddings[idx], "metadata": { "company_name": company_name }})
    index.upsert(vectors,namespace= PINECONE_NAME_SPACE)
    

@app.get("/")
def read_root():
    return "Hello world :)"

@app.post("/upload")
def upload(file: UploadFile = File(...)):
    try:
        filename=file.filename
        contents = file.file.read()
        print(file.filename)
        chunks = chunks_from_html(contents)
        embeddings = get_chunk_embeddings(chunks)
        write(filename, chunks, embeddings)
    except Exception:
        import ipdb; ipdb.set_trace()
        print(f'the exception being thrown: {Exception}')
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    return { "message": f"Successfully uploaded {file.filename}" }

class SearchQuery(BaseModel):
   search_term: str 
   company_filter: Optional[str]
   limit: Optional[int] = 5

@app.post("/search")
def read_item(query: SearchQuery):
    print(query.search_term, query.company_filter)
    search_vector = get_chunk_embeddings([query.search_term])
    filter = None

    # TODO: select valid company filter from list of company tags 
    if query.company_filter is not None and len(query.company_filter) > 0:
        filter = {"company_name": query.company_filter } 
    
    search_results  = index.query(
        namespace=PINECONE_NAME_SPACE,
        vector=search_vector[0].tolist(),
        top_k=query.limit,
        include_values=False,
        include_metadata=True,
        filter=filter,
    )    
    
    matchIds = [int(match["id"]) for match in search_results["matches"]]
    matchChunks = session.query(Chunks).filter(Chunks.id.in_(matchIds)).all()

    if len(matchChunks) == 0:
        return "No results found"
    else:
        return matchChunks

@app.get('/companies')
def get_companies():
    print("Runing get_companies")
    companies = session.query(Chunks.company_name).distinct().all()
    response = [str(comp[0]) for comp in companies]
    return { 'companies': tuple(response)}

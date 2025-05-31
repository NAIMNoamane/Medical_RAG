from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http.models import PointStruct
from uuid import uuid4
from dotenv import load_dotenv

import StoringParentArticles
import re 
import json
import os 



load_dotenv()
collection_name = "Gale_Chunks"
# For inserting Artcile with  its unique ID 
parent_ids = {}
qdrant_api_key = os.getenv("QDRANT_API_KEY")

# Establish connection to Qdrant cloud 
qdrant_client = QdrantClient(
    url="https://995828ea-aab5-412e-9766-dd32680878b2.europe-west3-0.gcp.cloud.qdrant.io:6333",
    api_key=qdrant_api_key,
    check_compatibility=False,
    timeout=180
)
# Run only for one time 
qdrant_client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=768, distance=Distance.COSINE)  # BioBERT = 768
)

# Tools for Chunking and Embbeding
text_splitter = RecursiveCharacterTextSplitter(chunk_size=150,chunk_overlap= 50)
embedding_model = HuggingFaceEmbeddings(model_name="pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb")


#============== Function to Clean the Articles =======================
def CleanArticle(article):
    # Remove GALE/scan artifacts
    cleaned_article = re.sub(r"GALE ENCYCLOPEDIA OF MEDICINE.*?Page \d+", "", article)
    cleaned_article = re.sub(r"GEM\s*-\s*\d+\s*to\s*\d+\s*-\s*[A-Z]?", "", cleaned_article)
    cleaned_article = re.sub(r"Page \d+", "", cleaned_article)
    #Fix line breaks inside paragraphs
    cleaned_article = re.sub(r"(?<!\n)(?<!\n\n)\n(?![\n•A-Z])", " ", cleaned_article )
    #Normalize multiple newlines
    cleaned_article = re.sub(r"\n{2,}", "\n\n", cleaned_article)
    #Strip excessive whitespace
    cleaned_article = re.sub(r"[ \t]+", " ", cleaned_article).strip()
    cleaned_article = re.sub(r"(?:\n)?Resources\s*\n(?:.*\n)*", " ", cleaned_article, flags=re.IGNORECASE)
    #Ensure section headers are separated clearly
    cleaned_article = re.sub(r"\n([A-Z][a-z]+(?: [A-Z][a-z]+)*):?\n", r"\n\n\1\n\n", cleaned_article)

    return cleaned_article

#============== Function for Chunking the Articles =======================


def ParentChildChunking(cleaned_article,article_title):
    points = []
    chunks_doc = []
    parent_id = str(uuid4())
    parent_ids[parent_id] = cleaned_article
    # Chunk the article 
    chunks = text_splitter.create_documents(
        [cleaned_article],
        metadatas=[{
            "title":article_title,
            "parent_id": parent_id}]
    )
    chunks_doc.extend(chunks)
    # embedd the vectors 
    vectors = embedding_model.embed_documents([c.page_content for c in chunks_doc])
    # Create Point for Qdrant injection 
    for index, doc in enumerate(chunks_doc):
        point = PointStruct(
            id=str(uuid4()),
            vector=vectors[index],
            payload={
                **doc.metadata
            }
        )
        points.append(point)
    return points

#============== Function for Chunking the Articles =======================

def PointInjection(Points:list,Qdrant_client):
    Qdrant_client.upload_points(
        collection_name =collection_name,
        points=Points
    )


#============== Main Function =======================

def Main(Books:list):
    # Fetch books 
    for book in Books:
        with open(book,"r",encoding="utf-8") as f :
            # Load book content
            content = json.load(f)
            # Fetch article's book 
            for i in range(len(content)):
                # Get Article and Article title 
                article_title = content[i]["title"]
                article = content[i]["content"]
                # Clean the article 
                cleaned_article = CleanArticle(article)
                # Create Qdrant points from child chunks 
                article_points = ParentChildChunking(cleaned_article,article_title)
                # Inject child points in Qdrant DB 
                PointInjection(article_points,qdrant_client)
        print(f"The {book} has been chunked, embedded and stored in Qdrant DB")

if __name__ == '__main__':
    Books = [f"gale_articles_Vol_{i}.json" for i in range(1,6)]
    Main(Books)
    # Load Parent Documents to Google Cloud Storage
    for id, article in parent_ids.items():
        StoringParentArticles.uploadParentDoc(parent_id=id,parent_article=article)

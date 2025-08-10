from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from functools import partial
from google.cloud import storage
from dotenv import load_dotenv
import functions as fn 
import os 




def main(question,prompt_rag_fusion,llm,qdrant_client,gcs_client,embedding_model,text_splitter):

    # Create partial functions for handling extra arguments 
    embed_queries_partial = partial(fn.embed_queries,embedding_model=embedding_model)
    search_qdrant_for_queries = partial(fn.search_qdrant_for_queries,qdrant_client=qdrant_client)
    parent_document_partial = partial(fn.donwloadParents,GCS_client=gcs_client)
    response_generator = partial(fn.Responder,question=question,Text_Splitter=text_splitter,LLM=llm)

    #Define the chain 
    chain=(
        prompt_rag_fusion
        |llm
        |StrOutputParser()
        |(lambda x: x.split("\n"))
        |fn.get_queries
        |embed_queries_partial
        |search_qdrant_for_queries
        |fn.reciprocal_rank_fusion
        |parent_document_partial
        |response_generator
    )
    output = chain.invoke({"question":question})
    return output

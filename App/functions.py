from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from qdrant_client import QdrantClient
from langchain.load import dumps, loads
from google.cloud import storage 
from multiprocessing.dummy import Process, Queue









# =====================================

# function to get  multiple queries 
def get_queries(output_multi_query):
  queries = [
        line.strip("12345:.- ").strip()
        for line in output_multi_query[-5:]
        if line.strip()
    ]
  return queries

# function to embedd queries 
def embed_queries(queries,embedding_model):
  embed_queries = [embedding_model.embed_query(query) for query in queries]
  return embed_queries
# function to search for similar queries 
def search_qdrant_for_queries(embed_queries,qdrant_client):
    results=[]
    for embedded in embed_queries:
      hits = qdrant_client.query_points(
          collection_name="gale_books",
          query=embedded,
          limit=3,
      ).points
      result_per_query = [hit.payload['parent_id'] for hit in hits]
      results.append(result_per_query)
    return results


# function for reciprocal rank fusion
def reciprocal_rank_fusion(results: list[list], k=60):
    """ Reciprocal_rank_fusion that takes multiple lists of ranked documents 
        and an optional parameter k used in the RRF formula """
    
    # Initialize a dictionary to hold fused scores for each unique  child IDs
    fused_scores = {}

    # Iterate through each list of ranked child IDs 
    for IDS in results:
        # Iterate through each document in the list, with its rank (position in the list)
        for rank, id in enumerate(IDS):
            # If the document is not yet in the fused_scores dictionary, add it with an initial score of 0
            if id not in fused_scores:
                fused_scores[id] = 0
            # Retrieve the current score of the document, if any
            previous_score = fused_scores[id]
            # Update the score of the document using the RRF formula: 1 / (rank + k)
            fused_scores[id] += 1 / (rank + k)

    # Sort the documents based on their fused scores in descending order to get the final reranked results
    reranked_results = [
        (id, score)
        for id, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    ]
    # Get the 4 most similar child documents
    if len(reranked_results) > 3:
      reranked_results = reranked_results[:3]
    return reranked_results

# function to fetch Parent document 
def donwloadParents(reranked_results,GCS_client):
  Parent_articles = []
  for result in reranked_results:
    parent_id = result[0]
    bucket = GCS_client.get_bucket('gale-parent-docs')
    blob = bucket.blob(f"{parent_id}.json")
    article = blob.download_as_string().decode()
    article = dict(eval(article))
    Parent_articles.append(article["content"])
  return Parent_articles
 
# function to chunk articles 
def chunk_doc(articles,Text_Splitter):
  chunks_docs = []
  for article in articles:
    chunk_docs = Text_Splitter.split_text(article)
    chunks_docs.append(chunk_docs)
  return chunks_docs

# Define function to chunk Parent Article
def chunker(articles, chunk_queue,Text_Splitter, batch_size):
      for article in articles:
          chunks = Text_Splitter.split_text(article)
          batch = []
          for chunk in chunks:
              batch.append(chunk)
              if len(batch) == batch_size:
                  chunk_queue.put(batch)
                  batch = []
          
          if batch:  
              chunk_queue.put(batch)

          chunk_queue.put(None)    
        

# Define function for inference
def inferer(chunk_queue, question,LLM, result_queue):
      from langchain.prompts import ChatPromptTemplate

      template_2 = """Add this knowledge:{context} and this one also : {previous_answer} to your knowledge and Answer the question: {question}"""
      prompt_2 = ChatPromptTemplate.from_template(template_2)
      chain_2 = (prompt_2
                |LLM)
      response = None
      while True:
          batch = chunk_queue.get()
          if batch is None:
              break

          context = "\n\n".join(batch)
          response = chain_2.invoke({
              "context": context,
              "question": question,
              "previous_answer": response
          })
      
      result_queue.put(response)
      result_queue.put(None)

      
def Responder(articles, question,Text_Splitter,LLM):

    chunk_queue = Queue()
    result_queue = Queue()
  # Define Processes 
    p1 = Process(target=chunker, args=(articles, chunk_queue,Text_Splitter, 2))
    p2 = Process(target=inferer, args=(chunk_queue, question,LLM, result_queue))

    p1.start()
    p2.start()
    p1.join()
    p2.join()

    results = []
    while True:
        result = result_queue.get()
        if result is None:
            break
        results.append(result)

    return results[0].content

<h1 align="center"> Medic🩺🩺 </h1>
<p align="center"> 
  <b>AI conversational platform powered by RAG system </b></p>
<p align="center">
  
  ![redis](https://img.shields.io/badge/redis-6.2.0-red)
  ![pymongo](https://img.shields.io/badge/pymongo-3.12.0-blue)
  ![dotenv](https://img.shields.io/badge/dotenv-0.9.9-green)
  ![langchain](https://img.shields.io/badge/langchain-0.3.25-yellow)
  ![qdrant--client](https://img.shields.io/badge/qdrant--client-1.14.2-orange)
  ![google--cloud](https://img.shields.io/badge/google--cloud-0.34.0-lightgrey)
  ![chainlit](https://img.shields.io/badge/chainlit-2.5.5-purple)
  ![logging](https://img.shields.io/badge/logging-0.4.9.6-brightgreen) </p>

---
This AI platform is powered by a Medical RAG system where its knowledge comes from The Gale Encyclopedia of Medecine. It uses the <b>Chainlit</b> framework for building the platform and get the response from the medical RAG system.

## **Medical RAG**
The RAG system inspires from Gale Encyclopedias for Medecine, books of many articles about diseases where each article talk about a specific disease, specific definition,symptoms.,ect...
### Techniques used 
 - ParentChild Chunking for better Indexing and context improvement.
 - Reciprocal Rank Fusion (RRF) to retrieve precisely information.
### Workflow

---

#### 1. **User Query**
The user asks a question or provides a prompt.

---

#### 2. **Query Multiplication**
Using **deepseek-r1-distill-llama-70b** to generate multiple queries from the user query while keeping the same meaning.

---

#### 3. **Query Embedding**
Each query is converted into a **768 vector representation** using **BioBERT-mnli-snli**.

---

#### 4. **Vector Search**
The vector is matched against a ** Qdrant vector database** to find the **most relevant documents** from the knowledge base.
- Uses **cosine similarity** for searching similarity .
- Uses **RRF** for rankings.
- Retrieves *top 3* Parent documents of the *top 3* relevant child documents.

---

#### 5. **Context Assembly**
The retrieved documents are **merged** into a context block

---

#### 6. **Generation**
The query **+ retrieved context** are passed to the **deepseek-r1-distill-llama-70b**

---

## **AI Platform**
- The platform is created using *chainlit* framework.
- Uses Token-based Authentication.

**Only educational uses are permitted. Feel free to us it**





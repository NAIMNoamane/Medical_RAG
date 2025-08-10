import chainlit as cl
import asyncio
import os
from typing import Optional
from fastapi import Request, Response
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import main as mn
import dbController
import re

# ---- Heavy tools loading functions ----
@cl.cache
def load_llm():
    load_dotenv()
    groq_api_key = os.getenv("GROQ_API_KEY")
    llm = ChatOpenAI(
        model_name="deepseek-r1-distill-llama-70b",
        temperature=0.4,
        openai_api_base="https://api.groq.com/openai/v1",
        openai_api_key=groq_api_key,                                 
    )
    return llm

@cl.cache
def load_embedd_model():
    embedding_model = HuggingFaceEmbeddings(
        model_name="pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb"
    )
    return embedding_model

@cl.cache
def load_splitter():
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=10000, chunk_overlap=2000
    )
    return text_splitter

async def load_tools():
    async def _load_llm(): return load_llm()
    async def _load_embedd_model(): return load_embedd_model()
    async def _load_splitter(): return load_splitter()
    llm, embedding_model, text_splitter = await asyncio.gather(
        _load_llm(), _load_embedd_model(), _load_splitter()
    )
    return {"llm": llm, "embedding_model": embedding_model, "text_splitter": text_splitter}

# ---- Background tools loader ----
tools_task = None  # Global tools loading task

def start_loading_tools():
    global tools_task
    if tools_task is None:
        loop = asyncio.get_event_loop()
        tools_task = loop.create_task(load_tools())

def get_tools_task():
    global tools_task
    return tools_task

# Start loading tools as soon as the app loads!
start_loading_tools()

# ---- Authentication ----
@cl.password_auth_callback
async def auth_callback(username:str,password:str) -> Optional[cl.User]:
    user = dbController.authenticate_user(username,password)

    if not user :   
        return None
    
    # let's check for existing refresh token 
    stored_refresh_token = dbController.get_refresh_token(user['idUser'])
    if stored_refresh_token and dbController.verify_refresh_token(stored_refresh_token):
        access_token = dbController.create_access_token(user['idUser'],user['username'])
        refresh_token = stored_refresh_token

    else: # invalid token or token expired 
        access_token = dbController.create_access_token(user['idUser'], username)
        refresh_token = dbController.create_refresh_token(user['idUser'])
        dbController.storeRefreshToken(user['idUser'], refresh_token)

    # Load user conversations from MongoDB to Redis after successful authentication
    try:
        if user and user.get('idUser'):
            dbController.pushConversationsFromMongoToRedis(user['idUser'])
    except Exception as e:
        print(f"Failed to load conversations to Redis: {e}")

    return cl.User(
        identifier=user['username'],
        metadata={
            "id":user['idUser'],
            "access_token":access_token,
            "refresh_token":refresh_token

        }
    )
# ---- Conversation Start ----
@cl.on_chat_start
async def start():
    user = cl.user_session.get("user")
    msg = await cl.Message(content=f"⚡ Connected! Welcome {user.identifier}").send()
    await asyncio.sleep(2)
    await msg.remove()
    tools_future = get_tools_task()
    if not tools_future.done():
        # Show loading message while tools are loading
        msg = await cl.Message(content="⏳ Loading heavy tools, please wait...").send()
        await tools_future
        await msg.remove()
    tools = await tools_future

    # Ready! Initialize session as before
    load_dotenv()
    prompt_rag_fusion = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful medical assistant."),
        ("human", "Given a user query, generate 5 alternative medical search queries that may retrieve relevant medical information.Generate only the queries without any added words . Keep them concise and medically accurate.\n User query: {question}")
    ])
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    qdrant_client = QdrantClient(
        url="https://995828ea-aab5-412e-9766-dd32680878b2.europe-west3-0.gcp.cloud.qdrant.io:6333",
        api_key=qdrant_api_key,
        check_compatibility=False,
        timeout=120
    )
    GCS_CREDENTIALS_PATH = os.getenv("GCS_CREDENTIALS_PATH")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GCS_CREDENTIALS_PATH
    from google.cloud import storage
    gcs_client = storage.Client()

    # Add session objects
    cl.user_session.set("prompt_rag_fusion", prompt_rag_fusion)
    cl.user_session.set("qdrant_client", qdrant_client)
    cl.user_session.set("gcs_client", gcs_client)
    cl.user_session.set("tools", tools)

    # Sidebar: List last conversations
    try:
        user_id = user.metadata.get("id")
        conversation_titles = dbController.getConversationTitles(user_id) or []
        # Fallback when no conversations
        if not conversation_titles:
            conversation_titles = ["No conversations"]
        settings = cl.ChatSettings([
            cl.Select(
                id="conversation_selector",
                label="Last Conversations",
                values=conversation_titles,
                initial_index=0
            )
        ])
        await settings.send()
    except Exception as e:
        print(f"Failed to initialize conversation sidebar: {e}")

    await cl.Message(content=f"Hello {user.identifier}! I'm your Medical Assistant. Ask me anything!").send()
    
# ---- Handle message ----
@cl.on_message
async def handle_message(message: cl.Message):
    try:
        prompt_rag_fusion = cl.user_session.get("prompt_rag_fusion")
        qdrant_client = cl.user_session.get("qdrant_client")
        gcs_client = cl.user_session.get("gcs_client")
        tools = cl.user_session.get("tools")
        llm = tools["llm"]
        embedding_model = tools["embedding_model"]
        text_splitter = tools["text_splitter"]

        # Call your main business logic
        content_response = mn.main(
            message.content, prompt_rag_fusion, llm,
            qdrant_client, gcs_client, embedding_model, text_splitter
        )
        content_response = re.search(r'<think>(.*)<\/think>(.*)', content_response, flags=re.DOTALL)
        if content_response:
            content_response = content_response.group(2)
        else:
            content_response = "Sorry, I couldn't process your request."
    except Exception as e:
        print(f"Exception: {e}")
        content_response = "A network error occurred. Please check your connection and try again."
        
    await cl.Message(content=content_response).send()

# ---- On stop ----
@cl.on_stop
async def on_stop():
    await cl.Message("Task stopped!").send()

# ---- React to sidebar selection ----
@cl.on_settings_update
async def on_settings_update(settings):
    try:
        selected_title = settings.get("conversation_selector")
        if not selected_title or selected_title == "No conversations":
            return
        user = cl.user_session.get("user")
        user_id = user.metadata.get("id")
        content = dbController.retrieveConversationForUser(user_id, selected_title)
        if content:
            await cl.Message(author="History", content=content).send()
        else:
            await cl.Message(content="No content found for this conversation.").send()
    except Exception as e:
        await cl.Message(content=f"Error loading conversation: {e}").send()

# ---- On logout ----
@cl.on_logout
def on_logout(request: Request, response: Response):
    for cookie_name in request.cookies.keys():
        response.delete_cookie(cookie_name)

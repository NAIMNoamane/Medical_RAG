import redis
from dotenv import load_dotenv
import os 
import draft
import redis.client


# create custom logging
logger = draft.customLogger()

def getRedisConnection()->redis.client :
    try: 
        load_dotenv()
        PASSWORD_REDIS = os.getenv("PASSWORD_REDIS")
        redisClient = redis.Redis(
            host='redis-12238.c327.europe-west1-2.gce.redns.redis-cloud.com',
            port=12238,
            decode_responses=True,
            username="default",
            password=PASSWORD_REDIS,
        )
        return redisClient
    except Exception as e :
        logger.error(f'Type of eror: {e}')

# -------- Load conversations to redis DB ----------
def pushConversationsToRedisDB(id_user:int, conversations:dict):
    try:
        redisClient = getRedisConnection()
        redisClient.hset(
                id_user,
                mapping=conversations
            )
    except Exception as e :
        logger.error(f'Type of eror: {e}')

# -------- Retrieve conversation --------
def retrieveConversation(id_user:int, conversation_title:str)->str:
    try:
        redisClient = getRedisConnection()
        result = redisClient.hget(id_user,conversation_title)

        return result
    except Exception as e :
        logger.error(f'Type of eror: {e}')

# -------- Remove conversation ------
def removeConversation(id_user:int, conversation_title:str): 
    try :
        redisClient = getRedisConnection()
        redisClient.hdel(id_user,conversation_title)
    except Exception as e : 
        logger.error(f'Type of eror: {e}')


# -------- Remove session conversation ------- 
def removeSessionConversation(id_user:int):
    try:
        redisClient = getRedisConnection()
        redisClient.delete(id_user)
    except Exception as e : 
        logger.error(f'Type of eror: {e}')

# -------- Add new conversation -----------
def addConversation(id_user:int, conversation:dict):
    try: 
        redisClient = getRedisConnection()
        redisClient.hset(id_user, mapping=conversation)
    except Exception as e :
        logger.error(f'Type of eror: {e}')


# -------- Get conversation titles -----------
def getConversationTitles(id_user: int):
    try:
        redisClient = getRedisConnection()
        return redisClient.hkeys(id_user)
    except Exception as e:
        logger.error(f'Type of eror: {e}')
        return []


# -------- Get all conversations -----------
def getAllConversations(id_user: int):
    try:
        redisClient = getRedisConnection()
        return redisClient.hgetall(id_user)
    except Exception as e:
        logger.error(f'Type of eror: {e}')
        return {}
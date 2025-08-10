from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import draft
import certifi
import os 




# create Logger 
logger = draft.customLogger()


#------- Create Database connection ---------------
def getMongoDBConnection()->MongoClient:
    try : 
        load_dotenv()
        PASSWORD_MONGODB = os.getenv("PASSWORD_MONGODB")
        uri = "mongodb+srv://noamannaim1990:"+PASSWORD_MONGODB+"@cluster0.qcnrfw3.mongodb.net/?retryWrites=true&w=majority&appName=Medic"
        client = MongoClient(uri, server_api=ServerApi('1'),tlsCAFile=certifi.where())

        return client
    except Exception as e : 
        logger.error(f'Type of eror: {e}')

#------- insert user conversation --------
def insertDoc(id_user:int, conversation:dict)->bool:
    try:
        client = getMongoDBConnection()
        user_colletion = client['Medic']['userchainlit']
        result = user_colletion.update_one(
                {"id" : id_user},
                {"$push": {"conversations" : conversation}},
                upsert=True
            )
        if result:
            return True
    except Exception as e : 
        logger.error(f'Type of eror: {e}')

#------- Remove user conversation --------
def removeConversation(id_user:int, conversation_title:str)->bool:
    try :
        client = getMongoDBConnection()
        user_colletion = client['Medic']['userchainlit']
        result = user_colletion.update_one(
                {"id" : id_user},
                {"$pull" : {"conversations": {"conversation_title" :conversation_title }}}
            )
        if result : 
            return True
    except Exception as e :
        logger.error(f'Type of eror: {e}')

#------- retrieve conversations --------
def retrieveConversations(id_user:int):
    try : 

        client = getMongoDBConnection()
        user_colletion = client['Medic']['userchainlit']
        result = user_colletion.find_one({"id":id_user})

        return result['conversations']
    except Exception as e : 
        logger.error(f'Type of eror: {e}')


from dotenv import load_dotenv
import os 
import mongodb as mn
import redisdb as rs 
import mysqlconnection 
import tokenAuthentication 
'''This Controller shares data between Databases especially MongoDB and RedisDB 
for faster conversations load and better user experience '''


# retrieve  MongoDB conversations and put them into redis DB 
def pushConversationsFromMongoToRedis(id_user):
    conversations = mn.retrieveConversations(id_user)
    dict_conversations = {}
    for conversation in conversations : dict_conversations.update(conversation)
    try :   
        rs.pushConversationsToRedisDB(id_user,dict_conversations)
    except:
        print("Error occured!! Try again..")
# Retrieve conversation for the user
def retrieveConversationForUser(id_user,conversation_title):
    conversation_content = rs.retrieveConversation(id_user,conversation_title)
    return conversation_content
# Remove conversation 
def removeConversationFromBothDB(id_user,conversation_title):
    try:
        rs.removeConversation(id_user,conversation_title)
        mn.removeConversation(id_user,conversation_title)
    except:
        print("Error Connection! Try again... ")
# Add conversation 
def addConversationToBothDB(id_user,conversation:dict):
    mn.insertDoc(id_user,conversation)
    rs.addConversation(id_user, conversation)

# get conversation titles from redis
def getConversationTitles(id_user):
    return rs.getConversationTitles(id_user)

# get all conversations from redis
def getAllConversations(id_user):
    return rs.getAllConversations(id_user)

# authenticate user 
def authenticate_user(username, password ):
    return mysqlconnection.authenticate_user(username, password)

# get refresh token 
def get_refresh_token(user_id):
    return mysqlconnection.get_refresh_token(user_id)

# create access token
def create_access_token(user_id, username):
    return tokenAuthentication.create_access_token(user_id,username)

#create refresh token
def create_refresh_token(user_id):
    return tokenAuthentication.create_refresh_token(user_id)
# Store refresh token 
def storeRefreshToken(user_id,refresh_token):
    return mysqlconnection.storeRefreshToken(user_id,refresh_token)
# Verify access token 
def verify_access_token(token):
    return tokenAuthentication.verify_access_token(token)
# Verify refresh token 
def verify_refresh_token(token):
    return tokenAuthentication.verify_refresh_token(token)
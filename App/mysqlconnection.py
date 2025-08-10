from dotenv import load_dotenv
import mysql.connector
import draft 
import os 


''' Mysql database is used for security reasons;  
    Simple Authentication and Token-based Authentication. Here, it authenticates the user, store 
    and retrieve refresh token '''

# create a Logger 
logger = draft.customLogger()

# --------- Establish Database Connection --------
def getMysqlConnection():
    try : 
        load_dotenv()
        MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password=MYSQL_PASSWORD,
            database="users"
        )
    except Exception as e  : 
        logger.error(f'Type of error : {e}')

# --------- Authentication --------
def authenticate_user(username:str, password:str):
    try:
        connection = getMysqlConnection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM clients  WHERE username=%s", (username,))
        user = cursor.fetchone()
        connection.close()
        if user and password == user['password']:
            return user
        return None
    except Exception as e  : 
        logger.error(f'Type of error : {e}')

# --------- Store Refresh Token --------
def storeRefreshToken(user_id:int, refresh_token):
    try : 
        connection = getMysqlConnection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("UPDATE clients SET refreshtoken=%s WHERE idUser=%s", (refresh_token, user_id))
        connection.commit()
        connection.close()
    except Exception as e : 
        logger.error(f'Type of error : {e}')

# --------- Retrieve Refresh Token -------- 
def get_refresh_token(user_id:int):
    try :
        connection = getMysqlConnection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT refreshtoken FROM clients WHERE idUser=%s",(user_id,))
        refreshToken = cursor.fetchone()
        connection.close()

        return refreshToken
    except Exception as e : 
        logger.error(f'Type of error : {e}')
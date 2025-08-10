from dotenv import load_dotenv
import jwt, secrets
import datetime
import draft
import os 


''' We use Token-based Authentication to make the application more secure. We use 
    Access Tokens and Refresh Tokens for better user experience '''

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_SECRET = os.getenv("REFRESH_SECRET")
ALGORITHM = os.getenv("ALGORITHM")
# create a Logger 
logger = draft.customLogger()


# ------ Create Access Token ----------
def create_access_token(user_id, username):
    try: 
        payload = {
            "id": user_id, 
            "username" : username, 
            "exp" : datetime.datetime.utcnow() + datetime.timedelta(minutes=50)# Access Tokens expire in 50 minutes
        }
        return jwt.encode(payload, SECRET_KEY,ALGORITHM)
    except Exception as e :
        logger.error(f'Type of error: {e}')

# ------ Create Refresh Token ----------
def create_refresh_token(user_id):
    try: 
        payload = {
            "id" : user_id,
            "exp" : datetime.datetime.utcnow() + datetime.timedelta(days=2)# Access Tokens expire after 2 days
        }
        return jwt.encode(payload, REFRESH_SECRET,ALGORITHM)
    except Exception as e :
        logger.error(f'Type of error: {e}')

# ------ Verify Access Token ----------
def verify_access_token(token):
    try : 
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except Exception as e :
        logger.error(f'Type of error: {e}')
 
# ------ Verify Refresh Token ----------
def verify_refresh_token(token):
    try:
        return jwt.decode(token, REFRESH_SECRET, algorithms=["HS256"])
    except Exception as e :
        logger.error(f'Type of error: {e}')
    

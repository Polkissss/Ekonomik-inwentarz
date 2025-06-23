import os
from dotenv import load_dotenv

load_dotenv()

ROOT_LOGINS = ["pkrzastek@ekonomik.gniezno.pl"] # Default users allowed to log in
SESSION_TYPE = "filesystem"
LOGIN_ENABLED = True
SECRET_KEY = os.getenv("SECRET_KEY")
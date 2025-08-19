import environ
import firebase_admin
from firebase_admin import credentials, firestore

env = environ.Env()
environ.Env.read_env()  # .env 읽기

# settings.py에서 초기화하지 않는다면, 여기서 초기화해도 됩니다.
if not firebase_admin._apps:
    cred_path = env("FIREBASE_CREDENTIALS_PATH")
    project_id = env("FIREBASE_PROJECT_ID", default=None)

    opts = {"projectId": project_id} if project_id else None
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, opts)

_db = None

def get_firestore():
    global _db
    if _db is None:
        _db = firestore.client()
    return _db

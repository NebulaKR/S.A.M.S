import os, json
import firebase_admin
from firebase_admin import credentials

def _init():
    if firebase_admin._apps:
        return

    proj_id = os.environ.get("FIREBASE_PROJECT_ID")
    json_inline = os.environ.get("FIREBASE_CREDENTIALS_JSON")
    key_path = os.environ.get("FIREBASE_CREDENTIALS_PATH")

    if json_inline:
        cred = credentials.Certificate(json.loads(json_inline))
    elif key_path:
        cred = credentials.Certificate(key_path)
    else:
        # GCP 배포 환경에선 ADC(Application Default Credentials)도 가능
        cred = credentials.ApplicationDefault()

    firebase_admin.initialize_app(cred, {"projectId": proj_id})

_init()

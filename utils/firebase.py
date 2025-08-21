# utils/firebase.py
import os
from pathlib import Path
import environ
import firebase_admin
from firebase_admin import credentials, firestore

_db = None
_env_loaded = False

def _read_env():
    """여러 후보 위치에서 .env를 읽되, 단 한 번만 시도"""
    global _env_loaded
    if _env_loaded:
        return
    env = environ.Env()

    # 이 파일 기준으로 프로젝트 루트 추정 + CWD도 후보에 포함
    here = Path(__file__).resolve()
    candidates = [
        here.parent.parent / ".env",        # <project>/utils/.. -> <project>/.env
        here.parent.parent.parent / ".env", # 한 단계 더 위
        Path.cwd() / ".env",                # 현재 작업 디렉터리
    ]
    for p in candidates:
        if p.is_file():
            environ.Env.read_env(str(p))
            break
    # .env가 없어도 OS 환경변수만으로 동작 가능
    _env_loaded = True

def _init_firebase_if_needed():
    """firebase_admin을 한 번만 초기화"""
    _read_env()
    if firebase_admin._apps:
        return

    env = environ.Env()
    cred_path = env("FIREBASE_CREDENTIALS_PATH", default=None)

    # 예비 경로: 표준 GCP 환경변수도 허용
    if not cred_path:
        cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if not cred_path:
        raise RuntimeError(
            "Firebase 자격 경로를 찾지 못했습니다. "
            "'.env'에 FIREBASE_CREDENTIALS_PATH=... 또는 "
            "OS 환경변수 GOOGLE_APPLICATION_CREDENTIALS 를 설정하세요."
        )

    project_id = env("FIREBASE_PROJECT_ID", default=None)
    opts = {"projectId": project_id} if project_id else None

    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, opts)

def get_firestore():
    """최초 호출 시에만 초기화하고, 같은 클라이언트를 재사용"""
    global _db
    if _db is None:
        _init_firebase_if_needed()
        _db = firestore.client()
    return _db

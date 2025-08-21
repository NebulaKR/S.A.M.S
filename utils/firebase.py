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
    
    # 이미 초기화된 Firebase가 있는지 확인
    if firebase_admin._apps:
        print("Firebase가 이미 초기화되어 있습니다.")
        return

    # settings.py에서 이미 초기화했는지 확인
    try:
        from django.conf import settings
        if hasattr(settings, 'FIREBASE_INITIALIZED') and settings.FIREBASE_INITIALIZED:
            print("Django settings에서 Firebase가 이미 초기화되었습니다.")
            return
    except:
        pass

    env = environ.Env()
    cred_path = env("FIREBASE_CREDENTIALS_PATH", default=None)
    cred_json = env("FIREBASE_CREDENTIALS_JSON", default=None)

    # 예비 경로: 표준 GCP 환경변수도 허용
    if not cred_path:
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    
    # JSON 형태의 자격 증명도 확인
    if not cred_json:
        cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")

    if not cred_path and not cred_json:
        print("Firebase 자격 경로를 찾지 못했습니다. 개발 모드로 실행됩니다.")
        return

    try:
        project_id = env("FIREBASE_PROJECT_ID", default=None)
        if not project_id:
            project_id = os.getenv("FIREBASE_PROJECT_ID")
        
        opts = {"projectId": project_id} if project_id else None

        if cred_json:
            # JSON 형태의 자격 증명 사용
            import json
            cred_dict = json.loads(cred_json)
            cred = credentials.Certificate(cred_dict)
        else:
            # 파일 경로의 자격 증명 사용
            cred = credentials.Certificate(cred_path)
        
        firebase_admin.initialize_app(cred, opts)
        print("Firebase 초기화 성공!")
    except Exception as e:
        print(f"Firebase 초기화 실패 (개발 모드): {e}")
        return

def get_firestore():
    """최초 호출 시에만 초기화하고, 같은 클라이언트를 재사용"""
    global _db
    if _db is None:
        try:
            _init_firebase_if_needed()
            if firebase_admin._apps:
                _db = firestore.client()
            else:
                print("Firebase가 초기화되지 않았습니다. 개발 모드로 실행됩니다.")
                _db = None
        except Exception as e:
            print(f"Firestore 클라이언트 생성 실패 (개발 모드): {e}")
            _db = None
    return _db

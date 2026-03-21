"""
config 프로젝트의 ASGI 설정입니다.

이 파일은 ASGI 호출 가능 객체를 ``application``이라는 모듈 수준 변수로
노출합니다.

자세한 내용은 다음 문서를 참조하세요:
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()

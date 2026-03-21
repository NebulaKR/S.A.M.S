"""
config 프로젝트의 WSGI 설정입니다.

이 파일은 WSGI 호출 가능 객체를 ``application``이라는 모듈 변수로
노출합니다.

자세한 내용은 다음 문서를 참고하세요:
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

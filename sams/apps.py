from django.apps import AppConfig


class SamsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sams'
    
    def ready(self):
        """Django 앱이 시작될 때 실행되는 메서드"""
        import os
        
        # 자동 시뮬레이션 시작 비활성화 (관리자 대시보드에서 수동 제어)
        print("📊 S.A.M.S 시뮬레이션 시스템이 준비되었습니다.")
        print("🎮 관리자 대시보드에서 시뮬레이션을 시작하세요.")

from django.apps import AppConfig


class SamsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sams'
    
    def ready(self):
        """Django 앱이 시작될 때 실행되는 메서드"""
        import os
        
        # 개발 환경에서만 백그라운드 시뮬레이션 자동 시작
        if os.environ.get('RUN_MAIN') == 'true':
            try:
                from .services import SimulationService
                
                # 백그라운드 시뮬레이션 자동 시작
                result = SimulationService.start_background_simulation()
                if result['success']:
                    print("✅ Django 서버 시작과 함께 백그라운드 시뮬레이션이 자동으로 시작되었습니다.")
                else:
                    print(f"⚠️ 백그라운드 시뮬레이션 자동 시작 실패: {result['message']}")
                    
            except Exception as e:
                print(f"⚠️ 백그라운드 시뮬레이션 자동 시작 중 오류: {e}")
                print("수동으로 시뮬레이션을 시작할 수 있습니다.")

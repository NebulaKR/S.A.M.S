#!/usr/bin/env python3
"""
Firebase Functions 배포 스크립트
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """명령어 실행 및 결과 출력"""
    print(f"🔄 {description}...")
    print(f"실행 명령어: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 완료")
        if result.stdout:
            print(f"출력: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 실패")
        print(f"오류: {e.stderr}")
        return False

def main():
    """메인 배포 프로세스"""
    print("🚀 Firebase Functions 배포 시작")
    
    # 1. functions 디렉토리로 이동
    functions_dir = Path("functions")
    if not functions_dir.exists():
        print("❌ functions 디렉토리가 존재하지 않습니다.")
        return False
    
    os.chdir(functions_dir)
    print(f"📁 작업 디렉토리: {os.getcwd()}")
    
    # 2. Python 가상환경 활성화
    if not run_command("..\\.venv\\Scripts\\Activate.ps1", "가상환경 활성화"):
        print("⚠️ 가상환경 활성화 실패, 계속 진행...")
    
    # 3. Firebase Functions 로컬 테스트
    print("🧪 Firebase Functions 로컬 테스트...")
    print("테스트 URL: http://localhost:8080")
    print("Ctrl+C로 테스트 중단 후 배포 진행")
    
    try:
        subprocess.run("functions-framework --target django_app --debug", shell=True)
    except KeyboardInterrupt:
        print("\n✅ 로컬 테스트 완료")
    
    # 4. Firebase Functions 배포
    print("🚀 Firebase Functions 배포 중...")
    print("⚠️ Firebase CLI가 설치되어 있지 않으면 수동으로 배포해야 합니다.")
    
    # 5. 배포 가이드 출력
    print("\n📋 수동 배포 가이드:")
    print("1. Node.js 설치: https://nodejs.org/")
    print("2. Firebase CLI 설치: npm install -g firebase-tools")
    print("3. Firebase 로그인: firebase login")
    print("4. Functions 배포: firebase deploy --only functions")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


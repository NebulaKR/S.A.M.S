#!/usr/bin/env python3
"""
Firebase Hosting 배포 스크립트
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
    print("🚀 Firebase Hosting 배포 시작")
    
    # 1. Django 정적 파일 수집
    if not run_command("python manage.py collectstatic --noinput", "Django 정적 파일 수집"):
        print("❌ 정적 파일 수집 실패. 배포를 중단합니다.")
        return False
    
    # 2. Firebase CLI 설치 확인
    try:
        subprocess.run("firebase --version", shell=True, check=True, capture_output=True)
        print("✅ Firebase CLI가 이미 설치되어 있습니다.")
    except subprocess.CalledProcessError:
        print("⚠️ Firebase CLI가 설치되어 있지 않습니다.")
        print("📥 https://firebase.google.com/docs/cli 에서 설치 방법을 확인하세요.")
        return False
    
    # 3. Firebase 프로젝트 초기화 (처음 배포 시에만)
    if not Path(".firebaserc").exists():
        print("🔧 Firebase 프로젝트 초기화...")
        project_id = input("Firebase 프로젝트 ID를 입력하세요 (예: sams-295be): ").strip()
        
        if not run_command(f"firebase init hosting --project {project_id} --public static", "Firebase 프로젝트 초기화"):
            return False
    
    # 4. Firebase 배포
    if not run_command("firebase deploy --only hosting", "Firebase Hosting 배포"):
        return False
    
    print("🎉 Firebase Hosting 배포 완료!")
    print("🌐 배포된 URL을 확인하려면 Firebase Console을 방문하세요.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


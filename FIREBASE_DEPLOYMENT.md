# 🚀 Firebase Hosting 배포 가이드

## 📋 **사전 준비사항**

### 1. **Firebase 프로젝트 생성**
- [Firebase Console](https://console.firebase.google.com/)에서 새 프로젝트 생성
- 프로젝트 ID 확인 (예: `sams-295be`)

### 2. **Firebase CLI 설치**
```bash
# Windows (PowerShell)
npm install -g firebase-tools

# 또는 직접 다운로드
# https://firebase.google.com/docs/cli#install-cli-windows
```

### 3. **Firebase 로그인**
```bash
firebase login
```

## 🔧 **배포 단계**

### **자동 배포 (권장)**
```bash
python deploy.py
```

### **수동 배포**

#### 1. **Django 정적 파일 수집**
```bash
python manage.py collectstatic --noinput
```

#### 2. **Firebase 프로젝트 초기화**
```bash
firebase init hosting
# 프로젝트 선택: sams-295be
# 공개 디렉토리: static
# SPA 설정: Yes
```

#### 3. **Firebase 배포**
```bash
firebase deploy --only hosting
```

## 🌐 **배포 후 확인**

### **배포된 URL**
- Firebase Console → Hosting에서 확인
- 기본 URL: `https://sams-295be.web.app`

### **도메인 커스터마이징**
- Firebase Console → Hosting → Custom domains
- 자체 도메인 연결 가능

## ⚠️ **주의사항**

### **정적 파일 제한**
- Firebase Hosting은 정적 파일만 호스팅
- Django 백엔드는 Firebase Functions로 별도 배포 필요

### **API 엔드포인트**
- `/api/**` 경로는 Firebase Functions로 라우팅
- Django 백엔드 API는 Functions에서 실행

### **데이터베이스**
- Firebase Firestore는 별도로 설정 필요
- 자격 증명 파일 경로 확인

## 🔍 **문제 해결**

### **Firebase CLI 오류**
```bash
# 버전 확인
firebase --version

# 재설치
npm uninstall -g firebase-tools
npm install -g firebase-tools
```

### **정적 파일 수집 오류**
```bash
# Django 설정 확인
python manage.py check

# 정적 파일 경로 확인
python manage.py findstatic admin/css/base.css
```

### **배포 실패**
```bash
# 로그 확인
firebase deploy --only hosting --debug

# 캐시 정리
firebase logout
firebase login
```

## 📚 **추가 리소스**

- [Firebase Hosting 문서](https://firebase.google.com/docs/hosting)
- [Django 배포 가이드](https://docs.djangoproject.com/en/5.2/howto/deployment/)
- [Firebase Functions 문서](https://firebase.google.com/docs/functions)


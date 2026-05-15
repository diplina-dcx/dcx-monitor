# DCX 카페 평판 모니터 v2.0

강북삼성병원 홍보팀 | 네이버 카페 고객 경험 수집·분석 웹앱

---

## 로컬 실행 (테스트)

```bash
pip install -r requirements.txt
streamlit run app.py
```

브라우저에서 http://localhost:8501 접속

---

## Streamlit Cloud 배포 (권장)

### 1단계 — GitHub 업로드
```
dcx_streamlit/
├── app.py
├── requirements.txt
├── .gitignore          ← secrets.toml 제외됨
└── .streamlit/
    └── secrets.toml    ← 로컬용, GitHub에 올라가지 않음
```

### 2단계 — Streamlit Cloud 연결
1. https://share.streamlit.io 접속
2. GitHub 계정 연결
3. 저장소 선택 → Main file: `app.py`
4. Deploy 클릭

### 3단계 — API 키 등록 (핵심)
1. 배포된 앱 → 우상단 `⋮` → **Settings**
2. **Secrets** 탭 클릭
3. 아래 내용 붙여넣기:

```toml
NAVER_CLIENT_ID     = "실제_Client_ID"
NAVER_CLIENT_SECRET = "실제_Client_Secret"
```

4. Save → 앱 자동 재시작

> API 키가 코드에 노출되지 않고 서버에만 안전하게 보관됩니다.

---

## 네이버 API 설정

1. https://developers.naver.com 접속
2. Application 등록
3. **카페글 검색** 권한 체크
4. Client ID / Secret 복사
5. 웹 서비스 URL: `https://your-app.streamlit.app` 추가

---

## 파일 구성

| 파일 | 역할 |
|------|------|
| `app.py` | 전체 앱 (UI + 분석 로직 통합) |
| `requirements.txt` | 패키지 목록 |
| `.streamlit/secrets.toml` | API 키 (로컬용, Git 제외) |
| `.gitignore` | secrets.toml GitHub 업로드 차단 |

---

Copyright (c) 2026 Sang-Man Lee. All rights reserved.

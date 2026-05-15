# -*- coding: utf-8 -*-
"""
DCX 카페 평판 모니터 — Streamlit 웹앱 v2.0
강북삼성병원 홍보팀 | 고객 경험(DCX) 수집 분석 도구
"""

import streamlit as st
import requests
import re
import time
import datetime
import json
import csv
import io
from collections import Counter

# ── 페이지 설정 ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DCX 카페 평판 모니터",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── SMC 디자인 CSS (UI Guidelines v1 완전 반영) ───────────────────────────────
st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

html, body, [class*="css"] {
    font-family: 'Pretendard', 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif !important;
}

/* ── Lv1: 최상위 배경 #1C1C1E ── */
.stApp { background-color: #1C1C1E; }
.block-container { padding-top: 1rem !important; }

/* ── 사이드바 (Surface Dark) ── */
[data-testid="stSidebar"] {
    background-color: #111111 !important;
    border-right: 1px solid #2C2C2E;
}
[data-testid="stSidebar"] * { color: #CCCCCC !important; }
[data-testid="stSidebar"] label { color: #888 !important; font-size: 12px !important; }
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea {
    background: #1C1C1E !important;
    color: #EEE !important;
    border: 0.5px solid #3A3A3C !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] .stSlider label { color: #888 !important; }

/* ── Lv2: 화이트 카드 패널 (메인 컨텐츠 영역 전체) ── */
/* 메인 컬럼들을 흰 카드로 감쌈 */
.panel-card {
    background: #FFFFFF;
    border-radius: 20px;
    border: 0.5px solid #E4E4E4;
    padding: 20px 20px 24px;
    margin-bottom: 16px;
}

/* 패널 헤더 바 */
.panel-header {
    font-size: 11px; font-weight: 600; letter-spacing: 0.08em;
    color: #999; text-transform: uppercase;
    border-bottom: 0.5px solid #E8E8E8;
    padding-bottom: 8px; margin-bottom: 14px;
}

/* ── 메인 헤더 ── */
.main-header {
    background: linear-gradient(135deg, #1428A0 0%, #1E6FE8 100%);
    border-radius: 16px;
    padding: 22px 28px;
    margin-bottom: 16px;
}
.main-header h1 { margin:0; font-size:20px; font-weight:700; color:#fff; }
.main-header p  { margin:4px 0 0; font-size:12px; color:#AAC9F8; }

/* ── 라디오 버튼 — 흰 배경 위 텍스트 강제 ── */
div[data-testid="stHorizontalBlock"] .stRadio label,
.stRadio label,
.stRadio span,
[data-testid="stWidgetLabel"],
div[role="radiogroup"] label,
div[role="radiogroup"] span {
    color: #111111 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}
div[role="radiogroup"] {
    background: #F5F5F5;
    border-radius: 8px;
    padding: 6px 8px;
    border: 0.5px solid #EBEBEB;
}

/* ── 캡션 텍스트 ── */
.stCaption, .stCaption p { color: #888 !important; font-size: 11px !important; }

/* ── Lv3: 내부 섹션 카드 (중첩 영역 #F5F5F5) ── */
.inner-card {
    background: #F5F5F5;
    border-radius: 8px;
    border: 0.5px solid #EBEBEB;
    padding: 12px 14px;
    margin-bottom: 10px;
}

/* ── 감성 뱃지 ── */
.badge-pos { background:#E8F5EC; color:#1E8A3E; border-radius:100px; padding:2px 10px; font-size:11px; font-weight:600; }
.badge-neu { background:#FFF8E0; color:#B07D00; border-radius:100px; padding:2px 10px; font-size:11px; font-weight:600; }
.badge-neg { background:#FDECEA; color:#C0392B; border-radius:100px; padding:2px 10px; font-size:11px; font-weight:600; }
.badge-mix { background:#F3EAF9; color:#7B3FA0; border-radius:100px; padding:2px 10px; font-size:11px; font-weight:600; }
.badge-s   { background:#1E6FE8; color:#fff; border-radius:4px; padding:2px 8px; font-size:10px; font-weight:600; }
.badge-a   { background:#1428A0; color:#fff; border-radius:4px; padding:2px 8px; font-size:10px; font-weight:600; }
.badge-b   { background:#555;    color:#fff; border-radius:4px; padding:2px 8px; font-size:10px; font-weight:600; }
.badge-c   { background:#999;    color:#fff; border-radius:4px; padding:2px 8px; font-size:10px; font-weight:600; }

/* ── 게시글 카드 ── */
.post-card {
    background: #FFFFFF;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 8px;
    border-left: 4px solid #E4E4E4;
    border-top: 0.5px solid #F0F0F0;
    border-right: 0.5px solid #F0F0F0;
    border-bottom: 0.5px solid #F0F0F0;
}
.post-card.pos { border-left-color: #1E8A3E; }
.post-card.neg { border-left-color: #C0392B; }
.post-card.neu { border-left-color: #B07D00; }
.post-card.mix { border-left-color: #7B3FA0; }
.post-title { font-size:13px; font-weight:600; color:#111; margin-bottom:4px; }
.post-body  { font-size:12px; color:#555; line-height:1.6; margin-bottom:6px; }
.post-meta  { font-size:11px; color:#999; }
.post-tag   { background:#E8F0FD; color:#0D3A8A; border-radius:100px; padding:1px 7px; font-size:10px; margin-right:4px; }

/* ── 지표 카드 ── */
.metric-card {
    border-radius: 10px;
    padding: 14px 10px;
    text-align: center;
}
.metric-num   { font-size:26px; font-weight:700; line-height:1; }
.metric-pct   { font-size:12px; margin-top:2px; }
.metric-label { font-size:11px; margin-top:4px; opacity:0.8; }

/* ── 점수 박스 ── */
.score-box {
    background: #E8F0FD;
    border: 1px solid #C5D8F9;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
}
.score-num   { font-size:40px; font-weight:700; color:#1E6FE8; line-height:1; }
.score-grade { font-size:15px; font-weight:600; margin-top:4px; }
.score-desc  { font-size:11px; color:#888; margin-top:4px; }

/* ── 키워드 태그 ── */
.kw-tag {
    display: inline-block;
    background: #E8F0FD; color: #0D3A8A;
    border-radius: 100px; padding: 3px 10px;
    font-size: 12px; margin: 2px;
}

/* ── 섹션 구분선 ── */
hr { border-color: #E8E8E8 !important; margin: 16px 0 !important; }

/* ── 다운로드/버튼 ── */
.stButton button, .stDownloadButton button {
    border-radius: 8px !important;
    font-family: 'Pretendard', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}

/* ── 구분선 위 섹션 타이틀 ── */
.section-title {
    font-size: 11px; font-weight: 600; letter-spacing: 0.08em;
    color: #999; text-transform: uppercase;
    border-bottom: 0.5px solid #E8E8E8;
    padding-bottom: 6px; margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# 감성 분석 로직 (dcx_scorer 인라인)
# ══════════════════════════════════════════════════════════════════════════════

POSITIVE_KW = {
    "완치":3.0,"회복":3.0,"좋아짐":3.0,"정상":2.5,"호전":3.0,
    "나았":3.0,"완쾌":3.0,"치료됐":3.0,"치료되었":3.0,
    "명의":2.5,"실력":2.0,"최고":2.5,"믿음":2.5,"감사":2.5,
    "신뢰":2.5,"훌륭":2.5,"최선":2.0,"베테랑":2.5,
    "친절":2.0,"설명":1.5,"배려":2.0,"꼼꼼":2.0,"자세히":1.5,
    "잘해주":2.0,"따뜻":2.0,"정성":2.0,
    "추천":2.0,"강추":2.5,"추천드":2.0,"꼭 가":2.0,
    "다행":1.5,"안심":1.5,"든든":1.5,"기쁨":1.5,"행복":1.5,
    "만족":2.0,"감동":2.0,"뿌듯":1.5,
}
NEGATIVE_KW = {
    "오진":3.0,"부작용":3.0,"합병증":2.5,"재수술":3.0,"의료사고":3.0,
    "실수":2.5,"오류":2.5,"잘못된":2.5,
    "불친절":3.0,"무시":2.5,"설명없":2.5,"돌팔이":3.0,
    "퉁명":2.5,"무관심":2.5,"거만":2.5,"무례":2.5,
    "대기 너무":2.0,"대기가 너무":2.0,"예약 불가":2.0,"혼잡":1.5,
    "오래 기다":2.0,"대기시간":1.5,"예약이 안":2.0,
    "비싸다":2.0,"과잉진료":2.5,"바가지":2.5,"너무 비":2.0,
    "돈만":2.0,"과잉 진료":2.5,
    "후회":2.5,"실망":2.5,"다신 안":2.5,"최악":3.0,
    "절대 안":2.5,"안 감":2.0,"가지 마":2.5,"비추":2.5,"비추천":2.5,
}
SPAM_PATTERNS = [
    re.compile(r"(공구|공동구매|할인코드|클릭|구매하세요|판매합니다)"),
    re.compile(r"(카카오|텔레그램|오픈채팅).{0,10}(문의|연락|DM)"),
    re.compile(r"(블로그|유튜브|인스타).{0,10}(놀러오세요|구독|팔로우)"),
    re.compile(r"(치료비지원|의료비지원).{0,20}(신청|클릭|링크)"),
]
RUMOR_PATTERNS = ["들었는데","카더라","라고 하더라","라더라","친구의 친구","아는 분의 지인"]
FIRST_PERSON  = ["나는","저는","제가","내가","우리 엄마","우리 아버지",
                 "아버지가","어머니가","남편이","아내가","직접","제 경험","경험담"]
MEDICAL_CTX   = ["진료","수술","검사","입원","외래","시술","응급","치료","처방",
                 "주사","MRI","CT","내시경","수납","예약","퇴원","재활","항암"]
TAG_MAP = {
    "암/종양":   ["암","종양","암세포","항암","방사선치료","뇌종양","폐암","위암","간암"],
    "심뇌혈관":  ["심장","뇌졸중","뇌경색","심근경색","협심증","혈관","스텐트"],
    "척추/관절": ["척추","디스크","관절","무릎","허리","척추수술","고관절"],
    "신경계":    ["신경","뇌","파킨슨","치매","루게릭","뇌수술"],
    "소화기":    ["위","대장","간","췌장","담낭","내시경","복강경"],
    "호흡기":    ["폐","기관지","천식","폐렴","호흡"],
    "희귀/난치": ["희귀","난치","루게릭","희귀질환"],
    "소아":      ["소아","어린이","아이","아기","신생아"],
    "여성건강":  ["산부인과","자궁","유방","임신","출산","난소"],
    "로봇수술":  ["로봇수술","다빈치","로봇"],
    "명의":      ["명의","교수님"],
    "대기문제":  ["대기","기다","줄"],
    "친절도":    ["친절","불친절"],
    "비용":      ["비용","비싸","저렴","수납","바가지"],
}

def clean(text: str) -> str:
    return text.replace("<b>","").replace("</b>","").strip()

def score_post(post: dict) -> dict:
    text = clean(post.get("title","") + " " + post.get("description",""))

    # 스팸 체크
    if len(text) < 15:
        return _mark_invalid(post, "초단문")
    for pat in SPAM_PATTERNS:
        if pat.search(text):
            return _mark_invalid(post, "스팸")
    if len(text) < 30:
        return _mark_invalid(post, "30자 미만")
    for r in RUMOR_PATTERNS:
        if r in text:
            return _mark_invalid(post, "소문성")

    # 점수 산정
    pos = sum(w for kw,w in POSITIVE_KW.items() if kw in text)
    neg = sum(w for kw,w in NEGATIVE_KW.items() if kw in text)
    net = pos - neg

    if pos >= 2.0 and neg >= 2.0:
        sent = "mixed"
    elif net > 1.0:
        sent = "positive"
    elif net < -1.0:
        sent = "negative"
    else:
        sent = "neutral"

    # 품질 등급
    char_cnt    = len(text)
    has_doctor  = any(k in text for k in ["교수","의사","선생님","집도"])
    has_hosp    = any(k in text for k in ["병원","의원","의료원","센터"])
    has_first   = any(k in text for k in FIRST_PERSON)
    sent_clear  = sent in ("positive","negative")

    if has_first and has_doctor and char_cnt >= 100 and sent_clear:
        grade = "S"
    elif has_first and has_hosp and char_cnt >= 50:
        grade = "A"
    elif char_cnt >= 30:
        grade = "B"
    else:
        grade = "C"

    tags = [tag for tag, kws in TAG_MAP.items() if any(k in text for k in kws)]

    post.update({
        "spam_flag": False, "valid": True,
        "sentiment": sent, "sentiment_score": round(net,2),
        "quality_grade": grade, "tags": tags,
    })
    return post

def _mark_invalid(post, reason):
    post.update({"spam_flag":True,"valid":False,"sentiment":"neutral",
                 "sentiment_score":0.0,"quality_grade":"C","tags":[],"exclude_reason":reason})
    return post


# ══════════════════════════════════════════════════════════════════════════════
# 네이버 API 호출
# ══════════════════════════════════════════════════════════════════════════════

def fetch_cafe(keyword: str, max_count: int, client_id: str, client_secret: str) -> list:
    url     = "https://openapi.naver.com/v1/search/cafearticle.json"
    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
    results = []
    start   = 1

    while len(results) < max_count:
        batch  = min(100, max_count - len(results))
        params = {"query": keyword, "display": batch, "start": start, "sort": "date"}
        try:
            r = requests.get(url, params=params, headers=headers, timeout=10)
            if r.status_code != 200:
                st.warning(f"API 오류 {r.status_code}: {r.text[:100]}")
                break
            items = r.json().get("items", [])
            if not items:
                break
            for item in items:
                item["_keyword"] = keyword
            results.extend(items)
            start += len(items)
            if start > 1000:
                break
        except Exception as e:
            st.error(f"네트워크 오류: {e}")
            break
        time.sleep(0.4)

    return results[:max_count]


# ══════════════════════════════════════════════════════════════════════════════
# 유틸
# ══════════════════════════════════════════════════════════════════════════════

SENT_KR   = {"positive":"긍정","neutral":"중립","negative":"부정","mixed":"혼재"}
SENT_COLOR= {"positive":"#1E8A3E","neutral":"#B07D00","negative":"#C0392B","mixed":"#7B3FA0"}
SENT_BG   = {"positive":"#E8F5EC","neutral":"#FFF8E0","negative":"#FDECEA","mixed":"#F3EAF9"}
SENT_BORDER={"positive":"#1E8A3E","neutral":"#B07D00","negative":"#C0392B","mixed":"#7B3FA0"}
SENT_ICON = {"positive":"😊","neutral":"😐","negative":"😟","mixed":"🔀"}

def fmt_date(raw: str) -> str:
    try:
        dt = datetime.datetime.strptime(raw, "%a, %d %b %Y %H:%M:%S +0900")
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return raw

def rep_score(counts: dict, total: int) -> int:
    if total == 0:
        return 0
    pos_pct = counts.get("positive",0)/total*100
    neg_pct = counts.get("negative",0)/total*100
    return max(0, min(100, round(50 + (pos_pct - neg_pct)/2)))

def grade_label(score: int) -> tuple:
    if score >= 80: return "A+", "#1E8A3E"
    if score >= 70: return "A",  "#1E8A3E"
    if score >= 60: return "B",  "#B07D00"
    if score >= 50: return "C",  "#B07D00"
    return "D", "#C0392B"

def build_csv(posts: list) -> str:
    buf = io.StringIO()
    cols = ["title","cafename","pubDate","sentiment","sentiment_score",
            "quality_grade","description","link","tags"]
    w = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    for p in posts:
        row = {k: p.get(k,"") for k in cols}
        row["title"]       = clean(row["title"])
        row["description"] = clean(row["description"])
        row["tags"]        = ", ".join(row.get("tags") or [])
        w.writerow(row)
    return buf.getvalue()

def build_txt(posts: list, keyword: str, counts: dict) -> str:
    total = len(posts)
    lines = [
        f"[DCX 카페 평판 분석 보고서]",
        f"검색 키워드 : {keyword}",
        f"수집 일시   : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"총 수집건수 : {total}건",
        f"감성 분포   : 긍정 {counts.get('positive',0)}건 / "
        f"중립 {counts.get('neutral',0)}건 / "
        f"부정 {counts.get('negative',0)}건 / "
        f"혼재 {counts.get('mixed',0)}건",
        "="*60, "",
    ]
    for p in posts:
        sent = SENT_KR.get(p.get("sentiment","neutral"),"중립")
        lines += [
            f"[{sent} / {p.get('sentiment_score',0):+.1f} / {p.get('quality_grade','C')}등급]",
            f"제목 : {clean(p.get('title',''))}",
            f"카페 : {p.get('cafename','')} | 날짜 : {fmt_date(p.get('pubDate',''))}",
            f"내용 : {clean(p.get('description',''))[:300]}",
            f"링크 : {p.get('link','')}",
            "",
        ]
    return "\n".join(lines)

def build_ai_prompt(posts: list, keyword: str, counts: dict) -> str:
    total = len(posts)
    lines = [
        "아래는 네이버 카페에서 수집한 환자·보호자 실제 경험 게시글입니다.",
        f"검색 키워드: {keyword} | 총 {total}건",
        f"감성 분포: 긍정 {counts.get('positive',0)}건 / 중립 {counts.get('neutral',0)}건 / "
        f"부정 {counts.get('negative',0)}건 / 혼재 {counts.get('mixed',0)}건",
        "",
        "--- 수집 데이터 (S/A등급 우선, 상위 30건) ---",
    ]
    top = [p for p in posts if p.get("quality_grade") in ("S","A")][:30]
    if len(top) < 30:
        top += [p for p in posts if p.get("quality_grade") not in ("S","A")][:30-len(top)]
    for p in top:
        sent = SENT_KR.get(p.get("sentiment","neutral"),"중립")
        lines += [
            f"[{sent}] {clean(p.get('title',''))}",
            clean(p.get("description",""))[:300],
            "",
        ]
    lines += [
        "="*60,
        "위 데이터를 분석하여 다음 항목을 정리해 주세요:",
        "1. 핵심 긍정 요인 (환자들이 높이 평가하는 점)",
        "2. 핵심 부정 요인 (불만 사항 및 개선이 필요한 점)",
        "3. 주요 언급 의료진 또는 진료과",
        "4. 홍보 메시지에 활용할 수 있는 환자 언어·표현",
        "5. 신환 유치를 위한 콘텐츠 기획 제안",
    ]
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# 메인 UI
# ══════════════════════════════════════════════════════════════════════════════

# ── 사이드바 ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏥 DCX 평판 모니터")
    st.markdown("---")

    st.markdown("**🔑 네이버 API 설정**")
    client_id  = st.text_input("Client ID",
                               value=st.secrets.get("NAVER_CLIENT_ID",""),
                               type="default",
                               placeholder="네이버 Client ID 입력")
    client_sec = st.text_input("Client Secret",
                               value=st.secrets.get("NAVER_CLIENT_SECRET",""),
                               type="password",
                               placeholder="네이버 Client Secret 입력")

    st.markdown("---")
    st.markdown("**🔍 검색 설정**")
    keywords_raw = st.text_area(
        "검색 키워드 (쉼표 또는 줄바꿈 구분)",
        placeholder="예: 강북삼성병원, 신경외과, 척추수술",
        height=100,
    )
    max_count = st.select_slider(
        "키워드당 최대 수집 건수",
        options=[30, 50, 100, 200],
        value=100,
    )

    st.markdown("---")
    st.markdown("**🚫 제외 키워드**")
    excl_raw = st.text_input(
        "제외 키워드 (쉼표 구분)",
        value="동물병원,수의사,한의원,한약,성형외과,미용,보톡스",
    )

    st.markdown("---")
    run_btn = st.button("▶  카페 게시글 수집 시작", type="primary", use_container_width=True)

    st.markdown("---")
    st.caption("Copyright © 2026 Sang-Man Lee\nDCX Cafe Monitor v2.0")


# ── 헤더 ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>📊 DCX 카페 평판 모니터</h1>
  <p>강북삼성병원 홍보팀 · 네이버 카페 고객 경험 수집 분석 시스템</p>
</div>
""", unsafe_allow_html=True)


# ── 세션 스테이트 초기화 ──────────────────────────────────────────────────────
if "posts" not in st.session_state:
    st.session_state.posts   = []
if "keyword_label" not in st.session_state:
    st.session_state.keyword_label = ""


# ── 수집 실행 ─────────────────────────────────────────────────────────────────
if run_btn:
    if not client_id or not client_sec:
        st.error("좌측 사이드바에서 네이버 API 키를 입력해 주세요.")
        st.stop()

    keywords = [k.strip()
                for k in re.split(r"[,\n]", keywords_raw)
                if k.strip()]
    if not keywords:
        st.error("검색 키워드를 입력해 주세요.")
        st.stop()

    excl_kws = [k.strip() for k in excl_raw.split(",") if k.strip()]

    all_posts = []
    prog = st.progress(0, text="수집 준비 중...")
    for i, kw in enumerate(keywords):
        prog.progress((i) / len(keywords), text=f"'{kw}' 검색 중... ({i+1}/{len(keywords)})")
        fetched = fetch_cafe(kw, max_count, client_id, client_sec)
        all_posts.extend(fetched)

    prog.progress(1.0, text="감성 분석 중...")

    # 제외 키워드 필터
    if excl_kws:
        all_posts = [p for p in all_posts
                     if not any(ek in clean(p.get("title","") + p.get("description",""))
                                for ek in excl_kws)]

    # 중복 제거
    seen, unique = set(), []
    for p in all_posts:
        k = p.get("link","")
        if k not in seen:
            seen.add(k); unique.append(p)

    # 감성 분석
    scored = [score_post(p) for p in unique]
    scored = [p for p in scored if p.get("valid", True)]  # 스팸 제거

    # 점수 내림차순 정렬 (기본)
    scored.sort(key=lambda p: p.get("sentiment_score",0), reverse=True)

    st.session_state.posts         = scored
    st.session_state.keyword_label = ", ".join(keywords)
    prog.empty()
    st.success(f"✅ 수집 완료 — 유효 게시글 {len(scored)}건 (중복·스팸 제외)")


# ── 결과 표시 ─────────────────────────────────────────────────────────────────
posts = st.session_state.posts

if not posts:
    st.markdown("""
    <div style="text-align:center; padding:60px; color:#888;">
        <div style="font-size:48px;">🔍</div>
        <div style="font-size:16px; margin-top:12px;">좌측 사이드바에서 키워드를 입력하고 수집을 시작하세요</div>
        <div style="font-size:13px; margin-top:8px; color:#555;">의료진 이름, 진료과, 질환명 등을 입력할 수 있습니다</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ── 분석 요약 섹션 (Lv2 흰 카드) ─────────────────────────────────────────────
counts = Counter(p.get("sentiment","neutral") for p in posts)
total  = len(posts)
score  = rep_score(counts, total)
grade, grade_color = grade_label(score)

st.markdown('<div class="panel-card">', unsafe_allow_html=True)
st.markdown('<div class="panel-header">📊 감성 분석 요약</div>', unsafe_allow_html=True)

col_s, col_pos, col_neu, col_neg, col_mix = st.columns([1.2, 1, 1, 1, 1])

with col_s:
    st.markdown(f"""
    <div class="score-box">
        <div class="score-num">{score}</div>
        <div class="score-grade" style="color:{grade_color}">등급 {grade}</div>
        <div class="score-desc">종합 평판 점수</div>
    </div>
    """, unsafe_allow_html=True)

for col, key in zip([col_pos, col_neu, col_neg, col_mix],
                    ["positive","neutral","negative","mixed"]):
    with col:
        c = counts.get(key,0)
        pct = c/total*100 if total else 0
        st.markdown(f"""
        <div class="metric-card" style="background:{SENT_BG[key]}; border:1px solid {SENT_COLOR[key]}">
            <div style="font-size:22px">{SENT_ICON[key]}</div>
            <div class="metric-num" style="color:{SENT_COLOR[key]}">{c}</div>
            <div class="metric-pct" style="color:{SENT_COLOR[key]}">{pct:.1f}%</div>
            <div class="metric-label" style="color:{SENT_COLOR[key]}">{SENT_KR[key]}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # /panel-card

# ── 차트 + 키워드 섹션 (Lv2 흰 카드 2열) ────────────────────────────────────
chart_col, kw_col = st.columns([1, 1])

with chart_col:
    st.markdown('<div class="panel-card" style="height:100%">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">🍩 감성 분포 차트</div>', unsafe_allow_html=True)
    try:
        import plotly.graph_objects as go
        labels = [SENT_KR[k] for k in ["positive","neutral","negative","mixed"]]
        values = [counts.get(k,0) for k in ["positive","neutral","negative","mixed"]]
        colors = [SENT_COLOR[k] for k in ["positive","neutral","negative","mixed"]]
        fig = go.Figure(go.Pie(
            labels=labels, values=values,
            hole=0.55,
            marker=dict(colors=colors, line=dict(color="#fff", width=2)),
            textinfo="label+percent",
            textfont=dict(size=12, family="Pretendard"),
        ))
        fig.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            height=230,
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        for key in ["positive","neutral","negative","mixed"]:
            c = counts.get(key,0)
            pct = c/total*100 if total else 0
            st.markdown(f"""
            <div style="margin-bottom:8px;display:flex;align-items:center;gap:10px">
              <span style="color:{SENT_COLOR[key]};font-weight:600;min-width:32px">{SENT_KR[key]}</span>
              <div style="flex:1;background:#F0F0F0;border-radius:4px;height:8px">
                <div style="width:{pct:.0f}%;background:{SENT_COLOR[key]};height:100%;border-radius:4px"></div>
              </div>
              <span style="font-size:12px;color:#888;min-width:52px">{c}건 ({pct:.0f}%)</span>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with kw_col:
    st.markdown('<div class="panel-card" style="height:100%">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">🏷 주요 언급 키워드</div>', unsafe_allow_html=True)
    tag_counter = Counter(t for p in posts for t in p.get("tags",[]))
    if tag_counter:
        tags_html = ""
        for tag, cnt in tag_counter.most_common(12):
            tags_html += f'<span class="kw-tag">#{tag} <b style="color:#1428A0">{cnt}</b></span>'
        st.markdown(f'<div style="line-height:2.4">{tags_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<span style="color:#aaa;font-size:13px">태그 없음</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ── 내보내기 섹션 (Lv2 흰 카드) ──────────────────────────────────────────────
st.markdown('<div class="panel-card">', unsafe_allow_html=True)
st.markdown('<div class="panel-header">📤 데이터 출력 및 내보내기</div>', unsafe_allow_html=True)

csv_data = build_csv(posts)
txt_data = build_txt(posts, st.session_state.keyword_label, counts)
ai_data  = build_ai_prompt(posts, st.session_state.keyword_label, counts)
today    = datetime.date.today().strftime("%Y%m%d")

exp1, exp2, exp3, exp4 = st.columns(4)
with exp1:
    st.download_button(
        "📊 엑셀 저장 (.csv)",
        data=csv_data.encode("utf-8-sig"),
        file_name=f"dcx_cafe_{today}.csv",
        mime="text/csv",
        use_container_width=True,
    )
with exp2:
    st.download_button(
        "📄 텍스트 저장 (.txt)",
        data=txt_data.encode("utf-8"),
        file_name=f"dcx_cafe_{today}.txt",
        mime="text/plain",
        use_container_width=True,
    )
with exp3:
    st.download_button(
        "🤖 AI 분석 프롬프트",
        data=ai_data.encode("utf-8"),
        file_name=f"dcx_ai_prompt_{today}.txt",
        mime="text/plain",
        use_container_width=True,
    )
with exp4:
    if st.button("📋 AI 프롬프트 미리보기", use_container_width=True):
        st.session_state.show_ai = not st.session_state.get("show_ai", False)

if st.session_state.get("show_ai", False):
    st.markdown('<div class="inner-card">', unsafe_allow_html=True)
    st.text_area("AI 분석용 프롬프트 (복사하여 ChatGPT/Claude에 붙여넣기)",
                 value=ai_data, height=200, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # /panel-card


# ── 게시글 리스트 + 우측 패널 (Lv2 흰 카드 2열) ─────────────────────────────
list_col, detail_col = st.columns([3, 2])

with list_col:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">📋 수집 게시글</div>', unsafe_allow_html=True)

    # ── 필터/정렬 (Lv3 내부 섹션 #F5F5F5) ──
    st.markdown('<div class="inner-card">', unsafe_allow_html=True)
    filter_col, sort_col = st.columns([1, 1])
    with filter_col:
        st.markdown('<span style="font-size:11px;color:#888;font-weight:600">감성 필터</span>',
                    unsafe_allow_html=True)
        filter_tab = st.radio(
            "감성 필터",
            ["전체", "긍정", "중립", "부정", "혼재"],
            horizontal=True,
            label_visibility="collapsed",
        )
    with sort_col:
        st.markdown('<span style="font-size:11px;color:#888;font-weight:600">정렬 기준</span>',
                    unsafe_allow_html=True)
        sort_opt = st.radio(
            "정렬",
            ["최신순", "점수순(긍정↑)", "점수순(부정↑)", "등급순"],
            horizontal=True,
            label_visibility="collapsed",
        )
    st.markdown('</div>', unsafe_allow_html=True)  # /inner-card

    # 필터 적용
    sent_map = {"전체":None,"긍정":"positive","중립":"neutral","부정":"negative","혼재":"mixed"}
    filtered = posts if not sent_map[filter_tab] else \
               [p for p in posts if p.get("sentiment") == sent_map[filter_tab]]

    # 정렬 적용
    if sort_opt == "최신순":
        filtered = sorted(filtered, key=lambda p: p.get("pubDate",""), reverse=True)
    elif sort_opt == "점수순(긍정↑)":
        filtered = sorted(filtered, key=lambda p: p.get("sentiment_score",0), reverse=True)
    elif sort_opt == "점수순(부정↑)":
        filtered = sorted(filtered, key=lambda p: p.get("sentiment_score",0))
    else:
        grade_order = {"S":0,"A":1,"B":2,"C":3}
        filtered = sorted(filtered, key=lambda p: grade_order.get(p.get("quality_grade","C"),3))

    st.markdown(f'<p style="font-size:12px;color:#888;margin:4px 0 8px">'
                f'{len(filtered)}건 표시 중 (전체 {total}건)</p>', unsafe_allow_html=True)

    # 게시글 카드 렌더 (Lv3 흰 카드)
    for p in filtered[:50]:
        sent    = p.get("sentiment","neutral")
        sc      = p.get("sentiment_score",0)
        grade_p = p.get("quality_grade","C")
        pub     = fmt_date(p.get("pubDate",""))
        cafe    = p.get("cafename","")
        title   = clean(p.get("title","(제목 없음)"))
        desc    = clean(p.get("description",""))
        link    = p.get("link","")
        tags    = p.get("tags",[])

        badge_sent  = f'<span class="badge-{sent[:3]}">{SENT_ICON[sent]} {SENT_KR[sent]}</span>'
        badge_grade = f'<span class="badge-{grade_p.lower()}">{grade_p}등급</span>'
        tag_html    = "".join(f'<span class="post-tag">#{t}</span>' for t in tags[:4])
        link_html   = f'<a href="{link}" target="_blank" style="color:#1E6FE8;font-size:11px">🔗 원문 보기</a>' if link else ""

        st.markdown(f"""
        <div class="post-card {sent[:3]}">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                <span style="font-size:11px;color:#999">📌 {cafe}</span>
                <span>{badge_sent}&nbsp;{badge_grade}&nbsp;
                      <span style="font-size:11px;color:#aaa">{sc:+.1f}점</span></span>
            </div>
            <div class="post-title">{title}</div>
            <div class="post-body">{desc[:200]}{"…" if len(desc)>200 else ""}</div>
            <div style="display:flex;justify-content:space-between;align-items:center">
                <div><span class="post-meta">🕐 {pub}</span>&nbsp;&nbsp;{tag_html}</div>
                {link_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

    if len(filtered) > 50:
        st.markdown(f'<p style="font-size:11px;color:#aaa">상위 50건만 표시 — 전체 {len(filtered)}건은 CSV로 다운로드</p>',
                    unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # /panel-card

with detail_col:
    # ── 품질 등급 카드 ──
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">🏅 품질 등급별 현황</div>', unsafe_allow_html=True)

    grade_counts = Counter(p.get("quality_grade","C") for p in posts)
    for g, lbl, desc_g in [
        ("S","S등급","명의 언급 + 직접 경험 + 100자↑"),
        ("A","A등급","직접 경험 + 병원 언급 + 50자↑"),
        ("B","B등급","간접 경험 또는 병원 언급 + 30자↑"),
        ("C","C등급","최소 기준 통과 (참고용)"),
    ]:
        cnt = grade_counts.get(g,0)
        pct = cnt/total*100 if total else 0
        st.markdown(f"""
        <div style="display:flex;align-items:center;margin-bottom:6px">
            <span class="badge-{g.lower()}" style="min-width:44px;text-align:center">{lbl}</span>
            <div style="flex:1;background:#F0F0F0;border-radius:4px;height:8px;margin:0 10px">
                <div style="width:{pct:.0f}%;background:#1E6FE8;height:100%;border-radius:4px"></div>
            </div>
            <span style="font-size:12px;color:#555;min-width:58px">{cnt}건 ({pct:.0f}%)</span>
        </div>
        <div style="font-size:10px;color:#bbb;margin-bottom:10px;padding-left:52px">{desc_g}</div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── S등급 긍정 카드 ──
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">📌 S등급 긍정 (명의 브랜딩 활용)</div>', unsafe_allow_html=True)

    s_posts = [p for p in posts if p.get("quality_grade")=="S"
               and p.get("sentiment")=="positive"][:5]
    if s_posts:
        for p in s_posts:
            title = clean(p.get("title",""))
            desc  = clean(p.get("description",""))
            pub   = fmt_date(p.get("pubDate",""))
            link  = p.get("link","")
            st.markdown(f"""
            <div style="background:#E8F5EC;border-radius:8px;padding:10px 12px;margin-bottom:8px;
                        border-left:3px solid #1E8A3E">
                <div style="font-size:12px;font-weight:600;color:#111">{title}</div>
                <div style="font-size:11px;color:#555;margin-top:3px">{desc[:150]}…</div>
                <div style="font-size:10px;color:#999;margin-top:4px">🕐 {pub}
                    {"&nbsp;&nbsp;<a href='" + link + "' target='_blank' style='color:#1E6FE8'>원문</a>" if link else ""}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<span style="font-size:12px;color:#aaa">S등급 긍정 게시글이 없습니다.</span>',
                    unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 부정 긴급 대응 카드 ──
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">⚠️ 부정 S/A등급 (즉시 대응 필요)</div>', unsafe_allow_html=True)

    neg_urgent = [p for p in posts
                  if p.get("sentiment")=="negative"
                  and p.get("quality_grade") in ("S","A")][:5]
    if neg_urgent:
        for p in neg_urgent:
            title = clean(p.get("title",""))
            desc  = clean(p.get("description",""))
            pub   = fmt_date(p.get("pubDate",""))
            link  = p.get("link","")
            st.markdown(f"""
            <div style="background:#FDECEA;border-radius:8px;padding:10px 12px;margin-bottom:8px;
                        border-left:3px solid #C0392B">
                <div style="font-size:12px;font-weight:600;color:#111">{title}</div>
                <div style="font-size:11px;color:#555;margin-top:3px">{desc[:150]}…</div>
                <div style="font-size:10px;color:#999;margin-top:4px">🕐 {pub}
                    {"&nbsp;&nbsp;<a href='" + link + "' target='_blank' style='color:#C0392B'>원문</a>" if link else ""}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<span style="font-size:12px;color:#aaa">긴급 대응 필요 게시글 없음</span>',
                    unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

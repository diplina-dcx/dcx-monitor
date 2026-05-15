# -*- coding: utf-8 -*-
"""
DCX 카페 평판 모니터 — Streamlit 웹앱 v3.0
강북삼성병원 홍보팀 | 고객 경험(DCX) 수집 분석 도구
Copyright (c) 2026 Sang-Man Lee. All rights reserved.
"""

import streamlit as st
import requests
import re
import time
import datetime
import csv
import io
from collections import Counter

VERSION = "v3.4.0"

# ── 페이지 설정 ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=f"DCX 고객 경험 평판 모니터 {VERSION}",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

/* ── 폰트 ── */
html, body, [class*="css"] {
    font-family: 'Pretendard', 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif !important;
}

/* ══ 전체 배경 — 라이트 모드 ══ */
html, body { background-color: #F0F2F6 !important; }
.stApp { background-color: #F0F2F6 !important; }
.block-container { padding-top: 0.8rem !important; padding-bottom: 2rem !important; }

/* 모든 컨테이너 배경 투명 (흰 카드만 배경 가짐) */
.stApp > div,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
section[data-testid="stMain"],
section[data-testid="stMain"] > div,
[data-testid="stVerticalBlock"],
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stHorizontalBlock"],
[data-testid="stColumn"],
[data-testid="stColumn"] > div,
[data-testid="stColumn"] > div > div,
.element-container,
.stMarkdown { background-color: transparent !important; }

/* ── 텍스트 기본 검정 ── */
body, p, span, div, li { color: #111111; }
label { color: #333333; }
h1, h2, h3 { color: #111111; }

/* 라디오 텍스트 */
div[role="radiogroup"] label span,
div[role="radiogroup"] label p,
.stRadio label span { color: #111111 !important; font-size: 12px !important; }

/* 위젯 배경 투명 */
.stRadio, .stRadio > div, .stSelectSlider,
.stTextInput > div, .stTextArea > div { background-color: transparent !important; }

/* hr 완전 제거 */
hr { display: none !important; height: 0 !important; margin: 0 !important; }

/* 빈 마크다운 제거 */
.stMarkdown:empty, .stMarkdown p:empty { display: none !important; }

/* ══ 사이드바 — 흰 배경 ══ */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div { background-color: #FFFFFF !important; border-right: 0.5px solid #E4E4E4; }
[data-testid="stSidebar"] * { color: #111111 !important; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label { color: #333333 !important; font-size: 11px !important; }
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea {
    background: #F5F5F5 !important; color: #111 !important;
    border: 0.5px solid #E4E4E4 !important; border-radius: 8px !important; font-size: 12px !important;
}
[data-testid="stSidebar"] .stButton button {
    background: #1E6FE8 !important; color: #FFFFFF !important;
    border: none !important; border-radius: 8px !important;
    font-size: 12px !important; font-weight: 700 !important;
}
/* 사이드바 라디오 버튼 텍스트 */
[data-testid="stSidebar"] div[role="radiogroup"] label span { color: #111111 !important; font-size: 12px !important; }

/* ══ Lv2 흰 패널 카드 ══ */
.panel-card {
    background: #FFFFFF !important;
    border-radius: 20px; border: 0.5px solid #E4E4E4;
    padding: 18px 20px 20px; margin-bottom: 14px;
}
.panel-header {
    font-size: 10px !important; font-weight: 700 !important;
    letter-spacing: 0.1em; color: #111111 !important;
    text-transform: uppercase; border-bottom: 0.5px solid #EBEBEB;
    padding-bottom: 7px; margin-bottom: 12px;
}

/* Lv3 내부 섹션 */
.inner-card {
    background: #F5F5F5 !important; border-radius: 8px;
    border: 0.5px solid #EBEBEB; padding: 10px 12px; margin-bottom: 10px;
}

/* ══ 메인 헤더 ══ */
.main-header {
    background: linear-gradient(135deg, #1428A0 0%, #1E6FE8 100%);
    border-radius: 16px; padding: 20px 26px; margin-bottom: 14px;
}
.main-header h1 { margin:0; font-size:19px; font-weight:700; color:#FFFFFF !important; }
.main-header p  { margin:3px 0 0; font-size:12px; color:#AAC9F8 !important; }
.main-header span { color:#FFFFFF !important; }

/* ══ 감성 뱃지 ══ */
.badge-pos { background:#E8F5EC; color:#1E8A3E !important; border-radius:100px; padding:2px 9px; font-size:10px; font-weight:600; }
.badge-neu { background:#FFF3E0; color:#E65100 !important; border-radius:100px; padding:2px 9px; font-size:10px; font-weight:600; }
.badge-neg { background:#FDECEA; color:#C0392B !important; border-radius:100px; padding:2px 9px; font-size:10px; font-weight:600; }
.badge-mix { background:#F3EAF9; color:#7B3FA0 !important; border-radius:100px; padding:2px 9px; font-size:10px; font-weight:600; }
.badge-s   { background:#1E6FE8; color:#fff !important; border-radius:4px; padding:1px 7px; font-size:9px; font-weight:700; }
.badge-a   { background:#1428A0; color:#fff !important; border-radius:4px; padding:1px 7px; font-size:9px; font-weight:700; }
.badge-b   { background:#777;    color:#fff !important; border-radius:4px; padding:1px 7px; font-size:9px; font-weight:700; }
.badge-c   { background:#BBB;    color:#fff !important; border-radius:4px; padding:1px 7px; font-size:9px; font-weight:700; }

/* ══ 게시글 카드 ══ */
.post-card {
    background: #FFFFFF !important; border-radius: 10px;
    padding: 12px 14px; margin-bottom: 7px;
    border-left: 3px solid #E4E4E4;
    border-top: 0.5px solid #F0F0F0;
    border-right: 0.5px solid #F0F0F0;
    border-bottom: 0.5px solid #F0F0F0;
}
.post-card.pos { border-left-color: #2ECC71; }
.post-card.neg { border-left-color: #E74C3C; }
.post-card.neu { border-left-color: #E67E22; }
.post-card.mix { border-left-color: #9B59B6; }
.post-title { font-size:12px; font-weight:600; color:#111111 !important; margin-bottom:3px; line-height:1.5; }
.post-body  { font-size:11px; color:#555555 !important; line-height:1.6; margin-bottom:4px; }
.post-meta  { font-size:10px; color:#AAAAAA !important; }
.post-tag   { background:#E8F0FD; color:#0D3A8A !important; border-radius:100px; padding:1px 6px; font-size:9px; margin-right:3px; }

/* ══ 지표 카드 ══ */
.metric-card { border-radius: 10px; padding: 12px 8px; text-align: center; }
.metric-num  { font-size:24px; font-weight:700; line-height:1; }
.metric-pct  { font-size:11px; margin-top:2px; }
.metric-lbl  { font-size:10px; margin-top:3px; opacity:0.85; }

/* ══ 점수 박스 ══ */
.score-box   { background:#E8F0FD !important; border:1px solid #C5D8F9; border-radius:12px; padding:14px; text-align:center; }
.score-num   { font-size:38px; font-weight:700; color:#1E6FE8 !important; line-height:1; }
.score-grade { font-size:14px; font-weight:600; margin-top:3px; }
.score-desc  { font-size:10px; color:#888888 !important; margin-top:3px; }

/* ══ 키워드 태그 ══ */
.kw-tag { display:inline-block; background:#E8F0FD; color:#0D3A8A !important; border-radius:100px; padding:3px 9px; font-size:11px; margin:2px; }

/* ══ 버튼 ══ */
.stButton button, .stDownloadButton button {
    border-radius: 8px !important; font-family: 'Pretendard', sans-serif !important;
    font-weight: 600 !important; font-size: 12px !important;
}
.stDownloadButton button {
    background-color: #FFFFFF !important; border: 1px solid #E4E4E4 !important; color: #111111 !important;
}
.stDownloadButton button:hover {
    background-color: #F0F4FF !important; border-color: #1E6FE8 !important; color: #1E6FE8 !important;
}

/* ══ 버전 뱃지 ══ */
.ver-badge {
    display:inline-block; background:#E8F0FD; color:#1428A0 !important;
    border-radius:100px; padding:2px 9px; font-size:10px; font-weight:700;
    margin-left:8px; vertical-align:middle;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# 감성 분석 로직
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
FIRST_PERSON   = ["나는","저는","제가","내가","우리 엄마","우리 아버지",
                  "아버지가","어머니가","남편이","아내가","직접","제 경험","경험담"]
TAG_MAP = {
    "암/종양":   ["암","종양","항암","방사선치료","뇌종양","폐암","위암","간암"],
    "심뇌혈관":  ["심장","뇌졸중","뇌경색","심근경색","협심증","혈관","스텐트"],
    "척추/관절": ["척추","디스크","관절","무릎","허리","척추수술","고관절"],
    "신경계":    ["신경","파킨슨","치매","루게릭","뇌수술"],
    "소화기":    ["위암","대장","췌장","담낭","복강경"],
    "호흡기":    ["폐","기관지","천식","폐렴","호흡"],
    "희귀/난치": ["희귀","난치","루게릭"],
    "소아":      ["소아","어린이","신생아"],
    "여성건강":  ["산부인과","자궁","유방","임신","출산","난소"],
    "로봇수술":  ["로봇수술","다빈치"],
    "명의":      ["명의","교수님"],
    "대기문제":  ["대기","기다","줄"],
    "친절도":    ["친절","불친절"],
    "비용":      ["비용","비싸","바가지"],
    "검사":      ["MRI","CT","PET","조직검사"],
}

def clean(text):
    return text.replace("<b>","").replace("</b>","").strip()

def score_post(post):
    text = clean(post.get("title","") + " " + post.get("description",""))
    if len(text) < 15:       return _invalid(post,"초단문")
    for p in SPAM_PATTERNS:
        if p.search(text):   return _invalid(post,"스팸")
    if len(text) < 30:       return _invalid(post,"30자 미만")
    for r in RUMOR_PATTERNS:
        if r in text:        return _invalid(post,"소문성")

    pos = sum(w for k,w in POSITIVE_KW.items() if k in text)
    neg = sum(w for k,w in NEGATIVE_KW.items() if k in text)
    net = pos - neg

    sent = ("mixed"    if pos>=2.0 and neg>=2.0 else
            "positive" if net>1.0 else
            "negative" if net<-1.0 else "neutral")

    n    = len(text)
    h_dr = any(k in text for k in ["교수","의사","선생님","집도"])
    h_hp = any(k in text for k in ["병원","의원","의료원","센터"])
    h_fp = any(k in text for k in FIRST_PERSON)
    s_cl = sent in ("positive","negative")

    grade = ("S" if h_fp and h_dr and n>=100 and s_cl else
             "A" if h_fp and h_hp and n>=50 else
             "B" if n>=30 else "C")

    tags = [t for t,kws in TAG_MAP.items() if any(k in text for k in kws)]
    post.update({"spam_flag":False,"valid":True,"sentiment":sent,
                 "sentiment_score":round(net,2),"quality_grade":grade,"tags":tags})
    return post

def _invalid(post, reason):
    post.update({"spam_flag":True,"valid":False,"sentiment":"neutral",
                 "sentiment_score":0.0,"quality_grade":"C","tags":[],"exclude_reason":reason})
    return post


# ── 네이버 API ────────────────────────────────────────────────────────────────
def fetch_cafe(keyword, max_count, cid, csec):
    url  = "https://openapi.naver.com/v1/search/cafearticle.json"
    hdrs = {"X-Naver-Client-Id":cid,"X-Naver-Client-Secret":csec}
    res, start = [], 1
    while len(res) < max_count:
        batch  = min(100, max_count - len(res))
        params = {"query":keyword,"display":batch,"start":start,"sort":"date"}
        try:
            r = requests.get(url, params=params, headers=hdrs, timeout=10)
            if r.status_code != 200: st.warning(f"API {r.status_code}"); break
            items = r.json().get("items",[])
            if not items: break
            for item in items: item["_keyword"] = keyword
            res.extend(items); start += len(items)
            if start > 1000: break
        except Exception as e: st.error(f"오류: {e}"); break
        time.sleep(0.4)
    return res[:max_count]


# ── 유틸 ─────────────────────────────────────────────────────────────────────
SENT_KR    = {"positive":"긍정","neutral":"중립","negative":"부정","mixed":"혼재"}
SENT_COLOR = {"positive":"#2ECC71","neutral":"#E67E22","negative":"#E74C3C","mixed":"#9B59B6"}
SENT_BG    = {"positive":"#E8F9F0","neutral":"#FFF3E0","negative":"#FDECEA","mixed":"#F3EAF9"}
SENT_ICON  = {"positive":"😊","neutral":"😐","negative":"😟","mixed":"🔀"}

def fmt_date(raw):
    try:
        return datetime.datetime.strptime(raw,"%a, %d %b %Y %H:%M:%S +0900").strftime("%Y-%m-%d %H:%M")
    except: return raw

def rep_score(cnt, total):
    if not total: return 0
    return max(0,min(100,round(50+(cnt.get("positive",0)-cnt.get("negative",0))/total*50)))

def grade_label(s):
    return (("A+","#1E8A3E") if s>=80 else ("A","#1E8A3E") if s>=70 else
            ("B","#B07D00") if s>=60 else ("C","#B07D00") if s>=50 else ("D","#C0392B"))

def build_csv(posts):
    buf  = io.StringIO()
    cols = ["title","cafename","pubDate","sentiment","sentiment_score","quality_grade","description","link","tags"]
    w    = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    for p in posts:
        row = {k:p.get(k,"") for k in cols}
        row["title"]       = clean(row["title"])
        row["description"] = clean(row["description"])
        row["tags"]        = ", ".join(row.get("tags") or [])
        w.writerow(row)
    return buf.getvalue()

def build_txt(posts, kw, cnt):
    total = len(posts)
    lines = [
        "[DCX 카페 평판 분석 보고서]",
        f"검색 키워드 : {kw}",
        f"수집 일시   : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"버전        : DCX Cafe Monitor {VERSION}",
        f"총 수집건수 : {total}건",
        f"감성 분포   : 긍정 {cnt.get('positive',0)} / 중립 {cnt.get('neutral',0)} / "
        f"부정 {cnt.get('negative',0)} / 혼재 {cnt.get('mixed',0)}",
        "="*60,"",
    ]
    for p in posts:
        sent = SENT_KR.get(p.get("sentiment","neutral"),"중립")
        lines += [
            f"[{sent} / {p.get('sentiment_score',0):+.1f} / {p.get('quality_grade','C')}등급]",
            f"제목 : {clean(p.get('title',''))}",
            f"카페 : {p.get('cafename','')} | 날짜 : {fmt_date(p.get('pubDate',''))}",
            f"내용 : {clean(p.get('description',''))[:500]}",
            f"링크 : {p.get('link','')}","",
        ]
    return "\n".join(lines)

def build_ai(posts, kw, cnt):
    total = len(posts)
    lines = [
        "아래는 네이버 카페에서 수집한 환자·보호자 실제 경험 게시글입니다.",
        f"검색 키워드: {kw} | {total}건 | {VERSION}",
        f"감성: 긍정 {cnt.get('positive',0)} / 중립 {cnt.get('neutral',0)} / "
        f"부정 {cnt.get('negative',0)} / 혼재 {cnt.get('mixed',0)}",
        "","--- 수집 데이터 (S/A등급 우선, 상위 30건) ---",
    ]
    top = [p for p in posts if p.get("quality_grade") in ("S","A")][:30]
    top += [p for p in posts if p.get("quality_grade") not in ("S","A")][:max(0,30-len(top))]
    for p in top[:30]:
        sent = SENT_KR.get(p.get("sentiment","neutral"),"중립")
        lines += [f"[{sent}] {clean(p.get('title',''))}", clean(p.get("description",""))[:300],""]
    lines += ["="*60,"위 데이터를 분석하여 다음 항목을 정리해 주세요:",
              "1. 핵심 긍정 요인","2. 핵심 부정 요인 및 개선점",
              "3. 주요 언급 의료진·진료과",
              "4. 홍보 메시지에 활용할 환자 언어·표현",
              "5. 신환 유치를 위한 콘텐츠 기획 제안"]
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# 메인 UI
# ══════════════════════════════════════════════════════════════════════════════

# ── 사이드바 (화이트, 컴팩트) ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f'<div style="padding:8px 0 4px">'
        f'<span style="font-size:14px;font-weight:700;color:#111">🏥 DCX 고객 경험 평판 모니터</span>'
        f'<span class="ver-badge">{VERSION}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div style="border-top:0.5px solid #EBEBEB;margin:8px 0"></div>', unsafe_allow_html=True)

    st.markdown('<p style="font-size:10px;font-weight:700;color:#999;letter-spacing:0.08em;margin:0 0 5px">🔑 NAVER API</p>', unsafe_allow_html=True)
    client_id  = st.text_input("cid",  value=st.secrets.get("NAVER_CLIENT_ID",""),
                               placeholder="Client ID", label_visibility="collapsed")
    client_sec = st.text_input("csec", value=st.secrets.get("NAVER_CLIENT_SECRET",""),
                               type="password", placeholder="Client Secret", label_visibility="collapsed")

    st.markdown('<div style="border-top:0.5px solid #EBEBEB;margin:8px 0"></div>', unsafe_allow_html=True)

    st.markdown('<p style="font-size:10px;font-weight:700;color:#999;letter-spacing:0.08em;margin:0 0 5px">🔍 검색 키워드</p>', unsafe_allow_html=True)
    keywords_raw = st.text_area("kw",
        placeholder="의료진 이름, 진료과, 질환명\n쉼표 또는 줄바꿈으로 구분",
        height=75, label_visibility="collapsed")

    st.markdown('<p style="font-size:10px;color:#999;margin:0 0 4px">최대 수집 건수 (키워드당)</p>', unsafe_allow_html=True)
    max_count = st.radio("mc", options=[30,50,100,200], index=2, horizontal=True, label_visibility="collapsed")

    st.markdown('<div style="border-top:0.5px solid #EBEBEB;margin:8px 0"></div>', unsafe_allow_html=True)

    st.markdown('<p style="font-size:10px;font-weight:700;color:#999;letter-spacing:0.08em;margin:0 0 5px">🚫 제외 키워드</p>', unsafe_allow_html=True)
    excl_raw = st.text_input("excl",
        value="동물병원,수의사,한의원,한약,성형외과,미용,보톡스",
        label_visibility="collapsed")

    st.markdown('<div style="border-top:0.5px solid #EBEBEB;margin:8px 0"></div>', unsafe_allow_html=True)
    run_btn = st.button("▶  수집 시작", type="primary", use_container_width=True)
    st.markdown('<div style="border-top:0.5px solid #EBEBEB;margin:8px 0"></div>', unsafe_allow_html=True)
    st.markdown(
        f'<p style="font-size:10px;color:#CCC;text-align:center;line-height:1.7">'
        f'Copyright © 2026 Sang-Man Lee<br>DCX Cafe Monitor {VERSION}</p>',
        unsafe_allow_html=True)


# ── 헤더 ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="main-header">
  <h1>📊 DCX 고객 경험 평판 모니터
    <span style="font-size:13px;opacity:0.65;font-weight:400">{VERSION}</span>
  </h1>
  <p>네이버 카페 고객 경험 수집 분석</p>
</div>
""", unsafe_allow_html=True)


# ── 세션 초기화 ───────────────────────────────────────────────────────────────
if "posts"         not in st.session_state: st.session_state.posts         = []
if "keyword_label" not in st.session_state: st.session_state.keyword_label = ""


# ── 수집 실행 ─────────────────────────────────────────────────────────────────
if run_btn:
    if not client_id or not client_sec:
        st.error("사이드바에서 네이버 API 키를 입력해 주세요.")
        st.stop()
    keywords = [k.strip() for k in re.split(r"[,\n]", keywords_raw) if k.strip()]
    if not keywords:
        st.error("검색 키워드를 입력해 주세요.")
        st.stop()

    excl_kws  = [k.strip() for k in excl_raw.split(",") if k.strip()]
    all_posts = []
    prog = st.progress(0, text="수집 준비 중...")
    for i, kw in enumerate(keywords):
        prog.progress(i/len(keywords), text=f"'{kw}' 검색 중... ({i+1}/{len(keywords)})")
        all_posts.extend(fetch_cafe(kw, max_count, client_id, client_sec))
    prog.progress(1.0, text="감성 분석 중...")

    if excl_kws:
        all_posts = [p for p in all_posts
                     if not any(ek in clean(p.get("title","")+p.get("description","")) for ek in excl_kws)]

    seen, unique = set(), []
    for p in all_posts:
        k = p.get("link","")
        if k not in seen: seen.add(k); unique.append(p)

    scored = [score_post(p) for p in unique]
    scored = [p for p in scored if p.get("valid",True)]
    scored.sort(key=lambda p: p.get("sentiment_score",0), reverse=True)

    st.session_state.posts         = scored
    st.session_state.keyword_label = ", ".join(keywords)
    prog.empty()
    st.success(f"✅ 수집 완료 — 유효 게시글 {len(scored)}건 (중복·스팸 제외)")


# ── 결과 없음 ─────────────────────────────────────────────────────────────────
posts = st.session_state.posts
if not posts:
    st.markdown("""
    <div class="panel-card" style="text-align:center;padding:48px 20px">
        <div style="font-size:38px">🔍</div>
        <div style="font-size:14px;color:#333;margin-top:10px;font-weight:600">수집을 시작해 주세요</div>
        <div style="font-size:12px;color:#888;margin-top:6px">좌측 사이드바에서 키워드 입력 후 수집 시작</div>
    </div>""", unsafe_allow_html=True)
    st.stop()


# ── 요약 카드 ─────────────────────────────────────────────────────────────────
counts = Counter(p.get("sentiment","neutral") for p in posts)
total  = len(posts)
score  = rep_score(counts, total)
grade, grade_color = grade_label(score)

st.markdown('<div class="panel-card">', unsafe_allow_html=True)
st.markdown('<div class="panel-header">📊 감성 분석 요약</div>', unsafe_allow_html=True)
c0,c1,c2,c3,c4 = st.columns([1.2,1,1,1,1])
with c0:
    st.markdown(f"""<div class="score-box">
        <div class="score-num">{score}</div>
        <div class="score-grade" style="color:{grade_color}">등급 {grade}</div>
        <div class="score-desc">종합 평판 점수</div>
    </div>""", unsafe_allow_html=True)
for col, key in zip([c1,c2,c3,c4],["positive","neutral","negative","mixed"]):
    with col:
        c = counts.get(key,0); pct = c/total*100 if total else 0
        st.markdown(f"""<div class="metric-card" style="background:{SENT_BG[key]};border:1px solid {SENT_COLOR[key]}">
            <div style="font-size:20px">{SENT_ICON[key]}</div>
            <div class="metric-num" style="color:{SENT_COLOR[key]}">{c}</div>
            <div class="metric-pct" style="color:{SENT_COLOR[key]}">{pct:.1f}%</div>
            <div class="metric-lbl" style="color:{SENT_COLOR[key]}">{SENT_KR[key]}</div>
        </div>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# ── 차트 + 키워드 ────────────────────────────────────────────────────────────
cc, kc = st.columns([1,1])
with cc:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">🍩 감성 분포 차트</div>', unsafe_allow_html=True)
    try:
        import plotly.graph_objects as go
        fig = go.Figure(go.Pie(
            labels=[SENT_KR[k] for k in ["positive","neutral","negative","mixed"]],
            values=[counts.get(k,0) for k in ["positive","neutral","negative","mixed"]],
            hole=0.55,
            marker=dict(colors=[SENT_COLOR[k] for k in ["positive","neutral","negative","mixed"]],
                        line=dict(color="#fff",width=2)),
            textinfo="label+percent", textfont=dict(size=11,family="Pretendard"),
        ))
        fig.update_layout(margin=dict(t=5,b=5,l=5,r=5),height=210,
                          showlegend=False,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        for key in ["positive","neutral","negative","mixed"]:
            c = counts.get(key,0); pct = c/total*100 if total else 0
            st.markdown(f"""<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
              <span style="color:{SENT_COLOR[key]};font-weight:600;min-width:28px;font-size:12px">{SENT_KR[key]}</span>
              <div style="flex:1;background:#F0F0F0;border-radius:4px;height:7px">
                <div style="width:{pct:.0f}%;background:{SENT_COLOR[key]};height:100%;border-radius:4px"></div>
              </div>
              <span style="font-size:11px;color:#888;min-width:50px">{c}건 {pct:.0f}%</span>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with kc:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">🏷 주요 언급 키워드</div>', unsafe_allow_html=True)
    tag_cnt = Counter(t for p in posts for t in p.get("tags",[]))
    if tag_cnt:
        html = "".join(f'<span class="kw-tag">#{t} <b style="color:#1428A0">{c}</b></span>'
                       for t,c in tag_cnt.most_common(12))
        st.markdown(f'<div style="line-height:2.5">{html}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<span style="font-size:12px;color:#aaa">태그 없음</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ── 내보내기 ─────────────────────────────────────────────────────────────────
st.markdown('<div class="panel-card">', unsafe_allow_html=True)
st.markdown('<div class="panel-header">📤 데이터 출력 및 내보내기</div>', unsafe_allow_html=True)

csv_data = build_csv(posts)
txt_data = build_txt(posts, st.session_state.keyword_label, counts)
ai_data  = build_ai(posts, st.session_state.keyword_label, counts)
today    = datetime.date.today().strftime("%Y%m%d")
slug     = re.sub(r"[^\w가-힣]","_", st.session_state.keyword_label)[:20]

e1,e2,e3,e4 = st.columns(4)
with e1:
    st.download_button("📊 엑셀 저장 (.csv)",
        data=csv_data.encode("utf-8-sig"),
        file_name=f"DCX_{slug}_{today}_{VERSION}.csv",
        mime="text/csv", use_container_width=True)
with e2:
    st.download_button("📄 텍스트 저장 (.txt)",
        data=txt_data.encode("utf-8"),
        file_name=f"DCX_{slug}_{today}_{VERSION}.txt",
        mime="text/plain", use_container_width=True)
with e3:
    st.download_button("🤖 AI 분석 프롬프트",
        data=ai_data.encode("utf-8"),
        file_name=f"DCX_AI_{slug}_{today}_{VERSION}.txt",
        mime="text/plain", use_container_width=True)
with e4:
    if st.button("📋 AI 프롬프트 미리보기", use_container_width=True):
        st.session_state.show_ai = not st.session_state.get("show_ai",False)

if st.session_state.get("show_ai",False):
    st.markdown('<div class="inner-card">', unsafe_allow_html=True)
    st.text_area("ai", value=ai_data, height=170, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)


# ── 게시글 + 우측 패널 ───────────────────────────────────────────────────────
lc, dc = st.columns([3,2])

with lc:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">📋 수집 게시글</div>', unsafe_allow_html=True)

    # 필터/정렬 툴바
    st.markdown('<div class="inner-card">', unsafe_allow_html=True)
    fc, sc = st.columns([1,1])
    with fc:
        st.markdown('<span style="font-size:10px;color:#888;font-weight:700">감성 필터</span>', unsafe_allow_html=True)
        filter_tab = st.radio("ft",["전체","긍정","중립","부정","혼재"],
                              horizontal=True, label_visibility="collapsed")
    with sc:
        st.markdown('<span style="font-size:10px;color:#888;font-weight:700">정렬 기준</span>', unsafe_allow_html=True)
        sort_opt = st.radio("st",["최신순","점수순(긍정↑)","점수순(부정↑)","등급순"],
                            horizontal=True, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    sent_map = {"전체":None,"긍정":"positive","중립":"neutral","부정":"negative","혼재":"mixed"}
    filtered = posts if not sent_map[filter_tab] else \
               [p for p in posts if p.get("sentiment")==sent_map[filter_tab]]
    if   sort_opt=="최신순":        filtered = sorted(filtered,key=lambda p:p.get("pubDate",""),reverse=True)
    elif sort_opt=="점수순(긍정↑)": filtered = sorted(filtered,key=lambda p:p.get("sentiment_score",0),reverse=True)
    elif sort_opt=="점수순(부정↑)": filtered = sorted(filtered,key=lambda p:p.get("sentiment_score",0))
    else:                           filtered = sorted(filtered,key=lambda p:{"S":0,"A":1,"B":2,"C":3}.get(p.get("quality_grade","C"),3))

    st.markdown(f'<p style="font-size:11px;color:#888;margin:0 0 8px">{len(filtered)}건 표시 (전체 {total}건)</p>',
                unsafe_allow_html=True)

    # ── 게시글 카드 ──
    for idx, p in enumerate(filtered[:50]):
        sent  = p.get("sentiment","neutral")
        sc_v  = p.get("sentiment_score",0)
        grd   = p.get("quality_grade","C")
        pub   = fmt_date(p.get("pubDate",""))
        cafe  = p.get("cafename","")
        title = clean(p.get("title","(제목 없음)"))
        desc  = clean(p.get("description",""))
        link  = p.get("link","")
        tags  = p.get("tags",[])
        uid   = f"post_{idx}"

        bs       = f'<span class="badge-{sent[:3]}">{SENT_ICON[sent]} {SENT_KR[sent]}</span>'
        bg       = f'<span class="badge-{grd.lower()}">{grd}등급</span>'
        th       = "".join(f'<span class="post-tag">#{t}</span>' for t in tags[:4])
        link_btn = (f'<a href="{link}" target="_blank" style="font-size:11px;color:#1E6FE8;'
                    f'text-decoration:none;font-weight:600">🔗 카페 원문</a>') if link else ""

        st.markdown(f"""
        <div class="post-card {sent[:3]}">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
                <span style="font-size:10px;color:#aaa">📌 {cafe}</span>
                <span>{bs}&nbsp;{bg}&nbsp;<span style="font-size:10px;color:#bbb">{sc_v:+.1f}점</span></span>
            </div>
            <div class="post-title">{title}</div>
            <div class="post-body">{desc[:200]}{"…" if len(desc)>200 else ""}</div>
            <div style="display:flex;justify-content:space-between;align-items:center;margin-top:2px">
                <div><span class="post-meta">🕐 {pub}</span>&nbsp;&nbsp;{th}</div>
                {link_btn}
            </div>
        </div>""", unsafe_allow_html=True)


with dc:
    # 품질 등급
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">🏅 품질 등급별 현황</div>', unsafe_allow_html=True)
    gc = Counter(p.get("quality_grade","C") for p in posts)
    for g,lbl,dsc in [("S","S등급","명의+직접경험+100자↑"),("A","A등급","직접경험+병원명+50자↑"),
                       ("B","B등급","병원명 또는 30자↑"),("C","C등급","최소기준(참고용)")]:
        cnt = gc.get(g,0); pct = cnt/total*100 if total else 0
        st.markdown(f"""
        <div style="display:flex;align-items:center;margin-bottom:4px">
            <span class="badge-{g.lower()}" style="min-width:42px;text-align:center">{lbl}</span>
            <div style="flex:1;background:#F0F0F0;border-radius:3px;height:6px;margin:0 8px">
                <div style="width:{pct:.0f}%;background:#1E6FE8;height:100%;border-radius:3px"></div>
            </div>
            <span style="font-size:11px;color:#555;min-width:52px">{cnt}건 {pct:.0f}%</span>
        </div>
        <div style="font-size:10px;color:#bbb;margin-bottom:9px;padding-left:48px">{dsc}</div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # S등급 긍정
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">📌 S등급 긍정 — 명의 브랜딩 활용</div>', unsafe_allow_html=True)
    sp = [p for p in posts if p.get("quality_grade")=="S" and p.get("sentiment")=="positive"][:5]
    if sp:
        for p in sp:
            t=clean(p.get("title","")); d=clean(p.get("description","")); pub=fmt_date(p.get("pubDate","")); lk=p.get("link","")
            st.markdown(f"""
            <div style="background:#E8F5EC;border-radius:8px;padding:9px 11px;margin-bottom:7px;border-left:3px solid #1E8A3E">
                <div style="font-size:12px;font-weight:600;color:#111">{t}</div>
                <div style="font-size:11px;color:#555;margin-top:3px">{d[:130]}…</div>
                <div style="font-size:10px;color:#999;margin-top:3px">🕐 {pub}
                {"&nbsp;<a href='"+lk+"' target='_blank' style='color:#1E6FE8;font-size:10px'>원문</a>" if lk else ""}
                </div></div>""", unsafe_allow_html=True)
    else:
        st.markdown('<span style="font-size:12px;color:#aaa">S등급 긍정 게시글 없음</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 부정 긴급
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">⚠️ 부정 S/A등급 — 즉시 대응 필요</div>', unsafe_allow_html=True)
    np_ = [p for p in posts if p.get("sentiment")=="negative" and p.get("quality_grade") in ("S","A")][:5]
    if np_:
        for p in np_:
            t=clean(p.get("title","")); d=clean(p.get("description","")); pub=fmt_date(p.get("pubDate","")); lk=p.get("link","")
            st.markdown(f"""
            <div style="background:#FDECEA;border-radius:8px;padding:9px 11px;margin-bottom:7px;border-left:3px solid #C0392B">
                <div style="font-size:12px;font-weight:600;color:#111">{t}</div>
                <div style="font-size:11px;color:#555;margin-top:3px">{d[:130]}…</div>
                <div style="font-size:10px;color:#999;margin-top:3px">🕐 {pub}
                {"&nbsp;<a href='"+lk+"' target='_blank' style='color:#C0392B;font-size:10px'>원문</a>" if lk else ""}
                </div></div>""", unsafe_allow_html=True)
    else:
        st.markdown('<span style="font-size:12px;color:#aaa">긴급 대응 게시글 없음</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

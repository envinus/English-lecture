"""
어린이 영어 학습 Streamlit 애플리케이션
StoryWeaver 동화책을 활용한 영어 학습 프로그램
"""

import streamlit as st
import json
import os
from gtts import gTTS
import base64
from io import BytesIO
import speech_recognition as sr
from difflib import SequenceMatcher
import random
from datetime import datetime, timedelta
from crawler import StoryWeaverCrawler
from pdf_processor import PDFProcessor
from gemini_helper import evaluate_pronunciation, generate_vocabulary_quiz

# 페이지 설정
st.set_page_config(
    page_title="어린이 영어 학습",
    page_icon="📚",
    layout="wide"
)

# CSS 스타일 적용 - 모던 글래스모피즘 디자인
st.markdown("""
<style>
    /* 웹폰트 불러오기 */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    /* 애니메이션 정의 */
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }

    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }

    /* 색상 변수 정의 - 모던 글래스모피즘 */
    :root {
        --color-primary: #667eea;
        --color-primary-light: #764ba2;
        --color-secondary: #f093fb;
        --color-accent: #4facfe;
        --color-success: #43e97b;
        --color-warning: #fa709a;
        --color-text-primary: #2d3748;
        --color-text-secondary: #4a5568;
        --color-text-light: #718096;
        --border-radius: 20px;
        --border-radius-large: 24px;
        --spacing-card: 24px;
        --glass-bg: rgba(255, 255, 255, 0.75);
        --glass-border: rgba(255, 255, 255, 0.3);
    }

    /* 전체 배경 - 그라디언트 */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-size: 200% 200%;
        animation: gradient-shift 15s ease infinite;
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    }

    /* 제목 스타일 - 글로우 효과 */
    .main-title {
        font-size: 2rem;
        text-align: center;
        padding: 1rem 2rem;
        color: #ffffff;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.5),
                     0 0 40px rgba(102, 126, 234, 0.3);
        letter-spacing: -0.02em;
    }

    /* h2 제목 크기 조정 */
    h2 {
        font-size: 1.5rem !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* 이미지 스타일 - 글래스 효과 */
    .story-image {
        border-radius: var(--border-radius-large);
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3),
                    0 0 0 1px rgba(255, 255, 255, 0.2);
        margin: 0.5rem auto;
        display: block;
        max-width: 100%;
        max-height: 50vh;
        object-fit: contain;
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        padding: 8px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .story-image:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 48px rgba(102, 126, 234, 0.4),
                    0 0 0 1px rgba(255, 255, 255, 0.3);
    }

    /* 영어 텍스트 카드 - 글래스모피즘 */
    .english-text {
        font-size: 1.6rem;
        color: var(--color-text-primary);
        text-align: center;
        padding: 2.5rem;
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: var(--border-radius);
        margin: var(--spacing-card) 0;
        font-weight: 600;
        line-height: 1.9;
        letter-spacing: 0.02em;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2),
                    inset 0 0 0 1px var(--glass-border);
        border: 1px solid rgba(255, 255, 255, 0.4);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .english-text:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 48px rgba(102, 126, 234, 0.3),
                    inset 0 0 0 1px rgba(255, 255, 255, 0.5);
    }

    /* 한국어 텍스트 카드 - 부드러운 글래스 */
    .korean-text {
        font-size: 1.1rem;
        color: var(--color-text-secondary);
        text-align: center;
        padding: 1.2rem 1.5rem;
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-radius: var(--border-radius);
        margin: 0.8rem 0;
        line-height: 1.7;
        box-shadow: 0 4px 24px rgba(102, 126, 234, 0.15),
                    inset 0 0 0 1px rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
        transition: all 0.3s ease;
    }

    .korean-text:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
    }

    /* 페이지 현황 표시 */
    .page-status {
        font-size: 1.1rem;
        text-align: center;
        color: rgba(255, 255, 255, 0.95);
        font-weight: 600;
        padding: 0.5rem 0;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }

    /* 컨트롤 패널 - 글래스모피즘 */
    .control-panel {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: var(--border-radius);
        padding: 1rem;
        margin: 0.5rem 0 1rem 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.25),
                    inset 0 0 0 1px rgba(255, 255, 255, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.5);
    }

    /* 버튼 그룹 구분선 */
    .button-divider {
        width: 1px;
        height: 35px;
        background: linear-gradient(to bottom,
            rgba(102, 126, 234, 0) 0%,
            rgba(102, 126, 234, 0.3) 50%,
            rgba(102, 126, 234, 0) 100%);
        margin: auto 0.5rem;
    }

    /* Streamlit 버튼 커스터마이징 */
    .stButton > button {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 1) 0%, rgba(118, 75, 162, 1) 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    .stButton > button:disabled {
        background: rgba(200, 200, 200, 0.5);
        color: rgba(255, 255, 255, 0.7);
        box-shadow: none;
    }

    /* 체크박스 스타일 */
    .stCheckbox {
        font-weight: 600;
    }

    /* 진행률 바 개선 */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        border-radius: 10px;
    }

    /* 학습 진행률 텍스트 */
    .progress-text {
        text-align: center;
        color: rgba(255, 255, 255, 0.9);
        font-weight: 600;
        font-size: 0.9rem;
        margin-top: 0.3rem;
        margin-bottom: 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }

    /* 성공 메시지 - 그라디언트 텍스트 */
    .success-message {
        font-size: 2rem;
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 800;
        text-shadow: 0 4px 12px rgba(67, 233, 123, 0.3);
    }

    /* 재시도 메시지 */
    .try-again-message {
        font-size: 1.4rem;
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 700;
    }

    /* 버튼 스타일 - 글래스모피즘 + 애니메이션 */
    .stButton>button {
        font-size: 1rem;
        padding: 0.9rem 2rem;
        border-radius: 16px;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255, 255, 255, 0.5);
        color: var(--color-primary);
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);
        cursor: pointer;
        letter-spacing: 0.02em;
    }

    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: rgba(255, 255, 255, 0.8);
    }

    .stButton>button:active {
        transform: translateY(-1px) scale(1);
    }

    .stButton>button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        transform: none !important;
    }

    /* 진행률 바 - 그라디언트 애니메이션 */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-size: 200% 100%;
        animation: shimmer 2s linear infinite;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }

    /* Metric 스타일 - 글래스 카드 */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-light) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.95rem;
        color: var(--color-text-secondary);
        font-weight: 600;
        letter-spacing: 0.03em;
    }

    /* Caption 스타일 */
    .stCaption {
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.8);
        font-weight: 500;
    }

    /* Selectbox 스타일 강화 */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 10px;
        border: 2px solid rgba(255, 255, 255, 0.5);
        transition: all 0.3s ease;
        padding: 0.3rem 0.5rem;
        font-size: 0.95rem;
    }

    .stSelectbox > div > div:hover {
        border-color: var(--color-primary);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
        transform: translateY(-1px);
    }

    /* Radio 버튼 스타일 강화 */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.4);
    }

    /* Checkbox 스타일 강화 */
    .stCheckbox {
        padding: 0.5rem;
        border-radius: 8px;
        transition: all 0.3s ease;
    }

    .stCheckbox:hover {
        background: rgba(255, 255, 255, 0.1);
    }

    .stCheckbox input:checked + div {
        background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-light) 100%);
    }

    /* Success/Error/Warning 메시지 강화 */
    .stSuccess, .stError, .stWarning, .stInfo {
        backdrop-filter: blur(10px);
        border-radius: 12px;
        border-left: 4px solid;
        animation: slideIn 0.3s ease;
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    /* 사이드바 헤더 스타일 */
    .sidebar .markdown-text-container h3 {
        color: var(--color-primary);
        font-weight: 800;
        text-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
    }

    .sidebar .markdown-text-container h4 {
        color: var(--color-text-primary);
        font-weight: 700;
        margin-top: 1rem;
    }

    /* Input 필드 스타일 */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 10px;
        border: 2px solid rgba(255, 255, 255, 0.5);
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--color-primary);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    /* Expander 스타일 - 글래스 효과 */
    .streamlit-expanderHeader {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--color-text-primary);
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 0.8rem 1.2rem;
        transition: all 0.3s ease;
    }

    .streamlit-expanderHeader:hover {
        background: rgba(255, 255, 255, 0.8);
        transform: translateX(4px);
    }

    /* Info/Success/Warning 박스 - 글래스 효과 */
    .stAlert {
        border-radius: 16px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    }

    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(102, 126, 234, 0.95) 0%, rgba(118, 75, 162, 0.95) 100%);
        backdrop-filter: blur(20px);
    }

    [data-testid="stSidebar"] * {
        color: white !important;
    }

    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stCheckbox label,
    [data-testid="stSidebar"] .stSlider label {
        color: rgba(255, 255, 255, 0.95) !important;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# 세션 상태 초기화
if 'current_story' not in st.session_state:
    st.session_state.current_story = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0
if 'show_korean' not in st.session_state:
    st.session_state.show_korean = False
if 'learning_mode' not in st.session_state:
    st.session_state.learning_mode = "읽기"
if 'quiz_question' not in st.session_state:
    st.session_state.quiz_question = None
if 'quiz_score' not in st.session_state:
    st.session_state.quiz_score = 0
if 'quiz_total' not in st.session_state:
    st.session_state.quiz_total = 0
if 'speech_speed' not in st.session_state:
    st.session_state.speech_speed = 1.0


# 접근성/UX 설정 초기화
if 'ui_font_scale' not in st.session_state:
    st.session_state.ui_font_scale = 1.0
if 'ui_high_contrast' not in st.session_state:
    st.session_state.ui_high_contrast = False

# 동적 CSS: 글꼴 크기, 포커스 가시성, 모바일 터치 타깃, 반응형 디자인
_scale = st.session_state.ui_font_scale
st.markdown(f"""
<style>
/* Font scaling overrides with glassmorphism design */
.main-title {{ font-size: calc({_scale} * 2.5rem); }}
.english-text {{ font-size: calc({_scale} * 1.6rem); line-height: 1.9; }}
.korean-text {{ font-size: calc({_scale} * 1.15rem); line-height: 1.8; }}
.stButton>button {{ font-size: calc({_scale} * 1rem); padding: calc({_scale} * 0.9rem) calc({_scale} * 2rem); min-height: 48px; }}
[data-testid="stMetricValue"] {{ font-size: calc({_scale} * 2.5rem); }}
[data-testid="stMetricLabel"] {{ font-size: calc({_scale} * 0.95rem); }}

/* Focus visibility - 접근성 강화 */
button:focus, a:focus, input:focus, select:focus, textarea:focus {{
  outline: 3px solid rgba(102, 126, 234, 0.8) !important;
  outline-offset: 3px;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2) !important;
}}

/* Responsive design - Tablet (768px and below) */
@media (max-width: 768px) {{
  .main-title {{
    font-size: calc({_scale} * 2rem);
    padding: 1.5rem;
  }}
  .english-text {{
    font-size: calc({_scale} * 1.4rem);
    padding: 2rem;
  }}
  .korean-text {{
    font-size: calc({_scale} * 1.05rem);
    padding: 1.5rem;
  }}
  .story-image {{
    max-width: 90%;
    margin: 20px auto;
  }}
  .stButton>button {{
    font-size: calc({_scale} * 0.95rem);
    padding: calc({_scale} * 0.85rem) calc({_scale} * 1.8rem);
    min-height: 48px;
  }}
  [data-testid="stMetricValue"] {{
    font-size: calc({_scale} * 2rem);
  }}
}}

/* Mobile tweaks (600px and below) */
@media (max-width: 600px) {{
  .main-title {{
    font-size: calc({_scale} * 1.8rem);
    padding: 1.2rem;
  }}
  .english-text {{
    font-size: calc({_scale} * 1.3rem);
    padding: 1.8rem;
    line-height: 2;
  }}
  .korean-text {{
    font-size: calc({_scale} * 1rem);
    padding: 1.3rem;
    line-height: 1.9;
  }}
  .story-image {{
    max-width: 100%;
    margin: 16px auto;
    border-radius: 20px;
  }}
  .stButton>button {{
    font-size: calc({_scale} * 0.95rem);
    padding: calc({_scale} * 0.8rem) calc({_scale} * 1.5rem);
    min-height: 50px;
    width: 100%;
  }}
  .success-message {{
    font-size: calc({_scale} * 1.6rem);
  }}
  .try-again-message {{
    font-size: calc({_scale} * 1.2rem);
  }}
  [data-testid="stMetricValue"] {{
    font-size: calc({_scale} * 1.8rem);
  }}
  [data-testid="stMetricLabel"] {{
    font-size: calc({_scale} * 0.85rem);
  }}
}}

/* Very small screens (400px and below) */
@media (max-width: 400px) {{
  .main-title {{
    font-size: calc({_scale} * 1.5rem);
  }}
  .english-text {{
    font-size: calc({_scale} * 1.2rem);
  }}
  .korean-text {{
    font-size: calc({_scale} * 0.95rem);
  }}
  [data-testid="stMetricValue"] {{
    font-size: calc({_scale} * 1.5rem);
  }}
}}
</style>
""", unsafe_allow_html=True)

# 고대비 모드 CSS - 접근성 강화
if st.session_state.ui_high_contrast:
    st.markdown(
        """
        <style>
        .main {
            background: #ffffff !important;
            animation: none !important;
        }
        .main-title {
            color: #000000 !important;
            text-shadow: none !important;
            background: none !important;
            -webkit-text-fill-color: #000000 !important;
        }
        .english-text {
            color: #000000 !important;
            background: #ffffff !important;
            border: 3px solid #000000 !important;
            box-shadow: none !important;
            backdrop-filter: none !important;
        }
        .english-text:hover {
            transform: none !important;
        }
        .korean-text {
            color: #000000 !important;
            background: #f5f5f5 !important;
            border: 3px solid #000000 !important;
            box-shadow: none !important;
            backdrop-filter: none !important;
        }
        .korean-text:hover {
            transform: none !important;
        }
        .stButton>button {
            background: #000000 !important;
            color: #ffffff !important;
            border: 3px solid #000000 !important;
            box-shadow: none !important;
            backdrop-filter: none !important;
        }
        .stButton>button:hover {
            background: #333333 !important;
            transform: none !important;
            box-shadow: none !important;
        }
        [data-testid="stMetricValue"] {
            color: #000000 !important;
            background: none !important;
            -webkit-text-fill-color: #000000 !important;
        }
        [data-testid="stSidebar"] {
            background: #e0e0e0 !important;
            backdrop-filter: none !important;
        }
        [data-testid="stSidebar"] * {
            color: #000000 !important;
        }
        .success-message {
            color: #006400 !important;
            background: none !important;
            -webkit-text-fill-color: #006400 !important;
            text-shadow: none !important;
        }
        .try-again-message {
            color: #8B4513 !important;
            background: none !important;
            -webkit-text-fill-color: #8B4513 !important;
        }
        .streamlit-expanderHeader {
            background: #f0f0f0 !important;
            color: #000000 !important;
            border: 2px solid #000000 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def load_stories():
    """저장된 동화책 목록을 불러옵니다."""
    try:
        with open('stories.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []


def load_learning_stats():
    """학습 통계를 불러옵니다."""
    try:
        with open('learning_stats.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {
            'total_pages_read': 0,
            'total_speaking_practice': 0,
            'total_quiz_attempts': 0,
            'total_quiz_correct': 0,
            'completed_stories': [],
            'last_study_date': None,
            'study_streak': 0,
            'study_dates': []
        }


def save_learning_stats(stats):
    """학습 통계를 저장합니다."""
    with open('learning_stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def update_page_read():
    """페이지 읽기 통계를 업데이트합니다."""
    stats = load_learning_stats()
    stats['total_pages_read'] = stats.get('total_pages_read', 0) + 1
    update_study_streak(stats)
    save_learning_stats(stats)


def update_speaking_practice():
    """말하기 연습 통계를 업데이트합니다."""
    stats = load_learning_stats()
    stats['total_speaking_practice'] = stats.get('total_speaking_practice', 0) + 1
    update_study_streak(stats)
    save_learning_stats(stats)


def update_quiz_stats(is_correct):
    """퀴즈 통계를 업데이트합니다."""
    stats = load_learning_stats()
    stats['total_quiz_attempts'] = stats.get('total_quiz_attempts', 0) + 1
    if is_correct:
        stats['total_quiz_correct'] = stats.get('total_quiz_correct', 0) + 1
    update_study_streak(stats)
    save_learning_stats(stats)


def update_study_streak(stats):
    """연속 학습 일수를 업데이트합니다."""
    from datetime import datetime, timedelta

    today = datetime.now().strftime('%Y-%m-%d')
    last_date = stats.get('last_study_date')

    if last_date != today:
        if last_date:
            last_datetime = datetime.strptime(last_date, '%Y-%m-%d')
            today_datetime = datetime.strptime(today, '%Y-%m-%d')
            days_diff = (today_datetime - last_datetime).days

            if days_diff == 1:
                stats['study_streak'] = stats.get('study_streak', 0) + 1
            elif days_diff > 1:
                stats['study_streak'] = 1
        else:
            stats['study_streak'] = 1

        stats['last_study_date'] = today

        # 학습 날짜 기록
        if 'study_dates' not in stats:
            stats['study_dates'] = []
        if today not in stats['study_dates']:
            stats['study_dates'].append(today)


def mark_story_completed(story_id, story_title):
    """동화책 완료 기록을 추가합니다."""
    stats = load_learning_stats()
    if 'completed_stories' not in stats:
        stats['completed_stories'] = []

    # 이미 완료한 동화책이 아니면 추가
    if story_id not in [s.get('id') for s in stats['completed_stories']]:
        stats['completed_stories'].append({
            'id': story_id,
            'title': story_title,
            'completed_date': datetime.now().strftime('%Y-%m-%d')
        })

    update_study_streak(stats)
    save_learning_stats(stats)


def text_to_speech(text, lang='en', speed=1.0):
    """텍스트를 음성으로 변환합니다. (속도 조절 가능)"""
    try:
        from pydub import AudioSegment
        import tempfile
        import os
        import time

        # gTTS로 음성 생성
        # speed가 0.7 이하면 slow=True 사용
        slow = (speed <= 0.7)
        tts = gTTS(text=text, lang=lang, slow=slow)

        # 임시 파일에 저장 (자동 삭제하지 않음)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_path = temp_file.name
        temp_file.close()  # 파일 핸들을 먼저 닫음

        tts.save(temp_path)

        # 오디오 로드
        audio = AudioSegment.from_mp3(temp_path)

        # 속도 조절 (slow=True일 때는 이미 느리므로 추가 조절 안함)
        if not slow and speed != 1.0:
            # frame_rate를 조절하여 속도 변경
            new_frame_rate = int(audio.frame_rate * (1.0 / speed))
            audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_frame_rate})
            audio = audio.set_frame_rate(44100)  # 표준 샘플링 레이트로 재설정

        # BytesIO로 변환
        fp = BytesIO()
        audio.export(fp, format='mp3')
        fp.seek(0)

        # 임시 파일 삭제 시도 (실패해도 무시)
        try:
            time.sleep(0.1)  # 짧은 대기
            os.unlink(temp_path)
        except Exception:
            pass  # 삭제 실패 시 무시 (시스템이 나중에 정리)

        return fp
    except ImportError:
        # pydub가 없으면 기본 gTTS만 사용
        try:
            slow = (speed <= 0.7)
            tts = gTTS(text=text, lang=lang, slow=slow)
            fp = BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return fp
        except Exception as e:
            st.error(f"음성 변환 오류: {str(e)}")
            return None
    except Exception as e:
        st.error(f"음성 변환 오류: {str(e)}")
        return None


def play_audio(audio_fp, autoplay=True):
    """오디오를 재생합니다."""
    if audio_fp:
        st.audio(audio_fp, format='audio/mp3', autoplay=autoplay)


def recognize_speech():
    """마이크로 음성을 인식합니다."""
    try:
        import pyaudio
        # 명시적으로 PyAudio를 사용하도록 설정
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("🎤 듣고 있습니다... 말씀해주세요!")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

        st.info("🔄 음성을 분석하고 있습니다...")
        text = recognizer.recognize_google(audio, language='en-US')
        return text
    except ImportError:
        st.error("오디오 처리를 위한 라이브러리가 설치되지 않았습니다.")
        return None
    except sr.WaitTimeoutError:
        st.warning("⏰ 시간이 초과되었습니다. 다시 시도해주세요.")
        return None
    except sr.UnknownValueError:
        st.warning("❓ 음성을 인식할 수 없습니다. 다시 시도해주세요.")
        return None
    except sr.RequestError as e:
        st.error(f"음성 인식 서비스 오류: {str(e)}")
        return None
    except OSError as e:
        # Windows에서 오디오 장치 접근 오류
        if "No Default Input Device Available" in str(e):
            st.error("❌ 오디오 입력 장치를 찾을 수 없습니다. 마이크가 연결되어 있는지 확인해주세요.")
        else:
            st.error(f"오디오 장치 오류: {str(e)}")
        return None
    except Exception as e:
        # 오류 메시지를 소문자로 변환하여 다양한 변형 처리
        error_msg = str(e).lower()
        original_msg = str(e)
        
        if "flac" in error_msg or "flac conversion" in error_msg:
            st.error("❌ 오디오 처리에 문제가 발생했습니다. Windows 시스템에 FLAC 변환 도구가 설치되어 있지 않아요.")
            st.info("💡 해결 방법:")
            st.info("1. https://github.com/microsoft/vcpkg 에서 vcpkg를 설치하고, 'vcpkg install flac' 명령어를 실행하거나")
            st.info("2. 또는 https://xiph.org/flac/download.html 에서 FLAC 도구를 설치하세요.")
            st.info("3. 가장 쉬운 방법은 Anaconda 환경을 사용하는 경우: 'conda install -c conda-forge flac' 명령어를 사용하세요.")
        elif "audio" in error_msg or "portaudio" in error_msg or "device" in error_msg:
            st.error(f"오디오 장치 오류: {original_msg}")
        else:
            st.error(f"오류가 발생했습니다: {original_msg}")
        return None


def calculate_similarity(text1, text2):
    """두 텍스트의 유사도를 계산합니다."""
    text1 = text1.lower().strip()
    text2 = text2.lower().strip()
    return SequenceMatcher(None, text1, text2).ratio()


# ==================== 사이드바 ====================
with st.sidebar:
    st.markdown("### 📚 영어 학습 프로그램")
    st.markdown("---")

    # 1. 동화책 선택 (최우선 - 항상 표시)
    stories = load_stories()
    if stories:
        st.markdown("#### 📖 동화책 선택")
        story_titles = [s['title'] for s in stories]
        selected_title = st.selectbox(
            "학습할 동화책을 선택하세요",
            story_titles,
            key="story_selector",
            label_visibility="collapsed"
        )

        # 선택된 동화책 설정
        for story in stories:
            if story['title'] == selected_title:
                st.session_state.current_story = story
                break

        if st.session_state.current_story:
            st.success(f"✅ {st.session_state.current_story['title']}")
            st.caption(f"📄 총 {len(st.session_state.current_story['pages'])} 페이지")
    else:
        st.warning("📚 동화책을 추가해주세요!")

    st.markdown("---")

    # 2. 학습 모드 선택 (두 번째 중요 - 항상 표시)
    st.markdown("#### 🎯 학습 모드")
    st.session_state.learning_mode = st.radio(
        "모드 선택",
        ["📖 읽기", "🎮 단어 퀴즈"],
        index=["📖 읽기", "🎮 단어 퀴즈"].index(
            f"{'📖 ' if st.session_state.learning_mode == '읽기' else '🎮 '}{ st.session_state.learning_mode}"
        ) if st.session_state.learning_mode in ["읽기", "단어 퀴즈"] else 0,
        label_visibility="collapsed"
    )
    st.session_state.learning_mode = st.session_state.learning_mode.split()[-1]
    # Normalize radio value to stable internal keys
    _mode = st.session_state.learning_mode
    _aliases = {"퀴즈": "단어 퀴즈"}
    st.session_state.learning_mode = _aliases.get(_mode, _mode)

    st.markdown("---")

    # 3. 학습 통계 (expander)
    stats = load_learning_stats()
    with st.expander("📊 나의 학습 통계"):
        col1, col2 = st.columns(2)

        with col1:
            st.metric("🔥 연속 학습", f"{stats['study_streak']}일")
            st.metric("📖 읽은 페이지", f"{stats['total_pages_read']}개")

        with col2:
            st.metric("🗣️ 말하기 연습", f"{stats['total_speaking_practice']}회")
            quiz_rate = int((stats['total_quiz_correct'] / stats['total_quiz_attempts'] * 100)) if stats['total_quiz_attempts'] > 0 else 0
            st.metric("🎯 퀴즈 정답률", f"{quiz_rate}%")

        # 완료한 동화책
        if stats['completed_stories']:
            st.markdown("**✅ 완료한 동화책:**")
            for story in stats['completed_stories'][-3:]:  # 최근 3개만 표시
                st.caption(f"• {story['title']}")

        # 학습 일수
        if stats['study_dates']:
            st.markdown(f"**📅 총 학습 일수:** {len(stats['study_dates'])}일")

    st.markdown("---")

    # 4. 동화책 추가 (expander)
    with st.expander("➕ 동화책 추가하기"):
        # 수동 동화책 추가
        st.markdown("**✍️ 수동으로 만들기**")
        st.info("StoryWeaver는 외부 크롤링을 차단합니다. 브라우저에서 보면서 텍스트를 복사해서 입력해주세요!")

        manual_title = st.text_input("동화책 제목", placeholder="예: The Cat's Fault")
        manual_pages = st.number_input("페이지 수", min_value=1, max_value=50, value=5)

        if st.button("📄 페이지 입력 시작", use_container_width=True):
            st.session_state.manual_pages = []
            st.session_state.manual_title = manual_title
            st.session_state.creating_manual = True
            st.session_state.manual_total_pages = manual_pages

        if st.session_state.get('creating_manual'):
            st.markdown(f"**{st.session_state.manual_title}** - 페이지 {len(st.session_state.manual_pages) + 1}/{st.session_state.manual_total_pages}")

            page_text = st.text_area("영어 텍스트를 입력하세요", height=100, key=f"page_text_{len(st.session_state.manual_pages)}")
            page_image = st.text_input("이미지 URL (선택사항)", key=f"page_img_{len(st.session_state.manual_pages)}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("➕ 페이지 추가", use_container_width=True):
                    if page_text.strip():
                        from deep_translator import GoogleTranslator
                        translator = GoogleTranslator(source='en', target='ko')
                        ko_text = translator.translate(page_text.strip())

                        st.session_state.manual_pages.append({
                            'image_url': page_image,
                            'en': page_text.strip(),
                            'ko': ko_text
                        })
                        st.success(f"페이지 {len(st.session_state.manual_pages)} 추가됨!")

                        if len(st.session_state.manual_pages) >= st.session_state.manual_total_pages:
                            # 저장
                            story_data = {
                                'id': str(__import__('uuid').uuid4()),
                                'title': st.session_state.manual_title,
                                'source_url': 'manual',
                                'pages': st.session_state.manual_pages
                            }
                            crawler = StoryWeaverCrawler()
                            if crawler.save_story(story_data):
                                st.success(f"✅ '{story_data['title']}' 동화책이 저장되었습니다!")
                                st.balloons()
                                st.session_state.creating_manual = False
                                st.rerun()
                    else:
                        st.warning("텍스트를 입력해주세요!")

            with col2:
                if st.button("❌ 취소", use_container_width=True):
                    st.session_state.creating_manual = False
                    st.rerun()

        st.markdown("---")

        # PDF 업로드
        st.markdown("**📄 PDF로 추가하기**")
        st.info("StoryWeaver에서 다운로드한 PDF 파일을 업로드하세요!")

        pdf_file = st.file_uploader(
            "PDF 파일 선택",
            type=['pdf'],
            help="StoryWeaver에서 다운로드한 동화책 PDF를 선택하세요"
        )

        pdf_title = st.text_input(
            "동화책 제목 (선택사항)",
            placeholder="제목을 입력하지 않으면 파일명이 사용됩니다",
            key="pdf_title"
        )

        if st.button("🚀 PDF 처리하기", use_container_width=True, key="process_pdf"):
            if pdf_file:
                try:
                    with st.spinner("PDF를 처리하고 번역하는 중입니다... 조금만 기다려주세요! ⏳"):
                        processor = PDFProcessor()
                        story_data = processor.process_pdf(
                            pdf_file,
                            title=pdf_title if pdf_title else None
                        )

                        # 에러 체크
                        if story_data and story_data.get('error'):
                            st.error(f"❌ PDF 처리 실패: {story_data['error']}")

                            if story_data.get('error_details'):
                                with st.expander("🔍 상세 오류 정보 보기"):
                                    st.code(story_data['error_details'])

                            st.warning("💡 해결 방법:")
                            st.info("1. PDF가 이미지로만 구성되어 있다면 텍스트가 포함된 PDF를 사용하세요")
                            st.info("2. PDF 파일이 손상되지 않았는지 확인하세요")
                            st.info("3. 다른 PDF 파일로 시도해보세요")

                        # 정상 처리
                        elif story_data and story_data.get('pages') and len(story_data['pages']) > 0:
                            if processor.save_story(story_data):
                                st.success(f"✅ '{story_data['title']}' 동화책이 추가되었습니다!")
                                st.info(f"📚 총 {len(story_data['pages'])} 페이지가 추출되었습니다.")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ 저장에 실패했습니다.")

                        # 페이지가 없는 경우
                        else:
                            st.error("❌ PDF에서 데이터를 추출할 수 없습니다.")
                            st.warning("💡 가능한 원인:")
                            st.info("1. PDF가 이미지로만 구성되어 있을 수 있습니다 (스캔본)")
                            st.info("2. PDF에 텍스트가 없거나 너무 짧을 수 있습니다")
                            st.info("3. PDF 파일이 손상되었을 수 있습니다")

                except Exception as e:
                    st.error(f"❌ 예상치 못한 오류 발생: {str(e)}")
                    st.error(f"오류 타입: {type(e).__name__}")
                    with st.expander("🔍 상세 오류 정보 보기"):
                        import traceback
                        st.code(traceback.format_exc())
            else:
                st.warning("⚠️ PDF 파일을 선택해주세요.")

    # 5. 동화책 관리 (expander - 선택된 동화책이 있을 때만)
    if st.session_state.current_story:
        with st.expander("⚙️ 동화책 관리"):
            st.markdown("**🗑️ 동화책 삭제**")
            if st.button("🗑️ 이 동화책 삭제하기", use_container_width=True, type="secondary"):
                st.session_state.confirm_delete = True

            if st.session_state.get('confirm_delete'):
                st.warning(f"정말로 '{st.session_state.current_story['title']}'을(를) 삭제하시겠습니까?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ 예, 삭제합니다", use_container_width=True):
                        # 동화책 삭제
                        stories = load_stories()
                        stories = [s for s in stories if s['id'] != st.session_state.current_story['id']]

                        # JSON 파일에 저장
                        with open('stories.json', 'w', encoding='utf-8') as f:
                            json.dump(stories, f, ensure_ascii=False, indent=2)

                        st.success("삭제되었습니다!")
                        st.session_state.current_story = None
                        st.session_state.confirm_delete = False
                        st.rerun()

                with col2:
                    if st.button("❌ 아니오, 취소", use_container_width=True):
                        st.session_state.confirm_delete = False
                        st.rerun()

            st.markdown("---")
            st.markdown("**✏️ 텍스트 수정**")
            if st.button("✏️ 페이지 텍스트 수정하기", use_container_width=True):
                st.session_state.editing_story = True

            if st.session_state.get('editing_story'):
                st.info("수정할 페이지를 선택하세요")

                page_options = [f"페이지 {i+1}: {p['en'][:30]}..." for i, p in enumerate(st.session_state.current_story['pages'])]
                selected_page_idx = st.selectbox(
                    "페이지 선택",
                    range(len(page_options)),
                    format_func=lambda x: page_options[x],
                    key="edit_page_selector"
                )

                current_page = st.session_state.current_story['pages'][selected_page_idx]

                # 자동 번역된 텍스트가 있으면 사용
                auto_translated_ko = st.session_state.get(f"auto_translated_{selected_page_idx}", None)

                st.markdown("**현재 영어 텍스트:**")
                new_en_text = st.text_area(
                    "영어 텍스트",
                    value=current_page['en'],
                    height=100,
                    key=f"edit_en_{selected_page_idx}"
                )

                st.markdown("**현재 한국어 번역:**")
                ko_value = auto_translated_ko if auto_translated_ko else current_page['ko']
                new_ko_text = st.text_area(
                    "한국어 번역",
                    value=ko_value,
                    height=100,
                    key=f"edit_ko_{selected_page_idx}"
                )

                # 자동 번역 결과 표시
                if auto_translated_ko:
                    st.info(f"✅ 자동 번역되었습니다! 필요시 수정 후 저장하세요.")

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("💾 저장", use_container_width=True):
                        # 텍스트 업데이트
                        stories = load_stories()
                        for story in stories:
                            if story['id'] == st.session_state.current_story['id']:
                                story['pages'][selected_page_idx]['en'] = new_en_text
                                story['pages'][selected_page_idx]['ko'] = new_ko_text
                                break

                        # JSON 파일에 저장
                        with open('stories.json', 'w', encoding='utf-8') as f:
                            json.dump(stories, f, ensure_ascii=False, indent=2)

                        st.success("저장되었습니다!")
                        st.session_state.current_story['pages'][selected_page_idx]['en'] = new_en_text
                        st.session_state.current_story['pages'][selected_page_idx]['ko'] = new_ko_text
                        # 자동 번역 상태 초기화
                        if f"auto_translated_{selected_page_idx}" in st.session_state:
                            del st.session_state[f"auto_translated_{selected_page_idx}"]
                        st.rerun()

                with col2:
                    if st.button("🔄 자동 번역", use_container_width=True):
                        with st.spinner("번역 중..."):
                            from gemini_helper import translate_to_korean
                            auto_ko = translate_to_korean(new_en_text)
                            st.session_state[f"auto_translated_{selected_page_idx}"] = auto_ko
                        st.rerun()

                with col3:
                    if st.button("❌ 취소", use_container_width=True):
                        st.session_state.editing_story = False
                        # 자동 번역 상태 초기화
                        if f"auto_translated_{selected_page_idx}" in st.session_state:
                            del st.session_state[f"auto_translated_{selected_page_idx}"]
                        st.rerun()

    st.markdown("---")

    # 6. 설정 (expander)
    with st.expander("🎨 설정"):
        st.session_state.ui_font_scale = st.slider(
            "글자 크기", min_value=0.9, max_value=1.6, step=0.05, value=st.session_state.ui_font_scale
        )
        st.session_state.ui_high_contrast = st.checkbox(
            "고대비 모드", value=st.session_state.ui_high_contrast
        )
        st.caption("단축키 안내: ←/→ 이전·다음, 1–4 보기 선택")


# ==================== 메인 영역 ====================
st.markdown('<h1 class="main-title">📚 어린이 영어 학습 프로그램</h1>', unsafe_allow_html=True)

if not st.session_state.current_story:
    st.info("👈 왼쪽 사이드바에서 동화책을 선택하거나 새로운 동화책을 추가해주세요!")
    st.markdown("""
    ### 사용 방법
    1. **동화책 추가**: StoryWeaver 웹사이트에서 동화책 URL을 복사하여 추가하세요
    2. **동화책 선택**: 저장된 동화책 중 하나를 선택하세요
    3. **학습 모드**: 읽기 또는 단어 퀴즈 모드를 선택하세요
    4. **즐겁게 학습**: 재미있게 영어를 공부해요! 🎉
    """)
else:
    story = st.session_state.current_story

    # ==================== 읽기 모드 ====================
    if st.session_state.learning_mode == "읽기":
        if story['pages']:
            current_page = st.session_state.current_page
            page = story['pages'][current_page]

            # 이미지 표시
            if page['image_url']:
                st.markdown(f'<img src="{page["image_url"]}" alt="{story["title"]} - 페이지 {current_page + 1} 삽화" class="story-image">', unsafe_allow_html=True)

            if page['en']:
                # 페이지 현황 표시
                st.markdown(f"<div class='page-status'>페이지 {current_page + 1} / {len(story['pages'])}</div>", unsafe_allow_html=True)

                # 컨트롤 패널
                st.markdown('<div class="control-panel">', unsafe_allow_html=True)

                # 컨트롤 행 - 그룹별로 구분
                col1, col2, sep1, col3, col4, sep2, col5, col6 = st.columns([1.5, 1, 0.1, 1, 1.2, 0.1, 0.8, 0.8])

                with col1:
                    # 속도 선택
                    speed_option = st.selectbox(
                        "🎵 발음 속도",
                        options=["0.5x (매우 느림)", "0.7x (느림)", "1.0x (보통)"],
                        index=2 if st.session_state.speech_speed == 1.0 else (1 if st.session_state.speech_speed == 0.7 else 0),
                        key=f"speed_{current_page}"
                    )
                    # 속도 값 추출
                    if "0.5x" in speed_option:
                        st.session_state.speech_speed = 0.5
                    elif "0.7x" in speed_option:
                        st.session_state.speech_speed = 0.7
                    else:
                        st.session_state.speech_speed = 1.0

                with col2:
                    if st.button("🔊 듣기", use_container_width=True):
                        with st.spinner("음성 생성 중..."):
                            audio_base64 = text_to_speech(page['en'], speed=st.session_state.speech_speed)
                            if audio_base64:
                                play_audio(audio_base64)

                with sep1:
                    st.markdown('<div class="button-divider"></div>', unsafe_allow_html=True)

                with col3:
                    st.session_state.show_korean = st.checkbox(
                        "🇰🇷 해석",
                        value=st.session_state.show_korean,
                        key=f"show_korean_{current_page}"
                    )

                with col4:
                    if st.button("🔄 다시 번역하기", use_container_width=True):
                        try:
                            from gemini_helper import translate_to_korean
                            with st.spinner("번역 중..."):
                                translated_text = translate_to_korean(page['en'])
                                st.session_state.current_story['pages'][current_page]['ko'] = translated_text
                            st.session_state.show_korean = True
                            st.success("번역 완료!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"번역 중 오류 발생: {str(e)}")
                            st.warning("Gemini API 키가 설정되어 있는지 확인해주세요.")

                with sep2:
                    st.markdown('<div class="button-divider"></div>', unsafe_allow_html=True)

                with col5:
                    if st.button("⬅️ 이전", disabled=(current_page == 0), use_container_width=True):
                        st.session_state.current_page -= 1
                        st.rerun()

                with col6:
                    if st.button("다음 ➡️", disabled=(current_page >= len(story['pages']) - 1), use_container_width=True):
                        # 통계 업데이트: 페이지 읽기
                        update_page_read()

                        # 마지막 페이지 완료 시 동화책 완료 기록
                        if current_page == len(story['pages']) - 2:  # 다음이 마지막 페이지
                            mark_story_completed(story['id'], story['title'])
                            st.success(f"🎉 '{story['title']}' 완독을 축하합니다!")
                            st.balloons()

                        st.session_state.current_page += 1
                        st.rerun()

                # 컨트롤 패널 닫기
                st.markdown('</div>', unsafe_allow_html=True)

                # 한국어 번역 표시
                if st.session_state.show_korean and page['ko']:
                    st.markdown(f'<div class="korean-text">{page["ko"]}</div>', unsafe_allow_html=True)

            # 진행 상황 시각화 (구분선 제거)
            progress = (current_page + 1) / len(story['pages'])
            st.progress(progress)
            st.markdown(f"<div class='progress-text'>📊 학습 진행률: {int(progress * 100)}%</div>", unsafe_allow_html=True)

    # ==================== 단어 학습 모드 ====================
    elif st.session_state.learning_mode == "단어 퀴즈":
        st.markdown("## 📚 핵심 단어 학습")

        # 세션 상태 초기화
        if 'vocabulary_data' not in st.session_state:
            st.session_state.vocabulary_data = None
        if 'vocabulary_cards' not in st.session_state:
            st.session_state.vocabulary_cards = []
        if 'current_card_index' not in st.session_state:
            st.session_state.current_card_index = 0
        if 'show_answer' not in st.session_state:
            st.session_state.show_answer = False
        if 'last_vocabulary_story_id' not in st.session_state:
            st.session_state.last_vocabulary_story_id = None

        # 책이 변경되면 vocabulary 데이터 리셋
        if st.session_state.last_vocabulary_story_id != story['id']:
            st.session_state.vocabulary_data = None
            st.session_state.vocabulary_cards = []
            st.session_state.current_card_index = 0
            st.session_state.show_answer = False
            st.session_state.last_vocabulary_story_id = story['id']

        # 핵심 단어 추출
        if st.session_state.vocabulary_data is None:
            with st.spinner("핵심 단어를 분석하고 있습니다..."):
                from gemini_helper import extract_key_vocabulary, generate_vocabulary_cards
                st.session_state.vocabulary_data = extract_key_vocabulary(story)

                if st.session_state.vocabulary_data and st.session_state.vocabulary_data.get('vocabulary'):
                    st.session_state.vocabulary_cards = generate_vocabulary_cards(
                        st.session_state.vocabulary_data['vocabulary']
                    )
                    st.success(f"✅ {len(st.session_state.vocabulary_data['vocabulary'])}개의 핵심 단어를 추출했습니다!")
                else:
                    st.error("❌ 단어 추출에 실패했습니다.")
                    st.info("💡 Gemini API 할당량 문제일 수 있습니다. 간단한 단어 추출 방식을 사용합니다.")

                    # 대체 방법: 간단한 단어 추출
                    from gemini_helper import extract_vocabulary_simple
                    st.session_state.vocabulary_data = extract_vocabulary_simple(story)

                    if st.session_state.vocabulary_data and st.session_state.vocabulary_data.get('vocabulary'):
                        st.session_state.vocabulary_cards = generate_vocabulary_cards(
                            st.session_state.vocabulary_data['vocabulary']
                        )
                        st.success(f"✅ {len(st.session_state.vocabulary_data['vocabulary'])}개의 단어를 추출했습니다!")

        # 핵심 단어와 문법 설명 표시
        if st.session_state.vocabulary_data and st.session_state.vocabulary_data['explanation']:
            with st.expander("📖 핵심 단어와 문법 설명 보기"):
                st.markdown(st.session_state.vocabulary_data['explanation'])

        # 단어 카드 학습
        if st.session_state.vocabulary_cards:
            current_card = st.session_state.vocabulary_cards[st.session_state.current_card_index]
            
            st.markdown(f"### 카드 학습")
            
            # 문제 표시
            if current_card['type'] == 'en_to_ko':
                st.markdown(f"### 영어 단어의 뜻을 맞춰보세요:")
                st.markdown(f'<div class="english-text">{current_card["question"]}</div>', unsafe_allow_html=True)
                
                # 듣기 버튼 (영어 단어만 듣기 가능)
                if st.button("🔊 단어 듣기", key="card_speech"):
                    audio_base64 = text_to_speech(current_card["question"], lang='en')
                    if audio_base64:
                        play_audio(audio_base64)
            else:
                st.markdown(f"### 한국어 뜻에 맞는 영어 단어를 맞춰보세요:")
                st.markdown(f'<div class="korean-text">{current_card["question"]}</div>', unsafe_allow_html=True)

            # 정답/선택지 표시
            if st.session_state.show_answer:
                st.markdown(f"### ✅ 정답:")
                if current_card['type'] == 'en_to_ko':
                    st.markdown(f'<div class="korean-text">{current_card["answer"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="english-text">{current_card["answer"]}</div>', unsafe_allow_html=True)
                
                # 카드 이동 버튼
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    if st.button("⬅️ 이전 카드", 
                                disabled=(st.session_state.current_card_index == 0), 
                                use_container_width=True):
                        st.session_state.current_card_index -= 1
                        st.session_state.show_answer = False
                        st.rerun()

                with col2:
                    st.markdown(f"<h5 style='text-align: center;'>카드 {st.session_state.current_card_index + 1} / {len(st.session_state.vocabulary_cards)}</h5>", 
                               unsafe_allow_html=True)

                with col3:
                    if st.button("다음 카드 ➡️", 
                                disabled=(st.session_state.current_card_index >= len(st.session_state.vocabulary_cards) - 1), 
                                use_container_width=True):
                        st.session_state.current_card_index += 1
                        st.session_state.show_answer = False
                        st.rerun()
                
                # 다시 학습하기 버튼
                if st.button("🔄 다시 학습하기", use_container_width=True):
                    st.session_state.show_answer = False
                    st.rerun()
            else:
                # 선택지 표시
                st.markdown("### 선택지:")
                
                for i, option in enumerate(current_card['options']):
                    if st.button(f"{chr(65+i)}. {option}", key=f"card_option_{i}", use_container_width=True):
                        is_correct = (option == current_card['answer'])

                        # 통계 업데이트: 퀴즈 시도
                        update_quiz_stats(is_correct)

                        st.session_state.show_answer = True
                        # 정답 확인은 보기만 하도록 (학습 중심)
                        st.info(f"{'🎉 정답입니다!' if is_correct else '💡 다시 생각해보세요!'}")
                        st.rerun()

            # 전체 카드 보기 (선택적)
            with st.expander("📋 전체 단어 목록 보기"):
                st.markdown("### 전체 단어 목록:")
                
                for i, vocab in enumerate(st.session_state.vocabulary_data['vocabulary']):
                    st.markdown(f"**{i+1}. {vocab['en']}** - {vocab['ko']}")
        else:
            st.info("눌러서 핵심 단어를 분석해주세요.", icon="💡")

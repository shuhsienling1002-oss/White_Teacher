import streamlit as st
import time
import os
import random
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 ---
st.set_page_config(
    page_title="阿美語 - 醃肉 Misasiraw", 
    page_icon="🥩", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# --- CSS 視覺魔法 (炭火燻烤美食風 - 醃肉專屬版) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Noto+Sans+TC:wght@400;700&display=swap');

    /* 全局背景：炭火深紅黑 */
    .stApp { 
        background-color: #1a0a05;
        background-image: radial-gradient(circle at 50% 0%, #4E342E 0%, #1a0a05 80%);
        font-family: 'Noto Sans TC', sans-serif;
        color: #FBE9E7;
    }
    
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; }

    /* --- Header --- */
    .header-container {
        background: rgba(78, 52, 46, 0.4);
        border: 1px solid #FF8A65;
        box-shadow: 0 0 15px rgba(255, 138, 101, 0.3);
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        margin-bottom: 40px;
        backdrop-filter: blur(10px);
    }
    
    .main-title {
        font-family: 'Roboto Mono', monospace;
        color: #FF8A65;
        font-size: 40px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 3px;
        text-shadow: 0 0 10px #FF8A65;
        margin: 0;
    }
    
    .sub-title { color: #FFCC80; font-size: 18px; margin-top: 10px; letter-spacing: 1px; }
    .teacher-tag { display: inline-block; margin-top: 15px; padding: 5px 15px; border: 1px solid #FFD54F; color: #FFD54F; border-radius: 50px; font-size: 12px; font-weight: bold; letter-spacing: 1px; }

    /* --- Cards --- */
    .word-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px 10px;
        text-align: center;
        border: 1px solid rgba(255, 138, 101, 0.2);
        height: 100%;
        margin-bottom: 15px;
    }
    .icon-box { font-size: 40px; margin-bottom: 10px; }
    .amis-word { font-size: 18px; font-weight: 700; color: #FFFFFF; margin-bottom: 5px; font-family: 'Roboto Mono', monospace; }
    .zh-word { font-size: 14px; color: #FFAB91; }

    /* --- Sentences --- */
    .sentence-box {
        background: linear-gradient(90deg, rgba(255,138,101,0.08) 0%, rgba(0,0,0,0) 100%);
        border-left: 4px solid #FFCC80;
        padding: 20px;
        margin-bottom: 20px;
        border-radius: 0 10px 10px 0;
    }
    .sentence-amis { font-size: 18px; color: #FFE082; font-weight: 700; margin-bottom: 8px; }
    .sentence-zh { font-size: 15px; color: #FFCC80; }

    /* --- Buttons --- */
    .stButton>button { width: 100%; border-radius: 5px; background: transparent; border: 2px solid #FF8A65; color: #FF8A65 !important; font-weight: bold; }
    .stButton>button:hover { background: #FF8A65; color: #000 !important; }

    /* --- Tab (分頁) 高對比修正 --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #FFFFFF !important; 
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
        opacity: 1 !important; 
    }

    .stTabs [aria-selected="true"] {
        background-color: #FF8A65 !important;
        color: #000000 !important;
        border: 1px solid #FF8A65 !important;
        box-shadow: 0 0 10px #FF8A65;
    }
    
    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }

    /* --- Debug Area --- */
    .debug-box { background: #222; color: #0f0; padding: 10px; font-family: monospace; font-size: 12px; border: 1px dashed #0f0; margin-top: 50px; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 資料設定 ---
VOCABULARY = [
    {"amis": "siraw", "zh": "醃肉", "emoji": "🥩", "file": "v_siraw"},
    {"amis": "hakhak", "zh": "糯米飯", "emoji": "🍚", "file": "v_hakhak"},
    {"amis": "cilak", "zh": "鹽巴", "emoji": "🧂", "file": "v_cilak"}, # 補充第三個單字以符合測驗邏輯
]

SENTENCES = [
    {
        "amis": "Komaen kako to siraw ato hakhak.", 
        "zh": "我吃醃肉和糯米飯。", 
        "emoji": "😋", 
        "file": "s_komaen"
    },
    {
        "amis": "Misasiraw kako.", 
        "zh": "我製作醃肉。", 
        "emoji": "👩‍🍳", 
        "file": "s_misasiraw"
    },
    {
        "amis": "Maolah kako to siraw.", 
        "zh": "我喜歡醃肉。", 
        "emoji": "❤️", 
        "file": "s_maolah" # 補充第三句以符合測驗邏輯
    },
]

QUIZ_DATA = [
    {"q": "Komaen kako to ______ ato hakhak.", "zh": "我吃醃肉和糯米飯。", "ans": "siraw", "opts": ["siraw", "hakhak", "cilak"]},
    {"q": "______ / 糯米飯", "zh": "糯米飯", "ans": "hakhak", "opts": ["hakhak", "siraw", "cilak"]},
    {"q": "Misasiraw ______.", "zh": "我製作醃肉。", "ans": "kako", "opts": ["kako", "siraw", "hakhak"]},
    {"q": "______ / 醃肉", "zh": "醃肉", "ans": "siraw", "opts": ["siraw", "hakhak", "cilak"]},
    {"q": "______ / 鹽巴", "zh": "鹽巴", "ans": "cilak", "opts": ["cilak", "siraw", "hakhak"]},
]

# --- 1.5 強力語音核心 (診斷版) ---
def play_audio(text, filename_base=None):
    if filename_base:
        for ext in ['m4a', 'mp3', 'ma4', 'wav']: 
            path = f"audio/{filename_base}.{ext}"
            if os.path.exists(path):
                mime = 'audio/mp4' if ext in ['m4a', 'ma4'] else 'audio/mp3'
                st.audio(path, format=mime)
                return
        
        st.markdown(f"<span style='color:red; font-size:12px;'>⚠️ 找不到檔案: {filename_base}.m4a</span>", unsafe_allow_html=True)

    try:
        speak_text = text.split('/')[0].strip()
        tts = gTTS(text=speak_text, lang='id') 
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format='audio/mp3')
    except:
        st.caption("🔇")

# --- 2. 隨機出題邏輯 ---
def init_quiz():
    st.session_state.score = 0
    st.session_state.current_q = 0
    
    # Q1
    q1_target = random.choice(VOCABULARY)
    others = [v for v in VOCABULARY if v['amis'] != q1_target['amis']]
    q1_options = random.sample(others, 2) + [q1_target]
    random.shuffle(q1_options)
    st.session_state.q1_data = {"target": q1_target, "options": q1_options}

    # Q2
    q2_data = random.choice(QUIZ_DATA)
    random.shuffle(q2_data['opts'])
    st.session_state.q2_data = q2_data

    # Q3
    q3_target = random.choice(SENTENCES)
    other_sentences = [s['zh'] for s in SENTENCES if s['zh'] != q3_target['zh']]
    if len(other_sentences) < 2:
        q3_options = other_sentences + [q3_target['zh']]
    else:
        q3_options = random.sample(other_sentences, 2) + [q3_target['zh']]
    random.shuffle(q3_options)
    st.session_state.q3_data = {"target": q3_target, "options": q3_options}

if 'q1_data' not in st.session_state:
    init_quiz()

# --- 3. 介面呈現 ---
def show_learning_mode():
    st.markdown("<h3 style='color:#FF8A65; text-align:center; margin-bottom:20px;'>資料庫：單字模組</h3>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    for idx, item in enumerate(VOCABULARY):
        with cols[idx % 3]:
            display_amis = item['amis'].replace(" nu ", "<br>nu ")
            st.markdown(f"""
            <div class="word-card">
                <div class="icon-box">{item['emoji']}</div>
                <div class="amis-word">{display_amis}</div>
                <div class="zh-word">{item['zh']}</div>
            </div>
            """, unsafe_allow_html=True)
            play_audio(item['amis'], filename_base=item['file'])
            st.write("")

    st.markdown("---")
    st.markdown("<h3 style='color:#FF8A65; text-align:center; margin-bottom:20px;'>資料庫：語法模組</h3>", unsafe_allow_html=True)
    
    for item in SENTENCES:
        st.markdown(f"""
        <div class="sentence-box">
            <div class="sentence-amis">{item['emoji']} {item['amis']}</div>
            <div class="sentence-zh">{item['zh']}</div>
        </div>
        """, unsafe_allow_html=True)
        play_audio(item['amis'], filename_base=item['file'])

def show_quiz_mode():
    st.markdown("<h3 style='text-align: center; color: #FFCC80;'>任務：知識檢測</h3>", unsafe_allow_html=True)
    st.progress((st.session_state.current_q) / 3)
    st.write("")

    if st.session_state.current_q == 0:
        data = st.session_state.q1_data
        target = data['target']
        st.markdown(f"""<div class="quiz-card" style="text-align:center; padding:20px; border:1px solid #FFCC80; border-radius:10px;"><h3>🔊 聲納訊號辨識 (聽力)</h3></div>""", unsafe_allow_html=True)
        play_audio(target['amis'], filename_base=target['file'])
        st.write("")
        
        cols = st.columns(3)
        for idx, opt in enumerate(data['options']):
            with cols[idx]:
                if st.button(f"{opt['zh']}", key=f"q1_{idx}"):
                    if opt['amis'] == target['amis']:
                        st.balloons()
                        st.success("訊號確認！")
                        time.sleep(1)
                        st.session_state.score += 1
                        st.session_state.current_q += 1
                        st.rerun()
                    else:
                        st.error("訊號錯誤")

    elif st.session_state.current_q == 1:
        data = st.session_state.q2_data
        st.markdown(f"""
        <div class="quiz-card" style="text-align:center; padding:20px; border:1px solid #FFCC80; border-radius:10px;">
            <h3>🧩 導航圖資修復 (填空)</h3>
            <h2 style="color:#FF8A65;">{data['q'].replace('______', '___?___')}</h2>
            <p style="color:#FFAB91;">{data['zh']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(3)
        for i, opt in enumerate(data['opts']):
            with cols[i]:
                if st.button(opt, key=f"q2_{i}"):
                    if opt == data['ans']:
                        st.balloons()
                        st.success("修復完成！")
                        time.sleep(1)
                        st.session_state.score += 1
                        st.session_state.current_q += 1
                        st.rerun()
                    else:
                        st.error("數據不符")

    elif st.session_state.current_q == 2:
        data = st.session_state.q3_data
        target = data['target']
        st.markdown(f"""
        <div class="quiz-card" style="text-align:center; padding:20px; border:1px solid #FFCC80; border-radius:10px;">
            <h3>📡 通訊解碼 (句意解析)</h3>
            <h2 style="color:#FFE082;">{target['amis']}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        play_audio(target['amis'], filename_base=target['file'])
        
        for opt in data['options']:
            if st.button(opt):
                if opt == target['zh']:
                    st.balloons()
                    st.success("解碼成功！")
                    time.sleep(1)
                    st.session_state.score += 1
                    st.session_state.current_q += 1
                    st.rerun()
                else:
                    st.error("解碼失敗")

    else:
        st.markdown(f"""
        <div class="quiz-card" style="text-align:center; padding:20px; border:1px solid #FF8A65; border-radius:10px;">
            <h1 style='color: #FF8A65;'>任務全數完成</h1>
            <p>目前積分: {st.session_state.score} / 3</p>
            <div style='font-size: 60px;'>🚀</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("重啟任務"):
            init_quiz()
            st.rerun()

# --- 4. 診斷工具 (Debug Tool) ---
def show_debug_info():
    st.markdown("---")
    st.markdown("### 📂 檔案診斷中心")
    
    if not os.path.exists("audio"):
        st.error("❌ 嚴重錯誤：找不到 'audio' 資料夾！")
        return

    files = os.listdir("audio")
    if not files:
        st.warning("⚠️ audio 資料夾是空的！請記得放入醃肉單元的音檔喔。")
    else:
        st.success(f"✅ audio 資料夾內發現 {len(files)} 個檔案，系統運作正常。")

# --- 主程式 ---
def main():
    st.markdown("""
    <div class="header-container">
        <h1 class="main-title">O MISASIRAW</h1>
        <div class="sub-title">製作醃肉</div>
        <div class="teacher-tag">講師：孫秀蘭 | 教材提供者：孫秀蘭</div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🥩 醃肉筆記", "🎮 挑戰任務"])
    
    with tab1:
        show_learning_mode()
    with tab2:
        show_quiz_mode()
        
    show_debug_info()

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 1. ページ設定と自動更新 (5秒おき) ---
st.set_page_config(page_title="Lecture Monitor", page_icon="📊")
st_autorefresh(interval=5000, key="datarefresh")

# --- 2. スプレッドシート接続 ---
URL = "https://docs.google.com/spreadsheets/d/1rJBb19fJkxVnX69zzxVhBqUiXABFEQzPhihN1-0Fe-Y/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# データ読み込み関数
def get_data():
    try:
        # シート1からステータスとカウントを取得
        df_status = conn.read(spreadsheet=URL, worksheet="シート1", nrows=1, header=None, ttl=0)
        status = str(df_status.iloc[0, 0]).strip().upper() == "TRUE"
        good_count = df_status.iloc[0, 1] if len(df_status.columns) > 1 else 0
        bad_count = df_status.iloc[0, 2] if len(df_status.columns) > 2 else 0
        
        # 「コメント」タブから全コメントを取得
        df_comments = conn.read(spreadsheet=URL, worksheet="コメント", header=None, ttl=0)
        comments = df_comments[0].dropna().tolist()
        
        return status, good_count, bad_count, comments
    except:
        return False, 0, 0, []

# データの取得
current_status, good_val, bad_val, all_comments = get_data()

# --- 3. URL判定とログイン管理 ---
query_params = st.query_params
is_admin_url = query_params.get("view") == "admin"

if "is_logged_in" not in st.session_state:
    st.session_state["is_logged_in"] = False

# --- 4. メインロジック ---

if is_admin_url:
    st.title("🛠 管理者リアルタイムモニター")
    
    # ログインチェック
    if not st.session_state["is_logged_in"]:
        pwd = st.text_input("パスワード", type="password")
        if st.button("ログイン"):
            if pwd == "Henoheno2236":
                st.session_state["is_logged_in"] = True
                st.rerun()
    
    # ログイン後の管理者画面
    if st.session_state["is_logged_in"]:
        st.write(f"公開状態: {'🟢 公開中' if current_status else '🔴 非公開'}")
        
        # 【リアルタイムカウント表示】
        st.subheader("現在の学生の反応")
        c1, c2 = st.columns(2)
        c1.metric("👍 よくわかる", f"{good_val} 人")
        c2.metric("🤔 よくわからない", f"{bad_val} 人")
        
        st.divider()
        
        # 【リアルタイムコメント表示】
        st.subheader("届いているコメント")
        if all_comments:
            for i, msg in enumerate(reversed(all_comments)):
                st.info(f"{msg}")
        else:
            st.write("まだコメントはありません。")
            
        if st.button("ログアウト"):
            st.session_state["is_logged_in"] = False
            st.rerun()

else:
    # ユーザー画面
    if not current_status:
        st.stop()
    
    st.title("❓ 講義コメント")
    st.write("ボタンを押して反応を教えてください。")
    
    col1, col2 = st.columns(2)
    col1.button("👍 よくわかる", use_container_width=True)
    col2.button("🤔 よくわからない", use_container_width=True)
    
    st.divider()
    st.text_input("質問・コメントをどうぞ")
    st.button("送信")
    

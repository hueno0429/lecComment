# -*- coding: utf-8 -*-
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 1. ページ設定と自動更新 ---
st.set_page_config(page_title="Lecture Comment System")
st_autorefresh(interval=5000, key="datarefresh") # 5秒ごとにチェック

# --- 2. スプレッドシート接続 ---
# 公開設定にしたスプレッドシートのURLを指定
URL = "https://docs.google.com/spreadsheets/d/あなたのスプレッドシートID/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_status():
    # A1セルの値を取得
    df = conn.read(spreadsheet=URL, worksheet="0", usecols=[0], nrows=1, header=None)
    return str(df.iloc[0, 0]).upper() == "TRUE"

# --- 3. URL判定 ---
query_params = st.query_params
is_admin_url = query_params.get("view") == "admin"

# --- 4. メインロジック ---
current_status = get_status()

if is_admin_url:
    st.title("🛠 管理者パネル")
    password = st.text_input("パスワード", type="password")
    
    if password == "Henoheno2236":
        st.success("認証されました")
        st.write(f"現在の公開状態: {'🟢 公開中' if current_status else '🔴 非公開（真っ白）'}")
        
        st.info("※状態を切り替えるには、GoogleスプレッドシートのA1セルを直接 TRUE または FALSE に書き換えてください。")
        st.write(f"[スプレッドシートを開く]({URL})")
    else:
        if password: st.error("パスワードが違います")

else:
    # 【ユーザーモード】
    if not current_status:
        # 管理者がスプレッドシートをTRUEにしていない限り、世界中の誰が見ても真っ白
        st.stop() 

    # --- ここから講義用コンテンツ ---
    st.title("❓ 講義コメント")
    st.write("講義が開始されました。質問をどうぞ。")
    user_input = st.text_input("コメントを入力")
    if st.button("送信"):
        st.success("送信されました")


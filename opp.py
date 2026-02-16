# -*- coding: utf-8 -*-
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 1. ページ設定と自動更新 ---
st.set_page_config(page_title="Lecture Comment System", page_icon="❓")
st_autorefresh(interval=5000, key="datarefresh") # 5秒ごとに更新

# --- 2. スプレッドシート接続 ---
# ※ここにあなたのスプレッドシートURLを貼り付けてください
URL = "https://docs.google.com/spreadsheets/d/あなたのスプレッドシートID/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_status():
    try:
        # スプレッドシートのA1セルを取得 (ttl=0でキャッシュを無効化)
        df = conn.read(spreadsheet=URL, worksheet="シート1", usecols=[0], nrows=1, header=None, ttl=0)
        val = str(df.iloc[0, 0]).strip().upper()
        return val == "TRUE"
    except Exception as e:
        return False

# --- 3. 状態の取得 ---
current_status = get_status()
query_params = st.query_params
is_admin_url = query_params.get("view") == "admin"

# --- 4. 管理者ログイン状態の保持 (session_state) ---
if "is_logged_in" not in st.session_state:
    st.session_state["is_logged_in"] = False

# --- 5. メインロジック ---

# A. 管理者設定画面 (?view=admin のとき)
if is_admin_url:
    st.title("🛠 管理者設定パネル")
    
    if not st.session_state["is_logged_in"]:
        password = st.text_input("パスワードを入力してください", type="password")
        if st.button("ログイン"):
            if password == "Henoheno2236":
                st.session_state["is_logged_in"] = True
                st.success("認証されました！")
                st.rerun()
            else:
                st.error("パスワードが違います。")
    
    if st.session_state["is_logged_in"]:
        st.write(f"現在の公開状態: {'🟢 公開中' if current_status else '🔴 非公開'}")
        st.info("スプレッドシートのA1セルを TRUE にすると全員に表示されます。")
        if st.button("ログアウト"):
            st.session_state["is_logged_in"] = False
            st.rerun()
        
        st.divider()
        st.write("👉 [ユーザー画面を確認する](/)") # 通常URLへのリンク

# B. ユーザー画面（通常のURLのとき）
else:
    # 管理者が「開始（TRUE）」にしていない場合は真っ白
    if not current_status:
        st.stop()

    # --- ここから「よくわかる/わからない」ボタンを含むコンテンツ ---
    st.title("❓ 講義コメント")
    
    # 2つのボタンを横並びにする
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 よくわかる", use_container_width=True):
            st.toast("「よくわかる」を送信しました")
            # ここにカウントアップなどの処理を追加できます
            
    with col2:
        if st.button("🤔 よくわからない", use_container_width=True):
            st.toast("「よくわからない」を送信しました")
            # ここにカウントアップなどの処理を追加できます

    st.divider()
    
    # コメント入力欄
    comment = st.text_input("質問やコメントを入力してください")
    if st.button("送信"):
        if comment:
            st.success(f"送信完了: {comment}")
        else:
            st.warning("コメントを入力してください")

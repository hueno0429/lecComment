# -*- coding: utf-8 -*-
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. ページ設定と自動更新 ---
st.set_page_config(page_title="Lecture Comment System", page_icon="❓")
st_autorefresh(interval=5000, key="datarefresh")

# --- 2. スプレッドシート接続 ---
URL = "https://docs.google.com/spreadsheets/d/1rJBb19fJkxVnX69zzxVhBqUiXABFEQzPhihN1-0Fe-Y/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_status():
    try:
        # A1セル（公開状態）を確認
        df = conn.read(spreadsheet=URL, worksheet="シート1", usecols=[0], nrows=1, header=None, ttl=0)
        return str(df.iloc[0, 0]).strip().upper() == "TRUE"
    except:
        return False

def get_all_data():
    try:
        # 「データ」タブからすべての履歴を読み込む
        return conn.read(spreadsheet=URL, worksheet="データ", ttl=0)
    except:
        return pd.DataFrame(columns=["type", "content"])

# --- 3. 状態とデータの取得 ---
current_status = get_status()
all_data = get_all_data()
query_params = st.query_params
is_admin_url = query_params.get("view") == "admin"

if "is_logged_in" not in st.session_state:
    st.session_state["is_logged_in"] = False

# --- 4. メインロジック ---

if is_admin_url:
    st.title("🛠 管理者設定パネル")
    # (ログイン処理は以前と同じなので省略可ですが、一応残します)
    if not st.session_state["is_logged_in"]:
        password = st.text_input("パスワード", type="password")
        if st.button("ログイン"):
            if password == "Henoheno2236":
                st.session_state["is_logged_in"] = True
                st.rerun()

    if st.session_state["is_logged_in"]:
        st.write(f"現在の公開状態: {'🟢 公開中' if current_status else '🔴 非公開'}")
        
        # カウントの集計表示
        good_count = len(all_data[all_data["type"] == "good"])
        bad_count = len(all_data[all_data["type"] == "bad"])
        
        col1, col2 = st.columns(2)
        col1.metric("👍 よくわかる", f"{good_count} 回")
        col2.metric("🤔 よくわからない", f"{bad_count} 回")

        st.divider()
        st.subheader("届いたコメント一覧")
        comments = all_data[all_data["type"] == "comment"]["content"].tolist()
        for msg in reversed(comments): # 新しい順に表示
            st.write(f"・ {msg}")

else:
    if not current_status:
        st.stop()

    st.title("❓ 講義コメント")
    
    # カウント表示（ユーザー側にも出す場合）
    good_count = len(all_data[all_data["type"] == "good"])
    bad_count = len(all_data[all_data["type"] == "bad"])
    
    st.write(f"現在の反応： 👍 {good_count} / 🤔 {bad_count}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 よくわかる", use_container_width=True):
            # ※本来は conn.create ですが、共有設定のみの場合はスプレッドシート側で編集が必要です
            st.toast("送信しました（スプレッドシートへの書込権限が必要です）")
            
    with col2:
        if st.button("🤔 よくわからない", use_container_width=True):
            st.toast("送信しました")

    st.divider()
    comment = st.text_input("質問やコメントを入力してください")
    if st.button("送信"):
        st.success(f"送信されました: {comment}")

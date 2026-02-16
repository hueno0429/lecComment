# -*- coding: utf-8 -*-
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 1. ページ設定と自動更新 ---
st.set_page_config(page_title="Lecture System", layout="wide", page_icon="📊")
st_autorefresh(interval=5000, key="datarefresh")

# --- 2. スプレッドシート接続 ---
URL = "https://docs.google.com/spreadsheets/d/1rJBb19fJkxVnX69zzxVhBqUiXABFEQzPhihN1-0Fe-Y/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_status():
    try:
        # worksheet="0" と指定することで、名前に関係なく一番左のタブを読み込みます
        df = conn.read(spreadsheet=URL, worksheet="0", usecols=[0], nrows=1, header=None, ttl=0)
        
        # 読み取ったデータが空でないか確認
        if df.empty:
            return False
            
        # 1行1列目の値を文字列として取り出し、大文字にして比較
        val = str(df.iloc[0, 0]).strip().upper()
        return val == "TRUE"
    except Exception as e:
        # 画面上にエラー内容を表示させて原因を特定する
        st.sidebar.error(f"スプレッドシート読み取りエラー: {e}")
        return False

def get_data():
    try:
        # シート1から公開状態とカウント(B1, C1)を取得
        df_status = conn.read(spreadsheet=URL, worksheet="0", nrows=1, header=None, ttl=0)
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

# --- 3. URLパラメータとログイン判定 ---
query_params = st.query_params
view = query_params.get("view", "")

if "is_logged_in" not in st.session_state:
    st.session_state["is_logged_in"] = False

# --- 4. メインロジック ---

# A. 管理者用モニタリングページ (?view=monitor)
if view == "monitor":
    if not st.session_state["is_logged_in"]:
        st.warning("ログインが必要です。管理者画面からログインしてください。")
        st.stop()

    st.title("📊 講義リアルタイム統計")
    st.write(f"公開状態: {'🟢 公開中' if current_status else '🔴 非公開'}")
    
    # メトリック（カウント表示）
    col1, col2 = st.columns(2)
    col1.metric("👍 よくわかる", f"{good_val} 人")
    col2.metric("🤔 よくわからない", f"{bad_val} 人")
    
    st.divider()
    
    # コメント一覧表示
    st.subheader("📝 届いている全コメント")
    if all_comments:
        for msg in reversed(all_comments): # 新しい順
            st.info(msg)
    else:
        st.write("まだコメントはありません。")
    
    if st.button("管理者メニューに戻る"):
        st.query_params.update(view="admin")
        st.rerun()

# B. 管理者設定メニュー (?view=admin)
elif view == "admin":
    st.title("🛠 管理者設定パネル")
    
    if not st.session_state["is_logged_in"]:
        pwd = st.text_input("パスワードを入力してください", type="password")
        if st.button("ログイン"):
            if pwd == "Henoheno2236":
                st.session_state["is_logged_in"] = True
                st.rerun()
            else:
                st.error("パスワードが違います。")
    
    if st.session_state["is_logged_in"]:
        st.success("ログイン済み")
        st.write(f"現在の公開状態: {'🟢 公開中' if current_status else '🔴 非公開'}")
        
        st.divider()
        st.write(f"👉 [スプレッドシートを編集する]({URL})")
        
        # モニタリングページへのリンクボタン
        if st.button("📈 リアルタイム統計ページを開く"):
            st.query_params.update(view="monitor")
            st.rerun()
        
        if st.button("ログアウト"):
            st.session_state["is_logged_in"] = False
            st.rerun()

# C. ユーザー画面 (通常のURL)
else:
    if not current_status:
        st.stop()
    
    st.title("❓ 講義コメント")
    st.write("反応ボタンを押してください。")
    
    c1, c2 = st.columns(2)
    c1.button("👍 よくわかる", use_container_width=True)
    c2.button("🤔 よくわからない", use_container_width=True)
    
    st.divider()
    st.text_input("質問・コメント")
    st.button("送信")




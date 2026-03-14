# -*- coding: utf-8 -*-
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- 1. ページ設定と自動更新 ---
st.set_page_config(page_title="Lecture System", layout="wide", page_icon="📊")
# 5秒ごとに画面を更新
st_autorefresh(interval=5000, key="datarefresh")

# --- 2. ローカルメモリ（全ユーザー共有）のデータ管理 ---
# st.cache_resource を使うと、全ブラウザ・全ユーザーで同じ変数を共有できます
@st.cache_resource
def get_shared_data():
    return {
        "status": True,      # 公開・非公開状態
        "good_count": 0,     # よくわかる
        "bad_count": 0,      # よくわからない
        "comments": []       # コメントリスト
    }

shared_data = get_shared_data()

# --- 3. URLパラメータとログイン判定 ---
query_params = st.query_params
view = query_params.get("view", "")

if "is_logged_in" not in st.session_state:
    st.session_state["is_logged_in"] = False

# --- 4. メインロジック ---

# --- 【A. 統計モニター画面】 ---
if view == "monitor":
    if not st.session_state["is_logged_in"]:
        st.warning("ログインが必要です。管理者画面からログインしてください。")
        st.stop()
    
    st.title("📊 講義リアルタイム統計")
    st.write(f"公開状態: {'🟢 公開中' if shared_data['status'] else '🔴 非公開'}")
    
    col1, col2 = st.columns(2)
    col1.metric("👍 よくわかる", f"{shared_data['good_count']} 人")
    col2.metric("🤔 よくわからない", f"{shared_data['bad_count']} 人")
    
    st.divider()
    st.subheader("📝 届いている全コメント")
    if shared_data['comments']:
        # 最新のコメントを上に表示
        for msg_item in reversed(shared_data['comments']):
            st.info(f"[{msg_item['time']}] {msg_item['text']}")
    else:
        st.write("まだコメントはありません。")
    
    if st.button("管理者メニューに戻る"):
        st.query_params.update(view="admin")
        st.rerun()

# --- 【B. 管理者画面】 ---
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
        
        # 公開状態の切り替え
        new_status = st.toggle("公開状態を切り替える", value=shared_data['status'])
        shared_data['status'] = new_status
        
        st.divider()
        if st.button("🗑 データをリセット（カウントとコメントを消去）"):
            shared_data['good_count'] = 0
            shared_data['bad_count'] = 0
            shared_data['comments'] = []
            st.success("リセットしました")
            st.rerun()
            
        if st.button("📈 リアルタイム統計ページを開く"):
            st.query_params.update(view="monitor")
            st.rerun()
        
        if st.button("ログアウト"):
            st.session_state["is_logged_in"] = False
            st.rerun()

# --- 【C. 学生用入力画面】 ---
else:
    if not shared_data['status']:
        st.title("🔴 現在、受付停止中です")
        st.write("講義が開始されるまでお待ちください。")
        st.stop()
        
    st.title("❓ 講義コメント")
    st.write("今の理解度を教えてください。")
    
    c1, c2 = st.columns(2)
    if c1.button("👍 よくわかる", use_container_width=True):
        shared_data['good_count'] += 1
        st.toast("「よくわかる」を送信しました！")
        
    if c2.button("🤔 よくわからない", use_container_width=True):
        shared_data['bad_count'] += 1
        st.toast("「よくわからない」を送信しました。")
        
    st.divider()
    with st.form("comment_form", clear_on_submit=True):
        comment_text = st.text_input("質問・コメント")
        submitted = st.form_submit_button("送信")
        if submitted and comment_text:
            now = datetime.now().strftime("%H:%M")
            shared_data['comments'].append({"time": now, "text": comment_text})
            st.success("コメントを送信しました。")
            
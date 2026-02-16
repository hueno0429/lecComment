# -*- coding: utf-8 -*-
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 1. ページ設定と自動更新 ---
st.set_page_config(page_title="Lecture Comment System", page_icon="❓")
# 5秒ごとに画面を自動更新して、スプレッドシートの状態（TRUE/FALSE）を反映させる
st_autorefresh(interval=5000, key="datarefresh")

# --- 2. スプレッドシート接続 ---
# 指定いただいたURLを使用
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
        st.info("スプレッドシートの「シート1」のA1セルが TRUE なら公開、FALSE なら非表示になります。")
        
        if st.button("ログアウト"):
            st.session_state["is_logged_in"] = False
            st.rerun()
        
        st.divider()
        st.write(f"👉 [スプレッドシートを編集する]({URL})")
        st.write("👉 [ユーザー画面（真っ白チェック）を確認する](/)")

# B. ユーザー画面（通常のURLのとき）
else:
    # スプレッドシートがTRUE（講義中）でない場合は、st.stop() で真っ白にする
    if not current_status:
        st.stop()

    # --- 講義中のみ表示されるコンテンツ ---
    st.title("❓ 講義コメント")
    
    # 「よくわかる」「よくわからない」ボタンを横並びで配置
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 よくわかる", use_container_width=True):
            st.toast("「よくわかる」を受け付けました")
            
    with col2:
        if st.button("🤔 よくわからない", use_container_width=True):
            st.toast("「よくわからない」を受け付けました")

    st.divider()
    
    # 自由入力のコメント欄
    comment = st.text_input("質問やコメントを入力してください")
    if st.button("送信"):
        if comment:
            st.success(f"送信完了: {comment}")
        else:
            st.warning("内容を入力してください")


# -*- coding: utf-8 -*-

import streamlit as st
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import qrcode
from io import BytesIO
from datetime import datetime, timedelta, timezone
import pandas as pd

# --- 1. ページ設定と自動更新 ---
st.set_page_config(page_title="Lecture System", layout="wide", page_icon="📊")

# 5秒ごとに画面を更新
st_autorefresh(interval=5000, key="datarefresh")

# --- 2. ローカルメモリ（全ユーザー共有）のデータ管理 ---
# st.cache_resource を使うと、全ブラウザ・全ユーザーで同じ変数を共有できます
@st.cache_resource
def get_shared_data():
    return {
        "status": True,        # 公開・非公開状態
        "good_count": 0,       # よくわかる
        "bad_count": 0,        # よくわからない
        "comments": [],        # コメントリスト
        "is_logged_in": False  # ログイン状態（ブラウザの戻るボタン対策）
    }

shared_data = get_shared_data()

# --- 3. URLパラメータとログイン判定 ---
query_params = st.query_params
view = query_params.get("view", "")

# --- QRコード生成関数を追加 ---
def generate_qr(url):
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- 4. メインロジック ---

# --- 【A. 統計モニター画面】 ---
if view == "monitor":
    if not shared_data["is_logged_in"]:
        st.warning("ログインが必要です。管理者画面からログインしてください。")
        st.stop()

    st.subheader("📊 講義リアルタイム統計")
    st.write(f"公開状態: {'🟢 公開中' if shared_data['status'] else '🔴 非公開'}")

    col1, col2 = st.columns(2)
    col1.metric("👍 よくわかる", f"{shared_data['good_count']} 人")
    col2.metric("🤔 よくわからない", f"{shared_data['bad_count']} 人")

    st.divider()
    st.markdown("#### 📝 届いている全コメント")
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
    st.subheader("🛠 管理者設定パネル")

    # --- 安全なパスワード取得 ---
    try:
        correct_password = st.secrets.get("admin_password", "password")
    except Exception:
        correct_password = "password"

    if not shared_data["is_logged_in"]:
        pwd = st.text_input("パスワードを入力してください", type="password")
        if st.button("ログイン"):
            if pwd == correct_password:
                shared_data["is_logged_in"] = True
                st.rerun()
            else:
                st.error("パスワードが違います。")

    # ログイン後の表示
    if shared_data["is_logged_in"]:
        st.success("ログイン済み")

        # --- データダウンロード ---
        st.markdown("#### 💾 データのバックアップ")

        JST = timezone(timedelta(hours=+9), 'JST')

        if shared_data['comments'] or shared_data['good_count'] > 0 or shared_data['bad_count'] > 0:
            df_comments = pd.DataFrame(shared_data['comments'])
            df_counts = pd.DataFrame([{
                "項目": "合計カウント",
                "👍 よくわかる": shared_data['good_count'],
                "🤔 よくわからない": shared_data['bad_count'],
                "時刻": datetime.now(JST).strftime("%Y-%m-%d %H:%M")
            }])
            df_export = pd.concat([df_counts, df_comments], axis=0, ignore_index=True)
            csv = df_export.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            fname = f"lecture_summary_{datetime.now(JST).strftime('%Y%m%d_%H%M')}.csv"
            st.download_button(
                label="📩 統計とコメントをCSVでダウンロード",
                data=csv,
                file_name=fname,
                mime='text/csv',
            )
        else:
            st.write("保存できるデータはまだありません。")

        st.divider()

        # --- QRコード表示 ---
        with st.expander("📱 スマホで参加（QRコード）"):
            current_url = "https://leccomment.streamlit.app/"
            qr_img = generate_qr(current_url)
            st.image(qr_img, caption="このコードをスキャンして投稿", width=200)

        # --- ステータス管理 ---
        st.markdown("#### ⚙️ 講義コントロール")
        shared_data['status'] = st.toggle("公開状態（学生が投稿できるか）", value=shared_data['status'])

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📈 統計画面へ", use_container_width=True):
                st.query_params.update(view="monitor")
                st.rerun()
        with col2:
            if st.button("🚪 ログアウト", use_container_width=True):
                shared_data["is_logged_in"] = False
                st.rerun()

        st.divider()

        if st.button("🗑 データをリセット（全消去）", type="primary"):
            shared_data['good_count'] = 0
            shared_data['bad_count'] = 0
            shared_data['comments'] = []
            st.success("すべてのデータを消去しました")
            st.rerun()

# --- 【C. 学生用入力画面】 ---
else:
    if not shared_data['status']:
        st.subheader("🔴 現在、受付停止中です")
        st.write("講義が開始されるまでお待ちください。")
        st.stop()

    st.subheader("❓ 講義コメント")

    with st.expander("📱 スマホで参加（QRコード）"):
        current_url = "https://leccomment.streamlit.app/"
        qr_img = generate_qr(current_url)
        st.image(qr_img, caption="このコードをスキャンして投稿", width=200)

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
            JST = timezone(timedelta(hours=+9), 'JST')
            now = datetime.now(JST).strftime("%H:%M")
            shared_data['comments'].append({"time": now, "text": comment_text})
            st.success("コメントを送信しました。")

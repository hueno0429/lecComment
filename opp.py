import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd  # CSV作成用に必要
from datetime import datetime

st.set_page_config(page_title="授業リアクション", layout="centered")

# --- 1. 全ユーザー共通のデータを作成 ---
@st.cache_resource
def get_shared_data():
    return {"comments": [], "count_unknown": 0, "count_clear": 0}

data = get_shared_data()

# --- 2. モード判定とパスワード設定 ---
query_params = st.query_params
is_admin_url = query_params.get("view") == "admin"
ADMIN_PASSWORD = "Henoheno2236"

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# --- 3. 画面の構築 ---

if is_admin_url:
    # 未認証時のサイドバー
    if not st.session_state.authenticated:
        st.sidebar.title("$D83D$DD10 管理者認証")
        pwd_input = st.sidebar.text_input("パスワードを入力してください", type="password")
        if pwd_input == ADMIN_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        elif pwd_input != "":
            st.sidebar.error("パスワードが違います")

    # 認証済み：教員用画面
    if st.session_state.authenticated:
        st_autorefresh(interval=5000, key="admin_refresh")
        st.title("$D83D$DCCA 教員用ダッシュボード")
        
        # 集計表示
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div style="text-align:center; background:#ffebee; padding:20px; border-radius:10px;">'
                        f'<p>$2753 分かりません</p><p style="font-size:80px; font-weight:bold; color:#d32f2f;">{data["count_unknown"]}</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div style="text-align:center; background:#e8f5e9; padding:20px; border-radius:10px;">'
                        f'<p>$D83D$DCA1 分かりやすい</p><p style="font-size:80px; font-weight:bold; color:#2e7d32;">{data["count_clear"]}</p></div>', unsafe_allow_html=True)

        st.write("")
        
        # --- 管理メニュー ---
        # 4つのボタンを並べる（リセット、CSV保存、消去、ログアウト）
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            if st.button("$267B$FE0F 数リセット"):
                data["count_unknown"] = 0
                data["count_clear"] = 0
                st.rerun()
        
        with c2:
            # CSVデータの作成
            if data["comments"]:
                total = len(data["comments"])
                # 番号とコメントのリストを作成
                df = pd.DataFrame({
                    "No": [total - i for i in range(total)],
                    "Comment": data["comments"]
                })
                # CSVに変換
                csv = df.to_csv(index=False).encode('utf_8_sig') # 日本語文字化け防止のためsig付き
                filename = f"comments_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
                
                st.download_button(
                    label="$D83D$DCE5 CSV保存",
                    data=csv,
                    file_name=filename,
                    mime='text/csv',
                )
            else:
                st.button("$D83D$DCE5 CSV保存", disabled=True)
                
        with c3:
            if st.button("$D83D$DDD1$FE0F 全消去"):
                data["comments"].clear()
                st.rerun()
                
        with c4:
            if st.button("$D83D$DEAA ログアウト"):
                st.session_state.authenticated = False
                st.rerun()

        st.write("---")
        st.subheader("$D83D$DCE9 届いているコメント")
        
        total_comments = len(data["comments"])
        for i, c in enumerate(data["comments"]):
            comment_number = total_comments - i
            st.chat_message("user").write(f"**No.{comment_number}**: {c}")
            
    else:
        st.title("$D83D$DCAC 授業コメント送信")
        st.info("管理者の方はサイドバーでログインしてください。")
        show_student_ui = True
else:
    show_student_ui = True

# 学生用UI
if 'show_student_ui' in locals() and show_student_ui:
    if not is_admin_url:
        st.title("$D83D$DCAC 授業コメント送信")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("$2753 分からない", use_container_width=True, key="std_q"):
            data["count_unknown"] += 1
            st.rerun()
    with col_btn2:
        if st.button("$D83D$DCA1 分かる！", use_container_width=True, key="std_a"):
            data["count_clear"] += 1
            st.rerun()

    with st.form(key='std_form', clear_on_submit=True):
        new_comment = st.text_input("匿名コメント")
        if st.form_submit_button("送信"):
            if new_comment:
                data["comments"].insert(0, new_comment)
                st.rerun()
              

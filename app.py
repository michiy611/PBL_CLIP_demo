"""
CLIP画像検索デモアプリケーション
Streamlitを使用したWebインターフェース
"""

import streamlit as st
import os
from PIL import Image
# import time # 強制ログテスト用に追加

# クラウド環境対応のキャッシュ設定
@st.cache_resource
def load_clip_model():
    """CLIPモデルのロードをキャッシュ"""
    from clip_feature_extractor import extract_text_features
    return extract_text_features

# データベース関数のインポート
try:
    from database_utils import (
        search_similar_images, 
        get_all_images_by_category, 
        get_database_stats,
        check_database_exists
    )
    from sheets_logger import search_logger
except ImportError as e:
    st.error(f"データベースモジュールの読み込みエラー: {e}")
    st.stop()

# ページ設定
st.set_page_config(
    page_title="CLIP画像検索デモ",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.result-container {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    background-color: white;
}
.similarity-score {
    font-weight: bold;
    color: #ff6b6b;
}
.category-badge {
    background-color: #4CAF50;
    color: white;
    padding: 0.2rem 0.8rem;
    border-radius: 15px;
    font-size: 0.8rem;
    margin-right: 0.5rem;
}
.debug-box {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 5px;
    padding: 0.5rem;
    font-family: monospace;
    font-size: 0.8rem;
    max-height: 300px;
    overflow-y: auto;
}
</style>
""", unsafe_allow_html=True)

def check_setup():
    """アプリケーションのセットアップ確認"""
    if not check_database_exists():
        st.error("❌ データベースが見つかりません")
        st.markdown("""
        ### セットアップが必要です
        
        以下のコマンドを実行してデータベースを作成してください：
        
        ```bash
        python batch_vectorize.py
        ```
        """)
        st.stop()

def display_image_safely(image_path, caption="", width=None):
    """画像を安全に表示"""
    try:
        if not os.path.exists(image_path):
            normalized_path = os.path.normpath(image_path)
            if os.path.exists(normalized_path):
                image_path = normalized_path
            else:
                st.error(f"画像ファイルが見つかりません: {image_path}")
                return
        
        image = Image.open(image_path)
        if width and width < 300:
            image.thumbnail((width * 2, width * 2), Image.Resampling.LANCZOS)
        st.image(image, caption=caption, width=width)
        
    except Exception as e:
        st.error(f"画像表示エラー: {str(e)}")

def search_page():
    """検索ページ (修正済み)"""
    st.markdown('<h1 class="main-header">🔍 CLIP画像検索</h1>', unsafe_allow_html=True)
    
    # 使い方説明
    st.markdown("---")
    st.markdown("### 📖 使い方（データ収集にご協力ください）")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔍 **パターン1: 落とし物探しゲーム**")
        st.markdown("""
        **手順：**
        1. 右側の「🖼️ ギャラリー」タブを開く
        2. 画像を1つ選んで覚える（これが**落とし物**です）
        3. この「🔍 画像検索」タブに戻る
        4. 覚えた画像の特徴を**自分の言葉**で検索してみる
        5. 検索結果の中に選んだ画像があったら**「✅ 正解」**ボタン
        6. なかったら**「❌ 正解なし」**ボタンを押す
        
        💡 **コツ：** 色、形、種類など、気づいた特徴を自由に入力してください
        """)
    
    with col2:
        st.markdown("#### 🆓 **パターン2: 自由検索**")
        st.markdown("""
        **手順：**
        1. 思いついた**キーワード**で自由に検索してみる
        2. 検索結果を見る
        3. 最後に**「🆓 フリー検索」**ボタンを押して完了
        
        **例：**
        - 「青いもの」
        - 「持ち歩くもの」
        - 「雨の日に使うもの」
        
        💡 **目的：** どんな言葉で何が見つかるかを調べています
        """)
    
    st.markdown("---")
    
    # 検索インターフェース
    search_query = st.text_input(
        "検索クエリを入力してください",
        placeholder="例: 赤いバッグ、グレーの折り畳み傘..."
    )
    search_button = st.button("🔍 検索（上位10件表示）", type="primary", use_container_width=True)
    
    # ----------------------------------------------------
    # ▼ 1. 検索実行と状態保存のロジック
    # ----------------------------------------------------
    if search_button and search_query:
        with st.spinner("検索中..."):
            try:
                extract_text_features = load_clip_model()
                query_vector = extract_text_features(search_query)
                results = search_similar_images(query_vector, 10)
                
                if results:
                    session_id = search_logger.log_search_query(search_query, results)
                    
                    # 検索結果をセッションステートに保存
                    st.session_state['current_search_session'] = session_id
                    st.session_state['search_results'] = results
                    st.session_state['search_query'] = search_query
                    
                    st.success(f"✅ 上位10件の結果を表示")
                    # 検索直後に再実行して、下の結果表示ロジックに処理を移す
                    st.rerun() 
                else:
                    st.warning("⚠️ 検索結果が見つかりませんでした")
                    # 以前の結果が残っている可能性があるのでクリアする
                    for key in ['current_search_session', 'search_results', 'search_query']:
                        if key in st.session_state:
                            del st.session_state[key]

            except Exception as e:
                st.error(f"❌ 検索エラー: {str(e)}")

    # --------------------------------------------------------------------
    # ▼ 2. 結果表示とフィードバックボタン処理のロジック
    #    session_stateに結果がある場合にのみ、このブロック全体が実行される
    # --------------------------------------------------------------------
    if 'search_results' in st.session_state and st.session_state['search_results']:
        results = st.session_state['search_results']
        session_id = st.session_state['current_search_session']

        st.subheader(f"「{st.session_state['search_query']}」の検索結果")

        # 各検索結果をループで表示
        for i, (similarity, image_id, filename, category, description, file_path) in enumerate(results):
            with st.container():
                st.markdown('<div class="result-container">', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    display_image_safely(file_path, width=200)
                
                with col2:
                    st.markdown(f"**順位:** {i+1}")
                    st.markdown(f'<span class="category-badge">{category}</span>', unsafe_allow_html=True)
                    st.markdown(f'<span class="similarity-score">類似度: {similarity:.3f}</span>', unsafe_allow_html=True)
                    st.markdown(f"**ファイル名:** {filename}")
                    st.markdown(f"**説明:** {description}")

                with col3:
                    # 「正解」ボタン
                    button_key = f"correct_{i}_{session_id}"
                    if st.button(f"✅ 正解", key=button_key, type="secondary"):
                        placeholder = st.empty()
                        placeholder.info(f"第{i+1}位を正解として記録中...")
                        
                        try:
                            result = search_logger.log_user_feedback(session_id, i + 1)
                            if result:
                                placeholder.success(f"✅ 第{i+1}位を正解として記録しました！")
                                for key in ['current_search_session', 'search_results', 'search_query']:
                                    if key in st.session_state: del st.session_state[key]
                                # time.sleep(1) # コメントアウト
                                st.rerun()
                            else:
                                placeholder.error("❌ Google Sheetsへの記録に失敗しました。")
                        except Exception as e:
                            placeholder.error(f"❌ 記録処理でエラーが発生しました: {str(e)}")
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # --------------------------------------------------
        # ▼ 「正解なし」ボタンも同じブロック内で処理
        # --------------------------------------------------
        st.markdown("---")
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col2:
            no_answer_key = f"no_answer_{session_id}"
            if st.button("❌ 正解なし", key=no_answer_key, type="secondary", use_container_width=True):
                placeholder = st.empty()
                placeholder.info("「正解なし」として記録中...")
                
                try:
                    # ランクをNoneとしてフィードバックを記録
                    result = search_logger.log_user_feedback(session_id, None) 
                    
                    if result:
                        placeholder.success("✅ 「正解なし」として記録しました。")
                        
                        # 成功したらセッションをクリアして初期状態に戻す
                        for key in ['current_search_session', 'search_results', 'search_query']:
                            if key in st.session_state:
                                del st.session_state[key]
                        
                        # time.sleep(1) # コメントアウト
                        st.rerun()
                    else:
                        placeholder.error("❌ Google Sheetsへの記録に失敗しました。")
                
                except Exception as e:
                    placeholder.error(f"❌ 記録処理でエラーが発生しました: {str(e)}")
        with col3:
            if st.button("🆓 フリー検索", key="free_search", type="secondary", use_container_width=True):
                placeholder = st.empty()
                placeholder.info("「フリー検索」として記録中...")
                
                try:
                    # ランクをNoneとしてフィードバックを記録
                    result = search_logger.log_user_feedback(session_id, None) 
                    
                    if result:
                        placeholder.success("✅ 「フリー検索」として記録しました。")
                        
                        # 成功したらセッションをクリアして初期状態に戻す
                        for key in ['current_search_session', 'search_results', 'search_query']:
                            if key in st.session_state:
                                del st.session_state[key]
                        
                        # time.sleep(1) # コメントアウト
                        st.rerun()
                    else:
                        placeholder.error("❌ Google Sheetsへの記録に失敗しました。")
                
                except Exception as e:
                    placeholder.error(f"❌ 記録処理でエラーが発生しました: {str(e)}")

def gallery_page():
    """全画像表示ページ"""
    st.markdown('<h1 class="main-header">🖼️ 画像ギャラリー</h1>', unsafe_allow_html=True)
    
    # カテゴリ別画像取得
    category_data = get_all_images_by_category()
    
    if not category_data:
        st.warning("⚠️ 画像データが見つかりません")
        return
    
    # カテゴリ選択
    selected_category = st.selectbox(
        "カテゴリを選択",
        options=["全て"] + list(category_data.keys()),
        index=0
    )
    
    # 1行あたりの画像数
    images_per_row = st.slider("1行あたりの画像数", 2, 6, 4)
    
    # 画像表示
    if selected_category == "全て":
        for category, images in category_data.items():
            st.subheader(f"📁 {category} ({len(images)}件)")
            
            for i in range(0, len(images), images_per_row):
                cols = st.columns(images_per_row)
                for j in range(images_per_row):
                    if i + j < len(images):
                        image_id, filename, description, file_path = images[i + j]
                        with cols[j]:
                            display_image_safely(file_path, caption=f"{filename}\n{description}")
            
            st.divider()
    else:
        if selected_category in category_data:
            images = category_data[selected_category]
            st.subheader(f"📁 {selected_category} ({len(images)}件)")
            
            for i in range(0, len(images), images_per_row):
                cols = st.columns(images_per_row)
                for j in range(images_per_row):
                    if i + j < len(images):
                        image_id, filename, description, file_path = images[i + j]
                        with cols[j]:
                            display_image_safely(file_path, caption=f"{filename}\n{description}")

def main():
    """メイン処理"""
    # セットアップ確認
    check_setup()
    
    # サイドバー
    st.sidebar.title("🎯 ナビゲーション")
    page = st.sidebar.radio(
        "ページを選択",
        ["🔍 画像検索", "🖼️ ギャラリー"],
        index=0
    )
    
    # 統計情報をサイドバーに表示
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 データベース情報")
    
    try:
        stats = get_database_stats()
        st.sidebar.metric("総画像数", stats['total_images'])
        
        st.sidebar.markdown("**カテゴリ別件数:**")
        for category, count in stats['category_counts'].items():
            st.sidebar.markdown(f"- {category}: {count}件")
    except:
        st.sidebar.error("データベース情報の取得に失敗")
    
    # 検索統計をサイドバーに表示
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 検索統計")
    st.sidebar.metric("総検索回数", search_logger.get_session_count())
    st.sidebar.metric("評価済み", search_logger.get_feedback_count())
    
    # セッション情報をサイドバーに表示（デバッグ用）
    # st.sidebar.markdown("---")
    # st.sidebar.markdown("### 🔍 セッション情報")
    # current_session = st.session_state.get('current_search_session', None)
    # if current_session:
    #     st.sidebar.success(f"アクティブセッション: {current_session[-8:]}")  # 最後の8文字を表示
    #     current_query = st.session_state.get('search_query', 'Unknown')
    #     st.sidebar.text(f"クエリ: {current_query}")
    # else:
    #     st.sidebar.info("アクティブセッションなし")
    
    # 全セッション情報（デバッグ用）
    # total_sessions = search_logger.get_session_count()
    # if total_sessions > 0:
    #     st.sidebar.text(f"キャッシュ内セッション数: {total_sessions}")
    
    # デバッグ情報をサイドバーに表示
    # st.sidebar.markdown("---")
    # st.sidebar.markdown("### 🔧 デバッグ情報")
    
    # デバッグ情報の表示/非表示切り替え
    # show_debug = st.sidebar.checkbox("デバッグ情報を表示", value=False)
    
    # if show_debug:
    #     debug_info = search_logger.get_debug_info()
    #     if debug_info:
    #         # 最新の10件のみ表示
    #         recent_debug = debug_info[-10:] if len(debug_info) > 10 else debug_info
    #         debug_text = "\n".join(recent_debug)
    #         st.sidebar.markdown(f'<div class="debug-box">{debug_text}</div>', unsafe_allow_html=True)
    #     else:
    #         st.sidebar.text("デバッグ情報はありません")
    
    # Google Sheets 接続状態の表示
    if search_logger.worksheet:
        st.sidebar.success("✅ Google Sheets 接続済み")
    else:
        st.sidebar.error("❌ Google Sheets 未接続")
    
    # Streamlit secrets の確認
    if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
        st.sidebar.success("✅ Streamlit Secrets 設定済み")
    else:
        st.sidebar.warning("⚠️ Streamlit Secrets 未設定")
    
    # Secrets詳細診断ボタン
    # if st.sidebar.button("🔍 Secrets 詳細診断"):
    #     with st.sidebar:
    #         with st.spinner("診断中..."):
    #             diagnostic = search_logger.get_secrets_diagnostic()
                
    #             st.subheader("Secrets 診断結果")
                
    #             # 基本チェック
    #             if diagnostic['streamlit_has_secrets']:
    #                 st.success("✅ st.secrets 利用可能")
    #             else:
    #                 st.error("❌ st.secrets 利用不可")
                
    #             if diagnostic['gcp_section_exists']:
    #                 st.success("✅ [gcp_service_account] セクション存在")
    #             else:
    #                 st.error("❌ [gcp_service_account] セクション不在")
                
    #             # 詳細フィールド診断
    #             if diagnostic['gcp_section_exists']:
    #                 st.subheader("フィールド詳細")
                    
    #                 # Missing fields
    #                 if diagnostic['missing_fields']:
    #                     st.error(f"❌ 欠如フィールド: {', '.join(diagnostic['missing_fields'])}")
                    
    #                 # Empty fields  
    #                 if diagnostic['empty_fields']:
    #                     st.warning(f"⚠️ 空フィールド: {', '.join(diagnostic['empty_fields'])}")
                    
    #                 # Present fields
    #                 if diagnostic['field_values_safe']:
    #                     st.subheader("設定済みフィールド")
    #                     for field, value in diagnostic['field_values_safe'].items():
    #                         if value != "Empty":
    #                             st.text(f"✅ {field}: {value}")
                
    #             # 総合判定
    #             st.subheader("総合判定")
    #             st.write(diagnostic['diagnostic_message'])
                
    #             # 設定手順へのリンク
    #             if not diagnostic['gcp_section_exists'] or diagnostic['missing_fields'] or diagnostic['empty_fields']:
    #                 st.error("🔧 設定に問題があります")
    #                 st.markdown("**解決方法**: `STREAMLIT_SECRETS_GUIDE.md` を参照してください")
    
    # 接続テストボタン
    # if st.sidebar.button("🔗 Google Sheets 接続テスト"):
    #     with st.sidebar:
    #         with st.spinner("接続テスト中..."):
    #             test_result = search_logger.test_connection()
                
    #             st.subheader("接続テスト結果")
                
    #             # ライブラリの確認
    #             if test_result['libraries_available']:
    #                 st.success("✅ Google Sheets ライブラリ利用可能")
    #             else:
    #                 st.error("❌ Google Sheets ライブラリが利用できません")
                
    #             # シークレットの確認
    #             if test_result['secrets_found']:
    #                 st.success("✅ Streamlit Secrets 発見")
    #             else:
    #                 st.error("❌ Streamlit Secrets が見つかりません")
                
    #             # 認証の確認
    #             if test_result['credentials_valid']:
    #                 st.success("✅ 認証情報 有効")
    #             else:
    #                 st.error("❌ 認証情報 無効")
                
    #             # クライアント認証
    #             if test_result['client_authorized']:
    #                 st.success("✅ Google Sheets クライアント認証 成功")
    #             else:
    #                 st.error("❌ Google Sheets クライアント認証 失敗")
                
    #             # スプレッドシートアクセス
    #             if test_result['spreadsheet_accessible']:
    #                 st.success("✅ スプレッドシート アクセス可能")
    #             else:
    #                 st.error("❌ スプレッドシート アクセス不可")
                
    #             # ワークシートアクセス
    #             if test_result['worksheet_accessible']:
    #                 st.success("✅ ワークシート アクセス可能")
    #             else:
    #                 st.error("❌ ワークシート アクセス不可")
                
    #             # 書き込みテスト
    #             if test_result['can_write']:
    #                 st.success("✅ 書き込みテスト 成功")
    #             else:
    #                 st.error("❌ 書き込みテスト 失敗")
                
    #             # エラーメッセージ
    #             if test_result['error_message']:
    #                 st.error(f"エラー詳細: {test_result['error_message']}")
    
    # 強制ログ書き込みテストボタン（デバッグ用）
    # if st.sidebar.button("🧪 強制ログテスト"):
    #     with st.sidebar:
    #         with st.spinner("強制ログテスト中..."):
    #             # テスト用のセッションデータを作成
    #             test_session_id = "test_" + str(int(time.time()))
    #             test_results = [
    #                 (0.95, "test_id", "test_image.jpg", "テスト", "テスト画像", "/test/path")
    #             ]
                
    #             print(f"APP_DEBUG: === FORCE LOG TEST ===")
    #             print(f"APP_DEBUG: Test session ID: {test_session_id}")
                
    #             # 検索をログに記録
    #             session_id = search_logger.log_search_query("強制テストクエリ", test_results)
    #             print(f"APP_DEBUG: Test search logged with session ID: {session_id}")
                
    #             # フィードバックをログに記録
    #             result = search_logger.log_user_feedback(session_id, 1)
    #             print(f"APP_DEBUG: Test feedback result: {result}")
                
    #             if result:
    #                 st.sidebar.success("✅ 強制ログテスト成功")
    #             else:
    #                 st.sidebar.error("❌ 強制ログテスト失敗")
    
    # ページ切り替え
    if page == "🔍 画像検索":
        search_page()
    elif page == "🖼️ ギャラリー":
        gallery_page()
    
    # フッター
    st.markdown("---")
    st.markdown(
        '<div style="text-align: center; color: #666; font-size: 0.9rem;">'
        '画像検索デモアプリケーション'
        '</div>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 
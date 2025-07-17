"""
CLIP画像検索デモアプリケーション
Streamlitを使用したWebインターフェース
"""

import streamlit as st
import os
from PIL import Image

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
.search-container {
    background-color: #f0f2f6;
    padding: 1.5rem;
    border-radius: 10px;
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
    """検索ページ"""
    st.markdown('<h1 class="main-header">🔍 CLIP画像検索</h1>', unsafe_allow_html=True)
    
    # 統計情報表示
    stats = get_database_stats()
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("総画像数", stats['total_images'])
    
    category_counts = stats['category_counts']
    columns = [col2, col3, col4, col5, col6]
    for i, (category, count) in enumerate(category_counts.items()):
        if i < len(columns):
            with columns[i]:
                st.metric(f"{category}", count)
    
    # 検索インターフェース
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    
    search_query = st.text_input(
        "検索クエリを入力してください",
        placeholder="例: 赤いバッグ、グレーの折り畳み傘..."
    )
    
    search_button = st.button("🔍 検索（上位10件表示）", type="primary", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 検索実行
    if search_button and search_query:
        with st.spinner("検索中..."):
            try:
                # CLIPモデルのロード
                extract_text_features = load_clip_model()
                
                # テキストから特徴量抽出
                query_vector = extract_text_features(search_query)
                
                # 類似画像検索（固定10件）
                results = search_similar_images(query_vector, 10)
                
                if results:
                    # 検索をログに記録
                    session_id = search_logger.log_search_query(search_query, results)
                    
                    # セッションステートに保存
                    st.session_state['current_search_session'] = session_id
                    st.session_state['search_results'] = results
                    st.session_state['search_query'] = search_query
                    
                    st.success(f"✅ 上位10件の結果を表示")
                    
                    # 結果表示
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
                                # 正解ボタン
                                if st.button(f"✅ 正解", key=f"correct_{i}", type="secondary"):
                                    search_logger.log_user_feedback(session_id, i + 1)
                                    st.success(f"第{i+1}位を正解として記録しました！")
                                    st.rerun()
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                    
                    # 正解なしボタン
                    st.markdown("---")
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col2:
                        if st.button("❌ 正解なし", type="secondary", use_container_width=True):
                            search_logger.log_user_feedback(session_id, None)
                            st.info("「正解なし」として記録しました。")
                            st.rerun()
                    
                else:
                    st.warning("⚠️ 検索結果が見つかりませんでした")
                    
            except Exception as e:
                st.error(f"❌ 検索エラー: {str(e)}")

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
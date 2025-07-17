"""
CLIP画像検索デモアプリケーション
Streamlitを使用したWebインターフェース
"""

import streamlit as st
import os
import sys
from PIL import Image
import numpy as np

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
        # パスの正規化（相対パスの問題を解決）
        if image_path.startswith("../"):
            # "../data/img" -> "data/img" に変換
            normalized_path = image_path.replace("../", "")
        else:
            normalized_path = image_path
        
        if os.path.exists(normalized_path):
            image = Image.open(normalized_path)
            st.image(image, caption=caption, width=width)
        else:
            # プレースホルダー表示
            st.markdown(f"""
            <div style="
                border: 2px dashed #ccc; 
                padding: 20px; 
                text-align: center; 
                background-color: #f9f9f9;
                border-radius: 8px;
                width: {width if width else 200}px;
                height: 150px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                margin: 0 auto;
            ">
                <div style="font-size: 3em; color: #ddd;">📷</div>
                <div style="color: #666; font-size: 0.9em;">画像が見つかりません</div>
                <div style="color: #999; font-size: 0.8em; margin-top: 5px;">{caption}</div>
            </div>
            """, unsafe_allow_html=True)
            # デバッグ情報（セッション状態で管理）
            if st.session_state.get('debug_mode', False):
                st.error(f"画像パス: {image_path} → {normalized_path}")
    except Exception as e:
        st.error(f"画像表示エラー: {str(e)}")
        if st.session_state.get('debug_mode', False):
            st.text(f"パス: {image_path}")

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
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "検索クエリを入力してください",
            placeholder="例: 黒い傘、赤いバッグ、スマートフォン..."
        )
    
    with col2:
        top_k = st.selectbox(
            "表示件数",
            options=[5, 10, 15, 20],
            index=1
        )
    
    search_button = st.button("🔍 検索", type="primary", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 検索実行
    if search_button and search_query:
        with st.spinner("検索中..."):
            try:
                # CLIPモデルのロード（キャッシュ済み）
                extract_text_features = load_clip_model()
                
                # テキストから特徴量抽出
                query_vector = extract_text_features(search_query)
                
                # 類似画像検索
                results = search_similar_images(query_vector, top_k)
                
                if results:
                    st.success(f"✅ {len(results)}件の結果が見つかりました")
                    
                    # 結果表示
                    for i, (similarity, image_id, filename, category, description, file_path) in enumerate(results):
                        with st.container():
                            st.markdown('<div class="result-container">', unsafe_allow_html=True)
                            
                            col1, col2 = st.columns([1, 2])
                            
                            with col1:
                                display_image_safely(file_path, width=200)
                            
                            with col2:
                                st.markdown(f"**順位:** {i+1}")
                                st.markdown(f'<span class="category-badge">{category}</span>', unsafe_allow_html=True)
                                st.markdown(f'<span class="similarity-score">類似度: {similarity:.3f}</span>', unsafe_allow_html=True)
                                st.markdown(f"**ファイル名:** {filename}")
                                st.markdown(f"**説明:** {description}")
                            
                            st.markdown('</div>', unsafe_allow_html=True)
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
        # 全カテゴリ表示
        for category, images in category_data.items():
            st.subheader(f"📁 {category} ({len(images)}件)")
            
            # 画像をグリッド表示
            for i in range(0, len(images), images_per_row):
                cols = st.columns(images_per_row)
                for j in range(images_per_row):
                    if i + j < len(images):
                        image_id, filename, description, file_path = images[i + j]
                        with cols[j]:
                            display_image_safely(file_path, caption=f"{filename}\n{description}")
            
            st.divider()
    else:
        # 選択されたカテゴリのみ表示
        if selected_category in category_data:
            images = category_data[selected_category]
            st.subheader(f"📁 {selected_category} ({len(images)}件)")
            
            # 画像をグリッド表示
            for i in range(0, len(images), images_per_row):
                cols = st.columns(images_per_row)
                for j in range(images_per_row):
                    if i + j < len(images):
                        image_id, filename, description, file_path = images[i + j]
                        with cols[j]:
                            display_image_safely(file_path, caption=f"{filename}\n{description}")

def setup_page():
    """セットアップページ"""
    st.markdown('<h1 class="main-header">⚙️ セットアップガイド</h1>', unsafe_allow_html=True)
    
    try:
        from image_utils import show_gdrive_setup_guide
        show_gdrive_setup_guide()
    except ImportError:
        st.info("image_utils.py が見つかりません")
    
    st.markdown("---")
    
    st.markdown("""
    ## 🔧 画像表示の解決策
    
    現在、画像ファイルが見つからない状態です。以下の方法で解決できます：
    
    ### 1. GitHub LFS (推奨)
    ```bash
    # Git LFS をインストール
    git lfs install
    
    # 画像ファイルを追加
    git add data/img/
    git commit -m "Add images with LFS"
    git push origin main
    ```
    
    ### 2. Google Drive
    1. 画像をGoogle Driveにアップロード
    2. 各ファイルの共有リンクを取得
    3. `image_utils.py` の `GDRIVE_IMAGE_MAP` を更新
    
    ### 3. サンプル画像
    デモ用に数枚の画像のみ配置
    
    ---
    
    ### 📊 現在の状況
    """)
    
    # 統計情報表示
    try:
        stats = get_database_stats()
        st.success(f"✅ データベース: {stats['total_images']}件の画像データあり")
        for category, count in stats['category_counts'].items():
            st.info(f"📁 {category}: {count}件")
    except Exception as e:
        st.error(f"❌ データベースエラー: {e}")
    
    # 画像ファイル確認
    import os
    if os.path.exists("data/img"):
        files = []
        for root, dirs, filenames in os.walk("data/img"):
            for filename in filenames:
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    files.append(os.path.join(root, filename))
        
        if files:
            st.success(f"✅ ローカル画像: {len(files)}件見つかりました")
        else:
            st.warning("⚠️ ローカル画像ファイルが見つかりません")
    else:
        st.warning("⚠️ data/img フォルダが存在しません")

def main():
    """メイン処理"""
    # セットアップ確認
    check_setup()
    
    # サイドバー
    st.sidebar.title("🎯 ナビゲーション")
    page = st.sidebar.radio(
        "ページを選択",
        ["🔍 画像検索", "🖼️ ギャラリー", "⚙️ セットアップ"],
        index=0
    )
    
    # デバッグモード設定
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🐛 デバッグ設定")
    debug_mode = st.sidebar.checkbox("デバッグ情報を表示", value=False, key="debug_checkbox")
    st.session_state['debug_mode'] = debug_mode
    
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
    
    # ページ切り替え
    if page == "🔍 画像検索":
        search_page()
    elif page == "🖼️ ギャラリー":
        gallery_page()
    elif page == "⚙️ セットアップ":
        setup_page()
    
    # フッター
    st.markdown("---")
    st.markdown(
        '<div style="text-align: center; color: #666; font-size: 0.9rem;">'
        'CLIP画像検索デモアプリケーション | Powered by Streamlit & CLIP-Japanese'
        '</div>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 
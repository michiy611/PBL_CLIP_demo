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
        # デバッグ情報の表示（本番環境では削除）
        if not os.path.exists(image_path):
            # パスの正規化を試行
            normalized_path = os.path.normpath(image_path)
            if os.path.exists(normalized_path):
                image_path = normalized_path
            else:
                st.error(f"❌ 画像ファイルが見つかりません: `{image_path}`")
                st.info(f"🔍 現在のディレクトリ: `{os.getcwd()}`")
                st.info(f"🔍 存在チェック: `{os.path.exists(image_path)}`")
                return
        
        # image = Image.open(image_path)
        # 大きな画像のリサイズ（メモリ節約）
        # if width and width < 300:
            # サムネイル表示の場合はリサイズ
            # image.thumbnail((width * 2, width * 2), Image.Resampling.LANCZOS)
        st.image(image_path, caption=caption, width=(width * 2, width * 2))
        
    except Exception as e:
        st.error(f"❌ 画像表示エラー: {str(e)}")
        st.info(f"🔍 ファイルパス: `{image_path}`")

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

def debug_page():
    """デバッグページ"""
    st.markdown('<h1 class="main-header">🔧 システムデバッグ</h1>', unsafe_allow_html=True)
    
    # 現在のディレクトリ
    st.subheader("📁 現在のディレクトリ")
    st.code(f"os.getcwd(): {os.getcwd()}")
    
    # プロジェクトルートの確認
    st.subheader("📋 ルートファイル")
    try:
        root_files = os.listdir(".")
        st.write("ルートディレクトリの内容:", root_files)
    except Exception as e:
        st.error(f"ルートディレクトリの読み取りエラー: {e}")
    
    # dataディレクトリの確認
    st.subheader("🗂️ dataディレクトリ")
    if os.path.exists("data"):
        try:
            data_files = os.listdir("data")
            st.success(f"✅ dataディレクトリが存在します: {data_files}")
            
            # data/imgディレクトリの確認
            if os.path.exists("data/img"):
                img_dirs = os.listdir("data/img")
                st.success(f"✅ data/imgディレクトリが存在します: {img_dirs}")
                
                # 各カテゴリフォルダの確認
                for category in img_dirs[:3]:  # 最初の3つのみ
                    category_path = f"data/img/{category}"
                    if os.path.isdir(category_path):
                        files = os.listdir(category_path)
                        st.info(f"📁 {category}フォルダ: {len(files)}個のファイル")
                        if files:
                            st.code(f"最初のファイル: {files[0]}")
            else:
                st.error("❌ data/imgディレクトリが存在しません")
        except Exception as e:
            st.error(f"dataディレクトリの読み取りエラー: {e}")
    else:
        st.error("❌ dataディレクトリが存在しません")
    
    # データベースファイルの確認
    st.subheader("🗄️ データベース")
    if os.path.exists("image_vectors.db"):
        size = os.path.getsize("image_vectors.db")
        st.success(f"✅ image_vectors.db が存在します (サイズ: {size:,} bytes)")
    else:
        st.error("❌ image_vectors.db が存在しません")
    
    # 特定画像ファイルのテスト
    st.subheader("🖼️ サンプル画像テスト")
    test_paths = [
        "data/img/カサ/k22001-傘-0001-01.jpg",
        "data/img/バッグ/k22001-バッグ-0001-01.jpg",
        "data/img/スマホ/k22001-スマホ-0001-01.jpg"
    ]

    ## 画像表示テスト
    st.image(test_paths[0], caption="カサ", width=200)
    st.image(test_paths[1], caption="バッグ", width=200)
    st.image(test_paths[2], caption="スマホ", width=200)
    
    for path in test_paths:
        exists = os.path.exists(path)
        if exists:
            try:
                size = os.path.getsize(path)
                st.success(f"✅ `{path}` (サイズ: {size:,} bytes)")
            except Exception as e:
                st.warning(f"⚠️ `{path}` 存在するがサイズ取得エラー: {e}")
        else:
            st.error(f"❌ `{path}` が存在しません")

def main():
    """メイン処理"""
    # セットアップ確認
    check_setup()
    
    # サイドバー
    st.sidebar.title("🎯 ナビゲーション")
    page = st.sidebar.radio(
        "ページを選択",
        ["🔍 画像検索", "🖼️ ギャラリー", "🔧 デバッグ"],
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
    
    # ページ切り替え
    if page == "🔍 画像検索":
        search_page()
    elif page == "🖼️ ギャラリー":
        gallery_page()
    elif page == "🔧 デバッグ":
        debug_page()
    
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
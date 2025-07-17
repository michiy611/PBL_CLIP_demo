"""
簡単なCLIP画像検索デモアプリケーション
既存のclip-pblデータベースを活用
"""

import streamlit as st
import sqlite3
import sqlite_vec
import numpy as np
import os
import sys
from pathlib import Path

# パスの設定
sys.path.append(str(Path(__file__).parent.parent / "clip-pbl"))

# データベースパス
DB_PATH = "../clip-pbl/example.db"

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

def get_db_connection():
    """データベース接続を取得"""
    if not os.path.exists(DB_PATH):
        st.error(f"❌ データベースファイルが見つかりません: {DB_PATH}")
        st.stop()
    
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    return conn

def extract_text_features_simple(text: str) -> np.ndarray:
    """
    簡単なテキスト特徴量生成（デモ用）
    実際のCLIPモデルの代わりにダミーデータを使用
    """
    # 実際の実装では、ここでCLIPモデルを使用
    # 今回はデモのため、テキストベースの簡単な特徴量を生成
    import hashlib
    hash_object = hashlib.md5(text.encode())
    hash_hex = hash_object.hexdigest()
    
    # ハッシュから512次元のベクトルを生成
    feature_vector = np.zeros(512, dtype=np.float32)
    for i in range(0, min(len(hash_hex), 512)):
        feature_vector[i] = int(hash_hex[i], 16) / 15.0 - 0.5
    
    # 正規化
    norm = np.linalg.norm(feature_vector)
    if norm > 0:
        feature_vector = feature_vector / norm
    
    return feature_vector

def search_similar_items(query_text: str, top_k: int = 5):
    """類似アイテムを検索"""
    try:
        # テキスト特徴量を生成
        query_vector = extract_text_features_simple(query_text)
        
        # データベース接続
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 落とし物データを取得
        cursor.execute("""
        SELECT l.id, l.type, l.feature, l.lost_place, l.picture_path,
               v.embedding
        FROM lost l
        JOIN vec_lost v ON l.vector = v.rowid
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return []
        
        # 類似度計算
        similarities = []
        for row in results:
            item_id, item_type, feature, lost_place, picture_path, embedding_blob = row
            
            # バイナリデータからベクトルに変換
            item_vector = np.frombuffer(embedding_blob, dtype=np.float32)
            
            # コサイン類似度計算
            similarity = np.dot(query_vector, item_vector) / (
                np.linalg.norm(query_vector) * np.linalg.norm(item_vector)
            )
            
            similarities.append({
                'id': item_id,
                'type': item_type,
                'feature': feature,
                'lost_place': lost_place,
                'picture_path': picture_path,
                'similarity': float(similarity)
            })
        
        # 類似度でソート
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similarities[:top_k]
        
    except Exception as e:
        st.error(f"検索エラー: {str(e)}")
        return []

def get_database_stats():
    """データベース統計を取得"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 落とし物件数
        cursor.execute("SELECT COUNT(*) FROM lost")
        lost_count = cursor.fetchone()[0]
        
        # ベクトル数
        cursor.execute("SELECT COUNT(*) FROM vec_lost")
        vector_count = cursor.fetchone()[0]
        
        # カテゴリ別件数
        cursor.execute("SELECT type, COUNT(*) FROM lost GROUP BY type")
        category_counts = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_items': lost_count,
            'total_vectors': vector_count,
            'category_counts': category_counts
        }
    except Exception as e:
        st.error(f"統計情報取得エラー: {str(e)}")
        return {'total_items': 0, 'total_vectors': 0, 'category_counts': {}}

def display_search_page():
    """検索ページ表示"""
    st.markdown('<h1 class="main-header">🔍 CLIP画像検索デモ</h1>', unsafe_allow_html=True)
    
    # 統計情報表示
    stats = get_database_stats()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("総アイテム数", stats['total_items'])
    with col2:
        st.metric("ベクトル数", stats['total_vectors'])
    with col3:
        st.metric("カテゴリ数", len(stats['category_counts']))
    
    # 検索インターフェース
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "検索クエリを入力してください",
            placeholder="例: 青い傘、黒いバッグ、失くした物..."
        )
    
    with col2:
        top_k = st.selectbox(
            "表示件数",
            options=[5, 10, 15, 20],
            index=0
        )
    
    search_button = st.button("🔍 検索", type="primary", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 検索実行
    if search_button and search_query:
        with st.spinner("検索中..."):
            results = search_similar_items(search_query, top_k)
            
            if results:
                st.success(f"✅ {len(results)}件の結果が見つかりました")
                
                # 結果表示
                for i, item in enumerate(results):
                    with st.container():
                        st.markdown('<div class="result-container">', unsafe_allow_html=True)
                        
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            # 画像表示（パスがある場合）
                            if item['picture_path'] and os.path.exists(item['picture_path']):
                                try:
                                    st.image(item['picture_path'], width=200)
                                except:
                                    st.write("📷 画像表示不可")
                            else:
                                st.write("📷 画像なし")
                        
                        with col2:
                            st.markdown(f"**順位:** {i+1}")
                            st.markdown(f'<span class="category-badge">{item["type"]}</span>', unsafe_allow_html=True)
                            st.markdown(f'<span class="similarity-score">類似度: {item["similarity"]:.3f}</span>', unsafe_allow_html=True)
                            st.markdown(f"**特徴:** {item['feature']}")
                            st.markdown(f"**落とし場所:** {item['lost_place']}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ 検索結果が見つかりませんでした")

def display_items_page():
    """全アイテム表示ページ"""
    st.markdown('<h1 class="main-header">📋 登録アイテム一覧</h1>', unsafe_allow_html=True)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT id, type, feature, lost_place, picture_path, 
               datetime(created_at, 'localtime') as created_at
        FROM lost
        ORDER BY created_at DESC
        """)
        
        items = cursor.fetchall()
        conn.close()
        
        if items:
            st.success(f"📊 合計 {len(items)} 件のアイテムが登録されています")
            
            for item in items:
                item_id, item_type, feature, lost_place, picture_path, created_at = item
                
                with st.expander(f"{item_type}: {feature}"):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        if picture_path and os.path.exists(picture_path):
                            try:
                                st.image(picture_path, width=200)
                            except:
                                st.write("📷 画像表示不可")
                        else:
                            st.write("📷 画像なし")
                    
                    with col2:
                        st.markdown(f"**ID:** {item_id}")
                        st.markdown(f"**カテゴリ:** {item_type}")
                        st.markdown(f"**特徴:** {feature}")
                        st.markdown(f"**場所:** {lost_place}")
                        st.markdown(f"**登録日時:** {created_at}")
        else:
            st.info("📝 登録されているアイテムがありません")
            
    except Exception as e:
        st.error(f"データ取得エラー: {str(e)}")

def main():
    """メイン処理"""
    # サイドバー
    st.sidebar.title("🎯 ナビゲーション")
    page = st.sidebar.radio(
        "ページを選択",
        ["🔍 検索", "📋 アイテム一覧"],
        index=0
    )
    
    # データベース統計をサイドバーに表示
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 データベース情報")
    
    try:
        stats = get_database_stats()
        st.sidebar.metric("総アイテム数", stats['total_items'])
        st.sidebar.metric("ベクトル数", stats['total_vectors'])
        
        st.sidebar.markdown("**カテゴリ別件数:**")
        for category, count in stats['category_counts'].items():
            st.sidebar.markdown(f"- {category}: {count}件")
    except:
        st.sidebar.error("データベース情報の取得に失敗")
    
    # ページ表示
    if page == "🔍 検索":
        display_search_page()
    elif page == "📋 アイテム一覧":
        display_items_page()
    
    # フッター
    st.markdown("---")
    st.markdown(
        '<div style="text-align: center; color: #666; font-size: 0.9rem;">'
        'CLIP画像検索デモアプリケーション（簡易版）| Powered by Streamlit'
        '</div>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 
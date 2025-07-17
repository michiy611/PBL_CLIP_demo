"""
データベース操作のユーティリティ関数
"""

import sqlite3
import sqlite_vec
import numpy as np
from typing import List, Tuple, Optional
from database_setup import DB_PATH

def get_db_connection():
    """データベース接続を取得"""
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    return conn

def normalize_image_path(file_path: str) -> str:
    """
    画像パスを正規化
    
    Args:
        file_path: データベースに保存されているパス
        
    Returns:
        str: 正規化されたパス
    """
    if file_path.startswith("../"):
        return file_path.replace("../", "")
    return file_path

def search_similar_images(query_vector: np.ndarray, top_k: int = 5) -> List[Tuple]:
    """
    クエリベクトルに類似した画像を検索
    
    Args:
        query_vector: 検索クエリのベクトル (shape: [512])
        top_k: 返す結果の数
        
    Returns:
        List of tuples: (similarity, image_id, filename, category, description, file_path)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # SQLite-vecで類似検索（正しい構文）
    query_blob = query_vector.astype(np.float32).tobytes()
    
    query = '''
    SELECT 
        distance,
        i.id,
        i.filename, 
        i.category, 
        i.description,
        i.file_path
    FROM image_vectors v
    JOIN images i ON v.id = i.id
    WHERE v.embedding MATCH ?
    ORDER BY distance
    LIMIT ?
    '''
    
    cursor.execute(query, (query_blob, top_k))
    results = cursor.fetchall()
    conn.close()
    
    # 距離を類似度に変換し、パスを正規化
    formatted_results = []
    for row in results:
        distance, image_id, filename, category, description, file_path = row
        similarity = 1.0 / (1.0 + distance)  # 距離を類似度に変換
        normalized_path = normalize_image_path(file_path)  # パス正規化
        formatted_results.append((similarity, image_id, filename, category, description, normalized_path))
    
    return formatted_results

def get_all_images_by_category() -> dict:
    """
    カテゴリ別に全画像を取得
    
    Returns:
        dict: {category: [(image_id, filename, description, file_path), ...]}
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
    SELECT category, id, filename, description, file_path
    FROM images
    ORDER BY category, filename
    '''
    
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    
    # カテゴリ別に整理し、パスを正規化
    category_dict = {}
    for category, image_id, filename, description, file_path in results:
        if category not in category_dict:
            category_dict[category] = []
        normalized_path = normalize_image_path(file_path)  # パス正規化
        category_dict[category].append((image_id, filename, description, normalized_path))
    
    return category_dict

def get_database_stats() -> dict:
    """
    データベースの統計情報を取得
    
    Returns:
        dict: 統計情報
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 総件数
    cursor.execute("SELECT COUNT(*) FROM images")
    total_images = cursor.fetchone()[0]
    
    # カテゴリ別件数
    cursor.execute("SELECT category, COUNT(*) FROM images GROUP BY category")
    category_counts = dict(cursor.fetchall())
    
    conn.close()
    
    return {
        'total_images': total_images,
        'category_counts': category_counts
    }

def check_database_exists() -> bool:
    """データベースファイルの存在確認"""
    import os
    return os.path.exists(DB_PATH)

def get_image_by_id(image_id: int) -> Optional[Tuple]:
    """
    画像IDから画像情報を取得
    
    Args:
        image_id: 画像ID
        
    Returns:
        tuple: (filename, category, description, file_path) or None
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
    SELECT filename, category, description, file_path
    FROM images
    WHERE id = ?
    '''
    
    cursor.execute(query, (image_id,))
    result = cursor.fetchone()
    conn.close()
    
    return result 
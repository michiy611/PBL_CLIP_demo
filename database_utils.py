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

def search_similar_images(query_vector: np.ndarray, top_k: int = 10) -> List[Tuple]:
    """
    クエリベクトルに類似する画像を検索
    
    Args:
        query_vector: 検索クエリの特徴量ベクトル
        top_k: 取得する上位k件
        
    Returns:
        List of tuples: (similarity, image_id, filename, category, description, file_path)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # sqlite-vecを使用したベクトル類似度検索
    query_blob = query_vector.astype(np.float32).tobytes()
    
    query = '''
    SELECT 
        vec_distance_cosine(iv.embedding, ?) as similarity,
        i.id,
        i.filename,
        i.category,
        i.description,
        i.file_path
    FROM image_vectors iv
    JOIN images i ON iv.id = i.id
    ORDER BY similarity ASC
    LIMIT ?
    '''
    
    cursor.execute(query, (query_blob, top_k))
    results = cursor.fetchall()
    conn.close()
    
    # コサイン距離を類似度に変換（1 - distance）
    formatted_results = []
    for row in results:
        distance, image_id, filename, category, description, file_path = row
        similarity = 1 - distance  # 距離を類似度に変換
        formatted_results.append((similarity, image_id, filename, category, description, file_path))
    
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
    
    # カテゴリ別に整理
    category_dict = {}
    for category, image_id, filename, description, file_path in results:
        if category not in category_dict:
            category_dict[category] = []
        category_dict[category].append((image_id, filename, description, file_path))
    
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
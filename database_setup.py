"""
データベースセットアップスクリプト
画像の特徴量とメタデータを格納するデータベースを作成
"""

import sqlite3
import sqlite_vec
import os

DB_PATH = "image_vectors.db"

def setup_database():
    """データベースとテーブルを作成"""
    
    # 既存のデータベースファイルがあれば削除
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"既存のデータベース {DB_PATH} を削除しました")
    
    # データベース接続
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    
    cursor = conn.cursor()
    
    # 画像メタデータテーブル
    cursor.execute('''
    CREATE TABLE images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        file_path TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # ベクトルテーブル（sqlite-vec使用）
    cursor.execute('''
    CREATE VIRTUAL TABLE image_vectors USING vec0(
        id INTEGER PRIMARY KEY,
        embedding FLOAT[512]
    )
    ''')
    
    # インデックス作成
    cursor.execute('CREATE INDEX idx_category ON images(category)')
    cursor.execute('CREATE INDEX idx_filename ON images(filename)')
    
    conn.commit()
    conn.close()
    
    print(f"データベース {DB_PATH} を作成しました")
    print("テーブル: images, image_vectors")

def verify_database():
    """データベースの構造を確認"""
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    
    cursor = conn.cursor()
    
    # テーブル一覧
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("作成されたテーブル:", [table[0] for table in tables])
    
    # 各テーブルのスキーマ確認
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"\n{table_name} テーブルの構造:")
        for col in columns:
            print(f"  {col[1]} {col[2]}")
    
    conn.close()

if __name__ == "__main__":
    setup_database()
    verify_database() 
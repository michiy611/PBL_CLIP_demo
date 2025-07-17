"""
画像の特徴量抽出とベクトル化バッチ処理スクリプト
data/imgフォルダとdata/labelフォルダからデータを読み込み、
特徴量を抽出してデータベースに保存
"""

import os
import csv
import sqlite3
import sqlite_vec
import numpy as np
from tqdm import tqdm
from database_setup import DB_PATH, setup_database
import sys

# データディレクトリのパス
DATA_IMG_DIR = "./data/img"
DATA_LABEL_DIR = "./data/label"

# カテゴリ名
CATEGORIES = ["カサ", "サイフ", "スマホ", "タオル", "バッグ"]

def load_label_data():
    """ラベルCSVファイルからデータを読み込み"""
    image_data = {}
    
    for category in CATEGORIES:
        label_file = os.path.join(DATA_LABEL_DIR, f"{category}.csv")
        if not os.path.exists(label_file):
            print(f"警告: ラベルファイルが見つかりません: {label_file}")
            continue
            
        with open(label_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                filename = row['ファイル名']
                description = row['説明文']
                image_path = os.path.join(DATA_IMG_DIR, category, filename)
                
                # 画像ファイルが存在するかチェック
                if os.path.exists(image_path):
                    image_data[filename] = {
                        'category': category,
                        'description': description,
                        'file_path': image_path,
                        'filename': filename
                    }
                else:
                    print(f"警告: 画像ファイルが見つかりません: {image_path}")
    
    print(f"読み込み完了: {len(image_data)}件の画像データ")
    return image_data

def extract_and_save_features(image_data):
    """画像の特徴量を抽出してデータベースに保存"""
    
    # 一度だけCLIPモデルを初期化
    from clip_feature_extractor import CLIPFeatureExtractor
    extractor = CLIPFeatureExtractor()
    
    # データベース接続
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    cursor = conn.cursor()
    
    successful_count = 0
    error_count = 0
    
    print("画像の特徴量抽出を開始...")
    
    # バッチサイズを定義（メモリ使用量を制御）
    batch_size = 50
    batch_data = []
    
    for filename, data in tqdm(image_data.items(), desc="特徴量抽出中"):
        try:
            # 特徴量抽出（既に初期化済みのextractorを使用）
            features = extractor.extract_image_features(data['file_path'])
            
            # メタデータをimagesテーブルに保存
            cursor.execute('''
            INSERT INTO images (filename, category, description, file_path)
            VALUES (?, ?, ?, ?)
            ''', (
                data['filename'],
                data['category'],
                data['description'],
                data['file_path']
            ))
            
            image_id = cursor.lastrowid
            
            # 特徴量をimage_vectorsテーブルに保存
            feature_blob = features.astype(np.float32).tobytes()
            cursor.execute('''
            INSERT INTO image_vectors (id, embedding)
            VALUES (?, ?)
            ''', (image_id, feature_blob))
            
            successful_count += 1
            
            # バッチごとにコミット
            if successful_count % batch_size == 0:
                conn.commit()
                print(f"  {successful_count}件処理完了...")
            
        except Exception as e:
            print(f"エラー: {filename} の処理に失敗: {str(e)}")
            error_count += 1
            continue
    
    # 最終コミット
    conn.commit()
    conn.close()
    
    print(f"\n処理完了:")
    print(f"  成功: {successful_count}件")
    print(f"  エラー: {error_count}件")
    
    return successful_count, error_count

def verify_data():
    """データベースの内容を確認"""
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    cursor = conn.cursor()
    
    # 総件数確認
    cursor.execute("SELECT COUNT(*) FROM images")
    total_images = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM image_vectors")
    total_vectors = cursor.fetchone()[0]
    
    print(f"\nデータベース確認:")
    print(f"  画像メタデータ: {total_images}件")
    print(f"  特徴量ベクトル: {total_vectors}件")
    
    # カテゴリ別件数
    cursor.execute("SELECT category, COUNT(*) FROM images GROUP BY category")
    category_counts = cursor.fetchall()
    print(f"\nカテゴリ別件数:")
    for category, count in category_counts:
        print(f"  {category}: {count}件")
    
    # サンプルデータ表示
    cursor.execute("SELECT filename, category, description FROM images LIMIT 3")
    samples = cursor.fetchall()
    print(f"\nサンプルデータ:")
    for filename, category, description in samples:
        print(f"  {filename} [{category}]: {description}")
    
    conn.close()

def main():
    """メイン処理"""
    print("=== CLIP画像ベクトル化バッチ処理 ===")
    
    # データディレクトリの存在確認
    if not os.path.exists(DATA_IMG_DIR):
        print(f"エラー: 画像ディレクトリが見つかりません: {DATA_IMG_DIR}")
        sys.exit(1)
    
    if not os.path.exists(DATA_LABEL_DIR):
        print(f"エラー: ラベルディレクトリが見つかりません: {DATA_LABEL_DIR}")
        sys.exit(1)
    
    # データベースセットアップ
    print("1. データベースセットアップ...")
    setup_database()
    
    # ラベルデータ読み込み
    print("\n2. ラベルデータ読み込み...")
    image_data = load_label_data()
    
    if not image_data:
        print("エラー: 処理対象の画像データがありません")
        sys.exit(1)
    
    # 特徴量抽出とデータベース保存
    print("\n3. 特徴量抽出とデータベース保存...")
    successful_count, error_count = extract_and_save_features(image_data)
    
    # データベース内容確認
    print("\n4. データベース内容確認...")
    verify_data()
    
    print("\n=== 処理完了 ===")

if __name__ == "__main__":
    main() 
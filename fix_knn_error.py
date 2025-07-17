"""
sqlite-vec KNNクエリエラーの診断と修正ユーティリティ

エラー: "A LIMIT or 'k = ?' constraint is required on vec0 knn queries."
の原因を特定し、修正方法を提供します。
"""

import sqlite3
import sqlite_vec
import traceback
from database_setup import DB_PATH

def diagnose_knn_error():
    """KNNクエリエラーの診断を実行"""
    print("=== sqlite-vec KNNクエリ エラー診断 ===\n")
    
    # データベース接続テスト
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
        cursor = conn.cursor()
        print("✅ データベース接続成功")
    except Exception as e:
        print(f"❌ データベース接続エラー: {e}")
        return
    
    # テーブル存在確認
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='image_vectors'")
        if cursor.fetchone():
            print("✅ image_vectorsテーブルが存在")
        else:
            print("❌ image_vectorsテーブルが存在しません")
            return
    except Exception as e:
        print(f"❌ テーブル確認エラー: {e}")
        return
    
    # 正しいKNNクエリのテスト
    try:
        import numpy as np
        test_vector = np.random.rand(512).astype(np.float32).tobytes()
        
        # 正しいクエリ（LIMIT句あり）
        correct_query = '''
        SELECT distance, id
        FROM image_vectors
        WHERE embedding MATCH ?
        ORDER BY distance
        LIMIT ?
        '''
        cursor.execute(correct_query, (test_vector, 5))
        results = cursor.fetchall()
        print(f"✅ 正しいKNNクエリ実行成功: {len(results)}件取得")
        
    except Exception as e:
        print(f"❌ 正しいKNNクエリエラー: {e}")
    
    # 問題のあるKNNクエリのテスト（LIMIT句なし）
    try:
        incorrect_query = '''
        SELECT distance, id
        FROM image_vectors
        WHERE embedding MATCH ?
        ORDER BY distance
        '''
        cursor.execute(incorrect_query, (test_vector,))
        results = cursor.fetchall()
        print("❌ LIMIT句なしクエリが実行されました（本来エラーになるべき）")
        
    except Exception as e:
        print(f"✅ 期待通りのエラー: {str(e)}")
        if "LIMIT or 'k = ?' constraint is required" in str(e):
            print("   → これがユーザーが遭遇しているエラーです")
    
    conn.close()

def show_fix_examples():
    """修正例を表示"""
    print("\n=== 修正方法 ===\n")
    
    print("❌ 問題のあるクエリ例:")
    print("""
    cursor.execute('''
    SELECT distance, id, filename
    FROM image_vectors v
    JOIN images i ON v.id = i.id  
    WHERE v.embedding MATCH ?
    ORDER BY distance
    ''', (query_vector,))
    """)
    
    print("\n✅ 修正されたクエリ例:")
    print("""
    cursor.execute('''
    SELECT distance, id, filename
    FROM image_vectors v
    JOIN images i ON v.id = i.id  
    WHERE v.embedding MATCH ?
    ORDER BY distance
    LIMIT ?
    ''', (query_vector, top_k))
    """)
    
    print("\n🔧 修正手順:")
    print("1. SQLクエリにWHERE ... MATCH文を使用している箇所を探す")
    print("2. そのクエリにLIMIT句が含まれているかを確認")
    print("3. LIMIT句がない場合は 'LIMIT ?' を追加")
    print("4. execute()の引数にlimit値を追加")
    
    print("\n📋 チェックポイント:")
    print("- search_similar_images()関数")
    print("- 類似度検索を行う全ての関数")
    print("- vec0仮想テーブルに対するMATCHクエリ")

def find_potential_issues():
    """潜在的な問題箇所を特定"""
    print("\n=== 潜在的問題箇所の検索 ===\n")
    
    import os
    import re
    
    # Pythonファイルを検索
    python_files = []
    for root, dirs, files in os.walk('.'):
        # venvディレクトリは除外
        dirs[:] = [d for d in dirs if not d.startswith('venv')]
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    suspicious_patterns = [
        r'WHERE.*embedding.*MATCH.*(?!.*LIMIT)',  # MATCHがあってLIMITがない
        r'WHERE.*\.embedding.*MATCH.*ORDER BY.*(?!.*LIMIT)',  # より具体的なパターン
    ]
    
    found_issues = False
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for pattern in suspicious_patterns:
                matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
                if matches:
                    print(f"⚠️  潜在的問題: {file_path}")
                    for match in matches:
                        print(f"   マッチ: {match[:100]}...")
                    found_issues = True
                    
        except Exception as e:
            print(f"ファイル読み込みエラー {file_path}: {e}")
    
    if not found_issues:
        print("✅ 明らかな問題は見つかりませんでした")

def main():
    """メイン実行"""
    diagnose_knn_error()
    show_fix_examples() 
    find_potential_issues()
    
    print("\n=== 推奨次ステップ ===")
    print("1. エラーが発生した具体的な操作を特定")
    print("2. そのときのスタックトレースを確認")
    print("3. 該当するファイルの検索関数を確認")
    print("4. 上記の修正例を参考にLIMIT句を追加")

if __name__ == "__main__":
    main() 
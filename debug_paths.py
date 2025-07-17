"""
Streamlit Community Cloud用デバッグスクリプト
画像ファイルのパス問題を調査
"""

import os
import streamlit as st
from pathlib import Path

def debug_file_system():
    """ファイルシステムの状態をデバッグ"""
    st.header("🔍 ファイルシステムデバッグ")
    
    # 現在のディレクトリ
    st.subheader("現在のディレクトリ")
    st.code(f"os.getcwd(): {os.getcwd()}")
    
    # プロジェクトルートの確認
    st.subheader("プロジェクトファイル")
    root_files = os.listdir(".")
    st.write("ルートディレクトリのファイル:", root_files)
    
    # dataディレクトリの確認
    st.subheader("dataディレクトリ")
    if os.path.exists("data"):
        data_files = os.listdir("data")
        st.write("dataディレクトリの内容:", data_files)
        
        # data/imgディレクトリの確認
        if os.path.exists("data/img"):
            img_dirs = os.listdir("data/img")
            st.write("data/imgディレクトリの内容:", img_dirs)
            
            # 各カテゴリフォルダの確認
            for category in img_dirs:
                category_path = f"data/img/{category}"
                if os.path.isdir(category_path):
                    files = os.listdir(category_path)
                    st.write(f"{category}フォルダ ({len(files)}個のファイル):", files[:5])  # 最初の5個のみ表示
    else:
        st.error("❌ dataディレクトリが存在しません")
    
    # 特定ファイルの存在確認
    st.subheader("特定ファイルの存在確認")
    test_paths = [
        "data/img/カサ/k22001-傘-0001-01.jpg",
        "data/img/バッグ/k22001-バッグ-0001-01.jpg",
        "image_vectors.db",
        "app.py"
    ]
    
    for path in test_paths:
        exists = os.path.exists(path)
        st.write(f"{'✅' if exists else '❌'} `{path}`: {exists}")

if __name__ == "__main__":
    debug_file_system() 
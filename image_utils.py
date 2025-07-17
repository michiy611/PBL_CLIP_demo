"""
外部ストレージから画像を取得するユーティリティ
"""

import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import os
from typing import Optional

# Google Drive ファイルIDマッピング（例）
GDRIVE_IMAGE_MAP = {
    # カテゴリ/ファイル名 -> Google Drive ファイルID
    # 例: "カサ/umbrella1.jpg": "1ABC123...",
    # TODO: 実際の画像をアップロード後に更新
}

def get_gdrive_direct_url(file_id: str) -> str:
    """Google DriveファイルIDから直接ダウンロードURLを生成"""
    return f"https://drive.google.com/uc?export=download&id={file_id}"

@st.cache_data
def load_image_from_url(url: str) -> Optional[Image.Image]:
    """URLから画像を読み込み（キャッシュ付き）"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except Exception as e:
        st.error(f"画像読み込みエラー: {e}")
        return None

def get_image_from_gdrive(file_path: str) -> Optional[Image.Image]:
    """Google Driveから画像を取得"""
    if file_path in GDRIVE_IMAGE_MAP:
        file_id = GDRIVE_IMAGE_MAP[file_path]
        url = get_gdrive_direct_url(file_id)
        return load_image_from_url(url)
    return None

def display_image_with_fallback(file_path: str, caption: str = "", width: int = None):
    """
    画像表示（ローカル → Google Drive → プレースホルダーの順で試行）
    """
    # 1. ローカルファイル確認
    if os.path.exists(file_path):
        try:
            image = Image.open(file_path)
            st.image(image, caption=caption, width=width)
            return
        except Exception:
            pass
    
    # 2. Google Driveから取得
    relative_path = file_path.replace("data/img/", "").replace("\\", "/")
    gdrive_image = get_image_from_gdrive(relative_path)
    if gdrive_image:
        st.image(gdrive_image, caption=caption, width=width)
        return
    
    # 3. プレースホルダー表示
    st.warning(f"画像が見つかりません: {caption}")
    
    # プレースホルダー画像（オプション）
    placeholder_url = "https://via.placeholder.com/300x200?text=Image+Not+Found"
    placeholder_image = load_image_from_url(placeholder_url)
    if placeholder_image:
        st.image(placeholder_image, caption=f"{caption} (プレースホルダー)", width=width)

# Google Driveセットアップガイド
def show_gdrive_setup_guide():
    """Google Driveセットアップ手順を表示"""
    st.info("""
    ### 📁 Google Drive セットアップ手順
    
    1. **画像をGoogle Driveにアップロード**
       - フォルダ構造: カサ/, サイフ/, スマホ/, タオル/, バッグ/
    
    2. **各画像ファイルの共有設定**
       - 右クリック → 「リンクを取得」
       - 「リンクを知っている全員」に設定
       - ファイルIDを取得 (例: 1ABC123...)
    
    3. **image_utils.py を更新**
       - GDRIVE_IMAGE_MAP に ファイルパス → ファイルID のマッピングを追加
    
    4. **デプロイ・テスト**
       - 変更をcommit & push
       - Streamlitで動作確認
    """) 
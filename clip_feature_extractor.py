"""
CLIP日本語ベースモデルによる特徴量抽出関数

使用方法:
1. extract_image_features(image_path) - 画像パスから特徴量を抽出
2. extract_text_features(text) - テキストから特徴量を抽出
"""

import os
import numpy as np
from PIL import Image
import torch
from transformers import AutoImageProcessor, AutoModel, AutoTokenizer
from typing import Union, List

class CLIPFeatureExtractor:
    def __init__(self, model_path='line-corporation/clip-japanese-base', device=None):
        """
        CLIP特徴量抽出器の初期化
        
        Args:
            model_path (str): モデルのパス
            device (str): 実行デバイス ('cpu', 'cuda', または None で自動選択)
        """
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = model_path
        
        print(f"CLIPモデルを読み込み中... (デバイス: {self.device})")
        
        # モデル、プロセッサ、トークナイザーの初期化
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        self.processor = AutoImageProcessor.from_pretrained(model_path, trust_remote_code=True)
        self.model = AutoModel.from_pretrained(model_path, trust_remote_code=True).to(self.device)
        
        print("CLIPモデルの読み込み完了!")

    def extract_image_features(self, image_path: str, normalize: bool = True) -> np.ndarray:
        """
        画像パスから特徴量を抽出
        
        Args:
            image_path (str): 画像ファイルのパス
            normalize (bool): 特徴量を正規化するかどうか
            
        Returns:
            np.ndarray: 画像特徴量 (shape: [feature_dim])
            
        Raises:
            FileNotFoundError: 画像ファイルが見つからない場合
            Exception: 画像読み込みエラーの場合
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"画像ファイルが見つかりません: {image_path}")
        
        try:
            # 画像読み込み
            image = Image.open(image_path).convert('RGB')
            
            # 前処理
            processed_image = self.processor([image], return_tensors="pt").to(self.device)
            
            # 特徴量抽出
            with torch.no_grad():
                image_features = self.model.get_image_features(**processed_image)
                
                # 正規化
                if normalize:
                    image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                
                # CPUに移動してnumpy配列に変換
                return image_features.cpu().numpy().squeeze()
                
        except Exception as e:
            raise Exception(f"画像特徴量抽出エラー ({image_path}): {e}")

    def extract_text_features(self, text: Union[str, List[str]], normalize: bool = True) -> np.ndarray:
        """
        テキストから特徴量を抽出
        
        Args:
            text (str or List[str]): 入力テキスト（文字列または文字列のリスト）
            normalize (bool): 特徴量を正規化するかどうか
            
        Returns:
            np.ndarray: テキスト特徴量 (shape: [feature_dim] or [num_texts, feature_dim])
        """
        try:
            # 文字列の場合はリストに変換
            if isinstance(text, str):
                text_list = [text]
                single_text = True
            else:
                text_list = text
                single_text = False
            
            # トークナイズ
            text_inputs = self.tokenizer(text_list).to(self.device)
            
            # 特徴量抽出
            with torch.no_grad():
                text_features = self.model.get_text_features(**text_inputs)
                
                # 正規化
                if normalize:
                    text_features = text_features / text_features.norm(dim=-1, keepdim=True)
                
                # CPUに移動してnumpy配列に変換
                features = text_features.cpu().numpy()
                
                # 単一テキストの場合は次元を削減
                if single_text:
                    return features.squeeze()
                else:
                    return features
                    
        except Exception as e:
            raise Exception(f"テキスト特徴量抽出エラー: {e}")

    def compute_similarity(self, image_features: np.ndarray, text_features: np.ndarray) -> float:
        """
        画像特徴量とテキスト特徴量の類似度を計算
        
        Args:
            image_features (np.ndarray): 画像特徴量
            text_features (np.ndarray): テキスト特徴量
            
        Returns:
            float: コサイン類似度
        """
        # 正規化されていることを前提とした内積（コサイン類似度）
        return float(np.dot(image_features, text_features))

# グローバル関数として提供
_extractor = None

def get_extractor():
    """グローバルなextractorインスタンスを取得"""
    global _extractor
    if _extractor is None:
        _extractor = CLIPFeatureExtractor()
    return _extractor

def extract_image_features(image_path: str, normalize: bool = True) -> np.ndarray:
    """
    画像パスから特徴量を抽出（グローバル関数）
    
    Args:
        image_path (str): 画像ファイルのパス
        normalize (bool): 特徴量を正規化するかどうか
        
    Returns:
        np.ndarray: 画像特徴量
    """
    return get_extractor().extract_image_features(image_path, normalize)

def extract_text_features(text: Union[str, List[str]], normalize: bool = True) -> np.ndarray:
    """
    テキストから特徴量を抽出（グローバル関数）
    
    Args:
        text (str or List[str]): 入力テキスト
        normalize (bool): 特徴量を正規化するかどうか
        
    Returns:
        np.ndarray: テキスト特徴量
    """
    return get_extractor().extract_text_features(text, normalize)

def compute_similarity(image_features: np.ndarray, text_features: np.ndarray) -> float:
    """
    画像特徴量とテキスト特徴量の類似度を計算（グローバル関数）
    
    Args:
        image_features (np.ndarray): 画像特徴量
        text_features (np.ndarray): テキスト特徴量
        
    Returns:
        float: コサイン類似度
    """
    return get_extractor().compute_similarity(image_features, text_features) 
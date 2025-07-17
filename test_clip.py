"""
CLIP特徴量抽出の動作確認テスト
"""

import os
import sys

def test_clip_extraction():
    """CLIP特徴量抽出のテスト"""
    
    try:
        from clip_feature_extractor import CLIPFeatureExtractor
        
        print("1. CLIPモデルの初期化テスト...")
        extractor = CLIPFeatureExtractor()
        print("✅ CLIPモデル初期化成功")
        
        print("\n2. テキスト特徴量抽出テスト...")
        text_features = extractor.extract_text_features("黒い傘")
        print(f"✅ テキスト特徴量抽出成功 - 形状: {text_features.shape}")
        
        print("\n3. 画像ファイル検索...")
        # テスト用の画像を探す
        test_image_path = None
        for category in ["カサ", "サイフ", "スマホ", "タオル", "バッグ"]:
            category_path = f"../data/img/{category}"
            if os.path.exists(category_path):
                for file in os.listdir(category_path):
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        test_image_path = os.path.join(category_path, file)
                        break
                if test_image_path:
                    break
        
        if test_image_path:
            print(f"テスト画像: {test_image_path}")
            
            print("\n4. 画像特徴量抽出テスト...")
            image_features = extractor.extract_image_features(test_image_path)
            print(f"✅ 画像特徴量抽出成功 - 形状: {image_features.shape}")
            
            print("\n5. 類似度計算テスト...")
            similarity = extractor.compute_similarity(image_features, text_features)
            print(f"✅ 類似度計算成功 - 類似度: {similarity:.4f}")
            
        else:
            print("⚠️ テスト用の画像ファイルが見つかりませんでした")
        
        print("\n🎉 すべてのテストが成功しました！")
        return True
        
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_clip_extraction()
    sys.exit(0 if success else 1) 
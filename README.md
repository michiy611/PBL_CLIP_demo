# CLIP画像検索デモアプリケーション

CLIP（Contrastive Language-Image Pre-training）モデルを使用した日本語対応の画像検索デモアプリケーションです。

## 🚀 デモサイト

**→ [ライブデモはこちら](https://your-app-url.streamlit.app/)** *(デプロイ後にURLを更新)*

## ✨ 機能

- **🔍 自然言語検索**: 日本語で画像を検索
- **🖼️ ギャラリー表示**: カテゴリ別の画像一覧
- **📊 統計情報**: データベース内の画像統計
- **📱 レスポンシブデザイン**: モバイル・デスクトップ対応

## 🎯 使用例

```
検索例:
- "黒い傘"
- "赤いバッグ"
- "スマートフォン"
- "青いタオル"
```

## 🛠️ 技術スタック

- **フロントエンド**: Streamlit
- **機械学習**: CLIP-Japanese (line-corporation/clip-japanese-base)
- **データベース**: SQLite + sqlite-vec
- **画像処理**: PIL, OpenCV
- **バックエンド**: Python 3.10+

## 📦 ローカル実行

### 前提条件
- Python 3.10+
- pip

### インストール

1. リポジトリをクローン
```bash
git clone https://github.com/[username]/[repository].git
cd [repository]
```

2. 仮想環境の作成・アクティベート
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux  
source venv/bin/activate
```

3. 依存関係のインストール
```bash
pip install -r requirements.txt
```

4. データベースの作成（初回のみ）
```bash
python batch_vectorize.py
```

5. アプリケーションの起動
```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` にアクセス

## 🌐 デプロイ

### Streamlit Community Cloud（推奨）

1. GitHubにリポジトリをプッシュ
2. [share.streamlit.io](https://share.streamlit.io/) でアカウント作成
3. リポジトリを選択してデプロイ

詳細は [README_DEPLOY.md](README_DEPLOY.md) を参照

## 📁 プロジェクト構造

```
clip-demo/
├── app.py                    # メインアプリケーション
├── clip_feature_extractor.py # CLIP特徴量抽出
├── database_utils.py         # データベース操作
├── database_setup.py         # データベース設定
├── batch_vectorize.py        # バッチ処理
├── requirements.txt          # Python依存関係
├── packages.txt             # システムパッケージ
├── image_vectors.db         # SQLiteデータベース
├── .streamlit/
│   └── config.toml          # Streamlit設定
└── data/
    └── img/                 # 画像ファイル
        ├── カサ/
        ├── サイフ/
        ├── スマホ/
        ├── タオル/
        └── バッグ/
```

## 🔧 設定

### カスタマイズ

- 画像カテゴリの追加: `data/img/` に新しいフォルダを作成
- モデルの変更: `clip_feature_extractor.py` のモデルパスを修正
- UIのカスタマイズ: `app.py` のCSSを編集

### パフォーマンス調整

- バッチサイズ: メモリ使用量に応じて調整
- キャッシュ設定: Streamlitの `@st.cache_resource` を活用

## 📊 データベース情報

- **形式**: SQLite + sqlite-vec拡張
- **サイズ**: 約2.2MB
- **画像数**: プロジェクトによって異なる
- **ベクトル次元**: 512次元 (CLIP-Japanese)

## 🚨 制限事項

- **Streamlit Community Cloud**: CPU 1GB RAM制限
- **初回起動**: CLIPモデル読み込みで2-3分
- **同時接続**: 複数ユーザー対応だが性能は限定的

## 🤝 貢献

1. フォークを作成
2. フィーチャーブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトはMITライセンスのもとで公開されています。

## 🙏 謝辞

- [CLIP-Japanese](https://huggingface.co/line-corporation/clip-japanese-base) by LINE Corporation
- [sqlite-vec](https://github.com/asg017/sqlite-vec) by Alex Garcia
- [Streamlit](https://streamlit.io/) チーム

## 📞 サポート

問題が発生した場合は、[Issues](https://github.com/[username]/[repository]/issues) でお知らせください。 
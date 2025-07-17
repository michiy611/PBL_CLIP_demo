# CLIP画像検索デモアプリケーション（簡易版）

このアプリケーションは、既存のCLIPベクトルデータベースを活用した画像検索システムのデモです。

## 特徴

- 🔍 **テキスト検索**: 日本語でテキストを入力して類似アイテムを検索
- 📋 **アイテム一覧**: 登録されているアイテムの閲覧
- ⚡ **高速検索**: sqlite-vecを使用したベクトル類似度検索
- 🌐 **Web UI**: Streamlitベースの直感的なインターフェース
- ☁️ **クラウド対応**: URLを共有してアクセス可能

## セットアップ手順

### 1. 依存関係のインストール

```bash
pip install -r requirements_simple.txt
```

### 2. アプリケーションの起動

```bash
streamlit run simple_app.py
```

## ファイル構成

```
clip-demo/
├── simple_app.py              # Streamlitメインアプリケーション
├── requirements_simple.txt    # 軽量依存関係
├── setup.sh                  # クラウドデプロイ用セットアップ
├── Procfile                   # Herokuデプロイ用
├── .streamlit/
│   └── config.toml           # Streamlit設定
└── README_simple.md          # このファイル
```

## 使用方法

### 検索機能

1. **テキスト入力**: 「青い傘」「折りたたみ傘」などの検索クエリを入力
2. **件数選択**: 表示件数を5、10、15、20から選択
3. **検索実行**: 検索ボタンをクリック
4. **結果確認**: 類似度順にアイテムと説明が表示

### アイテム一覧

1. **一覧表示**: 登録されているすべてのアイテムを確認
2. **詳細表示**: 各アイテムをクリックして詳細情報を表示

## クラウドデプロイメント

### Streamlit Community Cloud

1. GitHubリポジトリにコードをプッシュ
2. [Streamlit Community Cloud](https://streamlit.io/cloud) にアクセス
3. リポジトリを選択してデプロイ
4. メインファイルとして `simple_app.py` を指定

### Heroku

```bash
# Heroku CLI を使用
heroku create your-app-name
git push heroku main
```

### その他のプラットフォーム

- **Railway**: 自動検出でデプロイ可能
- **Google Cloud Run**: Docker化してデプロイ

## 技術仕様

- **言語**: Python 3.8+
- **フレームワーク**: Streamlit
- **データベース**: SQLite + sqlite-vec
- **ベクトル検索**: コサイン類似度
- **特徴量**: 512次元ベクトル

## 注意事項

この簡易版では、実際のCLIPモデルの代わりにハッシュベースの特徴量を使用しています。
本格的な画像-テキスト類似度検索には、実際のCLIPモデルを統合する必要があります。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。 
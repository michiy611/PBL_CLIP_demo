# デプロイ前チェックリスト

## ✅ ファイル準備完了確認

### 必須ファイル
- [ ] `app.py` - メインアプリケーション
- [ ] `clip_feature_extractor.py` - CLIP特徴量抽出
- [ ] `database_utils.py` - データベース操作
- [ ] `database_setup.py` - データベース設定
- [ ] `requirements.txt` - Python依存関係
- [ ] `packages.txt` - システムパッケージ
- [ ] `image_vectors.db` - SQLiteデータベース（2.2MB）
- [ ] `.streamlit/config.toml` - Streamlit設定
- [ ] `.gitignore` - Git除外設定

### 画像データ
- [ ] `data/img/` フォルダとその中の画像ファイル

## ✅ GitHubリポジトリ設定

### リポジトリ作成
- [ ] GitHub上でパブリックリポジトリを作成
- [ ] リポジトリ名を決定（例：clip-image-search-demo）
- [ ] README.mdを作成（オプション）

### ファイルアップロード
1. 方法1: GitHub Web Interface
   - [ ] 各ファイルを個別にアップロード
   - [ ] フォルダ構造を維持

2. 方法2: Git コマンド
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/[username]/[repository].git
   git push -u origin main
   ```

## ✅ Streamlit Community Cloud設定

### アカウント設定
- [ ] [share.streamlit.io](https://share.streamlit.io/) でアカウント作成
- [ ] GitHubアカウントでサインイン
- [ ] GitHubリポジトリへのアクセス許可

### アプリ作成
- [ ] "New app" をクリック
- [ ] Repository: 作成したリポジトリを選択
- [ ] Branch: `main` を選択  
- [ ] Main file path: `app.py` を指定
- [ ] App URL: カスタムURLを設定（オプション）

## ✅ デプロイ後確認事項

### 基本動作確認
- [ ] アプリが正常に起動する
- [ ] 検索機能が動作する
- [ ] 画像が正しく表示される
- [ ] ギャラリー機能が動作する

### パフォーマンス確認
- [ ] 初回ロード時間（2-3分程度）
- [ ] 検索応答時間
- [ ] 複数ユーザーアクセス時の動作

### エラー対応
- [ ] 依存関係エラーがないか確認
- [ ] SQLite関連エラーがないか確認
- [ ] メモリエラーがないか確認

## 🔗 共有とアクセス

### URL共有
- [ ] デプロイ完了URLを取得
- [ ] チームメンバーにURL共有
- [ ] アクセステストの実施

### ドキュメント作成
- [ ] 使用方法の説明
- [ ] トラブルシューティングガイド
- [ ] 連絡先の記載

## 📝 注意事項

- SQLiteファイル（2.2MB）は容量制限内
- 初回起動時にCLIPモデルの読み込みで時間がかかります
- スリープ状態から復帰時も再起動時間が必要
- パブリックリポジトリのため機密情報は含めない 
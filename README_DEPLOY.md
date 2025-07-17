# CLIP画像検索デモアプリのデプロイ手順

## Streamlit Community Cloudでのデプロイ

### 前提条件
- GitHubアカウント
- Streamlit Community Cloudアカウント（GitHubアカウントで無料登録可能）

### 手順

#### 1. GitHubリポジトリの準備

1. GitHubで新しいパブリックリポジトリを作成
2. 以下のファイルをリポジトリにアップロード：
   ```
   app.py
   clip_feature_extractor.py
   database_utils.py
   database_setup.py
   batch_vectorize.py
   requirements.txt
   packages.txt
   image_vectors.db
   .streamlit/config.toml
   data/img/ (画像フォルダ)
   ```

#### 2. Streamlit Community Cloudでのデプロイ

1. [share.streamlit.io](https://share.streamlit.io/) にアクセス
2. GitHubアカウントでサインイン
3. "New app" をクリック
4. リポジトリ、ブランチ、メインファイル（`app.py`）を選択
5. "Deploy!" をクリック

#### 3. 設定のポイント

- **リポジトリタイプ**: パブリックリポジトリである必要があります
- **メインファイル**: `app.py`
- **Python version**: 3.10.x（自動選択）
- **SQLiteファイル**: 2.2MBなので容量制限内で問題なし

#### 4. トラブルシューティング

**モジュールが見つからないエラー**
- `requirements.txt`の内容を確認
- パッケージバージョンの互換性をチェック

**SQLite拡張エラー**
- `packages.txt`で`libsqlite3-dev`が指定されているか確認

**メモリエラー**
- 初回起動時にCLIPモデルの読み込みで時間がかかる場合があります
- リソース制限に達した場合は再起動を試行

#### 5. 共有とアクセス

デプロイ完了後、以下のようなURLが提供されます：
```
https://[app-name]-[random-string].streamlit.app/
```

このURLをチームメンバーに共有することで、ブラウザから直接アクセス可能です。

#### 6. 制限事項

- **リソース制限**: CPU 1GB RAM, 初回起動時間約2-3分
- **非アクティブ時**: 数時間使用されないとスリープモードに入ります
- **同時接続**: 複数ユーザーの同時アクセスに対応

### セキュリティ注意事項

- パブリックリポジトリのため、機密情報は含めないでください
- 必要に応じてプライベートリポジトリ対応の有料プランを検討してください

### 代替デプロイオプション

1. **Railway**: 月500時間の無料枠
2. **Render**: 750時間/月の無料枠
3. **Heroku**: 無料プランは廃止されましたが、学生プランあり

推奨は**Streamlit Community Cloud**です。Streamlitアプリに最適化されており、設定も簡単です。 
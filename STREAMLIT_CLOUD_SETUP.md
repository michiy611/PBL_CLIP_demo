# Streamlit Cloud デプロイガイド（Google Cloud Logging対応）

CLIP画像検索デモアプリケーションをStreamlit Cloudにデプロイする手順

## 📋 前提条件

1. GitHub アカウント
2. Google Cloud プロジェクト（サービスアカウント設定済み）
3. feature/log ブランチの準備完了

## 🚀 **Step 1: GitHubへのプッシュ**

### 1.1 変更をコミット
```bash
# 現在のブランチ確認
git status

# 変更をステージング
git add .

# コミット
git commit -m "Add Google Cloud Logging support for Streamlit Cloud"

# feature/logブランチをプッシュ
git push origin feature/log
```

## 🌐 **Step 2: Streamlit Cloud セットアップ**

### 2.1 Streamlit Cloud にアクセス
1. [Streamlit Cloud](https://share.streamlit.io/) にアクセス
2. GitHubアカウントでログイン
3. 「New app」をクリック

### 2.2 アプリケーション設定
1. **Repository**: あなたのGitHubリポジトリを選択
2. **Branch**: `feature/log` を選択
3. **Main file path**: `app.py`
4. **App URL**: 任意のURL名を設定（例：`clip-search-demo-log`）

### 2.3 Advanced settings（重要）
**「Advanced settings」をクリックして開く**

#### Python version
```
3.11
```

#### Requirements file
```
requirements.txt
```

#### Secrets
**ここが最重要！** 以下のセクションで詳しく説明します。

## 🔑 **Step 3: Google Cloud Secrets 設定**

### 3.1 サービスアカウントキー取得
Google Cloud Consoleから`service-account-key.json`をダウンロード済みであることを確認

### 3.2 Streamlit Cloud Secrets 設定
Streamlit Cloud の **「Secrets」** セクションに以下を入力：

```toml
[gcp]
project_id = "your-actual-project-id"

credentials = '''
{
  "type": "service_account",
  "project_id": "your-actual-project-id",
  "private_key_id": "actual-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nACTUAL_PRIVATE_KEY_CONTENT_HERE\n-----END PRIVATE KEY-----\n",
  "client_email": "clip-search-logger@your-project.iam.gserviceaccount.com",
  "client_id": "actual-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/clip-search-logger%40your-project.iam.gserviceaccount.com"
}
'''
```

### 3.3 実際の値の取得方法

#### Project ID
Google Cloud Console → プロジェクト選択 → プロジェクトIDをコピー

#### Credentials JSON
1. ダウンロードした `service-account-key.json` をテキストエディタで開く
2. **全内容をコピー**
3. Streamlit Secrets の `credentials` の `'''` と `'''` の間に貼り付け

**重要**: 改行も含めてそのまま貼り付けてください

## 🚀 **Step 4: デプロイ実行**

### 4.1 アプリケーションデプロイ
1. すべての設定を確認
2. **「Deploy!」**をクリック
3. デプロイ開始（5-10分程度）

### 4.2 デプロイ状況確認
- **「Logs」タブ**でリアルタイムデプロイログを確認
- `✅ Google Cloud Logging connected successfully` が表示されることを確認

### 4.3 エラーの場合
よくあるエラーと解決方法：

#### エラー1: "ModuleNotFoundError: google.cloud"
```
# requirements.txt に以下が含まれているか確認
google-cloud-logging>=3.8.0
google-auth>=2.17.0
```

#### エラー2: "DefaultCredentialsError"
- Secrets の `project_id` が正しいか確認
- Secrets の `credentials` JSON が完全で有効か確認

#### エラー3: "PermissionDenied"
- Google Cloud でサービスアカウントに「Logs Writer」ロールが付与されているか確認
- Cloud Logging API が有効になっているか確認

## 🧪 **Step 5: 動作確認**

### 5.1 アプリケーションテスト
1. デプロイ完了後、アプリのURLにアクセス
2. 検索クエリを入力（例：「赤いバッグ」）
3. 検索結果で「✅ 正解」または「❌ 正解なし」をクリック

### 5.2 Google Cloud Logging 確認
1. [Google Cloud Console](https://console.cloud.google.com/) → ログ → ログエクスプローラー
2. 以下のクエリで確認：
```
logName="projects/YOUR_PROJECT_ID/logs/clip-search-demo"
jsonPayload.event_type="search_query"
```
3. Streamlit Cloudからのログエントリが表示されることを確認

## 📊 **Step 6: ログ分析セットアップ**

### 6.1 基本的なログクエリ
```bash
# 検索クエリのみ
jsonPayload.event_type="search_query"

# ユーザーフィードバック
jsonPayload.event_type="user_feedback"

# 正解が見つかった検索
jsonPayload.is_correct_answer_found=true

# 特定の検索クエリ
jsonPayload.query_text:"赤いバッグ"
```

### 6.2 BigQuery エクスポート設定（オプション）
1. ログ → ログルーター → 「シンクを作成」
2. 宛先: BigQuery データセット
3. フィルタ: `logName="projects/YOUR_PROJECT_ID/logs/clip-search-demo"`

### 6.3 アラート設定（オプション）
1. モニタリング → アラート → 「ポリシーを作成」
2. 条件: `severity="ERROR"`
3. 通知: メール等

## 🔧 **Step 7: アプリケーション更新**

### 7.1 コード変更時
```bash
# 変更をコミット
git add .
git commit -m "Update description"
git push origin feature/log
```

### 7.2 Streamlit Cloud での自動再デプロイ
- GitHubへのプッシュで自動的に再デプロイされます
- 「Reboot」ボタンで手動再起動も可能

### 7.3 Secrets 変更時
1. Streamlit Cloud → App settings → Secrets
2. 設定を変更後、「Save」
3. アプリが自動的に再起動されます

## 🔐 **セキュリティのベストプラクティス**

### 7.1 Secrets 管理
- ✅ **Do**: Streamlit Secrets 機能を使用
- ❌ **Don't**: コードにハードコーディング
- ❌ **Don't**: service-account-key.json をGitにコミット

### 7.2 サービスアカウント権限
- ✅ **最小権限**: Logs Writer のみ
- ❌ **過大権限**: Editor や Owner は避ける

### 7.3 定期的なメンテナンス
- サービスアカウントキーの定期ローテーション（推奨：90日）
- 不要なログの定期削除（コスト管理）

## 📈 **Step 8: 本番運用のヒント**

### 8.1 パフォーマンス監視
```bash
# レスポンス時間監視
jsonPayload.event_type="search_query"
| fields timestamp, jsonPayload.response_time_ms
```

### 8.2 ユーザー行動分析
```bash
# 人気検索キーワード
jsonPayload.event_type="search_query"
| stats count by jsonPayload.query_text
| sort count desc
```

### 8.3 精度分析
```bash
# 検索精度の計算
jsonPayload.event_type="user_feedback"
| stats 
    count as total_feedback,
    countif(jsonPayload.is_correct_answer_found=true) as correct_answers
| eval accuracy_rate = correct_answers / total_feedback * 100
```

## 🚨 **トラブルシューティング**

### よくある問題と解決方法

#### 問題1: アプリが起動しない
**確認項目**:
1. requirements.txt が正しいか
2. app.py にシンタックスエラーがないか
3. Secrets が正しく設定されているか

#### 問題2: ログが送信されない
**確認項目**:
1. Google Cloud プロジェクトID が正しいか
2. サービスアカウントの権限が正しいか
3. Cloud Logging API が有効か

#### 問題3: 画像が表示されない
**確認項目**:
1. data/img フォルダがGitにコミットされているか
2. 画像ファイルのパスが正しいか
3. ファイルサイズ制限に引っかかっていないか

## 📞 **サポート**

### Streamlit Cloud サポート
- [Streamlit Community](https://discuss.streamlit.io/)
- [Streamlit Documentation](https://docs.streamlit.io/streamlit-cloud)

### Google Cloud サポート
- [Google Cloud Logging Documentation](https://cloud.google.com/logging/docs)
- [Google Cloud Support](https://cloud.google.com/support)

---

## 🎉 **完了！**

この手順に従って設定すれば、feature/logブランチがStreamlit Cloudにデプロイされ、Google Cloud Loggingでリアルタイムにユーザーの検索行動を記録・分析できるようになります。

**重要なURL**:
- **アプリURL**: `https://share.streamlit.io/[username]/[repo]/feature/log`
- **ログ確認**: `https://console.cloud.google.com/logs/query` 
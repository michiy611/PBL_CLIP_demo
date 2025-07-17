# Google Sheets設定ガイド

このアプリケーションは検索ログをGoogle Spreadsheetsに自動保存します。

## 1. Google Cloud Console設定

### 1.1 プロジェクト作成
1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成
3. プロジェクト名: `clip-search-logger` など

### 1.2 API有効化
1. 「APIs & Services」→「Library」
2. 以下のAPIを有効化：
   - Google Sheets API
   - Google Drive API

### 1.3 サービスアカウント作成
1. 「APIs & Services」→「Credentials」
2. 「CREATE CREDENTIALS」→「Service account」
3. 名前: `sheets-logger`
4. 作成後、JSONキーをダウンロード
5. ファイル名を `service-account-key.json` に変更

## 2. ローカル環境設定

### 2.1 認証ファイル配置
```bash
# プロジェクトルートに配置
cp ~/Downloads/service-account-key.json ./service-account-key.json
```

### 2.2 スプレッドシート権限設定
1. サービスアカウントのメールアドレスをコピー
2. Google Spreadsheetsで新しいシートを作成（またはログシートを開く）
3. 「共有」→サービスアカウントのメールを追加→「編集者」権限

## 3. Streamlit Cloud設定

### 3.1 Secrets設定
Streamlit Cloudのダッシュボードで「Settings」→「Secrets」に以下を追加：

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nyour-private-key\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account-email"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```

### 3.2 シークレット値の取得
`service-account-key.json`の内容をコピーして、各フィールドに対応する値を設定してください。

## 4. ログ形式

アプリケーションは以下の形式でログを記録します：

| 列名 | 説明 |
|------|------|
| timestamp | 検索実行時刻 |
| session_id | セッション識別子 |
| query_text | 検索クエリ |
| correct_rank | 正解の順位（1-10）または"no_correct_answer" |
| result_N_filename | N番目の結果のファイル名 |
| result_N_similarity | N番目の結果の類似度 |
| result_N_category | N番目の結果のカテゴリ |

## 5. 注意事項

- サービスアカウントキーは秘密情報です。Gitリポジトリにコミットしないでください
- スプレッドシートは自動作成されます（`CLIP Search Logs`）
- 初回実行時にヘッダー行が自動追加されます
- インターネット接続が必要です

## 6. トラブルシューティング

### 権限エラー
- サービスアカウントがスプレッドシートの編集権限を持っているか確認
- API（Sheets, Drive）が有効化されているか確認

### 認証エラー
- JSON形式が正しいか確認
- Streamlit Cloudのsecretsが正しく設定されているか確認

### スプレッドシートが見つからない
- アプリケーションが自動的に作成しますが、権限が不足している可能性があります
- 手動で作成し、サービスアカウントに共有してください 
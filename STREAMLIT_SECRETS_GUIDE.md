# Streamlit Cloud Secrets 設定ガイド

## 🔧 Streamlit Cloud での設定手順

### 1. Google Cloud Service Account の準備

#### 1.1 Google Cloud Console での作業
1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. プロジェクトを作成または選択
3. **APIs & Services > Library** で以下を有効化：
   - Google Sheets API
   - Google Drive API

#### 1.2 サービスアカウントの作成
1. **APIs & Services > Credentials**
2. **CREATE CREDENTIALS > Service account**
3. 名前: `clip-search-logger`
4. **Keys** タブ > **ADD KEY > Create new key**
5. **JSON** を選択してダウンロード

### 2. Streamlit Cloud での Secrets 設定

#### 2.1 ダッシュボードでの設定
1. [Streamlit Cloud](https://share.streamlit.io/) にログイン
2. 該当アプリを選択
3. **Settings** (⚙️) をクリック
4. **Secrets** タブを選択

#### 2.2 Secrets の記入

**重要**: 以下の形式で **完全に一致** するように入力してください：

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_CONTENT\n-----END PRIVATE KEY-----\n"
client_email = "clip-search-logger@your-project-id.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/clip-search-logger%40your-project-id.iam.gserviceaccount.com"
```

#### 2.3 値の取得方法

ダウンロードしたJSONファイルから以下のように値をコピーします：

**JSONファイルの例**:
```json
{
  "type": "service_account",
  "project_id": "clip-demo-123456",
  "private_key_id": "abcd1234...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n",
  "client_email": "clip-search-logger@clip-demo-123456.iam.gserviceaccount.com",
  "client_id": "123456789012345678901",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/clip-search-logger%40clip-demo-123456.iam.gserviceaccount.com"
}
```

### 3. 設定チェックリスト

#### ✅ 必須確認項目
- [ ] `[gcp_service_account]` セクション名が正確
- [ ] 全てのフィールドが存在する（10個）
- [ ] `private_key` に改行文字 `\n` が含まれている
- [ ] ダブルクォートで値を囲んでいる
- [ ] JSONファイルの値と一致している

#### ⚠️ よくある間違い
1. **セクション名の誤記**: `[gcp_service_account]` でなく `[gcp]` など
2. **private_key の改行**: `\n` が含まれていない
3. **メールアドレスの%エンコード**: `@` が `%40` になっていない場合
4. **値の欠如**: 必須フィールドが空文字になっている

### 4. 動作確認

#### 4.1 アプリの再起動
1. Streamlit Cloud でアプリを **Reboot**
2. ログを確認して起動エラーがないかチェック

#### 4.2 接続テスト
1. アプリのサイドバーで以下を確認：
   - ✅ Streamlit Secrets 設定済み
2. **🔗 Google Sheets 接続テスト** ボタンをクリック
3. 全てのステップが ✅ になることを確認

### 5. トラブルシューティング

#### Case 1: "Streamlit Secrets が見つかりません"
**原因**: Secrets が設定されていない、またはセクション名が間違っている
**解決**: 上記の手順に従って正確に設定

#### Case 2: "認証情報 無効"  
**原因**: JSONファイルの値が正しくコピーされていない
**解決**: 特に `private_key` の改行文字を確認

#### Case 3: "Google Sheets クライアント認証 失敗"
**原因**: APIが有効化されていない
**解決**: Google Cloud Console でAPI有効化を再確認

#### Case 4: "スプレッドシート アクセス不可"
**原因**: スプレッドシートが存在しない（初回実行時は正常）
**解決**: アプリが自動作成するので問題なし

### 6. 成功時の表示

正しく設定されている場合、以下のように表示されます：

```
✅ Google Sheets ライブラリ利用可能
✅ Streamlit Secrets 発見  
✅ 認証情報 有効
✅ Google Sheets クライアント認証 成功
✅ スプレッドシート アクセス可能
✅ ワークシート アクセス可能
✅ 書き込みテスト 成功
```

### 7. よくある質問

**Q: スプレッドシートは事前に作成する必要がありますか？**
A: いいえ。アプリが自動的に「CLIP Search Logs」を作成します。

**Q: サービスアカウントに特別な権限が必要ですか？**
A: Google Sheets API と Google Drive API が有効化されていれば十分です。

**Q: 複数のプロジェクトで同じサービスアカウントを使えますか？**
A: はい、可能です。ただし、それぞれで Secrets の設定が必要です。 
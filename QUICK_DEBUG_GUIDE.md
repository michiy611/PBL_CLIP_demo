# 🚨 Streamlit Secrets エラー解決ガイド

## "Streamlit Secrets が見つかりません" エラーの解決手順

### ⚡ 緊急対応手順

#### 1. まずアプリでデバッグを実行
1. Streamlit Cloud でアプリを開く
2. サイドバーの **🔍 Secrets 詳細診断** ボタンをクリック
3. どの段階で失敗しているかを確認

#### 2. エラーパターン別対処法

##### Case A: "st.secrets 利用不可"
```
❌ st.secrets 利用不可
```
**原因**: Streamlit Cloud でSecretsが全く設定されていない  
**解決**: Streamlit Cloud の Settings > Secrets タブに移動して設定

##### Case B: "[gcp_service_account] セクション不在"
```
✅ st.secrets 利用可能
❌ [gcp_service_account] セクション不在
```
**原因**: セクション名が間違っている  
**解決**: `[gcp_service_account]` が正確に入力されているか確認

##### Case C: "欠如フィールド" または "空フィールド"
```
✅ [gcp_service_account] セクション存在
❌ 欠如フィールド: project_id, private_key
⚠️ 空フィールド: client_email
```
**原因**: 必須フィールドが不足または空  
**解決**: 下記の完全な設定例を使用

### 📋 完全な設定例（コピー用）

Streamlit Cloud の Settings > Secrets に以下を**完全にコピー**してください：

```toml
[gcp_service_account]
type = "service_account"
project_id = "YOUR_PROJECT_ID"
private_key_id = "YOUR_PRIVATE_KEY_ID"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_CONTENT\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "YOUR_CLIENT_ID"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
```

### 🔧 値の入手方法

1. **Google Cloud Console** にアクセス
2. **APIs & Services > Credentials**
3. サービスアカウントの **Keys** タブ
4. **ADD KEY > Create new key > JSON**
5. ダウンロードしたJSONファイルから値をコピー

### ✅ 設定確認チェックリスト

- [ ] セクション名が `[gcp_service_account]` （正確）
- [ ] 10個すべてのフィールドが存在
- [ ] `private_key` に `\n` が含まれている
- [ ] すべての値がダブルクォートで囲まれている
- [ ] JSONファイルからコピーした値が正確

### 🎯 成功確認

設定後、以下が表示されることを確認：

```
✅ st.secrets 利用可能
✅ [gcp_service_account] セクション存在
✅ All required fields are present and non-empty
```

### 🔗 接続テスト

Secrets設定後：

1. **Reboot** アプリを再起動
2. **🔗 Google Sheets 接続テスト** を実行
3. 全ての項目が ✅ になることを確認

### ❗ まだ解決しない場合

1. **Google Cloud Console** で以下を確認：
   - Google Sheets API が有効化されている
   - Google Drive API が有効化されている
   - サービスアカウントが正しく作成されている

2. **JSON ファイルの再ダウンロード**：
   - 新しいキーを作成
   - 古いキーは削除

3. **ブラウザのキャッシュクリア**：
   - Streamlit Cloud をリロード
   - シークレットモードで試行

### 📞 サポート

それでも解決しない場合は、デバッグ診断の結果をスクリーンショットで保存し、問題を報告してください。 
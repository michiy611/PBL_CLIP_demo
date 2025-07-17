# Google Cloud Logging セットアップガイド

CLIP画像検索デモアプリケーション用のGoogle Cloud Logging設定手順

## 📋 前提条件

1. Googleアカウント
2. クレジットカード（無料枠内で使用可能）
3. Python環境

## 🚀 Step 1: Google Cloud Projectの作成

### 1.1 Google Cloud Consoleにアクセス
- [Google Cloud Console](https://console.cloud.google.com/)にアクセス
- Googleアカウントでログイン

### 1.2 新しいプロジェクトを作成
1. 画面上部の「プロジェクトを選択」をクリック
2. 「新しいプロジェクト」をクリック
3. プロジェクト名を入力（例：`clip-search-demo`）
4. 組織は「組織なし」のままでOK
5. 「作成」をクリック

### 1.3 プロジェクトIDをメモ
- 作成されたプロジェクトIDをメモしてください
- 例：`clip-search-demo-123456`

## 🔑 Step 2: 必要なAPIの有効化

### 2.1 Cloud Logging APIの有効化
1. 左側メニューから「APIとサービス」→「ライブラリ」
2. 「Cloud Logging API」を検索
3. 「有効にする」をクリック

### 2.2 Cloud Resource Manager APIの有効化（推奨）
1. 「Cloud Resource Manager API」も検索
2. 「有効にする」をクリック

## 🛡️ Step 3: サービスアカウントの作成

### 3.1 サービスアカウント作成
1. 左側メニューから「IAMと管理」→「サービスアカウント」
2. 「サービスアカウントを作成」をクリック
3. 以下を入力：
   - **名前**: `clip-search-logger`
   - **説明**: `CLIP search demo logging service`
4. 「作成して続行」をクリック

### 3.2 ロールの付与
1. 「このサービスアカウントにプロジェクトへのアクセスを許可する」で以下のロールを追加：
   - `Logs Writer` （必須）
   - `Monitoring Metric Writer` （オプション）
2. 「続行」をクリック
3. 「完了」をクリック

### 3.3 キーファイルのダウンロード
1. 作成されたサービスアカウントをクリック
2. 「キー」タブをクリック
3. 「キーを追加」→「新しいキーを作成」
4. 「JSON」を選択して「作成」
5. **ダウンロードされたJSONファイルを安全な場所に保存**

## 💻 Step 4: ローカル環境の設定

### 4.1 必要なライブラリのインストール
```bash
pip install google-cloud-logging
```

### 4.2 認証情報の設定

#### 方法A: 環境変数（推奨）
```bash
# Windowsの場合
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\your\service-account-key.json
set GOOGLE_CLOUD_PROJECT=your-project-id

# macOS/Linuxの場合
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

#### 方法B: .envファイル
1. プロジェクトルートに`.env`ファイルを作成
2. 以下を記述：
```
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json
GOOGLE_CLOUD_PROJECT=your-project-id
```

#### 方法C: JSONファイルをプロジェクトフォルダに配置
1. ダウンロードしたJSONファイルを `service-account-key.json` にリネーム
2. プロジェクトのルートフォルダに配置
3. **⚠️ 重要**: `.gitignore`に追加してGitにコミットしないように注意

## 🔧 Step 5: アプリケーションの設定確認

### 5.1 cloud_logger.pyの設定確認
`cloud_logger.py`で環境変数からプロジェクトIDを読み込み：

```python
import os
gcp_project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
search_logger = create_logger("cloud", project_id=gcp_project_id)
```

### 5.2 直接指定する場合
```python
# 直接プロジェクトIDを指定
search_logger = create_logger("cloud", project_id="your-project-id")
```

## 🧪 Step 6: 動作テスト

### 6.1 基本テスト
```python
from cloud_logger import search_logger

# テストログ送信
session_id = search_logger.log_search_query("テスト検索", [])
print(f"Session ID: {session_id}")
```

### 6.2 Google Cloud Consoleでログ確認
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 「オペレーション」→「ログ」
3. ログエクスプローラーで以下のクエリを実行：
```
resource.type="global"
logName="projects/YOUR_PROJECT_ID/logs/clip-search-demo"
```

## 💰 料金について

### 無料枠
- **月間50GB**まで無料
- **30日間の保存期間**（無料）
- **一般的な使用では無料枠内で十分**

### 料金発生の目安
- 50GB = 約2,500万行のログエントリ
- 本デモアプリの場合：
  - 1回の検索：約1KB
  - **月間50,000回検索まで無料**

### 課金される場合
- 50GB/月を超過：$0.50/GB
- 長期保存（30日超）：$0.01/GB/月

## 🔍 トラブルシューティング

### エラー: "google.auth.exceptions.DefaultCredentialsError"
**原因**: 認証情報が正しく設定されていません

**解決方法**:
1. `GOOGLE_APPLICATION_CREDENTIALS`環境変数が正しく設定されているか確認
2. JSONファイルのパスが正しいか確認
3. JSONファイルが破損していないか確認

### エラー: "google.api_core.exceptions.PermissionDenied"
**原因**: サービスアカウントの権限が不足しています

**解決方法**:
1. `Logs Writer`ロールが付与されているか確認
2. プロジェクトIDが正しいか確認
3. Cloud Logging APIが有効になっているか確認

### ログが表示されない
**確認事項**:
1. プロジェクトIDが正しいか確認
2. ログクエリの`logName`を確認
3. 時間範囲を適切に設定

### エラー: "google.api_core.exceptions.NotFound"
**原因**: プロジェクトが見つからない、またはAPIが無効

**解決方法**:
1. プロジェクトIDを再確認
2. Cloud Logging APIが有効になっているか確認
3. サービスアカウントが正しいプロジェクトに所属しているか確認

## 📊 ログ分析

### 6.1 基本的なフィルタリング
Google Cloud Consoleのログエクスプローラーで：

```
# 検索クエリのみ表示
jsonPayload.event_type="search_query"

# ユーザーフィードバックのみ表示
jsonPayload.event_type="user_feedback"

# 特定のクエリを検索
jsonPayload.query_text:"赤いバッグ"

# 正解があった検索のみ
jsonPayload.is_correct_answer_found=true

# エラーログのみ
severity="ERROR"
```

### 6.2 BigQueryでの高度な分析
1. 「ログ」→「ログルーター」で「シンクを作成」
2. BigQueryデータセットに送信設定
3. SQLクエリで詳細分析：

```sql
SELECT 
  JSON_EXTRACT_SCALAR(jsonPayload, '$.query_text') as query,
  COUNT(*) as search_count,
  COUNTIF(JSON_EXTRACT_SCALAR(jsonPayload, '$.event_type') = 'user_feedback' 
          AND JSON_EXTRACT_SCALAR(jsonPayload, '$.is_correct_answer_found') = 'true') as correct_count
FROM `your-project.your-dataset.clip_search_demo`
WHERE JSON_EXTRACT_SCALAR(jsonPayload, '$.event_type') = 'search_query'
GROUP BY query
ORDER BY search_count DESC
```

### 6.3 アラートの設定
1. 「モニタリング」→「アラート」
2. 「ポリシーを作成」でエラー監視：
   - **条件**: `severity="ERROR"`
   - **通知**: メール、Slack等

## 🚀 本番環境での運用

### Streamlit Cloudでの使用
1. Streamlit Cloudの「Secrets」機能を使用
2. `secrets.toml`に以下を追加：
```toml
[gcp]
project_id = "your-project-id"
credentials = '''
{
  "type": "service_account",
  "project_id": "your-project-id",
  ...
}
'''
```

3. アプリでsecrets取得：
```python
import streamlit as st
import json
from google.oauth2 import service_account

# Streamlit secretsから認証情報取得
if "gcp" in st.secrets:
    credentials_info = json.loads(st.secrets["gcp"]["credentials"])
    credentials = service_account.Credentials.from_service_account_info(credentials_info)
    project_id = st.secrets["gcp"]["project_id"]
```

### Docker環境での使用
```dockerfile
# 環境変数で設定
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/service-account-key.json
ENV GOOGLE_CLOUD_PROJECT=your-project-id

# または認証情報をbuildで追加
COPY service-account-key.json /app/
```

## 🔐 セキュリティのベストプラクティス

1. **サービスアカウントキーの管理**
   - 環境変数で管理
   - Gitにコミットしない
   - 定期的にローテーション（推奨：90日ごと）

2. **最小権限の原則**
   - `Logs Writer`ロールのみ付与
   - 不要な権限は削除

3. **個人情報の保護**
   - 検索クエリに個人情報が含まれないよう注意
   - 必要に応じてマスキング処理を実装

4. **監査ログの確認**
   - Cloud Audit Logsで使用状況を定期確認
   - 異常なアクセスパターンを監視

## 📈 高度な機能

### 7.1 カスタムメトリクスの作成
```python
from google.cloud import monitoring_v3

# 検索精度メトリクスを作成
client = monitoring_v3.MetricServiceClient()
# ... メトリクス作成コード
```

### 7.2 構造化ログの活用
```python
# 構造化ログエントリ
log_entry = {
    "event_type": "search_query",
    "query_text": query,
    "search_results": results,
    "metadata": {
        "response_time_ms": response_time,
        "model_version": "clip-japanese-v2",
        "user_agent": request.headers.get("User-Agent")
    }
}
```

### 7.3 Cloud Functionsとの連携
ログを受けて自動処理：
```python
def process_search_logs(cloud_event):
    """Cloud Loggingからトリガーされる処理"""
    log_entry = cloud_event.data
    # 自動分析・レポート生成
```

---

## 📞 サポート

設定で困った場合は、以下のリソースを参照：
- [Google Cloud Logging Documentation](https://cloud.google.com/logging/docs)
- [Python Client Library](https://cloud.google.com/logging/docs/setup/python)
- [Google Cloud Support](https://cloud.google.com/support) 
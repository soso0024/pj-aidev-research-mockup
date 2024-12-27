## コードベースの概要

### 主要コンポーネントと相互作用

- **main.py:** メインのエントリポイントであり、データベースの初期化、サンプルコードの登録、類似コード検索のデモを行います。
- **database/:** データベース関連の処理をまとめたディレクトリです。
  - **connection.py:** データベース接続を管理します。
  - **code_repository.py:** コードスニペットの挿入、埋め込みの更新、埋め込みの取得を行います。
  - **test_repository.py:** テストケースの挿入と取得を行います。
- **embedding/:** 埋め込みベクトル生成関連の処理をまとめたディレクトリです。
  - **api_client.py:** Bedrock API クライアントを実装します。
  - **gemini_client.py:** Gemini API クライアントを実装します。
  - **similarity.py:** 埋め込みベクトル間の類似度計算を行います。
- **sample_codes.py:** サンプルコードのリストを定義します。

### データフロー

1. `main.py` は `database/connection.py` を使用してデータベースに接続します。
2. `main.py` は `sample_codes.py` からサンプルコードを読み込み、`database/code_repository.py` と `database/test_repository.py` を使用してデータベースに挿入します。
3. `main.py` は `embedding/api_client.py` または `embedding/gemini_client.py` を使用してコードの埋め込みベクトルを生成し、`database/code_repository.py` を使用してデータベースに保存します。
4. `main.py` はユーザーからの入力に基づいて、`embedding/api_client.py` を使用して入力コードの埋め込みベクトルを生成し、`embedding/similarity.py` を使用して類似コードを検索します。
5. `main.py` は `database/test_repository.py` を使用して、類似コードに関連するテストケースを取得します。

### 外部依存関係

- **axios:** (実際には使用していません)
- **@modelcontextprotocol/sdk:** (実際には使用していません)

### 最近の重要な変更

- なし

### ユーザーフィードバックの統合と開発への影響

- まだユーザーフィードバックは得られていません。

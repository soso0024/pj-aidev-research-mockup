from typing import Dict, Any
from database.context import db_context


def get_database_stats() -> Dict[str, Any]:
    """データベースの統計情報を取得します。"""
    try:
        with db_context() as (_, cursor):
            # コードの統計
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_codes,
                    SUM(CASE WHEN embedding IS NOT NULL THEN 1 ELSE 0 END) as codes_with_embedding
                FROM codes
            """)
            code_stats = cursor.fetchone()

            # テストケースの統計
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_tests,
                    COUNT(DISTINCT code_id) as codes_with_tests,
                    AVG(LENGTH(input)) as avg_input_length,
                    AVG(LENGTH(expected_output)) as avg_output_length
                FROM test_cases
            """)
            test_stats = cursor.fetchone()

            return {
                "total_codes": code_stats[0],
                "codes_with_embedding": code_stats[1],
                "total_test_cases": test_stats[0],
                "codes_with_tests": test_stats[1],
                "avg_input_length": round(test_stats[2], 2) if test_stats[2] else 0,
                "avg_output_length": round(test_stats[3], 2) if test_stats[3] else 0
            }
    except Exception as e:
        print(f"Error getting database stats: {e}")
        return {}


def get_sample_data() -> Dict[str, Any]:
    """サンプルデータを取得します。"""
    try:
        with db_context() as (_, cursor):
            # 最新のコードサンプル
            cursor.execute("""
                SELECT id, substr(code, 1, 100) as code_preview, 
                       CASE WHEN embedding IS NOT NULL THEN 1 ELSE 0 END as has_embedding
                FROM codes 
                ORDER BY id DESC 
                LIMIT 1
            """)
            code_sample = cursor.fetchone()

            # そのコードのテストケース
            test_cases = []
            if code_sample:
                cursor.execute("""
                    SELECT input, expected_output 
                    FROM test_cases 
                    WHERE code_id = ? 
                    LIMIT 3
                """, (code_sample[0],))
                test_cases = cursor.fetchall()

            return {
                "sample_code": {
                    "id": code_sample[0] if code_sample else None,
                    "preview": code_sample[1] if code_sample else None,
                    "has_embedding": bool(code_sample[2]) if code_sample else False
                },
                "sample_test_cases": test_cases
            }
    except Exception as e:
        print(f"Error getting sample data: {e}")
        return {}


def verify_data():
    """データベースの状態を検証し、結果を表示します。"""
    # 統計情報の取得と表示
    stats = get_database_stats()
    if stats:
        print("\n=== データベース統計 ===")
        print(f"コードの総数: {stats['total_codes']}")
        print(f"埋め込みベクトルを持つコード: {stats['codes_with_embedding']}")
        print(f"テストケースの総数: {stats['total_test_cases']}")
        print(f"テストケースを持つコード: {stats['codes_with_tests']}")
        print(f"平均入力長: {stats['avg_input_length']}")
        print(f"平均出力長: {stats['avg_output_length']}")

    # サンプルデータの取得と表示
    samples = get_sample_data()
    if samples and samples["sample_code"]["id"]:
        print("\n=== 最新のコードサンプル ===")
        print(f"ID: {samples['sample_code']['id']}")
        print(f"コードプレビュー: {samples['sample_code']['preview']}...")
        print(f"埋め込みベクトルの有無: {'あり' if samples['sample_code']['has_embedding'] else 'なし'}")

        if samples["sample_test_cases"]:
            print("\n=== テストケースサンプル ===")
            for i, (input_val, expected_output) in enumerate(samples["sample_test_cases"], 1):
                print(f"\nテストケース {i}:")
                print(f"入力: {input_val}")
                print(f"期待される出力: {expected_output}")


if __name__ == "__main__":
    verify_data()

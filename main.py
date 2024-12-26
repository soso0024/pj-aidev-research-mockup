from database import connection, code_repository, test_repository
from embedding.api_client import BedrockClient
from embedding.similarity import find_most_similar


def insert_code_with_tests(code_data: dict):
    """コードとそれに関連するテストケースを挿入します。

    Args:
        code_data: {
            'code': str,          # コードスニペット
            'language': str,      # プログラミング言語
            'description': str,   # コードの説明
            'test_cases': list    # テストケースのリスト
        }
    """
    code_id = code_repository.insert_code(
        code=code_data["code"],
        language=code_data["language"],
        description=code_data["description"],
    )

    if code_id:
        print(f"Code ID: {code_id}")
        bedrock = BedrockClient()
        embedding = bedrock.get_embedding(code_data["code"])

        if code_repository.update_embedding(code_id, embedding):
            print(f"Updated embedding for code ID: {code_id}")

        for test_case in code_data["test_cases"]:
            if test_repository.insert_test_case(
                code_id=code_id,
                input_val=test_case["input"],
                expected_output=test_case["expected_output"],
                description=test_case["description"],
            ):
                print(
                    f"Inserted {test_case['description']} for {code_data['description']}"
                )


def find_similar_code(code: str):
    """類似コードを検索し、関連するテストケースを取得します。

    Args:
        code: 検索対象のコード
    """
    bedrock = BedrockClient()
    code_embedding = bedrock.get_embedding(code)
    code_embeddings = code_repository.get_embeddings()

    if not code_embeddings:
        print("\nコードデータが見つかりません")
        return

    best_match_id, similarity = find_most_similar(code_embedding, code_embeddings)

    if best_match_id:
        print(f"\n最も類似したコード ID: {best_match_id}")
        print(f"類似度: {similarity:.4f}")

        test_cases = test_repository.get_test_cases(best_match_id)
        if test_cases:
            print("\n選択されたテストケース:")
            for input_val, expected_output in test_cases:
                print(f"Input: {input_val}, Expected Output: {expected_output}")
        else:
            print(f"\nコード ID {best_match_id} のテストケースが見つかりません")
    else:
        print("\n類似コードが見つかりません")


def main():
    # データベース初期化
    connection.create_database()
    print("Database created/connected.")

    # サンプルコードの定義
    code_samples = [
        {
            "code": """def add(a, b):\n    return a + b""",
            "language": "Python",
            "description": "Addition function",
            "test_cases": [
                {
                    "input": "1, 2",
                    "expected_output": "3",
                    "description": "Basic addition",
                },
                {
                    "input": "5, -3",
                    "expected_output": "2",
                    "description": "Addition with negative number",
                },
                {
                    "input": "0, 0",
                    "expected_output": "0",
                    "description": "Adding zeros",
                },
                {
                    "input": "-5, -7",
                    "expected_output": "-12",
                    "description": "Adding negative numbers",
                },
                {
                    "input": "100, 200",
                    "expected_output": "300",
                    "description": "Adding large numbers",
                },
                {
                    "input": "0.5, 0.7",
                    "expected_output": "1.2",
                    "description": "Adding decimals",
                },
                {
                    "input": "-1.5, 2.5",
                    "expected_output": "1.0",
                    "description": "Adding mixed decimals",
                },
                {
                    "input": "999999, 1",
                    "expected_output": "1000000",
                    "description": "Adding to make million",
                },
                {
                    "input": "2.0, -2.0",
                    "expected_output": "0.0",
                    "description": "Adding to zero",
                },
                {
                    "input": "1.23456, 2.34567",
                    "expected_output": "3.58023",
                    "description": "Precise decimal addition",
                },
            ],
        },
        {
            "code": """def subtract(a, b):\n    return a - b""",
            "language": "Python",
            "description": "Subtraction function",
            "test_cases": [
                {
                    "input": "5, 3",
                    "expected_output": "2",
                    "description": "Basic subtraction",
                },
                {
                    "input": "10, -5",
                    "expected_output": "15",
                    "description": "Subtracting negative",
                },
                {
                    "input": "0, 0",
                    "expected_output": "0",
                    "description": "Subtracting zeros",
                },
                {
                    "input": "-5, -3",
                    "expected_output": "-2",
                    "description": "Subtracting negatives",
                },
                {
                    "input": "100, 99",
                    "expected_output": "1",
                    "description": "Close numbers",
                },
                {
                    "input": "1000, 1",
                    "expected_output": "999",
                    "description": "Large difference",
                },
                {
                    "input": "3.14, 1.14",
                    "expected_output": "2.0",
                    "description": "Decimal subtraction",
                },
                {
                    "input": "1, 2",
                    "expected_output": "-1",
                    "description": "Negative result",
                },
                {
                    "input": "0.5, 0.25",
                    "expected_output": "0.25",
                    "description": "Small decimals",
                },
                {
                    "input": "10.1, 0.1",
                    "expected_output": "10.0",
                    "description": "Even result",
                },
            ],
        },
        {
            "code": """def multiply(a, b):\n    return a * b""",
            "language": "Python",
            "description": "Multiplication function",
            "test_cases": [
                {
                    "input": "2, 3",
                    "expected_output": "6",
                    "description": "Basic multiplication",
                },
                {
                    "input": "5, 0",
                    "expected_output": "0",
                    "description": "Multiply by zero",
                },
                {
                    "input": "-4, 3",
                    "expected_output": "-12",
                    "description": "Multiply negative",
                },
                {
                    "input": "-2, -3",
                    "expected_output": "6",
                    "description": "Multiply two negatives",
                },
                {
                    "input": "0.5, 4",
                    "expected_output": "2.0",
                    "description": "Multiply decimal",
                },
                {
                    "input": "1.5, 2.5",
                    "expected_output": "3.75",
                    "description": "Multiply decimals",
                },
                {
                    "input": "10, 10",
                    "expected_output": "100",
                    "description": "Square number",
                },
                {
                    "input": "0.1, 0.1",
                    "expected_output": "0.01",
                    "description": "Small decimals",
                },
                {
                    "input": "100, 0.5",
                    "expected_output": "50.0",
                    "description": "Half of large number",
                },
                {
                    "input": "-1, 999",
                    "expected_output": "-999",
                    "description": "Large negative",
                },
            ],
        },
        {
            "code": """def divide(a, b):\n    return a / b if b != 0 else 'Error: Division by zero'""",
            "language": "Python",
            "description": "Division function with zero check",
            "test_cases": [
                {
                    "input": "6, 2",
                    "expected_output": "3.0",
                    "description": "Basic division",
                },
                {
                    "input": "5, 0",
                    "expected_output": "Error: Division by zero",
                    "description": "Division by zero",
                },
                {
                    "input": "-6, 2",
                    "expected_output": "-3.0",
                    "description": "Negative division",
                },
                {
                    "input": "0, 5",
                    "expected_output": "0.0",
                    "description": "Zero numerator",
                },
                {
                    "input": "10, 3",
                    "expected_output": "3.3333333333333335",
                    "description": "Recurring decimal",
                },
                {
                    "input": "1, 2",
                    "expected_output": "0.5",
                    "description": "Fraction result",
                },
                {
                    "input": "-10, -2",
                    "expected_output": "5.0",
                    "description": "Negative divided by negative",
                },
                {
                    "input": "100, 4",
                    "expected_output": "25.0",
                    "description": "Large number division",
                },
                {
                    "input": "1, 3",
                    "expected_output": "0.3333333333333333",
                    "description": "Recurring third",
                },
                {
                    "input": "7, 7",
                    "expected_output": "1.0",
                    "description": "Same numbers",
                },
            ],
        },
        {
            "code": """def power(base, exponent):\n    return base ** exponent""",
            "language": "Python",
            "description": "Power function",
            "test_cases": [
                {"input": "2, 3", "expected_output": "8", "description": "Basic power"},
                {
                    "input": "5, 0",
                    "expected_output": "1",
                    "description": "Zero exponent",
                },
                {
                    "input": "2, -1",
                    "expected_output": "0.5",
                    "description": "Negative exponent",
                },
                {"input": "3, 2", "expected_output": "9", "description": "Square"},
                {
                    "input": "10, 2",
                    "expected_output": "100",
                    "description": "Power of ten",
                },
                {
                    "input": "2, 10",
                    "expected_output": "1024",
                    "description": "Large exponent",
                },
                {
                    "input": "1, 5",
                    "expected_output": "1",
                    "description": "Power of one",
                },
                {
                    "input": "-2, 2",
                    "expected_output": "4",
                    "description": "Negative base even exp",
                },
                {
                    "input": "-2, 3",
                    "expected_output": "-8",
                    "description": "Negative base odd exp",
                },
                {
                    "input": "0.5, 2",
                    "expected_output": "0.25",
                    "description": "Decimal base",
                },
            ],
        },
        {
            "code": """def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)""",
            "language": "Python",
            "description": "Factorial function",
            "test_cases": [
                {
                    "input": "0",
                    "expected_output": "1",
                    "description": "Factorial of zero",
                },
                {
                    "input": "1",
                    "expected_output": "1",
                    "description": "Factorial of one",
                },
                {
                    "input": "2",
                    "expected_output": "2",
                    "description": "Factorial of two",
                },
                {
                    "input": "3",
                    "expected_output": "6",
                    "description": "Factorial of three",
                },
                {
                    "input": "4",
                    "expected_output": "24",
                    "description": "Factorial of four",
                },
                {
                    "input": "5",
                    "expected_output": "120",
                    "description": "Factorial of five",
                },
                {
                    "input": "6",
                    "expected_output": "720",
                    "description": "Factorial of six",
                },
                {
                    "input": "7",
                    "expected_output": "5040",
                    "description": "Factorial of seven",
                },
                {
                    "input": "8",
                    "expected_output": "40320",
                    "description": "Factorial of eight",
                },
                {
                    "input": "10",
                    "expected_output": "3628800",
                    "description": "Factorial of ten",
                },
            ],
        },
        {
            "code": """def is_palindrome(text):\n    text = str(text).lower()\n    return text == text[::-1]""",
            "language": "Python",
            "description": "Palindrome checker function",
            "test_cases": [
                {
                    "input": "'radar'",
                    "expected_output": "True",
                    "description": "Basic palindrome",
                },
                {
                    "input": "'hello'",
                    "expected_output": "False",
                    "description": "Non-palindrome",
                },
                {
                    "input": "'A man a plan a canal Panama'",
                    "expected_output": "False",
                    "description": "Sentence with spaces",
                },
                {
                    "input": "'12321'",
                    "expected_output": "True",
                    "description": "Numeric palindrome",
                },
                {
                    "input": "'Race a car'",
                    "expected_output": "False",
                    "description": "Non-palindrome with spaces",
                },
                {
                    "input": "'Was it a car or a cat I saw'",
                    "expected_output": "False",
                    "description": "Long phrase",
                },
                {
                    "input": "'12345'",
                    "expected_output": "False",
                    "description": "Regular number",
                },
                {
                    "input": "'Mom'",
                    "expected_output": "False",
                    "description": "Case sensitive check",
                },
                {
                    "input": "'madam'",
                    "expected_output": "True",
                    "description": "Another palindrome",
                },
                {
                    "input": "'10101'",
                    "expected_output": "True",
                    "description": "Binary-like palindrome",
                },
            ],
        },
        {
            "code": """def fibonacci(n):\n    if n <= 1: return n\n    return fibonacci(n-1) + fibonacci(n-2)""",
            "language": "Python",
            "description": "Fibonacci sequence function",
            "test_cases": [
                {"input": "0", "expected_output": "0", "description": "First number"},
                {"input": "1", "expected_output": "1", "description": "Second number"},
                {"input": "2", "expected_output": "1", "description": "Third number"},
                {"input": "3", "expected_output": "2", "description": "Fourth number"},
                {"input": "4", "expected_output": "3", "description": "Fifth number"},
                {"input": "5", "expected_output": "5", "description": "Sixth number"},
                {"input": "6", "expected_output": "8", "description": "Seventh number"},
                {"input": "7", "expected_output": "13", "description": "Eighth number"},
                {"input": "8", "expected_output": "21", "description": "Ninth number"},
                {"input": "9", "expected_output": "34", "description": "Tenth number"},
            ],
        },
        {
            "code": """def count_vowels(text):\n    return sum(1 for char in text.lower() if char in 'aeiou')""",
            "language": "Python",
            "description": "Vowel counter function",
            "test_cases": [
                {
                    "input": "'hello'",
                    "expected_output": "2",
                    "description": "Basic word",
                },
                {
                    "input": "'AEIOU'",
                    "expected_output": "5",
                    "description": "All vowels",
                },
                {
                    "input": "'rhythm'",
                    "expected_output": "0",
                    "description": "No vowels",
                },
                {
                    "input": "'Python'",
                    "expected_output": "1",
                    "description": "One vowel",
                },
                {
                    "input": "'beautiful'",
                    "expected_output": "5",
                    "description": "Multiple vowels",
                },
                {
                    "input": "'AeIoU'",
                    "expected_output": "5",
                    "description": "Mixed case vowels",
                },
                {
                    "input": "'123'",
                    "expected_output": "0",
                    "description": "Numbers only",
                },
                {
                    "input": "'OpenAI'",
                    "expected_output": "4",
                    "description": "Company name",
                },
                {
                    "input": "'aaa'",
                    "expected_output": "3",
                    "description": "Repeated vowels",
                },
                {
                    "input": "'XYZ'",
                    "expected_output": "0",
                    "description": "Consonants only",
                },
            ],
        },
        {
            "code": """def reverse_string(text):\n    return text[::-1]""",
            "language": "Python",
            "description": "String reversal function",
            "test_cases": [
                {
                    "input": "'hello'",
                    "expected_output": "'olleh'",
                    "description": "Basic word",
                },
                {
                    "input": "'Python'",
                    "expected_output": "'nohtyP'",
                    "description": "Capital letter",
                },
                {
                    "input": "'12345'",
                    "expected_output": "'54321'",
                    "description": "Numbers",
                },
                {
                    "input": "'Hi!'",
                    "expected_output": "'!iH'",
                    "description": "With punctuation",
                },
                {
                    "input": "'   '",
                    "expected_output": "'   '",
                    "description": "Spaces only",
                },
                {
                    "input": "'a'",
                    "expected_output": "'a'",
                    "description": "Single character",
                },
                {
                    "input": "'Hello, World!'",
                    "expected_output": "'!dlroW ,olleH'",
                    "description": "With spaces and punctuation",
                },
                {
                    "input": "'radar'",
                    "expected_output": "'radar'",
                    "description": "Palindrome",
                },
                {
                    "input": "'123 456'",
                    "expected_output": "'654 321'",
                    "description": "Numbers with space",
                },
                {
                    "input": "'!@#$%'",
                    "expected_output": "'%$#@!'",
                    "description": "Special characters",
                },
            ],
        },
    ]

    # サンプルコードの登録
    for code_data in code_samples:
        insert_code_with_tests(code_data)

    # 類似コード検索のデモ
    print("\n=== 類似コードの検索 ===")
    ai_code = """def fib_l(cnt):
    a, b = 0, 1
    fib_l=[]
    while cnt:
        cnt-=1
        fib_l.append(b)
        a, b = b, a+b
    return fib_l"""
    print(f"AI生成コード:\n{ai_code}")
    find_similar_code(ai_code)


if __name__ == "__main__":
    main()

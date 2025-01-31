## Blueprint

![blueprint](https://github.com/soso0024/pj-aidev-research-mockup/blob/main/imgs/Blueprint.png)

1. Request creating a program with natutral language
2. Redirect it to AI model
3. Create a program file
4. Receive it, and analyze "Cosine Similarity" with the programs in the database
5. The system will provide top 3 test cases that are similar to the program that is created by AI model
6. User can choose appropriate test case for the program that is created by AI model
7. Run the test case
8. Send the test result and if some test cases are failed, the system will create the failed test cases to the user

## Database

This project uses an **SQLite** database to manage code and test cases. The database is named `code_comparison.db`.

### Table Structure

The database has the following two main tables:

#### `codes` Table

- `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT): Unique identifier for the code
- `code` (TEXT, NOT NULL, UNIQUE): The content of the code
- `embedding` (TEXT): The embedding vector of the code (stored in JSON format)

#### `test_cases` Table

- `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT): Unique identifier for the test case
- `code_id` (INTEGER, FOREIGN KEY): ID of the related code
- `input` (TEXT, NOT NULL): Input value for the test case
- `expected_output` (TEXT, NOT NULL): Expected output for the test case

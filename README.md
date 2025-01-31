## Demo

This is a demo video.

### Prompt

> Write a function to find the shared elements from the given two lists.

https://github.com/user-attachments/assets/c55b4161-ff83-474b-8389-57daee65409b

As you can see, the user has provided a prompt to the system. The system will generate code based on this prompt. And then, the system will provide top three test cases for the generated code according to the cosine similarity with vectors of the codes in the database. After that, the user can choose the appropriate test case for the generated code. The system will run the test case and provide the result. If the test case fails, the system will generate the failed test case for the user.

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

## Code

### main.py

Run the system

### db_utils.py

Create Database and Tables

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

### Dataset

This project uses the [evalplus/mbppplus](https://huggingface.co/datasets/evalplus/mbppplus) dataset from Hugging Face to populate the database with code and test cases.

## Questions

The `questions` directory contains text files that include the natural language questions that are used to generate code.

## Failed Tests

The `failed_tests` directory contains the failed test cases that are generated by the system.
The name of the file is `failed_test_{code_id}_{test_case_id}.txt`.

# Backend Wizards — Stage 1 Task: String Analyzer Service (AWS Lambda/DynamoDB)

This is a RESTful API service built with **FastAPI** that analyzes strings, computes their properties, and provides endpoints to create, retrieve, filter, and delete them, with persistence managed by **AWS DynamoDB**.

This project is configured for deployment on **AWS Lambda** via **API Gateway** or **Function URL** using the `mangum` adapter.

---
## API Endpoints

### 1. Create/Analyze String

* **Endpoint:** `POST /strings`
* **Request Body:**
    ```json
    {
      "value": "string to analyze"
    }
    ```
* **Success Response (201 Created):**
    ```json
    {
      "id": "sha256_hash_value",
      "value": "string to analyze",
      "properties": {
        "length": 16,
        "is_palindrome": false,
        "unique_characters": 12,
        "word_count": 3,
        "sha256_hash": "abc123...",
        "character_frequency_map": {
          "s": 2,
          "t": 3,
          /* ... */
        }
      },
      "created_at": "2025-08-27T10:00:00Z"
    }
    ```
* **Error Responses:**
    * `409 Conflict`: String already exists.
    * `422 Unprocessable Entity`: Invalid request body (e.g., missing `value` or `value` is not a string).

### 2. Get Specific String

* **Endpoint:** `GET /strings/{string_value}`
* **Success Response (200 OK):**
    * Returns the same `StoredString` object as the POST response.
* **Error Responses:**
    * `404 Not Found`: String does not exist.

### 3. Get All Strings with Filtering

* **Endpoint:** `GET /strings`
* **Query Parameters:**
    * `is_palindrome` (boolean)
    * `min_length` (integer)
    * `max_length` (integer)
    * `word_count` (integer)
    * `contains_character` (string, 1 char)
* **Example:** `GET /strings?is_palindrome=true&min_length=5`
* **Success Response (200 OK):**
    ```json
    {
      "data": [
        {
          "id": "hash1",
          "value": "string1",
          /* ... */
        }
      ],
      "count": 1,
      "filters_applied": {
        "is_palindrome": true,
        "min_length": 5
      }
    }
    ```
* **Error Responses:**
    * `422 Unprocessable Entity`: Invalid query parameter types.

### 4. Natural Language Filtering

* **Endpoint:** `GET /strings/filter-by-natural-language`
* **Query Parameter:**
    * `query` (string)
* **Example:** `GET /strings/filter-by-natural-language?query=all%20single%20word%20palindromic%20strings`
* **Success Response (200 OK):**
    ```json
    {
      "data": [ /* array of matching strings */ ],
      "count": 3,
      "interpreted_query": {
        "original": "all single word palindromic strings",
        "parsed_filters": {
          "word_count": 1,
          "is_palindrome": true
        }
      }
    }
    ```
* **Error Responses:**
    * `400 Bad Request`: Unable to parse the query.
    * `422 Unprocessable Entity`: Missing `query` parameter.

### 5. Delete String

* **Endpoint:** `DELETE /strings/{string_value}`
* **Success Response:** `204 No Content` (empty body)
* **Error Responses:**
    * `404 Not Found`: String does not exist.

---
## Setup and Deployment

### Dependencies
* `fastapi`: The web framework.
* `uvicorn[standard]`: The ASGI server (for local development).
* `boto3`: AWS SDK for Python (used to interact with DynamoDB).
* `mangum`: ASGI to AWS Lambda adapter.

These are listed in `requirements.txt`.

### How to Run Locally

1.  **Clone the repository** and **create/activate a virtual environment**.
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the application (Requires AWS Credentials/Config):**
    For local testing, you must have your AWS credentials configured (e.g., via AWS CLI or environment variables) so `boto3` can communicate with DynamoDB.
    ```bash
    # Set the DynamoDB Table Name environment variable for local testing
    export DYNAMODB_TABLE_NAME="YourTableName" 
    
    # Run Uvicorn
    uvicorn main:app --reload
    ```
    The API will be live at `http://127.0.0.1:8000`.

### How to Deploy to AWS Lambda

#### Prerequisites
1.  **AWS Account** and configured **AWS CLI**.
2.  **DynamoDB Table:** Create a DynamoDB table with a **Partition Key** named `id` (String type). The recommended name for this table is set via the environment variable `DYNAMODB_TABLE_NAME`.
3.  **IAM Role:** An IAM Role for the Lambda function that grants:
    * `AWSLambdaBasicExecutionRole` (for CloudWatch Logs).
    * Permissions to perform `dynamodb:GetItem`, `dynamodb:PutItem`, `dynamodb:DeleteItem`, and **`dynamodb:Scan`** on the specific DynamoDB table.

#### Deployment Steps (Using `zip` and AWS CLI or Serverless Framework/SAM)

1.  **Package Dependencies:** Create a deployment package including your code and dependencies.
    ```bash
    pip install -r requirements.txt -t package
    cp main.py package/
    cd package
    zip -r ../deployment_package.zip .
    cd ..
    ```
2.  **Deploy via AWS CLI:** Create or update the Lambda function.
    ```bash
    aws lambda create-function \
        --function-name StringAnalyzerService \
        --runtime python3.11 \
        --role arn:aws:iam::[YOUR_ACCOUNT_ID]:role/[YOUR_LAMBDA_EXECUTION_ROLE] \
        --handler main.handler \
        --timeout 30 \
        --memory-size 512 \
        --zip-file fileb://deployment_package.zip \
        --environment Variables="{DYNAMODB_TABLE_NAME=YourTableName}"
    ```
3.  **Configure API Gateway/Function URL:** Set up an **API Gateway HTTP API** or a **Lambda Function URL** to expose the Lambda function as a public HTTP endpoint. The `mangum` handler will correctly process the requests.

### Environment Variables

| Variable Name | Description | Example Value |
| :--- | :--- | :--- |
| `DYNAMODB_TABLE_NAME` | The name of the DynamoDB table used for persistence. | `StringAnalyzerTable` |
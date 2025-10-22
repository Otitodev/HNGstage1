# String Analyzer Service

A powerful RESTful API service built with **FastAPI** that analyzes strings, computes their properties, and provides endpoints to create, retrieve, filter, and delete them. The service supports multiple deployment options including AWS Lambda, EC2, and Leapcell.

## 🚀 Deployment Options

This project supports three deployment methods:

1. **🌐 Leapcell.io** (Recommended) - Simple, scalable, and cost-effective
2. **☁️ AWS Lambda** - Serverless with DynamoDB persistence  
3. **🖥️ AWS EC2** - Traditional server deployment

Choose the deployment method that best fits your needs!

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

## 🚀 Quick Start

### Local Development

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd string-analyzer-service
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **For Leapcell version** (Recommended):
   ```bash
   pip install -r requirements_leapcell.txt
   python main_leapcell.py
   ```

3. **For AWS version**:
   ```bash
   pip install -r requirements.txt
   export DYNAMODB_TABLE_NAME="StringAnalyzerTable"  # Windows: set DYNAMODB_TABLE_NAME=StringAnalyzerTable
   python main.py
   ```

4. **Test the API**:
   ```bash
   curl http://localhost:8000/
   ```

---

## 🌐 Deployment Options

### Option 1: Leapcell.io (Recommended)

**Best for**: Quick deployment, automatic scaling, minimal configuration

**Advantages**:
- ✅ No infrastructure management
- ✅ Automatic HTTPS and global CDN
- ✅ Free tier available
- ✅ Git-based deployment
- ✅ Built-in monitoring

**Files needed**: `main_leapcell.py`, `requirements_leapcell.txt`, `leapcell.yaml`

**Quick Deploy**:
1. Sign up at [leapcell.io](https://leapcell.io)
2. Connect your Git repository
3. Leapcell auto-deploys from `leapcell.yaml`

📖 **[Complete Leapcell Guide](LEAPCELL_DEPLOYMENT.md)**

### Option 2: AWS Lambda (Serverless)

**Best for**: Pay-per-request pricing, AWS ecosystem integration

**Advantages**:
- ✅ Serverless architecture
- ✅ DynamoDB integration
- ✅ Pay only for requests
- ✅ Auto-scaling

**Files needed**: `main.py`, `requirements.txt`, `cloudformation.yaml`

**Quick Deploy**:
```bash
# Windows
deploy.bat

# Or manually
python deploy.py
```

📖 **[Complete Lambda Guide](DEPLOYMENT.md)**

### Option 3: AWS EC2 (Traditional Server)

**Best for**: Full control, consistent workloads, custom configurations

**Advantages**:
- ✅ Full server control
- ✅ Predictable pricing
- ✅ Custom software installation
- ✅ SSH access

**Files needed**: `main.py`, `requirements.txt`, `ec2_simple.yaml`

**Quick Deploy**:
```bash
# Windows
deploy_ec2.bat

# Or manually
python deploy_ec2.py
```

📖 **[Complete EC2 Guide](EC2_DEPLOYMENT.md)**

---

## 🧪 Testing Your Deployment

### Test Script
```bash
# For Leapcell
python test_leapcell.py https://your-app.leapcell.app

# For AWS Lambda/EC2
python test_api.py https://your-api-url
```

### Manual Testing
```bash
# Health check
curl https://your-api-url/

# Create a string
curl -X POST https://your-api-url/strings \
  -H "Content-Type: application/json" \
  -d '{"value": "hello world"}'

# Get all strings
curl https://your-api-url/strings
```

---

## 📊 Deployment Comparison

| Feature | Leapcell | AWS Lambda | AWS EC2 |
|---------|----------|------------|---------|
| **Setup Complexity** | ⭐ Simple | ⭐⭐ Medium | ⭐⭐⭐ Complex |
| **Cost (Light Usage)** | Free tier | ~$0.20/1M requests | ~$8.50/month |
| **Scaling** | Automatic | Automatic | Manual/Auto Scaling Groups |
| **Data Persistence** | In-memory* | DynamoDB | DynamoDB |
| **Custom Domains** | ✅ Built-in | ✅ API Gateway | ✅ Load Balancer |
| **SSH Access** | ❌ | ❌ | ✅ |
| **Infrastructure Control** | ❌ | ❌ | ✅ Full |

*Can be upgraded to database

---

## 🔧 Configuration Files

### Core Application Files
- `main_leapcell.py` - Leapcell version (no AWS dependencies)
- `main.py` - AWS version (with DynamoDB)
- `requirements_leapcell.txt` - Leapcell dependencies
- `requirements.txt` - AWS dependencies

### Deployment Configuration
- `leapcell.yaml` - Leapcell deployment config
- `cloudformation.yaml` - AWS Lambda infrastructure
- `ec2_simple.yaml` - AWS EC2 infrastructure
- `Dockerfile` - Container deployment option

### Deployment Scripts
- `deploy_ec2.py` / `deploy_ec2.bat` - EC2 deployment
- `deploy.py` / `deploy.bat` - Lambda deployment
- `test_leapcell.py` - Leapcell testing
- `test_api.py` - AWS testing

---

## 🛠️ Development

### Project Structure
```
string-analyzer-service/
├── main_leapcell.py          # Leapcell version
├── main.py                   # AWS version
├── requirements_leapcell.txt # Leapcell deps
├── requirements.txt          # AWS deps
├── leapcell.yaml            # Leapcell config
├── cloudformation.yaml      # Lambda infrastructure
├── ec2_simple.yaml          # EC2 infrastructure
├── Dockerfile               # Container option
├── deploy_ec2.py           # EC2 deployment
├── test_leapcell.py        # Testing script
└── README.md               # This file
```

### Dependencies

**Leapcell Version**:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation

**AWS Version**:
- `fastapi` - Web framework
- `uvicorn` - ASGI server  
- `boto3` - AWS SDK
- `pydantic` - Data validation

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with your preferred deployment method
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
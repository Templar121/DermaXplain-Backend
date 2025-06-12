# DermaXplain Backend


## How to run ?
### STEPS:


clone the repository

```bash
https://github.com/Templar121/DermaXplain-Backend
```

### STEP A - Create a conda environment after opening the repository

```bash
conda create -n mlproj python=3.8 -y
```

```bash
conda activate mlproj
```

### OR
### STEP B - Create a venv environment

```bash
python -m venv mlproj
```

```bash
source mlproj/Scripts/activate
```


### STEP 02 - Install the Requirements

```bash
pip install -r requirements.txt
```

### Run the API 
```bash
uvicorn app.main:app --reload
```

## API ENDPOINTS

### 1. GET /api/health 
```bash
/api/health
```

### 2. POST /api/users/register
```json
{
  "email": "user@example.com",
  "password": "Pass123!",
  "name": "John Doe"
}
```

### 3. POST /api/users/login
```json
{
  "email": "user@example.com",
  "password": "Pass123!"
}
```

### 4. GET /api/users/me
```bash
Header 

Authorization: Bearer < bearer token returned from /login >
```

### 5. GET /api/db

```bash
Check Database Connection
```

### 6. DELETE /api/users/delete
```bash
Header 

Authorization: Bearer < bearer token returned from /login >
```
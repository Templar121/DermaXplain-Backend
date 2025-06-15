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

## Create .ENV File 
```bash
SECRET_KEY=<your super secret key>
ALGORITHM=<Your Hashing Algorithm
ACCESS_TOKEN_EXPIRE_MINUTES=<time in minutes>
EMAIL_HOST=<desired email host>
EMAIL_PORT=<port number>
EMAIL_USER=<company or organization email>
EMAIL_PASSWORD= <password>
MONGO_URL=<cluster connecrtion url for database>
```

## Run the API 
```bash
uvicorn app.main:app --reload
```

## API ENDPOINTS

## Health Check and DB Connection check

### 1. GET /api/health 
```bash
/api/health
```

### 2. GET /api/db

```bash
Check Database Connection
```

## User Endpoints

### 1. POST /api/users/register

### POST
```json
{
  "email": "user@example.com",
  "password": "Pass123!",
  "name": "John Doe"
}
```
### Recieve



### 2. POST /api/users/login
```json
{
  "email": "user@example.com",
  "password": "Pass123!"
}
```

### 3. GET /api/users/me
```bash
Header 

Authorization: Bearer < bearer token returned from /login >
```



### 6. DELETE /api/users/delete
```bash
Header 

Authorization: Bearer < bearer token returned from /login iof User >
```

### 7. GET /api/admin/users
```bash
Header 

Authorization: Bearer < bearer token returned from /login of Admin >
```

### 8. DELETE /api/admin/users/user_id
```bash
Header 

Authorization: Bearer < bearer token returned from /login of Admin >
```

### 9. POST /scan/upload-scan
```json
{
  "patient_name": "Alice Roy",
  "patient_age": 32,
  "gender": "Female",
  "scan_area": "Face",
  "additional_info": "Red patches visible"
}
```

### 10. GET /scan/my-scans
```bash
Header 

Authorization: Bearer < bearer token returned from /login of User >
```
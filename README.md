# DermaXplain Backend


## How to run ?
### STEPS:


clone the repository

```bash
git clone https://github.com/Templar121/DermaXplain-Backend.git
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
ALGORITHM=<Your Hashing Algorithm>
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

### GET
```bash
/api/health
```
### Response
```json
{
    "status": "API is healthy ✅"
}
```

### 2. GET /api/db

### GET
```bash
Check Database Connection
```
### Response
```json
{
    "status": "✅ API is healthy and MongoDB connection successful!"
}
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
### Response
```json
{
    "_id": "unique user id",
    "email": "user email",
    "name": "user name",
    "role": "user" // user by default
}
```

### 2. POST /api/users/login

### POST
```json
{
  "email": "user@example.com",
  "password": "Pass123!"
}
```
### Response
```json
{
    "access_token": "user specific access token",
    "token_type": "bearer"
}
```

### Google Auth
### POST auth/google
### Content-Type: application/json
```json
{
  "token": "<Google ID token>"
}
```

### 3. GET /api/users/me

### GET
```bash
Header 

Authorization: Bearer < bearer token returned from /login >
```
### Response
```json
{
    "_id": "unique user id",
    "email": "user email",
    "name": "user name",
    "role": "user" // user by default
}
```

### 4. DELETE /api/users/delete
```bash
Header 

Authorization: Bearer < bearer token returned from /login iof User >
```

### 5. POST /scan/upload-scan
### Content-Type: multipart/form-data
```json 
{
  "patient_name": "Alice Roy",
  "patient_age": 32,
  "gender": "Female",
  "scan_area": "Face",
  "additional_info": "Red patches visible",
  "image": "file upload"
}
```

### 6. GET /scan/my-scans

### GET
```bash
Header 

Authorization: Bearer < bearer token returned from /login of User >
```
### Response
```json
{
  "id": "ID",
  "patient_name": "Alice Roy",
  "patient_age": 32,
  "prediction": {
    "class": "class",
    "confidence": "confidence"
  }
  
}
```

### 7. GET /scan/my-scans/{id}

### GET
```bash
Header 

Authorization: Bearer < bearer token returned from /login of User >
```
### Response
```json
{
  "id": "ID",
  "patient_name": "Alice Roy",
  "patient_age": 32,
  "gender": "Male",
  "scan_area": "scan_area",
  "additional_info": "info",
  "uploaded_at": "uploaded_at",
  "image_filename": "image_filename",
  "prediction": {
    "class": "class",
    "confidence": "confidence"
  },
  "image_base64": "imgae_base64"
  
}
```

### 8. DELETE /scan/my-scans/{id}

### DELETE
```bash
Header 

Authorization: Bearer < bearer token returned from /login of User >
```
### Response
```json
200 OK
```

### 9. GET /scan/my-scans/{id}/download
```bash
Header 

Authorization: Bearer < bearer token returned from /login of User >
```
### Response
```json
PDF Report
```

### 10. PUT api/users/update-username
```bash
Header 

Authorization: Bearer < bearer token returned from /login of User >
```
```json
{
  "new_name": "NewUser"
}
```
### 11. POST api/users/forgot-password
```bash
Header 

Authorization: Bearer < bearer token returned from /login of User >
```
```json
{
  "email": "email_id"
}
```
### Response
```json
{
    "msg": "Password reset link sent"
}
```

### 12. POST /reset-password
```bash
Header 

Authorization: Bearer < bearer token returned from /login of User >
```
```json
{
  "token": "<copied_token_from_email>",
  "new_password": "NewPassword123"
}
```

## Admin Endpoints

### 1. GET /api/admin/users

```bash
Header 

Authorization: Bearer < bearer token returned from /login of Admin >
```

### 2. DELETE /api/admin/users/user_id
```bash
Header 

Authorization: Bearer < bearer token returned from /login of Admin >
```

### 3. GET /api/admin/users/{user_id}/scans
```bash
Header 

Authorization: Bearer < bearer token returned from /login of Admin >
```
### Response 
```json
{
  "user_id": "686d29cf645a53096a3c2011",
  "scan_ids": [
    "686de2933c82d3521338f88a",
    "685040af2b9635a2dd99e0d5"
  ]
}
```

### 4. GET /api/admin/scans/{scan_id} 
```bash
Header 

Authorization: Bearer < bearer token returned from /login of Admin >
```
### Response 
```json
{
  "_id": "686de2933c82d3521338f88a",
  "user_email": "user@example.com",
  "patient_name": "Alice Roy",
  "patient_age": 32,
  "gender": "Female",
  "scan_area": "Face",
  "additional_info": "Red Patches",
  "uploaded_at": "2025-07-09T03:31:31.884000",
  "image_filename": "ISIC_0029307.jpg",
  "image_content_type": "image/jpeg",
  "prediction": {
    "class": "nv",
    "confidence": 0.8876
  },
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

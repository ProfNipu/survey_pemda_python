# Dasar Python (Minimal) — API Endpoints

## 📋 Table of Contents
- [Overview](#overview)
- [API v4.0 (Laravel Compatible)](#api-v40-laravel-compatible)
- [API v5.0 (Modern API)](#api-v50-modern-api)
- [Health & Utilities](#health--utilities)

---

## Overview

Dokumen ini khusus untuk instance **minimal** `dasar-python`.

Yang tersedia:
- API login ESIMPEG v4/v5 (session + JWT)
- Endpoint user list v5
- Health check

Yang **tidak tersedia** di instance minimal ini:
- API Pegawai
- API Master Data
- API Integrasi SIASN (ws_siasn)

## 🔵 API v4.0 (Laravel Compatible)

### Base URL
```
http://localhost:8007/apisimpeg/4.0
```

### Endpoints

#### 1. Session-Based Login (OLD)
**URL:** `/apisimpeg/4.0/login/username-esimpeg`  
**Method:** `GET` or `POST`  
**Parameters:**
- `login_username` - Username, email, atau NIP
- `login_password` - Password

**Response Format:**
```json
{
    "data": {
        "username": "199411192019031001",
        "name": "Brahmana Adiputra",
        "email": "199411192019031001",
        "password": "$2y$12$...",
        "user_id_opd": 0,
        "usermode": "user"
    },
    "success_message": "Login Success",
    "errors": [],
    "error_message": null
}
```

**Notes:**
- Creates session cookie
- For web applications with session management
- Laravel bcrypt password compatible

---

#### 2. JWT Login (Permanent Token) ⭐ NEW
**URL:** `/apisimpeg/4.0/login/get-token`  
**Method:** `GET` or `POST`  
**Parameters:**
- `login_email` - Username atau email
- `login_password` - Password

**Response Format:**
```json
{
    "data": {
        "name": "Developer ESIMPEG",
        "email": "prakom@Admin2024.com",
        "image": "img.jpg",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    },
    "success_message": "",
    "errors": [],
    "error_message": null
}
```

**Token Details:**
- ⚠️ **Lifetime: 100 YEARS (Permanent)**
- Algorithm: HS256
- Type: Bearer Token
- Expires: Year 2125

**Example Usage:**
```bash
# GET Method
curl 'http://localhost:8007/apisimpeg/4.0/login/get-token?login_email=user@example.com&login_password=password'

# POST Method
curl -X POST 'http://localhost:8007/apisimpeg/4.0/login/get-token' \
  -d 'login_email=user@example.com&login_password=password'
```

**Laravel Example:**
```php
$response = Http::get('https://esimpeg.pesisirselatankab.go.id/apisimpeg/4.0/login/get-token', [
    'login_email' => $email,
    'login_password' => $password
]);

$data = $response->json();
if ($data['error_message'] === null) {
    $token = $data['data']['token'];
    // Token ini permanent, tidak perlu refresh!
    session(['api_token' => $token]);
}
```

---

## 🟢 API v5.0 (Modern API)

### Base URL
```
http://localhost:8007/apisimpeg/5.0
```

### Authentication Endpoints

#### 1. Session-Based Login
**URL:** `/apisimpeg/5.0/login/username-esimpeg`  
**Method:** `GET` or `POST`  
**Parameters:**
- `login_username` - Username, email, atau NIP
- `login_password` - Password

**Response Format:**
```json
{
    "status": "success",
    "message": "Login berhasil",
    "data": {
        "user_id": 1,
        "username": "prakom@Admin2024.com",
        "name": "Developer ESIMPEG",
        "email": "",
        "id_pegawai": 0,
        "session_key": "xxx...",
        "is_active": true
    },
    "version": "5.0"
}
```

---

#### 2. JWT Login (24h Token)
**URL:** `/apisimpeg/5.0/auth/login`  
**Method:** `POST`  
**Content-Type:** `application/json`  
**Body:**
```json
{
    "username": "prakom@Admin2024.com",
    "password": "Prakom@2024"
}
```

**curl:**
```bash
curl -X POST 'http://localhost:8007/apisimpeg/5.0/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"Prakom@admin2025.com","password":"Prakom@2025"}'
```

**Response Format:**
```json
{
    "status": "success",
    "message": "Login successful",
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "token_type": "Bearer",
        "expires_in": 86400,
        "user": {
            "user_id": 1,
            "username": "prakom@Admin2024.com",
            "name": "Developer ESIMPEG",
            "email": "",
            "id_pegawai": 0,
            "is_active": true
        }
    },
    "version": "5.0"
}
```

**Token Details:**
- ✅ **Access Token Lifetime: 24 hours**
- ✅ **Refresh Token Lifetime: 7 days**
- Algorithm: HS256
- Type: Bearer Token

---

#### 3. Verify JWT Token
**URL:** `/apisimpeg/5.0/auth/verify`  
**Method:** `POST`  
**Headers:**
```
Authorization: Bearer <access_token>
```

**curl:**
```bash
curl -X POST 'http://localhost:8007/apisimpeg/5.0/auth/verify' \
  -H 'Authorization: Bearer <access_token>'
```

**Response:**
```json
{
    "status": "success",
    "message": "Token is valid",
    "data": {
        "user_id": 1,
        "username": "prakom@Admin2024.com",
        "name": "Developer ESIMPEG",
        "email": "",
        "token_type": "access",
        "exp": 1761960519
    },
    "version": "5.0"
}
```

---

#### 4. Refresh JWT Token
**URL:** `/apisimpeg/5.0/auth/refresh`  
**Method:** `POST`  
**Content-Type:** `application/json`  
**Body:**
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## Health & Utilities

### Health
`GET /health/`

### Session status
`GET /session/status`

**Response:**
```json
{
    "status": "success",
    "message": "Token refreshed successfully",
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "token_type": "Bearer",
        "expires_in": 86400
    },
    "version": "5.0"
}
```

---

### Resource Endpoints

#### 5. Users List
**URL:** `/apisimpeg/5.0/users/list`  
**Method:** `GET`  
**Headers:**
```
Authorization: Bearer <access_token>
```
**Query Parameters (Optional):**
- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 50, max: 100)
- `search` - Search by username/name/email
- `is_active` - Filter by active status (true/false)

**Response:**
```json
{
    "status": "success",
    "message": "Retrieved 50 users successfully",
    "data": {
        "users": [
            {
                "user_id": 1,
                "username": "prakom@Admin2024.com",
                "name": "Developer ESIMPEG",
                "email": "",
                "id_pegawai": 0,
                "user_id_opd": 0,
                "is_active": true,
                "date_joined": "2023-11-19T02:55:01",
                "last_login": "2025-10-31T08:11:18.749902"
            }
        ],
        "pagination": {
            "total": 9707,
            "page": 1,
            "per_page": 50,
            "total_pages": 195
        }
    },
    "version": "5.0"
}
```

**Example Usage:**
```bash
# Get first page
curl -H "Authorization: Bearer $TOKEN" \
  'http://localhost:8005/apisimpeg/5.0/users/list'

# Search users
curl -H "Authorization: Bearer $TOKEN" \
  'http://localhost:8005/apisimpeg/5.0/users/list?search=admin&per_page=10'

# Get active users only
curl -H "Authorization: Bearer $TOKEN" \
  'http://localhost:8005/apisimpeg/5.0/users/list?is_active=true'
```

---

## 📊 Response Format Comparison

### Error Response Format

#### v4.0 Format:
```json
{
    "data": null,
    "success_message": "",
    "errors": ["Error message here"],
    "error_message": "Error message here"
}
```

#### v5.0 Format:
```json
{
    "status": "error",
    "message": "Error message here",
    "code": "ERROR_CODE",
    "version": "5.0"
}
```

---

## 🔐 Authentication Methods Comparison

| Feature | v4.0 Session | v4.0 JWT | v5.0 JWT |
|---------|-------------|----------|----------|
| **Method** | Session Cookie | Permanent Token | Time-based Token |
| **Lifetime** | Browser session | 100 years ⚠️ | 24h + 7d refresh |
| **Stateless** | ❌ No | ✅ Yes | ✅ Yes |
| **Mobile Friendly** | ⚠️ Limited | ✅ Yes | ✅ Yes |
| **Refresh Needed** | ❌ No | ❌ No | ✅ Yes |
| **Security Level** | Medium | ⚠️ Low (permanent) | ✅ High |
| **Best For** | Web apps | Legacy systems | Modern APIs |

---

## 🚀 Quick Start Guide

### For Laravel Applications (v4.0)

**Using Permanent Token:**
```php
// 1. Login
$response = Http::get('https://esimpeg.pesisirselatankab.go.id/apisimpeg/4.0/login/get-token', [
    'login_email' => $email,
    'login_password' => $password
]);

$token = $response->json()['data']['token'];

// 2. Use token (no expiration!)
$users = Http::withHeaders([
    'Authorization' => 'Bearer ' . $token
])->get('https://esimpeg.pesisirselatankab.go.id/apisimpeg/5.0/users/list');
```

---

### For Modern Applications (v5.0)

**Using Time-based JWT:**
```bash
# 1. Login
curl -X POST 'http://localhost:8005/apisimpeg/5.0/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"user@example.com","password":"password"}'

# 2. Use access token
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
  'http://localhost:8005/apisimpeg/5.0/users/list'

# 3. Refresh when expired (after 24h)
curl -X POST 'http://localhost:8005/apisimpeg/5.0/auth/refresh' \
  -H 'Content-Type: application/json' \
  -d '{"refresh_token":"$REFRESH_TOKEN"}'
```

---

## ⚠️ Security Recommendations

### For v4.0 Permanent Token:
1. ✅ Store token securely (encrypted database)
2. ✅ Use HTTPS only
3. ✅ Implement IP whitelist if possible
4. ✅ Monitor login activity
5. ⚠️ Consider migrating to v5.0 for better security

### For v5.0 Time-based JWT:
1. ✅ Store tokens in secure storage (not localStorage)
2. ✅ Implement token refresh flow
3. ✅ Handle token expiration gracefully
4. ✅ Use HTTPS only
5. ✅ Implement CORS properly

---

## 📞 Support

For API support, contact: Developer ESIMPEG

**API Version:** 5.0  
**Last Updated:** October 31, 2025

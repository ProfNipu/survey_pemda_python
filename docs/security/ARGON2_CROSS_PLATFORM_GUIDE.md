# Argon2 Cross-Platform Guide - Universal Password Hashing

## Overview

**Argon2** adalah password hashing algorithm yang **universal** dan **cross-platform**. Berbeda dengan Laravel bcrypt yang spesifik ke PHP/Laravel, Argon2 memiliki library **native** di hampir semua bahasa programming.

---

## 🆚 Laravel Hash vs Argon2 - Portability Comparison

| Aspek | Laravel Bcrypt | Argon2 |
|-------|----------------|--------|
| **Standard** | PHP/Laravel specific | Universal (PHC Winner 2015) |
| **Library Availability** | Mostly PHP | **ALL major languages** |
| **Framework Dependency** | ❌ Laravel-dependent | ✅ Framework-independent |
| **Cross-language** | ⚠️ Need conversion | ✅ Native support |
| **Implementation Complexity** | Medium (need workaround) | **Easy (native)** |
| **Official Support** | PHP only | Python, Node.js, Go, Rust, Java, C#, Ruby, etc. |
| **Documentation** | Laravel docs only | Official specs + multi-language docs |

---

## 📚 Argon2 Library - All Major Languages

### 1. **Python** (Django, Flask, FastAPI)
```python
# Library: argon2-cffi
from argon2 import PasswordHasher

ph = PasswordHasher()

# Hash password
hash = ph.hash("password123")
# Output: $argon2id$v=19$m=65536,t=3,p=4$xxx

# Verify password
try:
    ph.verify(hash, "password123")
    print("✅ Valid")
except:
    print("❌ Invalid")
```

**Install:**
```bash
pip install argon2-cffi
```

**Django:** Built-in support!
```python
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # Native!
]
```

---

### 2. **Node.js / JavaScript** (Express, NestJS, Next.js)
```javascript
// Library: argon2
const argon2 = require('argon2');

// Hash password
const hash = await argon2.hash('password123');
// Output: $argon2id$v=19$m=65536,t=3,p=4$xxx

// Verify password
try {
  if (await argon2.verify(hash, 'password123')) {
    console.log('✅ Valid');
  }
} catch {
  console.log('❌ Invalid');
}
```

**Install:**
```bash
npm install argon2
# or
yarn add argon2
```

---

### 3. **PHP** (Laravel, Symfony, CodeIgniter)
```php
// Library: Built-in PHP 7.2+
// Hash password
$hash = password_hash('password123', PASSWORD_ARGON2ID);
// Output: $argon2id$v=19$m=65536,t=4,p=1$xxx

// Verify password
if (password_verify('password123', $hash)) {
    echo "✅ Valid";
} else {
    echo "❌ Invalid";
}
```

**Laravel:**
```php
// config/hashing.php
'driver' => 'argon2id',  // Built-in support!

// Usage
Hash::make('password123');
Hash::check('password123', $hash);
```

**Install:** No installation needed (PHP 7.2+)

---

### 4. **Go / Golang**
```go
// Library: golang.org/x/crypto/argon2
import "golang.org/x/crypto/argon2"

// Hash password
salt := []byte("randomsalt")
hash := argon2.IDKey([]byte("password123"), salt, 1, 64*1024, 4, 32)

// For full Argon2 with encoding, use: github.com/alexedwards/argon2id
import "github.com/alexedwards/argon2id"

hash, err := argon2id.CreateHash("password123", argon2id.DefaultParams)
// Output: $argon2id$v=19$m=65536,t=3,p=4$xxx

match, err := argon2id.ComparePasswordAndHash("password123", hash)
// Returns: true/false
```

**Install:**
```bash
go get golang.org/x/crypto/argon2
go get github.com/alexedwards/argon2id
```

---

### 5. **Java / Kotlin** (Spring Boot, Android)
```java
// Library: de.mkammerer:argon2-jvm
import de.mkammerer.argon2.Argon2Factory;
import de.mkammerer.argon2.Argon2;

Argon2 argon2 = Argon2Factory.create();

// Hash password
String hash = argon2.hash(2, 65536, 1, "password123".toCharArray());
// Output: $argon2id$v=19$m=65536,t=2,p=1$xxx

// Verify password
if (argon2.verify(hash, "password123".toCharArray())) {
    System.out.println("✅ Valid");
}

// Clean password from memory (security best practice)
argon2.wipeArray("password123".toCharArray());
```

**Maven:**
```xml
<dependency>
    <groupId>de.mkammerer</groupId>
    <artifactId>argon2-jvm</artifactId>
    <version>2.11</version>
</dependency>
```

**Gradle:**
```gradle
implementation 'de.mkammerer:argon2-jvm:2.11'
```

---

### 6. **C# / .NET** (ASP.NET Core, Blazor)
```csharp
// Library: Isopoh.Cryptography.Argon2
using Isopoh.Cryptography.Argon2;

// Hash password
var hash = Argon2.Hash("password123");
// Output: $argon2id$v=19$m=65536,t=3,p=4$xxx

// Verify password
if (Argon2.Verify(hash, "password123")) {
    Console.WriteLine("✅ Valid");
} else {
    Console.WriteLine("❌ Invalid");
}
```

**NuGet:**
```bash
dotnet add package Isopoh.Cryptography.Argon2
```

---

### 7. **Ruby** (Ruby on Rails)
```ruby
# Library: argon2
require 'argon2'

# Hash password
hasher = Argon2::Password.new
hash = hasher.create('password123')
# Output: $argon2id$v=19$m=65536,t=3,p=4$xxx

# Verify password
if Argon2::Password.verify_password('password123', hash)
  puts "✅ Valid"
else
  puts "❌ Invalid"
end
```

**Install:**
```bash
gem install argon2
```

**Rails:**
```ruby
# Gemfile
gem 'argon2'

# Usage in User model
has_secure_password validations: false
def password=(new_password)
  @password = new_password
  self.password_digest = Argon2::Password.create(new_password)
end
```

---

### 8. **Rust**
```rust
// Library: argon2
use argon2::{
    password_hash::{PasswordHash, PasswordHasher, PasswordVerifier, SaltString},
    Argon2
};

// Hash password
let salt = SaltString::generate(&mut OsRng);
let argon2 = Argon2::default();
let hash = argon2.hash_password(b"password123", &salt).unwrap();
// Output: $argon2id$v=19$m=19456,t=2,p=1$xxx

// Verify password
let parsed_hash = PasswordHash::new(&hash.to_string()).unwrap();
assert!(argon2.verify_password(b"password123", &parsed_hash).is_ok());
```

**Cargo.toml:**
```toml
[dependencies]
argon2 = "0.5"
```

---

### 9. **Swift** (iOS, macOS)
```swift
// Library: SwiftArgon2
import SwiftArgon2

// Hash password
let salt = Salt.newSalt()
let hash = try! Argon2.hash(password: "password123", salt: salt)
// Output: $argon2id$v=19$m=65536,t=3,p=4$xxx

// Verify password
let isValid = try! Argon2.verify(password: "password123", hash: hash)
if isValid {
    print("✅ Valid")
}
```

**Swift Package Manager:**
```swift
dependencies: [
    .package(url: "https://github.com/tmthecoder/SwiftArgon2", from: "1.0.0")
]
```

---

## 🔄 Cross-Platform Password Sharing Example

### Scenario: Multi-Platform App
- **Backend:** Python (Django) - untuk admin panel
- **API:** Node.js (Express) - untuk mobile/web API
- **Mobile:** Swift (iOS), Kotlin (Android)
- **Desktop:** Electron (JavaScript)

### Implementation

#### 1. Backend (Python - Django)
```python
# User registration
from django.contrib.auth.models import User

user = User.objects.create_user(
    username='john',
    password='SecurePass123'
)
# Hash stored: argon2$argon2id$v=19$m=102400,t=2,p=8$xxx
```

#### 2. API (Node.js - Express)
```javascript
// User login API
const argon2 = require('argon2');

app.post('/api/login', async (req, res) => {
    const user = await db.users.findOne({ username: req.body.username });
    
    // Verify password (same hash from Django!)
    const valid = await argon2.verify(user.password, req.body.password);
    
    if (valid) {
        res.json({ success: true, token: generateJWT(user) });
    } else {
        res.status(401).json({ error: 'Invalid credentials' });
    }
});
```

#### 3. Mobile (Swift - iOS)
```swift
// Offline password verification (if needed)
import SwiftArgon2

func verifyPassword(password: String, hash: String) -> Bool {
    do {
        return try Argon2.verify(password: password, hash: hash)
    } catch {
        return false
    }
}

// Usage
let userHash = "$argon2id$v=19$m=102400,t=2,p=8$xxx" // From API
let isValid = verifyPassword(password: "SecurePass123", hash: userHash)
```

#### 4. Desktop (Electron - JavaScript)
```javascript
// Same as Node.js
const argon2 = require('argon2');

async function login(username, password) {
    const user = await api.getUser(username);
    const valid = await argon2.verify(user.password, password);
    return valid;
}
```

✅ **Result:** Password hash dari Django bisa diverify di **semua platform** tanpa masalah!

---

## ⚠️ Laravel Hash - Cross-Platform Problem

### Problem
Laravel menggunakan format bcrypt dengan prefix `$2y$` yang **spesifik PHP**:
```
$2y$10$xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Issues

#### 1. **Python** - Need Conversion
```python
# Laravel hash dari PHP: $2y$10$xxx
# Python bcrypt library hanya support $2b$

import bcrypt

# ❌ Direct verify TIDAK BISA
laravel_hash = "$2y$10$xxx"
bcrypt.checkpw(b"password", laravel_hash.encode())  # ERROR!

# ✅ Need conversion
hash_converted = laravel_hash.replace('$2y$', '$2b$')
bcrypt.checkpw(b"password", hash_converted.encode())  # OK
```

#### 2. **Node.js** - Need Special Library
```javascript
// Standard bcrypt library mungkin tidak support $2y$
const bcrypt = require('bcryptjs');

// ⚠️ Need workaround atau special library
const hash = "$2y$10$xxx";
// Some libraries support, some don't
```

#### 3. **Go** - Manual Handling
```go
// golang.org/x/crypto/bcrypt support limited
// Need manual format conversion
```

#### 4. **Java** - Library Dependent
```java
// Some libraries support $2y$, some don't
// Need specific library like jBCrypt or Spring Security
```

### Complexity Score

| Language | Laravel Hash Support | Argon2 Support |
|----------|---------------------|----------------|
| Python | ⚠️ Need conversion | ✅ Native |
| Node.js | ⚠️ Library dependent | ✅ Native |
| PHP | ✅ Native | ✅ Native (7.2+) |
| Go | ⚠️ Manual handling | ✅ Native |
| Java | ⚠️ Library dependent | ✅ Native |
| C# | ⚠️ Need special lib | ✅ Native |
| Ruby | ⚠️ Compatible but tricky | ✅ Native |
| Rust | ⚠️ Need workaround | ✅ Native |
| Swift | ⚠️ Very limited | ✅ Native |

---

## 🎯 Why Argon2 is Better for Cross-Platform

### 1. **Universal Standard**
- Winner of Password Hashing Competition (PHC) 2015
- Official specification: RFC 9106
- Recognized by OWASP, NIST, etc.

### 2. **Native Library Availability**
- **ALL major languages** memiliki library official/maintained
- Tidak perlu workaround atau conversion
- Consistent behavior across platforms

### 3. **Same Hash Format Everywhere**
```
$argon2id$v=19$m=65536,t=3,p=4$[salt]$[hash]
```
Format ini **SAMA PERSIS** di semua bahasa!

### 4. **Easy Implementation**
```python
# Python
hash = ph.hash("password")
```
```javascript
// Node.js
const hash = await argon2.hash('password');
```
```go
// Go
hash, _ := argon2id.CreateHash("password", params)
```
```java
// Java
String hash = argon2.hash(2, 65536, 1, "password");
```

**Semua menghasilkan hash yang COMPATIBLE!**

### 5. **No Conversion Needed**
Hash dari Python bisa langsung verify di:
- Node.js ✅
- Go ✅
- Java ✅
- PHP ✅
- Ruby ✅
- Rust ✅
- Swift ✅

**Tidak perlu conversion seperti Laravel `$2y$` → `$2b$`!**

---

## 🚀 Real-World Use Case

### Case: Microservices Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Database                         │
│  username: john                                          │
│  password: argon2$argon2id$v=19$m=65536,t=3,p=4$xxx    │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Python    │    │   Node.js   │    │     Go      │
│   Django    │    │   Express   │    │  REST API   │
│             │    │             │    │             │
│  Admin      │    │  Auth API   │    │  Data API   │
│  Panel      │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
       │                  │                   │
       └──────────────────┼───────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   Mobile Apps         │
              │  - iOS (Swift)        │
              │  - Android (Kotlin)   │
              └───────────────────────┘
```

**Benefit:**
- ✅ Semua service bisa verify password yang sama
- ✅ Tidak perlu sync/conversion
- ✅ Native library di setiap service
- ✅ Consistent security level

---

## 📊 Migration Benefit Summary

### Before (Laravel Hash)
```
✗ Bergantung PHP/Laravel
✗ Cross-platform tricky (need conversion)
✗ Limited library support
✗ Framework-specific
✗ Implementation berbeda-beda per bahasa
```

### After (Argon2)
```
✓ Universal standard
✓ Native support ALL languages
✓ No conversion needed
✓ Framework-independent
✓ Same implementation everywhere
✓ More secure (GPU/ASIC resistant)
✓ Future-proof
```

---

## ✅ Recommendation

### Use Argon2 When:
- ✅ Building microservices (multi-language)
- ✅ Need cross-platform compatibility
- ✅ Mobile app + backend API
- ✅ Future scalability (add new services)
- ✅ Maximum security needed
- ✅ Modern architecture

### Keep Laravel Hash Only If:
- ⚠️ 100% pure PHP/Laravel ecosystem
- ⚠️ Legacy system yang tidak bisa diubah
- ⚠️ No plan untuk cross-platform

---

## 🎓 Conclusion

| Criteria | Laravel Hash | Argon2 |
|----------|--------------|--------|
| **Security** | Good | **Excellent** ⭐ |
| **Cross-Platform** | Limited | **Universal** ⭐ |
| **Easy Implementation** | PHP only | **All languages** ⭐ |
| **Future-Proof** | Aging | **Modern** ⭐ |
| **Maintenance** | Medium | **Easy** ⭐ |
| **Framework Dependency** | High | **None** ⭐ |

**Verdict:** Argon2 adalah pilihan yang **JAUH LEBIH BAIK** untuk aplikasi modern, apalagi jika ada rencana:
- Microservices
- Mobile app
- Multi-language backend
- Cross-platform
- Long-term scalability

---

**Updated:** November 3, 2025  
**Status:** ✅ Production Ready  
**Recommendation:** **Use Argon2 for all new projects**

# API Access Log Table Design

## Database Table Structure

### Table: `ms_log_api`

```sql
CREATE TABLE ms_log_api (
    -- Primary Key
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    
    -- Request Information
    method VARCHAR(10) NOT NULL,                    -- GET, POST, PUT, DELETE
    endpoint VARCHAR(500) NOT NULL,                 -- /apisimpeg/5.0/users/list
    full_url TEXT,                                   -- Full URL with query params
    
    -- User Information
    user_id INT UNSIGNED NULL,                      -- Django User ID (NULL for public endpoints)
    username VARCHAR(150) NULL,                     -- Username for quick reference
    
    -- Request Details
    ip_address VARCHAR(45) NOT NULL,                -- IPv4 or IPv6
    user_agent TEXT,                                -- Browser/client info
    request_headers JSON,                           -- All request headers
    request_body JSON,                              -- POST/PUT body (careful with size!)
    query_params JSON,                              -- GET parameters
    
    -- Response Details
    status_code SMALLINT UNSIGNED NOT NULL,         -- 200, 401, 500, etc
    response_size INT UNSIGNED,                     -- Response size in bytes
    response_time DECIMAL(8, 3),                    -- Response time in seconds (e.g., 0.245)
    
    -- Additional Info
    api_version VARCHAR(10),                        -- 4.0, 5.0
    rate_limit_hit BOOLEAN DEFAULT FALSE,           -- Did this request hit rate limit?
    error_message TEXT,                             -- Error message if failed
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_user_id (user_id),
    INDEX idx_endpoint (endpoint),
    INDEX idx_created_at (created_at),
    INDEX idx_status_code (status_code),
    INDEX idx_ip_address (ip_address),
    INDEX idx_method_endpoint (method, endpoint)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## Django Model

```python
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class APIAccessLog(models.Model):
    """
    Log all API access for monitoring and analytics
    """
    
    # Request Information
    method = models.CharField(max_length=10)  # GET, POST, etc
    endpoint = models.CharField(max_length=500, db_index=True)
    full_url = models.TextField(null=True, blank=True)
    
    # User Information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    username = models.CharField(max_length=150, null=True, blank=True)
    
    # Request Details
    ip_address = models.CharField(max_length=45, db_index=True)
    user_agent = models.TextField(null=True, blank=True)
    request_headers = models.JSONField(null=True, blank=True)
    request_body = models.JSONField(null=True, blank=True)
    query_params = models.JSONField(null=True, blank=True)
    
    # Response Details
    status_code = models.SmallIntegerField(db_index=True)
    response_size = models.IntegerField(null=True, blank=True)  # bytes
    response_time = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)  # seconds
    
    # Additional Info
    api_version = models.CharField(max_length=10, null=True, blank=True)
    rate_limit_hit = models.BooleanField(default=False)
    error_message = models.TextField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'ms_log_api'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['method', 'endpoint']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code} ({self.created_at})"
```

---

## Sample Data

```json
{
    "id": 1,
    "method": "POST",
    "endpoint": "/apisimpeg/5.0/auth/login",
    "full_url": "http://localhost:8005/apisimpeg/5.0/auth/login",
    "user_id": null,
    "username": null,
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "request_headers": {
        "Content-Type": "application/json",
        "Accept": "application/json"
    },
    "request_body": {
        "username": "prakom@Admin2024.com"
    },
    "query_params": {},
    "status_code": 200,
    "response_size": 1524,
    "response_time": 0.245,
    "api_version": "5.0",
    "rate_limit_hit": false,
    "error_message": null,
    "created_at": "2025-11-03 10:46:15"
}
```

---

## Useful Queries

### 1. Most Hit Endpoints Today
```sql
SELECT 
    endpoint,
    COUNT(*) as hit_count,
    AVG(response_time) as avg_response_time
FROM ms_log_api
WHERE DATE(created_at) = CURDATE()
GROUP BY endpoint
ORDER BY hit_count DESC
LIMIT 10;
```

### 2. Failed Requests (4xx, 5xx)
```sql
SELECT *
FROM ms_log_api
WHERE status_code >= 400
AND created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
ORDER BY created_at DESC;
```

### 3. Top Users by API Usage
```sql
SELECT 
    username,
    COUNT(*) as request_count,
    COUNT(DISTINCT endpoint) as unique_endpoints
FROM ms_log_api
WHERE user_id IS NOT NULL
AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY username
ORDER BY request_count DESC
LIMIT 10;
```

### 4. Slowest Endpoints
```sql
SELECT 
    endpoint,
    AVG(response_time) as avg_time,
    MAX(response_time) as max_time,
    COUNT(*) as hit_count
FROM ms_log_api
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
GROUP BY endpoint
HAVING avg_time > 1.0  -- Slower than 1 second
ORDER BY avg_time DESC;
```

### 5. Rate Limit Hits
```sql
SELECT 
    ip_address,
    endpoint,
    COUNT(*) as rate_limit_hits
FROM ms_log_api
WHERE rate_limit_hit = TRUE
AND created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
GROUP BY ip_address, endpoint
ORDER BY rate_limit_hits DESC;
```

### 6. Hourly Request Volume
```sql
SELECT 
    DATE_FORMAT(created_at, '%Y-%m-%d %H:00') as hour,
    COUNT(*) as request_count,
    AVG(response_time) as avg_response_time
FROM ms_log_api
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
GROUP BY hour
ORDER BY hour;
```

---

## Performance Considerations

### 1. Table Partitioning (for high volume)
```sql
-- Partition by month
ALTER TABLE api_access_log
PARTITION BY RANGE (YEAR(created_at) * 100 + MONTH(created_at)) (
    PARTITION p202511 VALUES LESS THAN (202512),
    PARTITION p202512 VALUES LESS THAN (202601),
    PARTITION p202601 VALUES LESS THAN (202602)
);
```

### 2. Archive Old Data
```sql
-- Move logs older than 90 days to archive table
CREATE TABLE ms_log_api_archive LIKE ms_log_api;

INSERT INTO ms_log_api_archive
SELECT * FROM ms_log_api
WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY);

DELETE FROM ms_log_api
WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY);
```

### 3. Don't Log Large Request Bodies
```python
# In middleware, limit body logging
if len(request.body) > 10240:  # 10KB
    log_entry.request_body = {"_truncated": "Body too large"}
else:
    log_entry.request_body = json.loads(request.body)
```

---

## Pros & Cons

### Database Logging ✅

**Pros:**
- ✅ Easy to query (SQL)
- ✅ Dashboard ready (charts, analytics)
- ✅ Searchable (by user, endpoint, date)
- ✅ Integration with admin panel

**Cons:**
- ❌ Performance overhead (INSERT on every request)
- ❌ Database growth (can be huge)
- ❌ Need regular cleanup
- ❌ May slow down API if high traffic

### File Logging ✅

**Pros:**
- ✅ Very fast (async write)
- ✅ No database overhead
- ✅ Industry standard
- ✅ Auto-rotate

**Cons:**
- ❌ Harder to query (need parsing)
- ❌ No built-in dashboard
- ❌ Manual analysis

---

## Hybrid Approach (Recommended) ⭐

**Best of both worlds:**

1. **File logging** for ALL requests (fast, complete)
2. **Database logging** for IMPORTANT events only:
   - Login attempts (success/fail)
   - Failed requests (4xx, 5xx)
   - Slow requests (> 2 seconds)
   - Rate limit hits

```python
# Log everything to file
file_logger.info(request_data)

# Log only important to database
if status_code >= 400 or response_time > 2.0 or rate_limited:
    APIAccessLog.objects.create(**log_data)
```

**Result:**
- ✅ Complete history in files (lightweight)
- ✅ Important events in database (queryable)
- ✅ Best performance
- ✅ Easy analytics

---

Last Updated: November 3, 2025

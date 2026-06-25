"""
Gunicorn configuration file
For production deployment with large data handling
"""
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = os.getenv('GUNICORN_WORKER_CLASS', 'sync')
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = int(os.getenv('GUNICORN_TIMEOUT', 300))  # 5 minutes for large data
keepalive = 5

# Logging
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = os.getenv('GUNICORN_PROC_NAME', 'aplikasi-test')

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 16384

# Memory optimization
preload_app = True  # Load application before forking workers (saves memory)

# Restart workers after this many requests (to prevent memory leaks)
max_requests = 1000
max_requests_jitter = 100

def pre_fork(server, worker):
    """Called just before a worker is forked"""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_exec(server):
    """Called just before a new master process is forked"""
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    """Called just after the server is started"""
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT"""
    worker.log.info("worker received INT or QUIT signal")

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal"""
    worker.log.info("worker received SIGABRT signal")

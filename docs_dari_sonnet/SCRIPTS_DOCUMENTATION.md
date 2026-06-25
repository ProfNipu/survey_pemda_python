# Scripts Documentation - Complete Guide

Dokumentasi lengkap untuk semua utility scripts di project ini.

---

## 📋 Table of Contents

1. [fix-docker-network.sh](#1-fix-docker-networksh)
2. [Installation Guide](#installation-guide)
3. [Usage Examples](#usage-examples)
4. [Troubleshooting](#troubleshooting)
5. [Technical Details](#technical-details)

---

## 1. fix-docker-network.sh

### Overview

Script all-in-one untuk fix DisallowedHost error setelah restart laptop.

**Location**: `projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh`

**Problem**: 
- Docker containers mendapat IP dinamis
- IP berubah setiap restart laptop
- Django ALLOWED_HOSTS validation menolak IP baru
- Survey Pemda tidak bisa connect ke ESIMPEG API

**Solution**:
- Auto-detect IP baru
- Auto-update .env file
- Auto-restart containers
- Optional: Install systemd service untuk auto-run on boot

### Features

✅ **All-in-One**: Semua fungsi dalam 1 file
✅ **No Dependencies**: Tidak perlu install package tambahan
✅ **Auto-Backup**: Backup .env sebelum update
✅ **Systemd Integration**: Optional auto-run on boot
✅ **Error Handling**: Comprehensive error checking
✅ **Logging**: Output ke stdout dan systemd journal
✅ **Interactive**: Clear output dengan colors

### Usage

#### Basic Usage

```bash
# Run auto-fix now
./projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh
```

**Output**:
```
==============================================
Auto-Fix Docker Network
==============================================
✅ Docker is running
Waiting for containers to be ready...

Container IPs:
  ESIMPEG:      172.21.0.2
  Survey Pemda: 172.21.0.3

Current .env: http://172.18.0.6:8000
New IP:       http://172.21.0.2:8000
⚠️  IP changed, updating .env...
✅ .env updated
Restarting Survey Pemda container...
✅ Container restarted

Testing connectivity...
✅ Survey Pemda → ESIMPEG: OK

==============================================
✅ Auto-fix complete!
==============================================
```

#### Install as Service

```bash
# Install systemd service
./projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh --install
```

**What happens**:
1. Create systemd service file
2. Install to `/etc/systemd/system/`
3. Enable service (auto-start on boot)
4. Test service
5. Show status

**Output**:
```
==============================================
Install Auto-Fix Systemd Service
==============================================
Installing service...
✅ Service installed

Testing service...

● docker-network-fix.service - Auto-fix Docker Network
   Loaded: loaded (/etc/systemd/system/docker-network-fix.service; enabled)
   Active: active (exited) since Mon 2026-04-06 11:00:00 WIB

==============================================
✅ Installation complete!
==============================================

Service will run automatically on boot.

Commands:
  Status: sudo systemctl status docker-network-fix.service
  Logs:   sudo journalctl -u docker-network-fix.service -f
  Stop:   sudo systemctl stop docker-network-fix.service
```

#### Check Service Status

```bash
# Check if service is running
./projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh --status
```

**Output**:
```
==============================================
Service Status
==============================================
● docker-network-fix.service - Auto-fix Docker Network
   Loaded: loaded (/etc/systemd/system/docker-network-fix.service; enabled)
   Active: active (exited) since Mon 2026-04-06 11:00:00 WIB
   
Recent logs:
Apr 06 11:00:00 hostname systemd[1]: Starting Auto-fix Docker Network...
Apr 06 11:00:05 hostname fix-docker-network.sh[1234]: ✅ Auto-fix complete!
Apr 06 11:00:05 hostname systemd[1]: Started Auto-fix Docker Network.
```

#### Uninstall Service

```bash
# Remove systemd service
./projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh --uninstall
```

**Output**:
```
==============================================
Uninstall Auto-Fix Service
==============================================
Stopping and disabling service...
Removing service file...
✅ Service uninstalled
```

#### Show Help

```bash
# Show usage help
./projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh --help
```

---

## Installation Guide

### Option 1: Auto-Run on Boot (Recommended)

Install systemd service untuk auto-fix setiap boot:

```bash
# Step 1: Install service
./projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh --install

# Step 2: Verify installation
./projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh --status

# Step 3: Done! Auto-fix akan jalan otomatis setiap boot
```

**Benefits**:
- ✅ Fully automatic
- ✅ No manual intervention
- ✅ Runs on every boot
- ✅ Logs available in journalctl

### Option 2: Manual Run

Jika tidak ingin install service, run manual setiap restart:

```bash
# After laptop restart
./projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh
```

**When to use**:
- Testing/development
- Don't want systemd service
- Prefer manual control

---

## Usage Examples

### Example 1: First Time Setup

```bash
# 1. Clone/pull project
cd ~/project-docker/all-projects-darireal

# 2. Install auto-fix service
./scripts/fix-docker-network.sh --install

# 3. Restart laptop to test
sudo reboot

# 4. After boot, check if auto-fix ran
sudo journalctl -u docker-network-fix.service -f
```

### Example 2: Manual Fix After Restart

```bash
# 1. Start Docker (if not started)
sudo systemctl start docker

# 2. Wait for containers
sleep 10

# 3. Run auto-fix
./scripts/fix-docker-network.sh

# 4. Check if working
docker exec survey_pemda_python_app curl -s http://$(docker inspect esimpeg_python_app | grep -m 1 '"IPAddress"' | grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}' | head -1):8000/health/
```

### Example 3: Debugging

```bash
# 1. Check service status
./projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh --status

# 2. View live logs
sudo journalctl -u docker-network-fix.service -f

# 3. Manual run with verbose output
./projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh

# 4. Check .env file
cat projects/survey_pemda_python/.env | grep ESIMPEG_API_URL

# 5. Check container IPs
docker inspect esimpeg_python_app | grep IPAddress
docker inspect survey_pemda_python_app | grep IPAddress
```

### Example 4: Uninstall and Reinstall

```bash
# 1. Uninstall service
./projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh --uninstall

# 2. Verify uninstalled
./projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh --status

# 3. Reinstall
./projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh --install

# 4. Test
sudo systemctl start docker-network-fix.service
./projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh --status
```

---

## Troubleshooting

### Issue 1: "Docker is not running"

**Symptom**:
```
❌ Docker is not running!
Please start Docker first.
```

**Solution**:
```bash
# Start Docker
sudo systemctl start docker

# Wait a bit
sleep 5

# Run script again
./scripts/fix-docker-network.sh
```

### Issue 2: "Cannot get ESIMPEG IP"

**Symptom**:
```
❌ Cannot get ESIMPEG IP
```

**Possible Causes**:
- Container not running
- Container not fully started
- Container name mismatch

**Solution**:
```bash
# Check if containers are running
docker ps --filter name=python_app

# If not running, start them
docker start esimpeg_python_app survey_pemda_python_app

# Wait for full startup
sleep 15

# Run script again
./scripts/fix-docker-network.sh
```

### Issue 3: ".env file not found"

**Symptom**:
```
❌ .env file not found: /path/to/.env
```

**Solution**:
```bash
# Check if .env exists
ls -la projects/survey_pemda_python/.env

# If not exists, copy from example
cp projects/survey_pemda_python/.env.example projects/survey_pemda_python/.env

# Edit .env
nano projects/survey_pemda_python/.env
```

### Issue 4: Service not starting on boot

**Symptom**:
Service installed but not running after boot

**Solution**:
```bash
# Check service status
sudo systemctl status docker-network-fix.service

# Check if enabled
sudo systemctl is-enabled docker-network-fix.service

# If not enabled, enable it
sudo systemctl enable docker-network-fix.service

# Check logs
sudo journalctl -u docker-network-fix.service -n 50

# Reinstall if needed
./scripts/fix-docker-network.sh --uninstall
./scripts/fix-docker-network.sh --install
```

### Issue 5: Permission denied

**Symptom**:
```
bash: ./scripts/fix-docker-network.sh: Permission denied
```

**Solution**:
```bash
# Make script executable
chmod +x projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh

# Run again
./projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh
```

### Issue 6: Connectivity test fails

**Symptom**:
```
⚠️  Survey Pemda → ESIMPEG: HTTP 000
```

**Solution**:
```bash
# Check if ESIMPEG is healthy
docker exec esimpeg_python_app curl -s http://localhost:8000/health/

# Check ESIMPEG logs
docker logs esimpeg_python_app --tail 50

# Restart ESIMPEG
docker restart esimpeg_python_app

# Wait and test again
sleep 15
./scripts/fix-docker-network.sh
```

---

## Technical Details

### How It Works

1. **Check Docker**: Verify Docker daemon is running
2. **Wait Containers**: Wait for containers to be ready (max 60s)
3. **Get IPs**: Extract container IPs using `docker inspect`
4. **Compare**: Compare current .env with new IP
5. **Backup**: Create timestamped backup of .env
6. **Update**: Use `sed` to update ESIMPEG_API_URL
7. **Restart**: Restart Survey Pemda container
8. **Test**: Curl health endpoint to verify connectivity

### File Locations

- **Script**: `projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh`
- **Service**: `/etc/systemd/system/docker-network-fix.service`
- **.env**: `projects/survey_pemda_python/.env`
- **Backups**: `projects/survey_pemda_python/.env.backup.TIMESTAMP`
- **Logs**: `sudo journalctl -u docker-network-fix.service`

### Dependencies

- `bash` (built-in)
- `docker` (required)
- `grep`, `sed`, `awk` (built-in)
- `curl` (in container)
- `systemd` (for service, optional)

### Environment Variables

Script uses these from .env:
- `ESIMPEG_API_URL` - Updated by script

### Exit Codes

- `0` - Success
- `1` - Error (Docker not running, container not found, etc.)

### Systemd Service

**Service Type**: `oneshot`
**User**: Current user (not root)
**After**: `docker.service`
**Requires**: `docker.service`
**WantedBy**: `multi-user.target`

### Backup Strategy

- Backup created before every update
- Format: `.env.backup.YYYYMMDD_HHMMSS`
- Location: Same directory as .env
- No automatic cleanup (manual cleanup recommended)

### Security

- Script runs as normal user (not root)
- Service runs as normal user
- No password/secrets in script
- .env backups contain secrets (protect them!)

---

## Related Documentation

- [89_FIX_DISALLOWED_HOST_AFTER_RESTART.md](./89_FIX_DISALLOWED_HOST_AFTER_RESTART.md) - Full problem analysis
- [88_FIX_PASSWORD_CHANGE_COMPLETE.md](./88_FIX_PASSWORD_CHANGE_COMPLETE.md) - Password change fix
- [64_FIX_DISALLOWED_HOST_FINAL.md](./64_FIX_DISALLOWED_HOST_FINAL.md) - Previous DisallowedHost fix

---

## Summary

✅ **One script to rule them all**
✅ **Install once, auto-fix forever**
✅ **No manual intervention needed**
✅ **Comprehensive error handling**
✅ **Full logging support**

**Quick Start**:
```bash
./projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh --install
```

**That's it!** 🎉

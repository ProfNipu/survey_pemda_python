# Scripts Collection

Kumpulan utility scripts untuk maintenance dan troubleshooting.

## 📁 Available Scripts

### 1. fix-docker-network.sh

**Purpose**: Auto-fix DisallowedHost error setelah restart laptop

**Problem**: Docker containers mendapat IP baru setiap restart, menyebabkan error koneksi

**Solution**: Script ini otomatis detect IP baru dan update konfigurasi

**Usage**:

```bash
# Run auto-fix sekarang
./scripts/fix-docker-network.sh

# Install service (auto-run on boot)
./scripts/fix-docker-network.sh --install

# Check service status
./scripts/fix-docker-network.sh --status

# Uninstall service
./scripts/fix-docker-network.sh --uninstall

# Show help
./scripts/fix-docker-network.sh --help
```

**Features**:
- ✅ Auto-detect container IP changes
- ✅ Auto-update .env file
- ✅ Auto-backup .env sebelum update
- ✅ Test connectivity
- ✅ Systemd integration (optional)
- ✅ All-in-one script (no dependencies)

**What it does**:
1. Check Docker status
2. Wait for containers ready
3. Get new container IPs
4. Compare with current .env
5. Update .env if changed
6. Restart Survey Pemda container
7. Test connectivity
8. Done!

**Install as Service** (Recommended):
```bash
# Install sekali saja
./scripts/fix-docker-network.sh --install

# Setelah install, auto-fix akan jalan otomatis setiap boot
# Tidak perlu run manual lagi!
```

**Check Logs**:
```bash
# View service logs
sudo journalctl -u docker-network-fix.service -f

# Check service status
sudo systemctl status docker-network-fix.service
```

---

## 📚 Documentation

Full documentation: `projects/survey_pemda_python/docs_dari_sonnet/89_FIX_DISALLOWED_HOST_AFTER_RESTART.md`

## 🔧 Troubleshooting

### Script error "Docker not running"
```bash
# Start Docker first
sudo systemctl start docker

# Then run script
./scripts/fix-docker-network.sh
```

### Script error "Cannot get ESIMPEG IP"
```bash
# Check if containers are running
docker ps --filter name=python_app

# Start containers if needed
docker start esimpeg_python_app survey_pemda_python_app

# Wait a bit, then run script
sleep 10
./scripts/fix-docker-network.sh
```

### Service not starting on boot
```bash
# Check service status
sudo systemctl status docker-network-fix.service

# Check logs
sudo journalctl -u docker-network-fix.service -n 50

# Reinstall service
./scripts/fix-docker-network.sh --uninstall
./scripts/fix-docker-network.sh --install
```

## 📝 Notes

- Script requires Docker to be running
- Script requires containers to be started
- Script creates backup of .env before updating
- Backup location: `projects/survey_pemda_python/.env.backup.TIMESTAMP`
- Service runs as current user (not root)
- Service logs to systemd journal

## 🎯 Quick Start

**First time setup**:
```bash
# Install service (recommended)
./scripts/fix-docker-network.sh --install
```

**After laptop restart**:
- Nothing! Service runs automatically
- Check logs if needed: `sudo journalctl -u docker-network-fix.service -f`

**Manual run** (if service not installed):
```bash
./scripts/fix-docker-network.sh
```

That's it! 🎉

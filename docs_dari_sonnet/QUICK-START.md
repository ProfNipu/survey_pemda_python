# Quick Start Guide

## 🚀 Setelah Restart Laptop

### Solusi Otomatis (Recommended)

**Install sekali saja**:
```bash
./projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh --install
```

Setelah install, auto-fix akan jalan otomatis setiap boot. **Tidak perlu run manual lagi!**

---

### Solusi Manual

Jika belum install service, run manual setiap restart:

```bash
./projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh
```

---

## 📚 Documentation

- **Script**: `projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh`
- **Full Docs**: `projects/survey_pemda_python/docs_dari_sonnet/SCRIPTS_DOCUMENTATION.md`

---

## 🔧 Common Commands

```bash
# Check service status
./projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh --status

# View logs
sudo journalctl -u docker-network-fix.service -f

# Uninstall service
./projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh --uninstall

# Show help
./projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh --help
```

---

## ❓ Troubleshooting

### Docker not running
```bash
sudo systemctl start docker
```

### Containers not running
```bash
docker start esimpeg_python_app survey_pemda_python_app
```

### Script permission denied
```bash
chmod +x projects/survey_pemda_python/docs_dari_sonnet/sh_dari_sonnet/fix-docker-network.sh
```

---

**That's it!** 🎉

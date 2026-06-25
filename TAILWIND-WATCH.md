# Tailwind CSS Auto-Rebuild

## 🚀 Quick Start

### Option 1: Foreground (Terminal Tetap Terbuka)
```bash
./tailwind-watch.sh
# Atau
npm run dev
```

### Option 2: Background (Bisa Close Terminal)
```bash
# Start
./tailwind-start.sh

# Stop
./tailwind-stop.sh
```

## 📋 Commands

| Command | Description |
|---------|-------------|
| `./tailwind-watch.sh` | Watch mode di foreground (Ctrl+C untuk stop) |
| `./tailwind-start.sh` | Start watch di background |
| `./tailwind-stop.sh` | Stop background watch |
| `npm run dev` | Watch mode via npm |
| `npm run build` | Build sekali (minified) |

## 🔍 Monitoring

### Check if Running
```bash
ps aux | grep tailwindcss
```

### View Logs (Background Mode)
```bash
tail -f tailwind-watch.log
```

## ⚡ Auto-Rebuild Trigger

Tailwind akan auto-rebuild saat file ini berubah:
- `templates/**/*.html`
- `apps/**/templates/**/*.html`
- `apps/**/forms.py`
- `**/templatetags/**/*.py`

## 🔄 Workflow Development

1. **Start watch mode:**
   ```bash
   ./tailwind-start.sh
   ```

2. **Edit template** (misalnya `_user_table.html`)
   - Tailwind auto-rebuild CSS baru
   - Refresh browser untuk lihat perubahan

3. **No need manual rebuild!** ✨

4. **Stop saat selesai:**
   ```bash
   ./tailwind-stop.sh
   ```

## 🐳 Docker Container

Container Docker harus direstart untuk load CSS baru:
```bash
docker restart esimpeg_python_app
```

Atau gunakan Docker volume mount untuk auto-reload.

## 📝 Notes

- Background mode menyimpan log di `tailwind-watch.log`
- PID process disimpan di `tailwind.pid`
- Watch mode menggunakan ~50-100MB RAM
- Build time: ~300-500ms per change

## 🛠️ Troubleshooting

**Watch tidak auto-rebuild?**
```bash
# Stop dan start ulang
./tailwind-stop.sh
./tailwind-start.sh
```

**Perubahan tidak muncul di browser?**
- Hard refresh: `Ctrl + Shift + R`
- Restart Docker container
- Clear browser cache

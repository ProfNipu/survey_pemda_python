# Pipeline ETL SIASN (Cache → Data Master)

Dokumen ini menjelaskan pipeline bertahap untuk:

1. Fetch data dari SIASN ke tabel cache `siasn_pegawai`
2. Apply (ETL) data dari `siasn_pegawai` ke tabel master internal (contoh: `ms_pegawai`)

Tujuan utama:
- Memisahkan proses **fetch** (network bound) dan **apply** (DB bound)
- Menghindari ketergantungan jadwal “harus selesai jam X”
- Memastikan proses **incremental**, ada **lock**, dan ada **audit log**

## Tahap 1 (awal): Apply `data_utama` → `ms_pegawai`

### Command

- `python manage.py siasn_apply_data_utama`

Parameter:
- `--since-minutes` (default 1440 = 24 jam)
- `--limit` (default 0 = tanpa limit)
- `--lock-file` (default `/tmp/esimpeg_siasn_apply_data_utama.lock`)

### Data sumber

- Tabel: `siasn_pegawai`
- Kolom: `dataUtama` (`SiasnPegawai.data_utama`)

### Target update

- Tabel: `ms_pegawai`
- Lookup pegawai: `MsPegawai.B_02B = NIP` (NIP baru)

Field yang di-update (minimal mengikuti pola Laravel):
- `id_lokasi` (dari `lokasiKerjaId` → `BknLokasiKerja.id_bkn`)
- `B_02` (NIP lama; dari `nipLama` atau `nipBaru`)
- `B_04` (tempat lahir)
- `B_05` (tanggal lahir)
- `B_06` (jenis kelamin)
- `B_07` (agama; `agamaId` → `MdAgama.id_bkn`)
- `J_01` (status kawin; `jenisKawinId` → `MdStatusPerkawinan.id_bkn`)
- `B_12` (alamat)
- `B_08` (no karpeg)
- `L_01A` (no askes)

### Audit log

Setiap perubahan field akan ditulis ke:
- tabel: `ms_log_data`
- action: `update`
- via: `system`
- description: `SIASN ETL data_utama for NIP <nip>`

Error akan ditulis ke:
- `ms_log_data` dengan action `<action>_error`

## Jadwal Cron yang direkomendasikan

### Konversi Waktu WIB ke UTC

**PENTING**: Server VPS 172.16.30.139 menggunakan timezone **UTC** (bukan Asia/Jakarta).

Konversi waktu untuk cron (UTC = WIB - 7 jam):

| Waktu WIB | Waktu UTC (untuk cron) | Keterangan |
|-----------|------------------------|------------|
| 01:00 WIB | 18:00 UTC (hari sebelumnya) | Fetch cache minimal |
| 03:10 WIB | 20:10 UTC (hari sebelumnya) | Apply ETL data_utama |
| 01:30 WIB (tgl 20) | 18:30 UTC (tgl 19) | Fetch integrasi lengkap |

### Jadwal Cron Saat Ini (Aktif)

```bash
# Fetch SIASN minimal - Run daily at 01:00 UTC (08:00 WIB)
0 1 * * * docker exec -i esimpeg-python python manage.py siasn_batch_sync --fetch-type minimal --stale-hours 24 --batch-size 50 --sleep-ms 150 >> /var/log/esimpeg_siasn_fetch.log 2>&1

# Apply ETL data_utama - Run daily at 03:10 UTC (10:10 WIB)
10 3 * * * docker exec -i esimpeg-python python manage.py siasn_apply_data_utama --since-minutes 1440 >> /var/log/esimpeg_siasn_etl.log 2>&1

# Fetch SIASN integrasi - Run monthly on 20th at 01:30 UTC (20th 08:30 WIB)
30 1 20 * * docker exec -i esimpeg-python python manage.py siasn_batch_sync --fetch-type integrasi --stale-hours 720 --batch-size 30 --sleep-ms 200 >> /var/log/esimpeg_siasn_integrasi.log 2>&1
```

**Status**: Cron ini jalan di **pagi hari** (08:00 & 10:10 WIB). Biarkan dulu sampai selesai, baru update.

### Jadwal Cron Rekomendasi (Dini Hari)

Untuk jalan di **dini hari** (01:00 & 03:10 WIB), update cron ke:

```bash
# Fetch SIASN minimal - Run daily at 18:00 UTC (01:00 WIB hari berikutnya)
0 18 * * * docker exec -i esimpeg-python python manage.py siasn_batch_sync --fetch-type minimal --stale-hours 24 --batch-size 50 --sleep-ms 150 >> /var/log/esimpeg_siasn_fetch.log 2>&1

# Apply ETL data_utama - Run daily at 20:10 UTC (03:10 WIB hari berikutnya)
10 20 * * * docker exec -i esimpeg-python python manage.py siasn_apply_data_utama --since-minutes 1440 >> /var/log/esimpeg_siasn_etl.log 2>&1

# Fetch SIASN integrasi - Run monthly on 19th at 18:30 UTC (20th 01:30 WIB)
30 18 19 * * docker exec -i esimpeg-python python manage.py siasn_batch_sync --fetch-type integrasi --stale-hours 720 --batch-size 30 --sleep-ms 200 >> /var/log/esimpeg_siasn_integrasi.log 2>&1
```

**Cara update**: Tunggu sampai jam 11:00 WIB (setelah ETL selesai), lalu jalankan `crontab -e` di VPS dan ganti jadwal.

ETL bersifat incremental, jadi walaupun fetch belum selesai semua, ETL tetap bisa apply untuk data yang sudah terambil.

## Catatan Penting: Timezone Server (Cron)

Cron memakai waktu **server (host VPS)**. Server VPS 172.16.30.139 menggunakan **UTC** (bukan Asia/Jakarta).

Cek timezone & jam server:

```bash
timedatectl
date
```

**Opsi 1**: Biarkan UTC dan gunakan konversi waktu di tabel di atas untuk jadwal cron.

**Opsi 2**: Set timezone ke Asia/Jakarta (di host VPS) agar jadwal cron langsung pakai waktu WIB:

```bash
sudo timedatectl set-timezone Asia/Jakarta
```

Setelah set timezone, restart cron atau tunggu cron reload otomatis.

## Tahap berikutnya

Setelah tahap 1 stabil:
- Apply `data_riwayat_pangkat`
- Apply `data_riwayat_jabatan`
- Apply `data_riwayat_pendidikan`

Untuk bulanan tgl 20:
- Jalankan fetch `integrasi` (full endpoints)
- Lanjutkan ETL lengkap

## Checklist Monitoring (Cron + Validasi Data)

Bagian ini untuk memastikan cron benar-benar jalan dan hasilnya masuk ke database.

### A) Cek cron terpasang

Di VPS (host):

```bash
crontab -l
```

Pastikan ada entry:
- Fetch minimal (harian) jam 01:00
- Apply ETL data_utama (harian) jam 03:10
- Fetch integrasi (bulanan) tgl 20 jam 01:30

### B) Cek log cron (besok setelah jam jalan)

Fetch log (harian 01:00):

```bash
tail -n 200 /var/log/esimpeg_siasn_fetch.log
```

ETL log (harian 03:10):

```bash
tail -n 200 /var/log/esimpeg_siasn_etl.log
```

Integrasi log (bulanan tgl 20 01:30):

```bash
tail -n 200 /var/log/esimpeg_siasn_integrasi.log
```

Jika file log belum ada, berarti cron belum pernah jalan atau path log berbeda.

### C) Test manual fetch (tanpa nunggu cron)

Jalankan batch kecil untuk memastikan koneksi & token OK:

```bash
docker exec -it esimpeg-python python manage.py siasn_batch_sync --fetch-type minimal --stale-hours 24 --limit 3
```

### D) Test manual ETL apply (tanpa nunggu cron)

Apply perubahan dari cache ke `ms_pegawai` untuk data yang diupdate dalam 24 jam terakhir:

```bash
docker exec -it esimpeg-python python manage.py siasn_apply_data_utama --since-minutes 1440 --limit 50
```

### E) Validasi cepat: cache terisi

Hitung jumlah pegawai cache yang sudah punya `data_utama`:

```bash
docker exec -it esimpeg-python python manage.py shell -c "from apps.integrations.siasn.models_cache import SiasnPegawai; print(SiasnPegawai.objects.exclude(data_utama=None).count())"
```

### F) Validasi cepat: ETL menulis audit log

Hitung jumlah audit log ETL `data_utama`:

```bash
docker exec -it esimpeg-python python manage.py shell -c "from esimpeg_core.models import MsLogData; print(MsLogData.objects.filter(description__icontains='SIASN ETL data_utama').count())"
```

Jika angka bertambah setelah ETL dijalankan, berarti proses apply berjalan dan perubahan dicatat.

---

## Status Verifikasi VPS 172.16.30.139

**Terakhir dicek**: 6 Maret 2026, 08:40 WIB

### ✅ Status Pipeline

- **Fetch SIASN**: Berjalan normal (cache: 229 pegawai dengan data_utama)
- **ETL Apply**: Berfungsi dengan baik (233 pegawai berhasil diupdate)
- **Cron Jobs**: Terpasang dan aktif
- **Audit Log**: 476+ entries (ms_pegawai + ms_tata_naskah_pegawai)

### ⚠️ Catatan Timezone

Server menggunakan **UTC** (bukan Asia/Jakarta). 

**Jadwal cron saat ini** (jalan di pagi hari):
- 01:00 UTC = **08:00 WIB** (Fetch) ← sedang jalan
- 03:10 UTC = **10:10 WIB** (ETL) ← akan jalan jam 10:10 WIB
- 01:30 UTC tgl 20 = **08:30 WIB** tgl 20 (Integrasi)

**Rekomendasi**: Setelah proses hari ini selesai (jam 11:00 WIB), update jadwal cron ke waktu UTC yang sesuai (lihat tabel konversi di atas) agar:
- Fetch jalan jam **01:00 WIB** (dini hari)
- ETL jalan jam **03:10 WIB** (dini hari)

Ini lebih baik karena tidak mengganggu jam kerja dan beban server lebih rendah di malam hari.

### Test Manual Berhasil

```bash
# Test ETL manual (semua data cache)
docker exec esimpeg-python python manage.py siasn_apply_data_utama --since-minutes 10080 --limit 0

# Hasil:
# - Processed: 240 pegawai
# - Updated: 233 pegawai  
# - Skipped: 5 pegawai
# - Failed: 2 pegawai
# - Duration: 21.47 detik
```

Data dari SIASN sudah berhasil masuk ke tabel `ms_pegawai` dan `ms_tata_naskah_pegawai`.

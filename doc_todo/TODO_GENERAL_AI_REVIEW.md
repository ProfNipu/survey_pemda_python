# TODO: General AI Review - dasar-python

## Tujuan
- Merangkum pekerjaan lanjutan yang sifatnya general (stabilitas, maintainability, security, deploy) berdasarkan hasil review.
- Menjaga output UI/UX tetap konsisten (no visual regression).

## High Priority (P0)
- [ ] Pastikan kontrol akses tidak bergantung pada `is_staff`
  - Standardisasi: gunakan `is_superadmin()` dan/atau permission keys.
  - Pastikan halaman sensitif return `403` (bukan hanya redirect) saat unauthorized.
- [ ] Perbaiki entrypoint untuk production
  - Jangan auto `makemigrations` saat container start.
  - `migrate` / `collectstatic` dijalankan hanya jika diizinkan via environment flag.
  - Jangan print credential / informasi sensitif ke log startup.
- [ ] Review secrets dan default config
  - Pastikan `SECRET_KEY`, password DB/Redis tidak mengandung nilai default yang committed.

## Medium Priority (P1)
- [ ] Dokumentasi deployment
  - Checklist deploy + rollback.
  - Catatan migrasi + perintah seeding yang wajib.
- [ ] Audit API URL dan kompatibilitas client
  - Pastikan dokumentasi mengikuti prefix API terbaru.
  - Pastikan error handling konsisten.

## Low Priority (P2)
- [ ] Rapikan struktur docs/todo
  - Kelompokkan TODO per area (auth/permission, UI/table, deploy).
  - Tutup item DONE untuk mengurangi noise.

## Catatan
- Kerjakan item P0 dulu sebelum refactor besar.

-- Reset Django migrations untuk fix custom User model
-- HATI-HATI: Ini akan hapus migration history

-- Delete migration records yang conflict
DELETE FROM django_migrations WHERE app IN ('admin', 'auth', 'contenttypes', 'sessions');

-- Check remaining migrations
SELECT * FROM django_migrations;

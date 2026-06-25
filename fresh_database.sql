-- Fresh database untuk ESIMPEG Python
-- Drop semua table Django tapi KEEP Laravel tables (ms_pegawai, ms_opd, dll)

-- Drop Django tables
DROP TABLE IF EXISTS django_migrations;
DROP TABLE IF EXISTS django_admin_log;
DROP TABLE IF EXISTS django_content_type;
DROP TABLE IF EXISTS django_session;
DROP TABLE IF EXISTS auth_group;
DROP TABLE IF EXISTS auth_group_permissions;
DROP TABLE IF EXISTS auth_permission;
DROP TABLE IF EXISTS auth_user;
DROP TABLE IF EXISTS auth_user_groups;
DROP TABLE IF EXISTS auth_user_user_permissions;
DROP TABLE IF EXISTS users;

-- Drop Python app tables
DROP TABLE IF EXISTS permissions_module;
DROP TABLE IF EXISTS permissions_control;
DROP TABLE IF EXISTS permissions_function;
DROP TABLE IF EXISTS permissions_modulemenu;
DROP TABLE IF EXISTS permissions_userpermission;
DROP TABLE IF EXISTS permissions_grouppermission;
DROP TABLE IF EXISTS integrations_wssiasntoken;
DROP TABLE IF EXISTS integrations_siasnapilog;
DROP TABLE IF EXISTS integrations_fetchprogress;
DROP TABLE IF EXISTS integrations_siasnpermission;
DROP TABLE IF EXISTS django_plotly_dash_dashapp;
DROP TABLE IF EXISTS django_plotly_dash_statelessapp;

-- Keep Laravel tables:
-- ms_pegawai, ms_opd, ms_jabatan, dll (TIDAK DIHAPUS)

SELECT 'Fresh database done! Laravel tables preserved.' AS message;

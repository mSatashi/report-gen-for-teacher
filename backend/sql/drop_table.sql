DROP TABLE IF EXISTS diagnostic_result CASCADE;
DROP TABLE IF EXISTS knowledge_state    CASCADE;
DROP TABLE IF EXISTS laporan            CASCADE;
DROP TABLE IF EXISTS rencana_studi      CASCADE;
DROP TABLE IF EXISTS draft_analisis     CASCADE;
DROP TABLE IF EXISTS log_pertemuan      CASCADE;
DROP TABLE IF EXISTS kelas_murid        CASCADE;
-- [TAMBAHAN] Tabel baru yang menangani Skill Graph dan Kurikulum
DROP TABLE IF EXISTS topik_prasyarat    CASCADE;
DROP TABLE IF EXISTS topik              CASCADE;
DROP TABLE IF EXISTS kelas              CASCADE;
DROP TABLE IF EXISTS mata_pelajaran     CASCADE;
-- [END TAMBAHAN]
DROP TABLE IF EXISTS murid              CASCADE;
DROP TABLE IF EXISTS pengajar           CASCADE;
DROP TABLE IF EXISTS pengguna           CASCADE;
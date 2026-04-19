CREATE EXTENSION IF NOT EXISTS "pgcrypto";
 
 
-- =============================================================================
-- 1. PENGGUNA  (tabel induk semua user)
-- =============================================================================
CREATE TABLE IF NOT EXISTS pengguna (
    id              VARCHAR(50)  PRIMARY KEY,
    username        VARCHAR(100) NOT NULL UNIQUE,
    email_address   VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    tipe_pengguna   VARCHAR(20)  NOT NULL CHECK (tipe_pengguna IN ('pengajar', 'murid', 'admin')),
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW()
);
 
COMMENT ON TABLE  pengguna IS 'Tabel induk semua pengguna sistem (pengajar dan murid)';
COMMENT ON COLUMN pengguna.tipe_pengguna IS 'Nilai: pengajar | murid | admin';
 
 
-- =============================================================================
-- 2. PENGAJAR  (profil tambahan pengajar)
-- =============================================================================
CREATE TABLE IF NOT EXISTS pengajar (
    id VARCHAR(50) PRIMARY KEY
        REFERENCES pengguna(id) ON DELETE CASCADE
);
 
COMMENT ON TABLE pengajar IS 'Profil tambahan untuk pengguna bertipe pengajar';
 
 
-- =============================================================================
-- 3. MURID  (profil tambahan murid — TANPA kolom password)
-- =============================================================================
-- Catatan: password TIDAK disimpan di sini.
-- Otentikasi murid dilakukan via tabel pengguna (hashed_password).
CREATE TABLE IF NOT EXISTS murid (
    id               VARCHAR(50) PRIMARY KEY
                         REFERENCES pengguna(id) ON DELETE CASCADE,
    nama             VARCHAR(150),
    usia             INTEGER,
    level            VARCHAR(50),
    diagnostic_level VARCHAR(50),
    credit_total     INTEGER NOT NULL DEFAULT 0,
    credit_used      INTEGER NOT NULL DEFAULT 0
);
 
COMMENT ON TABLE  murid IS 'Profil murid. Password ada di tabel pengguna, bukan di sini.';
COMMENT ON COLUMN murid.diagnostic_level IS 'Level hasil tes diagnostik awal';
COMMENT ON COLUMN murid.credit_total     IS 'Total sesi/kredit yang dialokasikan';
COMMENT ON COLUMN murid.credit_used      IS 'Sesi/kredit yang sudah digunakan';
 
 
-- =============================================================================
-- 4. KELAS
-- =============================================================================
CREATE TABLE IF NOT EXISTS kelas (
    id             VARCHAR(50)  PRIMARY KEY,
    nama           VARCHAR(100) NOT NULL,
    mata_pelajaran VARCHAR(100),
    pengajar_id    VARCHAR(50)  REFERENCES pengajar(id) ON DELETE SET NULL,
    kredit         INTEGER      NOT NULL DEFAULT 0,
    jadwal         VARCHAR(100),
    created_at     TIMESTAMP    NOT NULL DEFAULT NOW()
);
 
COMMENT ON TABLE  kelas IS 'Kelas belajar yang diajar pengajar';
COMMENT ON COLUMN kelas.kredit IS 'Jumlah total sesi/pertemuan yang direncanakan';
 
 
-- =============================================================================
-- 5. KELAS_MURID  (tabel pivot many-to-many kelas <-> murid)
-- =============================================================================
CREATE TABLE IF NOT EXISTS kelas_murid (
    kelas_id  VARCHAR(50) NOT NULL REFERENCES kelas(id)  ON DELETE CASCADE,
    murid_id  VARCHAR(50) NOT NULL REFERENCES murid(id)  ON DELETE CASCADE,
    joined_at TIMESTAMP   NOT NULL DEFAULT NOW(),
    PRIMARY KEY (kelas_id, murid_id)
);
 
COMMENT ON TABLE kelas_murid IS 'Pivot tabel — murid yang terdaftar di kelas tertentu';
 
 
-- =============================================================================
-- 6. LOG_PERTEMUAN  (daily log — F001 & F002)
-- =============================================================================
CREATE TABLE IF NOT EXISTS log_pertemuan (
    id                       VARCHAR(50)   PRIMARY KEY,
    kelas_id                 VARCHAR(50)   NOT NULL REFERENCES kelas(id)  ON DELETE CASCADE,
    murid_id                 VARCHAR(50)            REFERENCES murid(id)  ON DELETE CASCADE,
    tanggal                  DATE          NOT NULL,
    topik                    VARCHAR(255)  NOT NULL,
    nilai                    NUMERIC(5,2),
    tingkat_pemahaman        VARCHAR(50)   CHECK (tingkat_pemahaman IN ('sangat_paham','paham','cukup','perlu_review')),
    tingkat_keterlibatan     VARCHAR(50)   CHECK (tingkat_keterlibatan IN ('sangat_aktif','aktif','kurang_fokus')),
    kompetensi_dicapai       TEXT,
    target_materi_berikutnya TEXT,
    kendala                  TEXT,
    catatan                  TEXT,
    durasi_menit             INTEGER,
    metode_belajar           VARCHAR(100),
    created_at               TIMESTAMP     NOT NULL DEFAULT NOW()
);
 
COMMENT ON TABLE  log_pertemuan IS 'Log pertemuan harian — F001 (single) & F002 (bulk)';
COMMENT ON COLUMN log_pertemuan.murid_id IS 'NULL = log untuk seluruh kelas; diisi = log per murid';
 
 
-- =============================================================================
-- 7. DRAFT_ANALISIS  (output analisis NarrativeEngine LLM)
-- =============================================================================
CREATE TABLE IF NOT EXISTS draft_analisis (
    id       VARCHAR(50) PRIMARY KEY,
    kelas_id VARCHAR(50) REFERENCES kelas(id) ON DELETE CASCADE,
    murid_id VARCHAR(50) REFERENCES murid(id) ON DELETE CASCADE,
    konten   TEXT        NOT NULL,
    tanggal  TIMESTAMP   NOT NULL DEFAULT NOW()
);
 
COMMENT ON TABLE draft_analisis IS 'Hasil analisis log pertemuan oleh NarrativeEngine LLM — input untuk PlannerEngine';
 
 
-- =============================================================================
-- 8. RENCANA_STUDI  (learning plan — F004)
-- =============================================================================
CREATE TABLE IF NOT EXISTS rencana_studi (
    id                        VARCHAR(50) PRIMARY KEY,
    kelas_id                  VARCHAR(50) REFERENCES kelas(id)         ON DELETE CASCADE,
    murid_id                  VARCHAR(50) REFERENCES murid(id)         ON DELETE CASCADE,
    draft_analisis_id         VARCHAR(50) REFERENCES draft_analisis(id) ON DELETE SET NULL,
    waktu                     TIMESTAMP   NOT NULL DEFAULT NOW(),
    daftar_rekomendasi_materi JSONB,
    estimasi_waktu_selesai    TIMESTAMP,
    catatan_analisa           TEXT,
    jadwal_mingguan           JSONB,
    version                   INTEGER     NOT NULL DEFAULT 1
);
 
COMMENT ON TABLE  rencana_studi IS 'Rencana studi adaptif — F004 (BKT + LLM)';
COMMENT ON COLUMN rencana_studi.daftar_rekomendasi_materi IS 'JSON array of strings: ["Topik A","Topik B"]';
COMMENT ON COLUMN rencana_studi.jadwal_mingguan           IS 'JSON object: {"Minggu 1": ["Topik A"], ...}';
COMMENT ON COLUMN rencana_studi.version IS 'Bertambah setiap kali generate ulang untuk kelas+murid yang sama';
 
 
-- =============================================================================
-- 9. LAPORAN  (progress report — F003, F005, F006, F007)
-- =============================================================================
CREATE TABLE IF NOT EXISTS laporan (
    id              VARCHAR(50)  PRIMARY KEY,
    murid_id        VARCHAR(50)  NOT NULL REFERENCES murid(id) ON DELETE CASCADE,
    kelas_id        VARCHAR(50)           REFERENCES kelas(id) ON DELETE CASCADE,
    konten          TEXT         NOT NULL,
    tipe_laporan    VARCHAR(50)  NOT NULL DEFAULT 'perkembangan',
    status          VARCHAR(20)  NOT NULL DEFAULT 'draft'
                        CHECK (status IN ('draft','final','terkirim')),
    pdf_path        VARCHAR(255),
    tanggal         TIMESTAMP    NOT NULL DEFAULT NOW(),
    tanggal_dikirim TIMESTAMP,
    is_ai_generated BOOLEAN      NOT NULL DEFAULT TRUE,
    periode_mulai   DATE,
    periode_selesai DATE
);
 
COMMENT ON TABLE  laporan IS 'Laporan perkembangan siswa — F003 generate, F005 edit, F006 kirim, F007 lihat';
COMMENT ON COLUMN laporan.status IS 'draft → final → terkirim';
 
 
-- =============================================================================
-- 10. KNOWLEDGE_STATE  (output BKT per topik per murid)
-- =============================================================================
CREATE TABLE IF NOT EXISTS knowledge_state (
    id          VARCHAR(50)          PRIMARY KEY,
    murid_id    VARCHAR(50)  NOT NULL REFERENCES murid(id) ON DELETE CASCADE,
    topik       VARCHAR(255) NOT NULL,
    p_knowledge FLOAT        NOT NULL DEFAULT 0.0,
    p_learn     FLOAT        NOT NULL DEFAULT 0.2,
    p_guess     FLOAT        NOT NULL DEFAULT 0.1,
    p_slip      FLOAT        NOT NULL DEFAULT 0.05,
    updated_at  TIMESTAMP    NOT NULL DEFAULT NOW(),
    UNIQUE (murid_id, topik)
);
 
COMMENT ON TABLE  knowledge_state IS 'Probabilitas penguasaan materi murid per topik — output BKT';
COMMENT ON COLUMN knowledge_state.p_knowledge IS 'P(Ln): 0.0 = belum menguasai, 1.0 = sudah menguasai';
COMMENT ON COLUMN knowledge_state.p_learn     IS 'P(T): probabilitas belajar per sesi';
COMMENT ON COLUMN knowledge_state.p_guess     IS 'P(G): probabilitas tebak benar meski tidak tahu';
COMMENT ON COLUMN knowledge_state.p_slip      IS 'P(S): probabilitas jawab salah meski sudah tahu';
 
 
-- =============================================================================
-- 11. DIAGNOSTIC_RESULT  (tes diagnostik awal — F008)
-- =============================================================================
CREATE TABLE IF NOT EXISTS diagnostic_result (
    id               VARCHAR(50)  PRIMARY KEY,
    murid_id         VARCHAR(50)  NOT NULL REFERENCES murid(id)  ON DELETE CASCADE,
    kelas_id         VARCHAR(50)           REFERENCES kelas(id)  ON DELETE CASCADE,
    topik            VARCHAR(255),
    skor             FLOAT,
    diagnostic_score FLOAT,
    sequence_number  INTEGER      NOT NULL DEFAULT 1,
    model_ai         VARCHAR(100),
    created_at       TIMESTAMP    NOT NULL DEFAULT NOW()
);
 
COMMENT ON TABLE  diagnostic_result IS 'Hasil tes diagnostik awal — F008. Dipakai sebagai P(L0) untuk BKT.';
COMMENT ON COLUMN diagnostic_result.diagnostic_score IS 'Nilai 0–100 dari tes awal → dikonversi ke P(L0) = score/100';
 
 
-- =============================================================================
-- INDEX  (untuk mempercepat query yang sering dilakukan)
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_log_kelas     ON log_pertemuan (kelas_id);
CREATE INDEX IF NOT EXISTS idx_log_murid     ON log_pertemuan (murid_id);
CREATE INDEX IF NOT EXISTS idx_log_tanggal   ON log_pertemuan (tanggal);
CREATE INDEX IF NOT EXISTS idx_laporan_murid ON laporan       (murid_id);
CREATE INDEX IF NOT EXISTS idx_laporan_status ON laporan      (status);
CREATE INDEX IF NOT EXISTS idx_rencana_kelas ON rencana_studi (kelas_id);
CREATE INDEX IF NOT EXISTS idx_rencana_murid ON rencana_studi (murid_id);
CREATE INDEX IF NOT EXISTS idx_ks_murid      ON knowledge_state (murid_id);
CREATE INDEX IF NOT EXISTS idx_diag_murid    ON diagnostic_result (murid_id);
CREATE INDEX IF NOT EXISTS idx_kelas_pengajar ON kelas           (pengajar_id);
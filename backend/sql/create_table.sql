-- =============================================================================
-- create_table.sql (Versi Final Sinkron dengan AI Engine)
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. PENGGUNA
CREATE TABLE IF NOT EXISTS pengguna (
    id              VARCHAR(50)  PRIMARY KEY,
    username        VARCHAR(100) NOT NULL UNIQUE,
    email_address   VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    tipe_pengguna   VARCHAR(20)  NOT NULL, -- 'pengajar', 'admin'
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- 2. PENGAJAR
CREATE TABLE IF NOT EXISTS pengajar (
    id VARCHAR(50) PRIMARY KEY REFERENCES pengguna(id) ON DELETE CASCADE
);

-- 3. MURID
CREATE TABLE IF NOT EXISTS murid (
    id               VARCHAR(50)  PRIMARY KEY,
    email_address    VARCHAR(100) NOT NULL UNIQUE,
    nama             VARCHAR(150),
    education_level  VARCHAR(50),
    jenis_kelamin    VARCHAR(20),
    diagnostic_level VARCHAR(50),
    is_active        BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- 4. MATA PELAJARAN
CREATE TABLE IF NOT EXISTS mata_pelajaran (
    id                  VARCHAR(50)  PRIMARY KEY,
    nama_mata_pelajaran VARCHAR(150) NOT NULL,
    kredit              INTEGER      NOT NULL DEFAULT 0,
    hari                VARCHAR(10),
    jam                 VARCHAR(5),  -- Format HH:MM
    created_at          TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- 5. TOPIK (Penting untuk Skill Graph BKT/PSO)
CREATE TABLE IF NOT EXISTS topik (
    id                VARCHAR(50)  PRIMARY KEY,
    mata_pelajaran_id VARCHAR(50)  NOT NULL REFERENCES mata_pelajaran(id) ON DELETE CASCADE,
    nama              VARCHAR(150) NOT NULL,
    difficulty_index  FLOAT        DEFAULT 0.5, -- Digunakan PSO
    created_at        TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- 6. TOPIK_PRASYARAT (Relasi Many-to-Many untuk PSO Planner)
CREATE TABLE IF NOT EXISTS topik_prasyarat (
    topik_id     VARCHAR(50) NOT NULL REFERENCES topik(id) ON DELETE CASCADE,
    prasyarat_id VARCHAR(50) NOT NULL REFERENCES topik(id) ON DELETE CASCADE,
    PRIMARY KEY (topik_id, prasyarat_id)
);

-- 7. KELAS
CREATE TABLE IF NOT EXISTS kelas (
    id                VARCHAR(50)  PRIMARY KEY,
    nama              VARCHAR(100) NOT NULL UNIQUE,
    mata_pelajaran_id VARCHAR(50)  REFERENCES mata_pelajaran(id) ON DELETE SET NULL,
    pengajar_id       VARCHAR(50)  REFERENCES pengajar(id) ON DELETE SET NULL,
    hari              VARCHAR(10)  NOT NULL,
    jam               VARCHAR(5)   NOT NULL,
    created_at        TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- 8. KELAS_MURID
CREATE TABLE IF NOT EXISTS kelas_murid (
    kelas_id  VARCHAR(50) NOT NULL REFERENCES kelas(id) ON DELETE CASCADE,
    murid_id  VARCHAR(50) NOT NULL REFERENCES murid(id) ON DELETE CASCADE,
    joined_at TIMESTAMP   NOT NULL DEFAULT NOW(),
    PRIMARY KEY (kelas_id, murid_id)
);

-- 9. LOG_PERTEMUAN (Sumber Data BKT)
CREATE TABLE IF NOT EXISTS log_pertemuan (
    id                       VARCHAR(50)   PRIMARY KEY,
    kelas_id                 VARCHAR(50)   NOT NULL REFERENCES kelas(id) ON DELETE CASCADE,
    murid_id                 VARCHAR(50)   NOT NULL REFERENCES murid(id) ON DELETE CASCADE,
    tanggal                  DATE          NOT NULL,
    topik                    VARCHAR(255)  NOT NULL, -- Nama topik
    nilai                    NUMERIC(5,2),           -- Digunakan BKT
    tingkat_pemahaman        VARCHAR(50),
    tingkat_keterlibatan     VARCHAR(50),
    kompetensi_dicapai       TEXT,
    target_materi_berikutnya TEXT,
    kendala                  TEXT,
    catatan                  TEXT,
    durasi_menit             INTEGER,
    metode_belajar           VARCHAR(100),
    created_at               TIMESTAMP     NOT NULL DEFAULT NOW()
);

-- 10. KNOWLEDGE_STATE (Otak BKT)
CREATE TABLE IF NOT EXISTS knowledge_state (
    id          VARCHAR(50)  PRIMARY KEY,
    murid_id    VARCHAR(50)  NOT NULL REFERENCES murid(id) ON DELETE CASCADE,
    topik       VARCHAR(255) NOT NULL,
    p_knowledge FLOAT        NOT NULL DEFAULT 0.2, -- P(L)
    p_learn     FLOAT        NOT NULL DEFAULT 0.15, -- P(T)
    p_guess     FLOAT        NOT NULL DEFAULT 0.1,  -- P(G)
    p_slip      FLOAT        NOT NULL DEFAULT 0.05, -- P(S)
    updated_at  TIMESTAMP    NOT NULL DEFAULT NOW(),
    UNIQUE (murid_id, topik)
);

-- 11. DRAFT_ANALISIS (Output LLM Narrative)
CREATE TABLE IF NOT EXISTS draft_analisis (
    id       VARCHAR(50) PRIMARY KEY,
    kelas_id VARCHAR(50) REFERENCES kelas(id) ON DELETE CASCADE,
    murid_id VARCHAR(50) REFERENCES murid(id) ON DELETE CASCADE,
    konten   TEXT        NOT NULL,
    tanggal  TIMESTAMP   NOT NULL DEFAULT NOW()
);

-- 12. RENCANA_STUDI (Output PSO Planner)
CREATE TABLE IF NOT EXISTS rencana_studi (
    id                        VARCHAR(50) PRIMARY KEY,
    kelas_id                  VARCHAR(50) REFERENCES kelas(id) ON DELETE CASCADE,
    murid_id                  VARCHAR(50) REFERENCES murid(id) ON DELETE CASCADE,
    draft_analisis_id         VARCHAR(50) REFERENCES draft_analisis(id) ON DELETE SET NULL,
    daftar_rekomendasi_materi JSONB,      -- Hasil urutan PSO
    jadwal_mingguan           JSONB,      -- Distribusi per minggu
    catatan_analisa           TEXT,
    estimasi_waktu_selesai    TIMESTAMP,
    is_outdated               BOOLEAN     DEFAULT FALSE,
    version                   INTEGER     NOT NULL DEFAULT 1,
    waktu                     TIMESTAMP   NOT NULL DEFAULT NOW()
);

-- 13. LAPORAN (Laporan Final ke Orang Tua)
CREATE TABLE IF NOT EXISTS laporan (
    id              VARCHAR(50)  PRIMARY KEY,
    murid_id        VARCHAR(50)  NOT NULL REFERENCES murid(id) ON DELETE CASCADE,
    kelas_id        VARCHAR(50)  REFERENCES kelas(id) ON DELETE CASCADE,
    konten          TEXT         NOT NULL,
    tipe_laporan    VARCHAR(50)  NOT NULL DEFAULT 'perkembangan',
    status          VARCHAR(20)  NOT NULL DEFAULT 'draft',
    pdf_path        VARCHAR(255),
    tanggal         TIMESTAMP    NOT NULL DEFAULT NOW(),
    tanggal_dikirim TIMESTAMP,
    is_ai_generated BOOLEAN      NOT NULL DEFAULT TRUE,
    periode_mulai   DATE,
    periode_selesai DATE
);

-- 14. DIAGNOSTIC_RESULT
CREATE TABLE IF NOT EXISTS diagnostic_result (
    id               VARCHAR(50)  PRIMARY KEY,
    murid_id         VARCHAR(50)  NOT NULL REFERENCES murid(id) ON DELETE CASCADE,
    kelas_id         VARCHAR(50)  REFERENCES kelas(id) ON DELETE CASCADE,
    topik            VARCHAR(255),
    skor             FLOAT,
    diagnostic_score FLOAT,
    created_at       TIMESTAMP    NOT NULL DEFAULT NOW()
);
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
CREATE INDEX IF NOT EXISTS idx_kelas_mapel ON kelas (mata_pelajaran_id);
CREATE INDEX IF NOT EXISTS idx_mapel_nama ON mata_pelajaran (nama_mata_pelajaran);
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
 
 
-- =============================================================================
-- 1. PENGGUNA  (tabel induk semua user)
-- =============================================================================
CREATE TABLE IF NOT EXISTS pengguna (
    id              VARCHAR(50)  PRIMARY KEY,
    username        VARCHAR(100) NOT NULL UNIQUE,
    email_address   VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    tipe_pengguna   VARCHAR(20)  NOT NULL CHECK (tipe_pengguna IN ('pengajar', 'admin')),
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW()
);
 
-- =============================================================================
-- 2. PENGAJAR  (profil tambahan pengajar)
-- =============================================================================
CREATE TABLE IF NOT EXISTS pengajar (
    id VARCHAR(50) PRIMARY KEY
        REFERENCES pengguna(id) ON DELETE CASCADE
);
 
-- =============================================================================
-- 3. MURID  (profil tambahan murid)
-- =============================================================================
CREATE TABLE IF NOT EXISTS murid (
    id               VARCHAR(50) PRIMARY KEY,
    email_address   VARCHAR(100) NOT NULL UNIQUE,
    nama             VARCHAR(150),
    education_level  VARCHAR(50),
    jenis_kelamin    VARCHAR(20),
    diagnostic_level VARCHAR(50),
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE
);
 
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
 
-- =============================================================================
-- 5. KELAS_MURID  (tabel pivot many-to-many kelas <-> murid)
-- =============================================================================
CREATE TABLE IF NOT EXISTS kelas_murid (
    kelas_id  VARCHAR(50) NOT NULL REFERENCES kelas(id)  ON DELETE CASCADE,
    murid_id  VARCHAR(50) NOT NULL REFERENCES murid(id)  ON DELETE CASCADE,
    joined_at TIMESTAMP   NOT NULL DEFAULT NOW(),
    PRIMARY KEY (kelas_id, murid_id)
);
 
-- =============================================================================
-- 6. LOG_PERTEMUAN  (daily log — F001 & F002)
-- =============================================================================
CREATE TABLE IF NOT EXISTS log_pertemuan (
    id                       VARCHAR(50)   PRIMARY KEY,
    kelas_id                 VARCHAR(50)   NOT NULL REFERENCES kelas(id)  ON DELETE CASCADE,
    murid_id                 VARCHAR(50)   NOT NULL REFERENCES murid(id)  ON DELETE CASCADE,
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
 
 
-- =============================================================================
-- 9. LAPORAN  (progress report — F003, F005, F006, F007)
-- =============================================================================
CREATE TABLE IF NOT EXISTS laporan (
    id              VARCHAR(50)  PRIMARY KEY,
    murid_id        VARCHAR(50)  NOT NULL REFERENCES murid(id) ON DELETE CASCADE,
    kelas_id        VARCHAR(50)  NOT NULL REFERENCES kelas(id) ON DELETE CASCADE,
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

CREATE TABLE IF NOT EXISTS mata_pelajaran (
    id                 VARCHAR(50)  PRIMARY KEY,
    nama_mata_pelajaran VARCHAR(150) NOT NULL,
    kredit             INTEGER      NOT NULL CHECK (kredit > 0),
 
    -- Jadwal: hari dan jam terpisah agar bisa difilter dan divalidasi
    -- hari  : 'Senin' | 'Selasa' | 'Rabu' | 'Kamis' | 'Jumat' | 'Sabtu' | 'Minggu'
    -- jam   : format HH:MM, contoh '10:00', '13:30'
    hari               VARCHAR(10)  NOT NULL
                           CHECK (hari IN ('Senin','Selasa','Rabu','Kamis','Jumat','Sabtu','Minggu')),
    jam                VARCHAR(5)   NOT NULL,  -- HH:MM
    created_at         TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMP    NOT NULL DEFAULT NONE
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
CREATE INDEX IF NOT EXISTS idx_mapel_nama ON mata_pelajaran (nama_mata_pelajaran);
CREATE INDEX IF NOT EXISTS idx_mapel_hari ON mata_pelajaran (hari);
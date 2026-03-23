
CREATE TABLE pengguna (
    id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email_address VARCHAR(100) UNIQUE NOT NULL,
    tipe_pengguna VARCHAR(20) NOT NULL
);

CREATE TABLE murid (
    id VARCHAR(50) PRIMARY KEY REFERENCES pengguna(id) ON DELETE CASCADE
);

CREATE TABLE pengajar (
    id VARCHAR(50) PRIMARY KEY REFERENCES pengguna(id) ON DELETE CASCADE
);

CREATE TABLE kelas (
    id VARCHAR(50) PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    pengajar_id VARCHAR(50) REFERENCES pengajar(id) ON DELETE SET NULL
);

CREATE TABLE kelas_murid (
    kelas_id VARCHAR(50) REFERENCES kelas(id) ON DELETE CASCADE,
    murid_id VARCHAR(50) REFERENCES murid(id) ON DELETE CASCADE,
    PRIMARY KEY (kelas_id, murid_id)
);

CREATE TABLE log_pertemuan (
    id VARCHAR(50) PRIMARY KEY,
    kelas_id VARCHAR(50) REFERENCES kelas(id) ON DELETE CASCADE,
    tanggal DATE NOT NULL,
    topik VARCHAR(255) NOT NULL,
    nilai NUMERIC(5,2),
    catatan TEXT
);

CREATE TABLE draft_analisis (
    id VARCHAR(50) PRIMARY KEY,
    konten TEXT NOT NULL,
    tanggal TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE rencana_studi (
    id VARCHAR(50) PRIMARY KEY,
    waktu TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    daftar_rekomendasi_materi TEXT NOT NULL, 
    estimasi_waktu VARCHAR(100),
    catatan_analisa TEXT
);

CREATE TABLE planner_engine (
    id VARCHAR(50) PRIMARY KEY,
    model VARCHAR(100) NOT NULL,
    url_link VARCHAR(255) NOT NULL
);
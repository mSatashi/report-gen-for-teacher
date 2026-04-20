-- Pengajar contoh
INSERT INTO pengguna (id, username, email_address, hashed_password, tipe_pengguna, is_active)
VALUES
  ('pengajar-001', 'guru_rara',   'rara@sekolah.com',  '$2b$12$LqMdnb9VV/4Bj3oE.WFbVeUpuv8bUhqBFKPiS72P4rE7jNi8vqr.a', 'pengajar', true),
  ('pengajar-002', 'guru_budi',   'budi@sekolah.com',  '$2b$12$LqMdnb9VV/4Bj3oE.WFbVeUpuv8bUhqBFKPiS72P4rE7jNi8vqr.a', 'pengajar', true)
ON CONFLICT DO NOTHING;
 
INSERT INTO pengajar (id) VALUES ('pengajar-001'), ('pengajar-002')
ON CONFLICT DO NOTHING;
 
-- Murid contoh
INSERT INTO pengguna (id, username, email_address, hashed_password, tipe_pengguna, is_active)
VALUES
  ('murid-001', 'aisya_putri',   'aisya@email.com',  '$2b$12$LqMdnb9VV/4Bj3oE.WFbVeUpuv8bUhqBFKPiS72P4rE7jNi8vqr.a', 'murid', true),
  ('murid-002', 'budi_santoso',  'budis@email.com',  '$2b$12$LqMdnb9VV/4Bj3oE.WFbVeUpuv8bUhqBFKPiS72P4rE7jNi8vqr.a', 'murid', true),
  ('murid-003', 'nadia_fajar',   'nadia@email.com',  '$2b$12$LqMdnb9VV/4Bj3oE.WFbVeUpuv8bUhqBFKPiS72P4rE7jNi8vqr.a', 'murid', true)
ON CONFLICT DO NOTHING;
 
INSERT INTO murid (id, nama, usia, level, credit_total, credit_used)
VALUES
  ('murid-001', 'Aisya Putri',   14, 'SMP Kelas 2', 24, 8),
  ('murid-002', 'Budi Santoso',  15, 'SMA Kelas 1', 20, 5),
  ('murid-003', 'Nadia Fajar',   13, 'SMP Kelas 1', 24, 3)
ON CONFLICT DO NOTHING;
 
-- Kelas contoh
INSERT INTO kelas (id, nama, mata_pelajaran, pengajar_id, kredit, jadwal)
VALUES
  ('kelas-001', 'Matematika 10A', 'Matematika', 'pengajar-001', 20, 'Senin 08:00'),
  ('kelas-002', 'IPA 9B',         'IPA',        'pengajar-001', 20, 'Rabu 10:00'),
  ('kelas-003', 'B. Inggris 10',  'B. Inggris', 'pengajar-002', 16, 'Jumat 13:00')
ON CONFLICT DO NOTHING;
 
-- Daftarkan murid ke kelas
INSERT INTO kelas_murid (kelas_id, murid_id)
VALUES
  ('kelas-001', 'murid-001'),
  ('kelas-001', 'murid-002'),
  ('kelas-002', 'murid-003'),
  ('kelas-003', 'murid-001')
ON CONFLICT DO NOTHING;
"""
scripts/seed_bkt_params.py
═══════════════════════════════════════════════════════════════════════════════
Script untuk load parameter BKT hasil tuning (02_bkt_tuning.py) ke backend.
 
CARA PAKAI:
  # Setelah menjalankan experiment/02_bkt_tuning.py
  python scripts/seed_bkt_params.py --params-file experiment/models/bkt_global_params.csv
 
  # Atau otomatis dari Makefile / startup:
  python scripts/seed_bkt_params.py
 
KAPAN DIJALANKAN:
  - Setelah iterasi tuning baru di experiment/
  - Sebelum restart backend jika params berubah
  - Bisa dipanggil dari app/main.py jika AUTO_LOAD_BKT_PARAMS=true di .env
 
FILE YANG DIBACA:
  experiment/models/bkt_global_params.csv (output dari 02_bkt_tuning.py)
  Format: skill_name, learn, slip, guess
═══════════════════════════════════════════════════════════════════════════════
"""
import argparse
import csv
import logging
import os
import sys
from pathlib import Path
 
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)
 
DEFAULT_PARAMS_FILE = "experiment/models/bkt_global_params.csv"
 
 
def load_tuned_params(params_file: str) -> bool:
    """
    Baca bkt_global_params.csv dan update BKTEngine singleton.
 
    Return True jika berhasil, False jika gagal.
    """
    if not os.path.exists(params_file):
        logger.warning(
            "File params BKT tidak ditemukan: %s\n"
            "Jalankan experiment/02_bkt_tuning.py terlebih dahulu.\n"
            "Backend akan pakai parameter default berbasis difficulty.",
            params_file,
        )
        return False
 
    custom_params = {}
    try:
        with open(params_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                skill = row.get("skill_name", "").strip()
                if not skill:
                    continue
                custom_params[skill] = {
                    "learn": float(row.get("learn", 0.15)),
                    "slip":  float(row.get("slip",  0.05)),
                    "guess": float(row.get("guess", 0.10)),
                }
    except Exception as e:
        logger.error("Gagal membaca file params: %s", e)
        return False
 
    if not custom_params:
        logger.warning("File params kosong: %s", params_file)
        return False
 
    # Tambahkan root proyek ke path
    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root))
 
    try:
        from app.ai.bkt_engine import bkt_engine
        bkt_engine._custom = custom_params
 
        logger.info(
            "✅ BKT params ter-load dari %s (%d skill).",
            params_file, len(custom_params),
        )
        return True
    except ImportError as e:
        logger.error("Gagal import BKTEngine: %s", e)
        return False
 
 
def main():
    parser = argparse.ArgumentParser(
        description="Load tuned BKT params dari 02_bkt_tuning.py ke BKTEngine"
    )
    parser.add_argument(
        "--params-file",
        default=DEFAULT_PARAMS_FILE,
        help=f"Path ke bkt_global_params.csv (default: {DEFAULT_PARAMS_FILE})",
    )
    args = parser.parse_args()
    success = load_tuned_params(args.params_file)
    sys.exit(0 if success else 1)
 
 
if __name__ == "__main__":
    main()
 
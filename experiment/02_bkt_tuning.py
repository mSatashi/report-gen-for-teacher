import os
import pandas as pd
import numpy as np
from pyBKT.models import Model

def run_bkt_tuning():
    dataset_path = "../output/daily_logs_mock.csv"
    
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset tidak ditemukan di: {dataset_path}. Jalankan 01_dataset_gen.py terlebih dahulu.")
        
    try:
        df = pd.read_csv(dataset_path)
    except pd.errors.EmptyDataError:
        raise ValueError("File dataset kosong.")
    except Exception as e:
        raise RuntimeError(f"Gagal membaca file dataset: {str(e)}")

    required_columns = ["student_id", "topic", "is_correct"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise KeyError(f"Kolom wajib tidak ditemukan di dataset: {missing_columns}")

    df.rename(columns={
        "student_id": "user_id",
        "topic": "skill_name",
        "is_correct": "correct"
    }, inplace=True)

    print(f"Memulai BKT Tuning dengan {len(df)} baris data...")

    try:
        model = Model(seed=42, num_fits=5)
        
        evaluation_results = model.crossvalidate(
            data=df,
            folds=5,
            forgets=False,
            metric=['rmse', 'accuracy']
        )
        
        print("\n=== Hasil Evaluasi Cross-Validation ===")
        print(evaluation_results)
        
    except MemoryError:
        print("Error: Memori tidak cukup untuk memproses dataset. Coba kurangi jumlah folds atau ukuran data.")
    except ValueError as ve:
        print(f"Error pada nilai parameter BKT: {str(ve)}")
    except Exception as e:
        print(f"Terjadi error tidak terduga saat proses training: {str(e)}")
        
    try:
        os.makedirs("models", exist_ok=True)
        
        model.fit(data=df, forgets=False)
        print("\nModel BKT berhasil dilatih pada seluruh data.")
        
        params = model.params()
        params.to_csv("models/bkt_tuned_parameters.csv")
        print("Parameter akhir berhasil disimpan di models/bkt_tuned_parameters.csv")
        
    except Exception as e:
        print(f"Gagal menyimpan model atau parameter: {str(e)}")

if __name__ == "__main__":
    run_bkt_tuning()
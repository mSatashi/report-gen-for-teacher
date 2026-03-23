import pandas as pd
import os
from typing import Dict, Any

class ExcelProcessor:
    ALLOWED_EXTENSIONS = {'.xlsx', '.xls', '.xlsm', '.xlsb'}

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
        self._validate_file_type()

    def _validate_file_type(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File tidak ditemukan: {self.file_path}")
            
        extension = os.path.splitext(self.file_path)[1].lower()
        if extension not in self.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Tipe file tidak didukung: {extension}. "
                f"Hanya menerima: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )

    def load_data(self):
        try:
            self.df = pd.read_excel(self.file_path)
        except Exception as e:
            raise TypeError(f"File rusak atau bukan format Excel yang valid: {str(e)}")

    def get_student_list(self) -> list:
        if self.df is None:
            self.load_data()
        
        cleaned_df = self.df.dropna(how='all')
        
        return cleaned_df.to_dict(orient="records")

    def get_summary(self) -> Dict[str, Any]:
        // placeholder untuk ngolah dari excel guna simpan secara tabel
        if self.df is None:
            self.load_data()
            
        return {
            "total_rows": len(self.df),
            "columns": list(self.df.columns),
            "data_preview": self.df.head(5).to_dict(orient="records")
        }
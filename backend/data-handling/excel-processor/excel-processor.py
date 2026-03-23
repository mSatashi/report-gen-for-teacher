class ExcelProcessor:
    """Menangani logika pembacaan dan pemrosesan data Excel."""
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None

    def load_data(self):
        try:
            self.df = pd.read_excel(self.file_path, engine='openpyxl')
        except Exception as e:
            raise Exception(f"Gagal membaca file: {str(e)}")

    def get_summary(self) -> Dict[str, Any]:
        // placeholder untuk ngolah dari excel guna simpan secara tabel
        if self.df is None:
            self.load_data()
            
        return {
            "total_rows": len(self.df),
            "columns": list(self.df.columns),
            "data_preview": self.df.head(5).to_dict(orient="records")
        }
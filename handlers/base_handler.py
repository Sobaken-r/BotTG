from abc import ABC, abstractmethod
import pandas as pd
import io

class BaseReportHandler(ABC):
    
    def __init__(self, file_bytes, filename):
        self.file_bytes = file_bytes
        self.filename = filename
        self.df = None
        self.errors = []
        
    def load_dataframe(self):
        try:
            self.df = pd.read_excel(io.BytesIO(self.file_bytes))
            return True
        except Exception as e:
            self.errors.append(f"Ошибка чтения файла: {str(e)}")
            return False
    
    @abstractmethod
    def process_report(self):
        pass
    
    def get_result(self):
        if not self.load_dataframe():
            return "\n".join(self.errors)
        
        result = self.process_report()
        
        if self.errors:
            result += "\n\nОшибки при обработке:\n" + "\n".join(self.errors)
        
        return result
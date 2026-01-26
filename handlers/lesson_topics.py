import pandas as pd
import re
from .base_handler import BaseReportHandler

class LessonTopicsHandler(BaseReportHandler):
    
    def process_report(self):
        try:
            topic_col = self._find_topic_column()
            
            if not topic_col:
                return self._show_all_columns()
            
            valid, invalid = self._check_topics(topic_col)
            return self._create_report(valid, invalid, topic_col)
            
        except Exception as e:
            return f"Ошибка: {str(e)}"
    
    def _find_topic_column(self):
        for col in self.df.columns:
            col_str = str(col).lower()
            if 'тема урока' in col_str or 'lesson topic' in col_str or 'тема занятия' in col_str:
                return col
        
        for col in self.df.columns:
            sample = self.df[col].dropna().head(3)
            for val in sample:
                if isinstance(val, str) and ('урок' in val.lower() or 'тема' in val.lower()):
                    return col
        
        return None
    
    def _show_all_columns(self):
        result = "Не найден столбец с темами\n\nСтолбцы:\n"
        for i, col in enumerate(self.df.columns, 1):
            result += f"{i}. {col}\n"
        return result
    
    def _check_topics(self, topic_col):
        valid = []
        invalid = []
        
        patterns = [
            r'^Урок\s*№?\s*\d+\.?\s*Тема:\s*.+$',
            r'^Lesson\s*№?\s*\d+\.?\s*Topic:\s*.+$',
        ]
        
        for idx, row in self.df.iterrows():
            topic = row[topic_col] if topic_col in row else None
            
            if pd.isna(topic) or str(topic).strip() == '':
                invalid.append({'index': idx+1, 'topic': '(пусто)'})
                continue
            
            topic_str = str(topic).strip()
            is_valid = False
            
            for pattern in patterns:
                if re.match(pattern, topic_str, re.IGNORECASE):
                    is_valid = True
                    break
            
            if is_valid:
                has_num = re.search(r'урок\s*№?\s*\d+', topic_str, re.IGNORECASE)
                has_topic = re.search(r'тема:\s*.+', topic_str, re.IGNORECASE)
                if has_num and has_topic:
                    valid.append({'index': idx+1, 'topic': topic_str})
                else:
                    invalid.append({'index': idx+1, 'topic': topic_str})
            else:
                invalid.append({'index': idx+1, 'topic': topic_str})
        
        return valid, invalid
    
    def _create_report(self, valid, invalid, topic_col):
        total = len(self.df)
        valid_count = len(valid)
        invalid_count = len(invalid)
        
        result = "ОТЧЕТ ПО ТЕМАМ ЗАНЯТИЙ\n"
        result += "Задание: найти всё, что НЕ соответствует формату 'Урок № X. Тема: Y'\n\n"
        
        result += "СТАТИСТИКА:\n"
        result += f"Всего записей: {total}\n"
        result += f"Соответствуют формату: {valid_count}\n"
        result += f"Не соответствуют формату: {invalid_count}\n"
        
        if total > 0:
            result += f"Процент несоответствующих: {(invalid_count/total*100):.1f}%\n"
        
        result += f"\nСтолбец с темами: {topic_col}\n\n"
        
        if valid_count > 0:
            result += f"ПРАВИЛЬНЫЕ (примеры {min(3, valid_count)} из {valid_count}):\n"
            for i, v in enumerate(valid[:3], 1):
                result += f"  {i}. {v['topic']}\n"
            result += "\n"
        
        if invalid_count > 0:
            result += f"НЕПРАВИЛЬНЫЕ (все {invalid_count} записей):\n\n"
            
            for i, inv in enumerate(invalid, 1):
                result += f"{i:3}. {inv['topic']}\n"
            
        else:
            result += "Все записи соответствуют формату!\n"
        
        result += "\nФормат должен быть: 'Урок № X. Тема: Название темы'"
        return result + "\n\nОтчет готов"
import pandas as pd
import re
from .base_handler import BaseReportHandler

class StudentsReportHandler(BaseReportHandler):#Отчет по студентам
    
    def process_report(self):
        try:
            column_info = self._identify_columns()
            
            if not all([column_info['fio'], column_info['homework'], column_info['classroom']]):
                return self._show_missing_columns(column_info)
            
            filtered_students = self._filter_students(column_info)
            
            result = self._create_report(filtered_students, column_info)
            
            return result
            
        except Exception as e:
            self.errors.append(f"Ошибка обработки: {str(e)}")
            return f"Ошибка при обработке файла студентов: {str(e)}"
    
    def _identify_columns(self):#Идентификация столбцов
        columns = {
            'fio': None,      
            'homework': None,    
            'classroom': None,   
            'group': None,       
            'stream': None,      
            'score': None       
        }
        for col in self.df.columns:
            col_str = str(col).strip()
            col_lower = col_str.lower()
            
            if any(name in col_lower for name in ['fio', 'фио', 'студент', 'имя', 'фамилия']):
                if not columns['fio']:
                    columns['fio'] = col
            
            elif any(name in col_lower for name in ['homework', 'домашняя работа', 'дз', 'домашнее задание']):
                if not columns['homework']:
                    columns['homework'] = col
            
            elif any(name in col_lower for name in ['classroom', 'классная работа', 'работа в классе']):
                if not columns['classroom']:
                    columns['classroom'] = col
            
            elif any(name in col_lower for name in ['group', 'группа']):
                if not columns['group']:
                    columns['group'] = col
            
            elif any(name in col_lower for name in ['stream', 'поток']):
                if not columns['stream']:
                    columns['stream'] = col
            
            elif any(name in col_lower for name in ['average score', 'средний балл', 'рейтинг']):
                if not columns['score']:
                    columns['score'] = col
        
        if not columns['fio'] and 'FIO' in self.df.columns:
            columns['fio'] = 'FIO'
        if not columns['homework'] and 'Homework' in self.df.columns:
            columns['homework'] = 'Homework'
        if not columns['classroom'] and 'Classroom' in self.df.columns:
            columns['classroom'] = 'Classroom'
        
        if not any(columns.values()):
            self.errors.append("Столбцы не найдены. Проверяю первую строку как заголовки...")
            self.df.columns = self.df.iloc[0]
            self.df = self.df[1:].reset_index(drop=True)
            return self._identify_columns() 
        
        return columns
    
    def _is_numeric_grade(self, value):
        try:
            if pd.isna(value):
                return False
            
            if isinstance(value, (int, float)):
                num = float(value)
            else:
                num = float(str(value).replace(',', '.').strip())
            
            return 0 <= num <= 10
        except:
            if isinstance(value, str):
                value = value.strip().lower()
                grade_mapping = {
                    'неудовлетворительно': 2,
                    'удовлетворительно': 3,
                    'хорошо': 4,
                    'отлично': 5,
                    'н/а': None,
                    'нет': None,
                    '-': None
                }
                return value in grade_mapping
            return False
    
    def _convert_to_numeric(self, value):
        if pd.isna(value):
            return None
        
        try:
            if isinstance(value, (int, float)):
                return float(value)
            
            value_str = str(value).strip().lower()
            
            grade_mapping = {
                'неудовлетворительно': 2,
                'удовлетворительно': 3,
                'хорошо': 4,
                'отлично': 5,
                'н/а': None,
                'нет': None,
                '-': None,
                'да': None,
                'нет': None
            }
            
            if value_str in grade_mapping:
                return grade_mapping[value_str]
            
            return float(value_str.replace(',', '.'))
        except:
            return None
    
    def _filter_students(self, column_info):#Фильтрация студентов
        filtered = []
        
        try:
            df = self.df.copy()
            
            hw_col = column_info['homework']
            cls_col = column_info['classroom']
            
            df['hw_numeric'] = df[hw_col].apply(self._convert_to_numeric)
            df['cls_numeric'] = df[cls_col].apply(self._convert_to_numeric) 
            
            condition = (df['hw_numeric'] <= 3) & (df['cls_numeric'] < 4)
            
            filtered_df = df[condition].copy()
            
            if column_info['fio']:
                filtered_df = filtered_df.sort_values(column_info['fio'])
            
            for _, row in filtered_df.iterrows():
                student_info = {
                    'fio': row[column_info['fio']] if pd.notna(row[column_info['fio']]) else "Не указано",
                    'homework_score': row['hw_numeric'],
                    'classroom_score': row['cls_numeric'],
                    'homework_original': row[hw_col],
                    'classroom_original': row[cls_col]
                }
                
                for field in ['group', 'stream', 'score']:
                    col = column_info[field]
                    if col and col in row:
                        student_info[field] = row[col]
                
                filtered.append(student_info)
        
        except Exception as e:
            self.errors.append(f"Ошибка фильтрации: {str(e)}")
            import traceback
            self.errors.append(traceback.format_exc())
        
        return filtered
    
    def _create_report(self, filtered_students, column_info):
        total_students = len(self.df)
        filtered_count = len(filtered_students)
        
        result = "ОТЧЕТ\n"
        
        result += "КРИТЕРИИ ПОИСКА:\n"
        result += "• Оценка за домашнюю работу ≤ 3\n"
        result += "• Оценка за классную работу < 4\n\n"
        
        result += "СТАТИСТИКА:\n"
        result += f"• Всего студентов в файле: {total_students}\n"
        result += f"• Найдено по критериям: {filtered_count}\n"
        
        if total_students > 0:
            percentage = (filtered_count / total_students) * 100
            result += f"• Процент от общего числа: {percentage:.1f}%\n"
        
        result += "\n"
        
        if filtered_students:
            result += "СПИСОК СТУДЕНТОВ С НИЗКОЙ УСПЕВАЕМОСТЬЮ:\n\n"
            
            for i, student in enumerate(filtered_students, 1):
                result += f"{i}. {student['fio']}\n"
                result += f"ДЗ: {student['homework_original']} ({student['homework_score']}) | "
                result += f"Классная: {student['classroom_original']} ({student['classroom_score']})\n"
                
                details = []
                if 'group' in student and pd.notna(student['group']):
                    details.append(f"Группа: {student['group']}")
                if 'stream' in student and pd.notna(student['stream']):
                    details.append(f"Поток: {student['stream']}")
                
                if details:
                    result += f" {', '.join(details)}\n"
                
                result += "\n"
        else:
            result += "Студентов с низкой успеваемостью не найдено.\n\n"
        
        result += "ИСПОЛЬЗОВАННЫЕ СТОЛБЦЫ:\n"
        result += f"• ФИО: {column_info['fio'] or 'Не найден'}\n"
        result += f"• Домашняя работа: {column_info['homework'] or 'Не найден'}\n"
        result += f"• Классная работа: {column_info['classroom'] or 'Не найден'}\n"
        
        if column_info['group']:
            result += f"• Группа: {column_info['group']}\n"
        if column_info['stream']:
            result += f"• Поток: {column_info['stream']}\n"
        
        result += "Отчет успешно сформирован!"
        
        return result
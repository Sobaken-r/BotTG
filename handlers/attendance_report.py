import pandas as pd
from .base_handler import BaseReportHandler

class AttendanceReportHandler(BaseReportHandler):#посещ по преподам
    
    def process_report(self):
        try:
            columns = self._identify_columns()
            
            if not columns['teacher']:
                return self._show_columns_info("Не найден столбец с ФИО преподавателей")
            
            if not columns['attendance']:
                return self._show_columns_info("Не найден столбец с посещаемостью")
            
            teachers = self._get_low_attendance_teachers(columns)
            return self._create_report(teachers, columns)
            
        except Exception as e:
            return f"Ошибка: {str(e)}"
    
    def _identify_columns(self):
        columns = {'teacher': None, 'attendance': None, 'total_pairs': None, 'total_groups': None}
        
        for col in self.df.columns:
            col_lower = str(col).lower()
            
            if 'фио преподавателя' in col_lower or 'преподаватель' in col_lower:
                columns['teacher'] = col
            elif 'посещаемость' in col_lower or 'attendance' in col_lower:
                columns['attendance'] = col
            elif 'всего пар' in col_lower or 'пары' in col_lower:
                columns['total_pairs'] = col
            elif 'всего групп' in col_lower or 'группы' in col_lower:
                columns['total_groups'] = col
        
        return columns
    
    def _convert_to_percentage(self, value):
        if pd.isna(value):
            return None
        
        try:
            value_str = str(value).replace('%', '').strip()
            percentage = float(value_str)
            return percentage if 0 <= percentage <= 100 else None
        except:
            return None
    
    def _get_low_attendance_teachers(self, columns):
        teachers = []
        df = self.df.copy()
        
        teacher_col = columns['teacher']
        attendance_col = columns['attendance']
        
        df = df[df[teacher_col].astype(str).str.lower() != 'всего']
        df = df[df[teacher_col].astype(str).str.strip() != '']
        df = df[df[teacher_col].notna()]
        
        df['attendance_num'] = df[attendance_col].apply(self._convert_to_percentage)
        
        mask = df['attendance_num'] < 40
        df_filtered = df[mask].copy()
        df_filtered = df_filtered.sort_values('attendance_num')
        
        for _, row in df_filtered.iterrows():
            teacher = {
                'name': row[teacher_col],
                'attendance': row['attendance_num'],
                'attendance_original': row[attendance_col]
            }
            
            if columns['total_pairs'] and pd.notna(row[columns['total_pairs']]):
                teacher['total_pairs'] = row[columns['total_pairs']]
            
            if columns['total_groups'] and pd.notna(row[columns['total_groups']]):
                teacher['total_groups'] = row[columns['total_groups']]
            
            teachers.append(teacher)
        
        return teachers
    
    def _show_columns_info(self, message):
        result = f"{message}\n\n"
        result += "Столбцы в файле:\n\n"
        
        for i, col in enumerate(self.df.columns, 1):
            sample = self.df[col].dropna().head(2).tolist()
            sample_str = ", ".join(str(x) for x in sample)
            if sample_str:
                result += f"{i}. {col} → [{sample_str}]\n"
        
        return result
    
    def _create_report(self, teachers, columns):
        total = len(self.df[self.df[columns['teacher']].notna()])
        count = len(teachers)
        
        result = "ОТЧЕТ ПО ПОСЕЩАЕМОСТИ\n"
        result += "🔍 КРИТЕРИИ:\n"
        result += "• Посещаемость ниже 40%\n\n"
        
        result += f"Всего преподавателей: {total}\n"
        result += f"С низкой посещаемостью: {count}\n"
        
        if total > 0:
            result += f"Процент: {(count/total*100):.1f}%\n"
        
        result += "\n"
        
        if count > 0:
            result += "ПРЕПОДАВАТЕЛИ С НИЗКОЙ ПОСЕЩАЕМОСТЬЮ:\n\n"
            
            critical = []
            low = []
            warning = []
            
            for t in teachers:
                if t['attendance'] <= 20:
                    critical.append(t)
                elif t['attendance'] <= 30:
                    low.append(t)
                else:
                    warning.append(t)
            
            if critical:
                result += "0-20%:\n"
                for t in critical:
                    result += f"• {t['name']}: {t['attendance']:.1f}%\n"
                result += "\n"
            
            if low:
                result += "21-30%:\n"
                for t in low:
                    result += f"• {t['name']}: {t['attendance']:.1f}%\n"
                result += "\n"
            
            if warning:
                result += "31-39%:\n"
                for t in warning:
                    result += f"• {t['name']}: {t['attendance']:.1f}%\n"
                result += "\n"
            
        else:
            result += "Преподавателей не найдено.\n\n"
        
        result += f"Столбец ФИО: {columns['teacher']}\n"
        result += f"Столбец посещаемости: {columns['attendance']}\n"
        result += "Отчет успешно сформирован!"
        
        return result
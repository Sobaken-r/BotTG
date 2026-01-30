import pandas as pd
import re
from .base_handler import BaseReportHandler

class ScheduleReportHandler(BaseReportHandler):#анализа расписания занятий
    def process_report(self):
        try:
            result = self._analyze_schedule()
            return result if result else "Нет данных"
        except:
            return "Ошибка обработки"
    
    def _analyze_schedule(self):
        lines = ["РАСПИСАНИЕ:"]
        
        day_cols = []
        for col in self.df.columns:
            col_str = str(col).lower()
            if any(day in col_str for day in ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота']):
                day_cols.append(col)
        
        for day_col in day_cols:
            day_name = str(day_col).split('.')[0].strip()
            lines.append(f"\n{day_name}:")
            
            subject_teachers = {}
            
            for _, row in self.df.iterrows():
                cell = row[day_col]
                if pd.isna(cell) or not str(cell).strip():
                    continue
                
                cell_str = str(cell)
                
                subject_match = re.search(r'Предмет:\s*([^<>\n]+)', cell_str, re.IGNORECASE) #группировки данных
                if subject_match:
                    subject = subject_match.group(1).strip()
                    
                    teacher = "Не указан"
                    for pattern in [r'Препод\.:\s*([^<>\n]+)', r'Преподаватель:\s*([^<>\n]+)']:
                        teacher_match = re.search(pattern, cell_str, re.IGNORECASE)
                        if teacher_match:
                            teacher = teacher_match.group(1).strip()
                            break
                    
                    if subject not in subject_teachers:
                        subject_teachers[subject] = {}
                    
                    subject_teachers[subject][teacher] = subject_teachers[subject].get(teacher, 0) + 1
            
            for subject, teachers in subject_teachers.items():
                total_pairs = sum(teachers.values())
                teachers_list = []
                for teacher, count in teachers.items():
                    teachers_list.append(f"{teacher}: {count}")
                
                lines.append(f"  {subject}: {total_pairs} пар")
                for teacher_info in teachers_list:
                    lines.append(f"    {teacher_info}")
        
        return "\n".join(lines) if len(lines) > 1 else None
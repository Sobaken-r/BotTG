import pandas as pd
import re

def clean_percentage(value):
    if pd.isna(value):
        return 0
    
    value_str = str(value)
    value_str = value_str.replace('%', '').strip()
    
    try:
        return float(value_str)
    except ValueError:
        return 0

def detect_column(df, possible_names, default_index=0):
    for name in possible_names:
        if name in df.columns:
            return name
    
    for col in df.columns:
        col_lower = str(col).lower()
        for name in possible_names:
            if name.lower() in col_lower:
                return col
    
    return df.columns[default_index] if len(df.columns) > default_index else None
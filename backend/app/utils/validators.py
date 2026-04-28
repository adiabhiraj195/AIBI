import re
from typing import List
from fastapi import HTTPException

class FileValidator:
    """File validation utilities"""
    
    @staticmethod
    def validate_filename(filename: str) -> bool:
        """Validate filename format"""
        if not filename:
            return False
        
        # Check for dangerous characters
        dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in filename for char in dangerous_chars):
            return False
        
        # Check filename length
        if len(filename) > 255:
            return False
        
        return True
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename by removing dangerous characters"""
        # Remove dangerous characters
        sanitized = re.sub(r'[^\w\-_\.]', '_', filename)
        
        # Ensure it doesn't start with a dot
        if sanitized.startswith('.'):
            sanitized = 'file_' + sanitized
        
        # Limit length
        if len(sanitized) > 255:
            name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
            max_name_length = 255 - len(ext) - 1 if ext else 255
            sanitized = name[:max_name_length] + ('.' + ext if ext else '')
        
        return sanitized

class CSVValidator:
    """CSV-specific validation utilities"""
    
    @staticmethod
    def validate_csv_structure(data: List[dict]) -> bool:
        """Validate CSV data structure"""
        if not data:
            return False
        
        # Check if all rows have the same keys (columns)
        if len(data) > 1:
            first_row_keys = set(data[0].keys())
            for row in data[1:]:
                if set(row.keys()) != first_row_keys:
                    return False
        
        return True
    
    @staticmethod
    def validate_column_names(columns: List[str]) -> List[str]:
        """Validate and sanitize column names"""
        sanitized_columns = []
        
        for col in columns:
            # Remove leading/trailing whitespace
            col = str(col).strip()
            
            # Replace spaces and special characters with underscores
            col = re.sub(r'[^\w]', '_', col)
            
            # Ensure it doesn't start with a number
            if col and col[0].isdigit():
                col = 'col_' + col
            
            # Ensure it's not empty
            if not col:
                col = 'unnamed_column'
            
            sanitized_columns.append(col)
        
        return sanitized_columns
from typing import Callable

class ValidationResult():
    def __init__(self, error_type: str, error_object:str, error_message:str, is_critical:bool, fix_func:Callable) -> None: 
        self.error_type:str = error_type
        self.error_object:str = error_object
        self.error_message:str = error_message
        self.is_critical:bool = is_critical
        self.fix_func:Callable = fix_func
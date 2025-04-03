import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Модуль: my_module
# Описание: Этот модуль содержит функции для работы с числами.

def add_numbers(num1, num2):
    """
    Функция для сложения двух чисел.
    
    Параметры:
    num1 (int, float): Первое число для сложения.
    num2 (int, float): Второе число для сложения.
    
    Возвращает:
    int, float: Результат сложения двух чисел.
    """
    return num1 + num2

def subtract_numbers(num1, num2):
    """
    Функция для вычитания двух чисел.
    
    Параметры:
    num1 (int, float): Первое число для вычитания.
    num2 (int, float): Второе число для вычитания.
    
    Возвращает:
    int, float: Результат вычитания двух чисел.
    """
    return num1 - num2

def multiply_numbers(num1, num2):
    """
    Функция для умножения двух чисел.
    
    Параметры:
    num1 (int, float): Первое число для умножения.
    num2 (int, float): Второе число для умножения.
    
    Возвращает:
    int, float: Результат умножения двух чисел.
    """
    return num1 * num2

def divide_numbers(num1, num2):
    """
    Функция для деления двух чисел.
    
    Параметры:
    num1 (int, float): Первое число для деления.
    num2 (int, float): Второе число для деления.
    
    Возвращает:
    int, float: Результат деления двух чисел.
    
    Исключения:
    ZeroDivisionError: Если num2 равно 0.
    """
    if num2 == 0:
        raise ZeroDivisionError("Деление на ноль невозможно.")
    return num1 / num2
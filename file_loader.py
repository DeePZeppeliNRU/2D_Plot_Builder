import numpy as np
from tkinter import messagebox
import re

def load_txt(file_path):
    """
    Загружает данные из текстового файла (TXT) и обрабатывает их.
    Возвращает массив numpy с данными.
    """
    try:
        time_pattern = r'\b(\d{2}:\d{2}:\d{2})\b'

        # Инициализация пустого суточного списка (1440 минут)
        daily_matrix = []
        for hour in range(24):
            for minute in range(60):
                time_str = f"{hour:02d}:{minute:02d}"  # Формат HH:MM
                daily_matrix.append([time_str, 0, []])  # [Время, количество событий, список временных меток]

        # Чтение входного файла
        with open(file_path, 'r', encoding='utf-8') as input_file:
            for line in input_file:
                if 'Продавец' in line or 'Бот' in line:
                    match = re.search(time_pattern, line)
                    if match:
                        event_time = match.group().strip()  # Полное время, например, "13:37:20"
                        hour_minute = event_time[:5]  # Берем только часы и минуты, например, "13:37"

                        # Проверка корректности времени
                        try:
                            hour = int(hour_minute[:2])
                            minute = int(hour_minute[3:5])
                            if 0 <= hour < 24 and 0 <= minute < 60:
                                index = hour * 60 + minute
                                daily_matrix[index][1] += 1  # Увеличиваем счётчик событий
                                daily_matrix[index][2].append(event_time)  # Добавляем временную метку
                        except ValueError:
                            print(f"Некорректное время: {hour_minute}")

        # Преобразование daily_matrix в numpy массив
        data = np.array(daily_matrix, dtype=object)
        messagebox.showinfo("Успех", "TXT файл успешно загружен и обработан!")
        return data

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить или обработать TXT файл: {e}")
        return None

def load_bin(file_path):
    """
    Загружает данные из бинарного файла (BIN).
    Возвращает массив numpy с данными в формате [время, количество, список событий].
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()  # Читаем все строки
        
        # Преобразуем строки в список
        daily_matrix = []
        for line in lines:
            parts = line.strip().split(", ")  # Разбиваем по ", "
            time_str = parts[0]              # Время, например "00:00"
            count = int(parts[1])            # Количество, например 0
            events = parts[2:] if count > 0 else []  # События или пустой список
            daily_matrix.append([time_str, count, events])
        
        # Преобразуем в numpy массив
        data = np.array(daily_matrix, dtype=object)
        messagebox.showinfo("Успех", "BIN файл успешно загружен!")
        return data
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить BIN файл: {e}")
        return None
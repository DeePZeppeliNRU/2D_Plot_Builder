import os
import numpy as np
from matplotlib.figure import Figure

def save_bin(data, base_name):
    """
    Сохраняет данные в файл .bin в папке OUTdoor.
    Args:
        data: NumPy массив с данными.
        base_name: Базовое имя файла (без пути и расширения).
    Returns:
        tuple: (успех, сообщение).
    """
    if data is None:
        return (False, "Данные не загружены!")
    
    script_folder = os.path.dirname(os.path.abspath(__file__))  # Папка скрипта
    output_folder = os.path.join(script_folder, 'OUTdoor')      # Папка OUTdoor
    os.makedirs(output_folder, exist_ok=True)                   # Создаём, если нет
    
    output_file_name = f"{base_name}_out.bin"
    output_file_path = os.path.join(output_folder, output_file_name)
    
    if os.path.exists(output_file_path):
        return (False, f"Файл {output_file_path} уже существует! Используйте другой путь.")
    
    try:
        with open(output_file_path, 'w', encoding='utf-8') as file:
            for line in data:
                time_str = str(line[0])
                count = str(line[1])
                events = line[2]
                events_str = ", ".join(events) if events else "0"
                output_line = f"{time_str}, {count}, {events_str}\n"
                file.write(output_line)
        return (True, f"Данные сохранены в {output_file_path}")
    except Exception as e:
        return (False, f"Не удалось сохранить файл: {e}")

def save_png(fig, base_name, dpi):
    """
    Сохраняет график в файл PNG в папке Save_plots.
    Args:
        fig: Объект Figure из Matplotlib.
        base_name: Базовое имя файла (без пути и расширения).
        dpi: Разрешение в dpi.
    Returns:
        tuple: (успех, сообщение).
    """
    if fig is None:
        return (False, "График не создан!")
    
    script_folder = os.path.dirname(os.path.abspath(__file__))  # Папка скрипта
    output_folder = os.path.join(script_folder, 'Save_plots')   # Папка Save_plots
    os.makedirs(output_folder, exist_ok=True)                   # Создаём, если нет
    
    output_file_name = f"{base_name}_plot{dpi}.png"
    output_file_path = os.path.join(output_folder, output_file_name)
    
    if os.path.exists(output_file_path):
        return (False, f"Файл {output_file_path} уже существует! Используйте другой путь.")
    
    try:
        fig.savefig(output_file_path, dpi=dpi)
        return (True, f"График сохранён в {output_file_path} с разрешением {dpi}dpi")
    except Exception as e:
        return (False, f"Не удалось сохранить график: {e}")
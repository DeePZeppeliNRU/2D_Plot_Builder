import tkinter as tk
from tkinter import messagebox, filedialog, Menu
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import os
import webbrowser
import file_loader
import file_saver
import plot_builder
import stats_processor

# Глобальные переменные для хранения данных
data = None
input_file_path = None
is_bin_loaded = False
is_graph_plotted = False  # Флаг для отслеживания построения графика

# Функции из твоего кода
def plot_graph():
    global data, is_graph_plotted
    if data is None:
        messagebox.showwarning("Ошибка", "Данные не загружены!")
        return
    
    plot_data = {
        'hours': [],
        'minutes': [],
        'z_values': [],
        'sales_times': []
    }
    for row in data:
        if row[1] > 0:
            plot_data['hours'].append(int(row[0].split(':')[0]))
            plot_data['minutes'].append(int(row[0].split(':')[1]))
            plot_data['z_values'].append(row[1])
            plot_data['sales_times'].append(row[2])
    
    plot_builder.plot_graph(plot_data, ax)
    canvas.draw()
    is_graph_plotted = True
    if not is_bin_loaded:
        calc_stats_button.config(state=tk.NORMAL)
        show_stats_button.config(state=tk.NORMAL)

def save_bin():
    global data, input_file_path
    if data is None:
        messagebox.showwarning("Ошибка", "Данные не загружены!")
        return
    base_name = os.path.splitext(os.path.basename(input_file_path))[0] if input_file_path else "output"
    success, message = file_saver.save_bin(data, base_name)
    if success:
        messagebox.showinfo("Успех", message)
    else:
        messagebox.showerror("Ошибка", message)

def save_png(resolution):
    global data, input_file_path
    if data is None:
        messagebox.showwarning("Ошибка", "Данные не загружены!")
        return
    base_name = os.path.splitext(os.path.basename(input_file_path))[0] if input_file_path else "output"
    success, message = file_saver.save_png(fig, base_name, resolution)
    if success:
        messagebox.showinfo("Успех", message)
    else:
        messagebox.showerror("Ошибка", message)

def clear_data():
    global data, input_file_path, is_bin_loaded, is_graph_plotted
    data = None
    input_file_path = None
    is_bin_loaded = False
    is_graph_plotted = False
    ax.clear()
    canvas.draw()
    plot_button.config(state=tk.DISABLED)
    save_button.config(state=tk.DISABLED)
    clear_button.config(state=tk.DISABLED)
    calc_stats_button.config(state=tk.DISABLED)
    show_stats_button.config(state=tk.DISABLED)
    save_menu.entryconfig("Сохранить как BIN", state=tk.NORMAL)
    status_label.config(text="     Данные не загружены")

def exit_program():
    root.destroy()

def show_about():
    about_text = """
2D Builder v 2.1.RC4.b
   Автор: DeeP ZeppeliN

   Краткое описание:
Программа позволяет загружать сохранения
созданные в программе Monitoring_RC4.
На основе загруженных текстовых данных строит
интерактивные 2D графики и умеет сохранять их
в различных форматах.
          Подробнее см. раздел Справка.
"""
    messagebox.showinfo("О программе", about_text)

def show_help():
    help_dir = "Help"
    help_file_path = os.path.join(help_dir, "Index.html")
    if os.path.exists(help_file_path):
        try:
            url = f"file://{os.path.abspath(help_file_path)}"
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть справку: {e}")
    else:
        messagebox.showerror("Ошибка", "Файл справки (Index.html) не найден в папке Help!")

def load_txt():
    global data, input_file_path, is_bin_loaded, is_graph_plotted
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        data = file_loader.load_txt(file_path)
        if data is not None:
            input_file_path = file_path
            is_bin_loaded = False
            is_graph_plotted = False
            plot_button.config(state=tk.NORMAL)
            save_button.config(state=tk.NORMAL)
            clear_button.config(state=tk.NORMAL)
            calc_stats_button.config(state=tk.DISABLED)
            show_stats_button.config(state=tk.DISABLED)
            save_menu.entryconfig("Сохранить как BIN", state=tk.NORMAL)
            status_label.config(text=f"     Загружен файл: {os.path.basename(file_path)}")
        else:
            status_label.config(text="Ошибка загрузки")

def load_bin():
    global data, input_file_path, is_bin_loaded, is_graph_plotted
    file_path = filedialog.askopenfilename(filetypes=[("Binary files", "*.bin")])
    if file_path:
        data = file_loader.load_bin(file_path)
        if data is not None:
            input_file_path = file_path
            is_bin_loaded = True
            is_graph_plotted = False
            plot_button.config(state=tk.NORMAL)
            save_button.config(state=tk.NORMAL)
            clear_button.config(state=tk.NORMAL)
            calc_stats_button.config(state=tk.DISABLED)
            show_stats_button.config(state=tk.DISABLED)
            save_menu.entryconfig("Сохранить как BIN", state=tk.DISABLED)
            status_label.config(text=f"     Загружен файл: {os.path.basename(file_path)}")
        else:
            status_label.config(text="Ошибка загрузки")

# Новые функции для кнопок
def calculate_stats():
    global input_file_path
    if not input_file_path:
        messagebox.showerror("Ошибка", "Сначала загрузите TXT-файл и постройте график!")
        return
    sales_data = stats_processor.parse_sales(input_file_path)
    if sales_data:
        stats_processor.write_stats_to_file(sales_data, input_file_path)
        messagebox.showinfo("Успех", "Статистика сохранена в Statistics/")

def show_stats():
    global input_file_path
    if not input_file_path:
        messagebox.showerror("Ошибка", "Сначала загрузите TXT-файл!")
        return
    
    # Формируем путь к файлу статистики на основе загруженного лога
    base_name = os.path.splitext(os.path.basename(input_file_path))[0]
    file_path = os.path.join("Statistics", f"{base_name}_stats.txt")
    
    print(f"Попытка открыть файл: {os.path.abspath(file_path)}")  # Отладка
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            stats_text = f.read()
        stats_window = tk.Toplevel(root)
        stats_window.title("Статистика по TXT файлу")
        stats_window.geometry("800x600")  # Начальный размер окна
        
        text_frame = tk.Frame(stats_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD)
        text_widget.insert(tk.END, stats_text)
        text_widget.config(state=tk.DISABLED)
        
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        stats_window.grid_rowconfigure(0, weight=1)
        stats_window.grid_columnconfigure(0, weight=1)
    except FileNotFoundError:
        messagebox.showerror("Ошибка", f"Файл {file_path} не найден! Сначала обработайте статистику для TXT файла!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть файл {file_path}: {str(e)}")

# Создание окна Tkinter
root = tk.Tk()
root.title("2D Builder v 2.1.RC4.b")

# Создание фигуры Matplotlib
fig = Figure(figsize=(13, 6), dpi=100)
ax = fig.add_subplot(111)

# Встраиваем Matplotlib в Tkinter
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

# Создание фрейма для кнопок
button_frame = tk.Frame(root)
button_frame.pack(side=tk.BOTTOM, fill=tk.X)

# Кнопка "Загрузить файл" с выпадающим меню
load_button = tk.Menubutton(button_frame, text="Загрузить файл", relief=tk.RAISED)
load_button.pack(side=tk.LEFT, padx=5, pady=5)
load_menu = tk.Menu(load_button, tearoff=0)
load_button.config(menu=load_menu)
load_menu.add_command(label="Загрузить файл TXT", command=load_txt)
load_menu.add_command(label="Загрузить файл BIN", command=load_bin)

# Кнопка "Построить график"
plot_button = tk.Button(button_frame, text="Построить график", command=plot_graph, state=tk.DISABLED)
plot_button.pack(side=tk.LEFT, padx=5, pady=5)

# Кнопка "Сохранить график" с выпадающим меню
save_button = tk.Menubutton(button_frame, text="Сохранить файл", relief=tk.RAISED, state=tk.DISABLED)
save_button.pack(side=tk.LEFT, padx=5, pady=5)
save_menu = tk.Menu(save_button, tearoff=0)
save_button.config(menu=save_menu)
png_submenu = tk.Menu(save_menu, tearoff=0)
png_submenu.add_command(label="Сохранить в SD разрешении", command=lambda: save_png(65))
png_submenu.add_command(label="Сохранить в HD разрешении", command=lambda: save_png(90))
png_submenu.add_command(label="Сохранить в FHD разрешении", command=lambda: save_png(140))
save_menu.add_cascade(label="Сохранить как PNG", menu=png_submenu)
save_menu.add_command(label="Сохранить как BIN", command=save_bin)

# Кнопка "Очистить данные"
clear_button = tk.Button(button_frame, text="Очистить данные", command=clear_data, state=tk.DISABLED)
clear_button.pack(side=tk.LEFT, padx=5, pady=5)

# Новые кнопки для статистики
calc_stats_button = tk.Button(button_frame, text="Обработать статистику для TXT файла", command=calculate_stats, state=tk.DISABLED)
calc_stats_button.pack(side=tk.LEFT, padx=5, pady=5)
show_stats_button = tk.Button(button_frame, text="Показать статистику по TXT файлу", command=show_stats, state=tk.DISABLED)
show_stats_button.pack(side=tk.LEFT, padx=5, pady=5)

# Кнопка "Закончить работу"
exit_button = tk.Button(button_frame, text="Закончить работу", command=exit_program)
exit_button.pack(side=tk.LEFT, padx=5, pady=5)

# Кнопка "Help" с выпадающим меню
help_button = tk.Menubutton(button_frame, text="Help", relief=tk.RAISED)
help_button.pack(side=tk.RIGHT, padx=5, pady=5)
help_menu = tk.Menu(help_button, tearoff=0)
help_button.config(menu=help_menu)
help_menu.add_command(label="О программе", command=show_about)
help_menu.add_command(label="Справка", command=show_help)

# Статусная строка
status_label = tk.Label(root, text="     Данные не загружены", anchor="w", relief=tk.SUNKEN,
                        borderwidth=1, height=2, bg="#F0F0F0", fg="black")
status_label.pack(side=tk.BOTTOM, fill=tk.X)

# Запуск основного цикла Tkinter
root.mainloop()
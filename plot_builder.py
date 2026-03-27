import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

def plot_graph(data, ax):
    # Очищаем текущие оси перед построением нового графика, чтобы избежать наложения
    ax.clear()
    # Закомментировано отладочное сообщение: выводилось для подтверждения очистки осей
    # print("Axes cleared")  # Отладка: показывает, что оси очищены перед построением

    # Преобразуем данные из словаря в массивы numpy для удобной работы
    hours = np.array(data['hours'])      # Часы (0–23)
    minutes = np.array(data['minutes'])  # Минуты (0–59)
    z_values = np.array(data['z_values']) # Значения для цветовой шкалы (количество продаж)
    sales_times = data['sales_times']    # Список точных времён продаж для каждой точки
    # Закомментировано отладочное сообщение: показывало количество точек и сами данные
    # print(f"New data loaded: {len(hours)} points")  # Отладка: сколько точек загружено
    # print(f"Data received: {list(zip(hours, minutes, z_values))")  # Отладка: список точек (часы, минуты, значения)

    # Настраиваем цветовую шкалу: минимальное значение 1, максимальное — максимум из z_values
    vmin = 1  # Точки с z < 1 будут белыми (цвет фона)
    vmax = np.max(z_values) if len(z_values) > 0 else 1  # Если данных нет, vmax = 1
    norm = Normalize(vmin=vmin, vmax=vmax)  # Нормализация значений для цветовой шкалы
    cmap = plt.get_cmap('viridis')  # Используем цветовую карту "viridis"
    cmap.set_under('white')  # Значения ниже vmin (z < 1) отображаются белым

    # Рисуем точечный график: минуты по X, часы по Y, цвет зависит от z_values
    sc = ax.scatter(minutes, hours, c=z_values, cmap=cmap, norm=norm, marker='s', s=55)
    # marker='s' — квадратные маркеры, s=55 — размер маркеров в пикселях

    # Настраиваем подписи осей и заголовок графика
    ax.set_xlabel('Минуты')  # Подпись оси X
    ax.set_ylabel('Часы')    # Подпись оси Y
    ax.set_title('ГРАФИК ПРОДАЖ')  # Заголовок графика
    ax.grid(True)  # Включаем сетку с шагом, заданным тиками

    # Задаём тики для осей: шаг 1, но подписи только через определённые интервалы
    ax.set_xticks(np.arange(0, 60, 1))  # Тики минут: 0, 1, ..., 59
    ax.set_xticklabels(['{}'.format(i) if i % 5 == 0 else '' for i in range(0, 60, 1)])  # Подписи каждые 5 минут
    ax.set_yticks(np.arange(0, 24, 1))  # Тики часов: 0, 1, ..., 23
    ax.set_yticklabels(['{}'.format(i) if i % 2 == 0 else '' for i in range(0, 24, 1)])  # Подписи каждые 2 часа

    # Фиксируем масштаб осей с отступами для одинакового вида всех графиков
    ax.set_xlim(-2.5, 61.5)  # Минуты: от -1 до 60 (отступ 1 единица слева и справа от 0–59)
    ax.set_ylim(-1.5, 24.5)  # Часы: от -1 до 24 (отступ 1 единица снизу и сверху от 0–23)

    # Удаляем старую цветовую шкалу, если она есть, чтобы избежать наложения
    if hasattr(ax, 'cbar'):
        try:
            ax.cbar.remove()  # Удаляем предыдущую шкалу
        except AttributeError:
            pass  # Игнорируем ошибку, если удаление не удалось
    # Создаём новую цветовую шкалу справа от графика
    cb_ax = ax.figure.add_axes([0.91, 0.1, 0.015, 0.8])  # Позиция: [left, bottom, width, height]
    ax.cbar = ax.figure.colorbar(sc, cax=cb_ax)  # Привязываем шкалу к графику
    ax.cbar.set_label('Количество продаж', rotation=90, labelpad=15)  # Подпись шкалы, повёрнутая на 90°

    # Инициализируем атрибуты для работы с аннотациями
    setattr(ax, 'annotation', None)  # Текущая аннотация (изначально отсутствует)
    setattr(ax, 'current_idx', None) # Индекс выбранной точки (изначально не выбрано)
    setattr(ax, 'start_idx', 0)     # Начальный индекс для прокрутки списка продаж
    # Отключаем старый обработчик кликов, если он был, чтобы избежать дублирования
    if hasattr(ax, 'click_handler'):
        ax.figure.canvas.mpl_disconnect(ax.click_handler)

    # Функция обновления аннотации для выбранной точки
    def update_annotation(idx):
        # Если аннотация уже существует, удаляем её перед созданием новой
        if ax.annotation:
            ax.annotation.remove()
        
        # Получаем список точных времён продаж для выбранной точки
        sales = sales_times[idx]
        total_sales = len(sales)  # Общее количество продаж для точки
        end_idx = min(ax.start_idx + 10, total_sales)  # Ограничиваем список до 10 видимых строк
        visible_sales = sales[ax.start_idx:end_idx]  # Видимая часть списка
        
        # Формируем текст аннотации
        annotation_text = f"Вы выбрали время{' ' * 9}[X]\n  {hours[idx]:02d}:{minutes[idx]:02d}\nТочное время продаж:\n"
        # Добавляем видимые времена продаж, дополняем пустыми строками до 10
        annotation_text += "\n".join([f"  {value}" for value in visible_sales] + ["  "] * (10 - len(visible_sales)))
        # Добавляем строку прокрутки, если продаж больше 10
        if total_sales <= 10:
            scroll_text = " " * 23  # Пустая строка, если прокрутка не нужна
        else:
            up_arrow = "[↑]" if ax.start_idx > 0 else "   "  # Стрелка вверх, если можно прокрутить
            down_arrow = "[↓]" if ax.start_idx + 10 < total_sales else "   "  # Стрелка вниз, если можно прокрутить
            scroll_text = f" {up_arrow} прокрутка списка {down_arrow}"
        annotation_text += "\n" + scroll_text
        
        # Позиция текста аннотации: справа от точки, если минуты <= 20, иначе слева
        x_text = minutes[idx] + (5 if minutes[idx] <= 20 else -22)
        y_text = 22  # Фиксированная высота текста (вверху графика)
        
        # Создаём аннотацию с указанными параметрами
        ax.annotation = ax.annotate(annotation_text, 
                                    xy=(minutes[idx], hours[idx]),  # Точка привязки (координаты маркера)
                                    xytext=(x_text, y_text),  # Позиция текста
                                    xycoords='data', textcoords='data',  # Координаты в данных
                                    ha='left', va='top',  # Выравнивание: слева, сверху
                                    bbox=dict(boxstyle="round,pad=0.5", fc="#F0F0F0", alpha=0.94, ec="black", lw=1),  # Рамка
                                    arrowprops=dict(arrowstyle="->"),  # Стрелка от текста к точке
                                    fontfamily='monospace', fontsize=12)  # Шрифт и размер
        
        ax.current_idx = idx  # Сохраняем индекс текущей точки
        ax.figure.canvas.draw()  # Перерисовываем график с новой аннотацией

    # Функция обработки клика мыши
    def onclick(event):
        # Закомментировано отладочное сообщение: показывало координаты клика в пикселях
        # print(f"onclick triggered at pixel coords: ({event.x}, {event.y})", end="")
        # Проверяем, был ли клик внутри осей графика
        if event.inaxes != ax:
            # Закомментировано отладочное сообщение: подтверждало клик вне осей
            # print(", outside axes")  # Отладка: клик вне графика
            return
        
        # Закомментировано отладочное сообщение: показывало координаты клика в данных
        # print(f", data coords: x={event.xdata:.2f}, y={event.ydata:.2f}")  # Отладка: координаты в системе данных
        # Закомментировано отладочное сообщение: показывало текущие точки графика
        # print(f"Current data points: {list(zip(hours, minutes, z_values))")  # Отладка: список точек
        
        # Если аннотация уже есть, проверяем, кликнули ли на неё
        if ax.annotation and ax.current_idx is not None and ax.current_idx < len(sales_times):
            bbox = ax.annotation.get_bbox_patch().get_extents()  # Границы рамки аннотации
            if bbox.contains(event.x, event.y):  # Клик внутри аннотации
                x, y = event.xdata, event.ydata  # Координаты клика в данных
                bbox_data = bbox.transformed(ax.transData.inverted())  # Преобразуем пиксели в данные
                bbox_height = bbox_data.y1 - bbox_data.y0  # Высота рамки
                
                # Разделяем рамку на зоны: закрытие (вверху) и прокрутка (внизу)
                line_height = bbox_height / 14  # Примерная высота одной строки
                close_y_top = bbox_data.y1  # Верхняя граница зоны закрытия
                close_y_bottom = bbox_data.y1 - line_height  # Нижняя граница зоны закрытия
                scroll_y_bottom = bbox_data.y0  # Нижняя граница зоны прокрутки
                scroll_y_top = bbox_data.y0 + line_height  # Верхняя граница зоны прокрутки
                scroll_x_mid = bbox_data.x0 + (bbox_data.x1 - bbox_data.x0) / 2  # Середина по X для прокрутки
                
                # Если клик в зоне закрытия ([X]), убираем аннотацию
                if close_y_bottom <= y <= close_y_top and bbox_data.x0 <= x <= bbox_data.x1:
                    # Закомментировано отладочное сообщение: подтверждало закрытие аннотации
                    # print("Closing annotation")  # Отладка: аннотация закрывается
                    ax.annotation.remove()
                    ax.annotation = None
                    ax.current_idx = None
                    ax.start_idx = 0
                    ax.figure.canvas.draw()
                    return
                
                # Если клик в зоне прокрутки и продаж больше 10, обрабатываем прокрутку
                sales = sales_times[ax.current_idx]
                total_sales = len(sales)
                if total_sales > 10 and scroll_y_bottom <= y <= scroll_y_top:
                    if bbox_data.x0 <= x <= scroll_x_mid and ax.start_idx > 0:
                        ax.start_idx -= 1  # Прокрутка вверх
                        # Закомментировано отладочное сообщение: показывало прокрутку вверх
                        # print(f"Scrolling up, new start_idx={ax.start_idx}")  # Отладка: прокрутка вверх
                        update_annotation(ax.current_idx)
                    elif scroll_x_mid < x <= bbox_data.x1 and ax.start_idx + 10 < total_sales:
                        ax.start_idx += 1  # Прокрутка вниз
                        # Закомментировано отладочное сообщение: показывало прокрутку вниз
                        # print(f"Scrolling down, new start_idx={ax.start_idx}")  # Отладка: прокрутка вниз
                        update_annotation(ax.current_idx)
                    return
            return
        
        # Если аннотации нет, ищем ближайшую точку для отображения аннотации
        distances = np.hypot(event.xdata - minutes, event.ydata - hours)  # Расстояния до всех точек
        idx = np.argmin(distances)  # Индекс ближайшей точки
        tolerance = 2.0  # Допустимое расстояние для выбора точки
        # Закомментировано отладочное сообщение: показывало расстояние и значение точки
        # print(f"Distance to nearest point: {distances[idx]:.2f}, z_value: {z_values[idx]}")  # Отладка: расстояние до точки
        # Проверяем, попадает ли клик в допустимый радиус и есть ли продажи (z >= 1)
        if distances[idx] > tolerance or z_values[idx] < 1:
            # Закомментировано отладочное сообщение: подтверждало отсутствие подходящей точки
            # print("No valid data point at this location")  # Отладка: точка не выбрана
            return
        
        # Сбрасываем прокрутку и создаём аннотацию для выбранной точки
        ax.start_idx = 0
        update_annotation(idx)

    # Подключаем обработчик кликов к графику
    ax.click_handler = ax.figure.canvas.mpl_connect('button_press_event', onclick)
    # Закомментировано отладочное сообщение: подтверждало подключение обработчика
    # print("New onclick handler connected")  # Отладка: обработчик кликов подключён
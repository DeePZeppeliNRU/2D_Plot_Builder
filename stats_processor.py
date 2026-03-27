import configparser
import re
from datetime import datetime
import os

# Путь к папке Base (для конфигов)
BASE_DIR = "Base"
# Путь к папке Statistics (для результатов)
STATS_DIR = "Statistics"

# Чтение конфига
config = configparser.ConfigParser()
config_path = os.path.join(BASE_DIR, 'genders.ini')
if not config.read(config_path, encoding='utf-8'):
    raise Exception(f"Ошибка: файл '{config_path}' не найден или пустой!")

if 'Genders' not in config or 'TimePeriods' not in config:
    raise Exception("Ошибка: секции 'Genders' или 'TimePeriods' не найдены в 'genders.ini'!")

male_names = set(name.strip().lower() for name in config['Genders']['male'].split(',') if name.strip())
female_names = set(name.strip().lower() for name in config['Genders']['female'].split(',') if name.strip())
unknown_names = set(name.strip().lower() for name in config['Genders'].get('unknown', 'Аноним').split(',') if name.strip())

time_periods = {}
for period, range_str in config['TimePeriods'].items():
    start, end = range_str.split('-')
    start_hour, start_min = map(int, start.split(':'))
    end_hour, end_min = map(int, end.split(':'))
    time_periods[period] = {'start': start_hour * 60 + start_min, 'end': end_hour * 60 + end_min}

def get_time_of_day(time_str):
    try:
        if "UTC" in time_str:
            time_obj = datetime.strptime(time_str, '%H:%M:%S UTC')
        else:
            time_obj = datetime.strptime(time_str, '%H:%M:%S')
    except ValueError:
        return 'unknown'
    
    time_minutes = time_obj.hour * 60 + time_obj.minute
    for period, limits in time_periods.items():
        if limits['start'] <= time_minutes <= limits['end']:
            return period
    return 'unknown'

def parse_sales(file_path):
    seller_male = {'morning': [], 'day': [], 'evening': [], 'night': []}
    seller_female = {'morning': [], 'day': [], 'evening': [], 'night': []}
    seller_unknown = {'morning': [], 'day': [], 'evening': [], 'night': []}
    seller_anonymous = {'morning': [], 'day': [], 'evening': [], 'night': []}
    bot_male = {'morning': [], 'day': [], 'evening': [], 'night': []}
    bot_female = {'morning': [], 'day': [], 'evening': [], 'night': []}
    bot_unknown = {'morning': [], 'day': [], 'evening': [], 'night': []}
    bot_anonymous = {'morning': [], 'day': [], 'evening': [], 'night': []}
    male_names_count = {}
    female_names_count = {}
    unknown_names_log = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        
        # ============================================
        # ВАРИАНТ 1: НОВЫЙ формат (Время перед Затратами) — ТЕКУЩИЙ
        # Формат: Лот 1 - Вадим - Продавец. - Время продажи: 10:57:31 - Затраты 0 руб.
        pattern = r'Лот \d+ - (.+?) - (Продавец|Бот)\. - Затраты \d+ руб - Время продажи: (\d{2}:\d{2}:\d{2}(?: UTC)?)'
        
        # ВАРИАНТ 2: СТАРЫЙ формат (Затраты перед Временем)
        # Формат: Лот 7 - Дмитрий - Продавец. - Затраты 0 руб - Время продажи: 00:00:33.
        # pattern = r'Лот \d+ - (.+?) - (Продавец|Бот)\. - Затраты \d+ руб - Время продажи: (\d{2}:\d{2}:\d{2}(?: UTC)?)'
        # ============================================
        
        matches = re.findall(pattern, text)
        total_lines = len(matches)
        
        if total_lines > 0:
            for name, entity_type, sale_time in matches:
                original_name = name
                name = name.strip().lower()
                time_of_day = get_time_of_day(sale_time)
                if time_of_day == 'unknown':
                    continue
                
                if not name or name in unknown_names or name == "анонимный продавец":
                    display_name = "Аноним"
                    predicted_gender = "anonymous"
                elif name in male_names:
                    display_name = original_name
                    predicted_gender = "male"
                    male_names_count[display_name] = male_names_count.get(display_name, 0) + 1
                elif name in female_names:
                    display_name = original_name
                    predicted_gender = "female"
                    female_names_count[display_name] = female_names_count.get(display_name, 0) + 1
                else:
                    display_name = original_name
                    predicted_gender = "unknown"
                    unknown_names_log.add(original_name)
                
                entry = f"{display_name} (время: {sale_time})"
                if entity_type == "Продавец":
                    if predicted_gender == "male":
                        seller_male[time_of_day].append(entry)
                    elif predicted_gender == "female":
                        seller_female[time_of_day].append(entry)
                    elif predicted_gender == "unknown":
                        seller_unknown[time_of_day].append(entry)
                    elif predicted_gender == "anonymous":
                        seller_anonymous[time_of_day].append(entry)
                elif entity_type == "Бот":
                    if predicted_gender == "male":
                        bot_male[time_of_day].append(entry)
                    elif predicted_gender == "female":
                        bot_female[time_of_day].append(entry)
                    elif predicted_gender == "unknown":
                        bot_unknown[time_of_day].append(entry)
                    elif predicted_gender == "anonymous":
                        bot_anonymous[time_of_day].append(entry)
        
        if unknown_names_log:
            with open(os.path.join(BASE_DIR, 'unknown_names.txt'), 'a', encoding='utf-8') as unknown_f:
                for name in sorted(unknown_names_log):
                    unknown_f.write(f"{name}\n")
        
        return {
            "seller_male": seller_male, "seller_female": seller_female,
            "seller_unknown": seller_unknown, "seller_anonymous": seller_anonymous,
            "bot_male": bot_male, "bot_female": bot_female,
            "bot_unknown": bot_unknown, "bot_anonymous": bot_anonymous,
            "male_names_count": male_names_count, "female_names_count": female_names_count
        }
    except Exception as e:
        print(f"Ошибка при обработке файла {file_path}: {e}")
        return None

def write_stats_to_file(sales_data, input_file_path=None):
    # Создаём папку Statistics, если нет
    os.makedirs(STATS_DIR, exist_ok=True)
    
    # Формируем имя файла на основе входного
    if input_file_path:
        base_name = os.path.splitext(os.path.basename(input_file_path))[0]
        output_file = os.path.join(STATS_DIR, f"{base_name}_stats.txt")
    else:
        output_file = os.path.join(STATS_DIR, "sales_gender_stats.txt")  # фоллбэк
    
    print(f"Сохранение статистики в: {os.path.abspath(output_file)}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for period in ['morning', 'day', 'evening', 'night']:
            f.write(f"{period.capitalize()}: "
                    f"Продавцов мужчин {len(sales_data['seller_male'][period])}, "
                    f"Продавцов женщин {len(sales_data['seller_female'][period])}, "
                    f"Мужчин ботов {len(sales_data['bot_male'][period])}, "
                    f"Женщин ботов {len(sales_data['bot_female'][period])}, "
                    f"Анонимных продавцов {len(sales_data['seller_anonymous'][period])}, "
                    f"Анонимных ботов {len(sales_data['bot_anonymous'][period])}\n")
        
        total_seller_male = sum(len(sales_data['seller_male'][p]) for p in ['morning', 'day', 'evening', 'night'])
        total_seller_female = sum(len(sales_data['seller_female'][p]) for p in ['morning', 'day', 'evening', 'night'])
        total_bot_male = sum(len(sales_data['bot_male'][p]) for p in ['morning', 'day', 'evening', 'night'])
        total_bot_female = sum(len(sales_data['bot_female'][p]) for p in ['morning', 'day', 'evening', 'night'])
        total_seller_anonymous = sum(len(sales_data['seller_anonymous'][p]) for p in ['morning', 'day', 'evening', 'night'])
        total_bot_anonymous = sum(len(sales_data['bot_anonymous'][p]) for p in ['morning', 'day', 'evening', 'night'])
        
        f.write(f"Всего за сутки: "
                f"Продавцов мужчин {total_seller_male}, "
                f"Продавцов женщин {total_seller_female}, "
                f"Мужчин ботов {total_bot_male}, "
                f"Женщин ботов {total_bot_female}, "
                f"Анонимных продавцов {total_seller_anonymous}, "
                f"Анонимных ботов {total_bot_anonymous}\n\n")
        
        male_top = sorted(sales_data['male_names_count'].items(), key=lambda x: x[1], reverse=True)[:5]
        female_top = sorted(sales_data['female_names_count'].items(), key=lambda x: x[1], reverse=True)[:5]
        
        f.write("Топ-5 мужских имён:\n")
        for name, count in male_top:
            f.write(f"  {name}: {count}\n")
        f.write("Топ-5 женских имён:\n")
        for name, count in female_top:
            f.write(f"  {name}: {count}\n")
        
        f.write("\nПроцентное соотношение по частям суток:\n")
        for period in ['morning', 'day', 'evening', 'night']:
            total_male = (len(sales_data['seller_male'][period]) + len(sales_data['bot_male'][period]))
            total_female = (len(sales_data['seller_female'][period]) + len(sales_data['bot_female'][period]))
            total_anonymous = (len(sales_data['seller_anonymous'][period]) + len(sales_data['bot_anonymous'][period]))
            total = total_male + total_female + total_anonymous
            
            if total > 0:
                male_pct = round(total_male / total * 100, 1)
                female_pct = round(total_female / total * 100, 1)
                anon_pct = round(total_anonymous / total * 100, 1)
                f.write(f"{period.capitalize()}: "
                        f"Мужские имена {male_pct}%, "
                        f"Женские имена {female_pct}%, "
                        f"Анонимы {anon_pct}%\n")
            else:
                f.write(f"{period.capitalize()}: Нет данных\n")
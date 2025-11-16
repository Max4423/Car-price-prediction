import pandas as pd
import numpy as np

def load_car_dataset():
    """
    Завантажує датасет автомобілів для створення точної карти кузовів.
    """
    try:
        df = pd.read_csv('../data/used_cars.csv')  
        if 'brand' in df.columns:
            df['brand'] = df['brand'].astype(str).str.lower().str.strip()
        if 'model' in df.columns:
            df['model'] = df['model'].astype(str).str.lower().str.strip()
        if 'carbody' in df.columns:
            df['carbody'] = df['carbody'].astype(str).str.lower().str.strip()
        return df
    except Exception as e:
        print(f"Помилка завантаження датасету: {e}")
        return pd.DataFrame()

def create_body_mapping_from_dataset(df):
    """
    Створює точну карту типів кузова на основі датасету.
    Всі ключі зберігаються в нижньому регістрі для зручності пошуку.
    """
    if df.empty:
        return {}, {}
    
    body_mapping = {}

    model_body = df.groupby('model')['carbody'].agg(
        lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'sedan'
    ).to_dict()

    brand_model_body = df.groupby(['brand', 'model'])['carbody'].agg(
        lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'sedan'
    ).to_dict()
    
    return model_body, brand_model_body

def calculate_body_metrics_from_dataset(df):
    """
    Розраховує середні метрики для кожного типу кузова на основі датасету.
    """
    if df.empty:
        return {
            "sedan": {"wheelbase": 102.0, "carlength": 177.0, "carwidth": 66.5, "carheight": 54.5, "curbweight": 2500},
            "hatchback": {"wheelbase": 96.0, "carlength": 165.0, "carwidth": 65.0, "carheight": 53.5, "curbweight": 2200},
            "wagon": {"wheelbase": 105.0, "carlength": 183.0, "carwidth": 67.0, "carheight": 55.0, "curbweight": 2800},
            "hardtop": {"wheelbase": 100.0, "carlength": 175.0, "carwidth": 66.0, "carheight": 52.0, "curbweight": 2400},
            "convertible": {"wheelbase": 99.0, "carlength": 172.0, "carwidth": 66.0, "carheight": 52.5, "curbweight": 2600}
        }
    
    metrics = df.groupby('carbody').agg({
        'wheelbase': 'mean',
        'carlength': 'mean', 
        'carwidth': 'mean',
        'carheight': 'mean',
        'curbweight': 'mean'
    }).round(1).to_dict('index')
    
    return metrics

try:
    car_df = load_car_dataset()
    if not car_df.empty:
        MODEL_BODY_MAP, BRAND_MODEL_BODY_MAP = create_body_mapping_from_dataset(car_df)
        CAR_BODY_METRICS = calculate_body_metrics_from_dataset(car_df)
        
        print(f"✅ Завантажено {len(car_df)} автомобілів")
        print(f"✅ Створено карту для {len(MODEL_BODY_MAP)} моделей")
        print(f"✅ Доступні типи кузова: {list(CAR_BODY_METRICS.keys())}")
    else:
        raise ValueError("Датасет порожній")
    
except Exception as e:
    print(f"⚠️ Помилка завантаження датасету, використовуються значення за замовчуванням: {e}")
    CAR_BODY_METRICS = {
        "sedan": {"wheelbase": 102.0, "carlength": 177.0, "carwidth": 66.5, "carheight": 54.5, "curbweight": 2500},
        "hatchback": {"wheelbase": 96.0, "carlength": 165.0, "carwidth": 65.0, "carheight": 53.5, "curbweight": 2200},
        "wagon": {"wheelbase": 105.0, "carlength": 183.0, "carwidth": 67.0, "carheight": 55.0, "curbweight": 2800},
        "hardtop": {"wheelbase": 100.0, "carlength": 175.0, "carwidth": 66.0, "carheight": 52.0, "curbweight": 2400},
        "convertible": {"wheelbase": 99.0, "carlength": 172.0, "carwidth": 66.0, "carheight": 52.5, "curbweight": 2600}
    }
    
    MODEL_BODY_MAP = {}
    BRAND_MODEL_BODY_MAP = {}

def get_car_body_metrics(carbody):
    """
    Повертає середні метрики для заданого типу кузова.
    Приймає тип кузова в будь-якому регістрі.
    """
    carbody_normalized = str(carbody).lower().strip()
    return CAR_BODY_METRICS.get(carbody_normalized, CAR_BODY_METRICS.get("sedan", {})).copy()

def get_car_body_type(brand, model):
    """
    Визначає тип кузова на основі марки та моделі з датасету.
    Приймає марку та модель в будь-якому регістрі.
    """
    if not brand or not model:
        return "sedan"
    
    clean_brand = str(brand).lower().strip()
    clean_model = str(model).lower().strip()
    
    print(f"🔍 Пошук типу кузова для: {clean_brand} {clean_model}")
    
    brand_model_key = (clean_brand, clean_model)
    if brand_model_key in BRAND_MODEL_BODY_MAP:
        result = BRAND_MODEL_BODY_MAP[brand_model_key]
        print(f"✅ Знайдено за комбінацією: {result}")
        return result

    if clean_model in MODEL_BODY_MAP:
        result = MODEL_BODY_MAP[clean_model]
        print(f"✅ Знайдено за моделлю: {result}")
        return result

    common_patterns = {
        # SUV/кросовери
        'rav4': 'wagon', 'cr-v': 'wagon', 'crv': 'wagon', 'x5': 'wagon', 'x3': 'wagon',
        'highlander': 'wagon', 'pilot': 'wagon', 'explorer': 'wagon', 'tucson': 'wagon',
        'tiguan': 'wagon', 'touareg': 'wagon', 'cx-5': 'wagon', 'forester': 'wagon',
        
        # Хетчбеки
        'golf': 'hatchback', 'focus': 'hatchback', 'prius': 'hatchback', 'fit': 'hatchback',
        'civic': 'hatchback', 'corolla': 'hatchback', 'yaris': 'hatchback', 'micra': 'hatchback',
        'clio': 'hatchback', '208': 'hatchback', 'i30': 'hatchback',
        
        # Кабріолети
        'mustang': 'convertible', 'z4': 'convertible', 'boxter': 'convertible', 'cabrio': 'convertible',
        'miata': 'convertible', 'mx-5': 'convertible', 'slk': 'convertible',
        
        # Седани 
        'camry': 'sedan', 'accord': 'sedan', 'passat': 'sedan', 'jetta': 'sedan',
        'sonata': 'sedan', 'optima': 'sedan', 'fusion': 'sedan', 'malibu': 'sedan',
        'a4': 'sedan', '3 series': 'sedan', 'c-class': 'sedan'
    }

    for pattern, body_type in common_patterns.items():
        if pattern in clean_model:
            print(f"✅ Знайдено за евристикою: {body_type}")
            return body_type

    print("⚠️ Тип кузова не знайдено, використовую седан за замовчуванням")
    return "sedan"

def format_car_body_name(carbody):
    """
    Форматує назву типу кузова для красивого відображення.
    """
    body_names = {
        'sedan': 'Седан',
        'hatchback': 'Хетчбек', 
        'wagon': 'Універсал',
        'convertible': 'Кабріолет',
        'hardtop': 'Хардтоп'
    }
    return body_names.get(carbody, carbody.title())

def print_body_mapping_stats():
    """
    Виводить статистику по карті кузовів для відладки.
    """
    print(f"📊 Статистика карти кузовів:")
    print(f"   - Моделей у MODEL_BODY_MAP: {len(MODEL_BODY_MAP)}")
    print(f"   - Комбінацій у BRAND_MODEL_BODY_MAP: {len(BRAND_MODEL_BODY_MAP)}")
    
    if MODEL_BODY_MAP:
        print(f"   - Приклад моделей: {list(MODEL_BODY_MAP.items())[:5]}")
    
    print(f"   - Доступні типи кузова: {list(CAR_BODY_METRICS.keys())}")

if __name__ == "__main__":
    print_body_mapping_stats()
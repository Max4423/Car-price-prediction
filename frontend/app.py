import streamlit as st
import requests
from forms import car_form
from processing import preprocess_car_input
from utils import display_price
from config import API_URL
from car_metrics import get_car_body_type, get_car_body_metrics

def fetch_metadata():
    try:
        resp = requests.get(f"{API_URL.rstrip('/')}/metadata", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return data.get("unique_brands", []), data.get("brand_model_map", {})
    except Exception:
        return ["toyota"], {"toyota": ["corolla"]}

def normalize_brands(brands_list):
    """
    Нормалізує список брендів: приводить до правильного регістру.
    """
    normalized_brands = []
    for brand in brands_list:
        clean_brand = str(brand).strip()
        normalized_brand = clean_brand.title()
        normalized_brands.append(normalized_brand)
    
    return sorted(normalized_brands)

def normalize_brand_model_map(brand_model_map, normalized_brands):
    """
    Нормалізує карту моделей до правильного регістру.
    """
    normalized_map = {}
    
    for old_brand, models in brand_model_map.items():
        clean_brand = str(old_brand).strip().title()
        
        if clean_brand in normalized_brands:
            normalized_models = []
            for model in models:
                clean_model = str(model).strip()
                normalized_model = clean_model.title()
                normalized_models.append(normalized_model)
            
            normalized_map[clean_brand] = sorted(normalized_models)
    
    return normalized_map

def format_car_name(name):
    """
    Форматує назву автомобіля до правильного регістру.
    Обробляє спеціальні випадки як BMW, Mercedes-Benz тощо.
    """
    if not name:
        return name

    special_cases = {
        'bmw': 'BMW',
        'mercedes-benz': 'Mercedes-Benz', 
        'mercedes': 'Mercedes',
        'vw': 'VW',
        'audi': 'Audi',
        'volkswagen': 'Volkswagen',
        'porsche': 'Porsche',
        'jaguar': 'Jaguar',
        'land rover': 'Land Rover',
        'alfa romeo': 'Alfa Romeo',
        'aston martin': 'Aston Martin',
        'rolls-royce': 'Rolls-Royce'
    }
    
    lower_name = name.lower()
    if lower_name in special_cases:
        return special_cases[lower_name]
    
    return name.title()

st.set_page_config(layout="wide")
st.title("Прогноз ціни автомобіля 🚗")

unique_brands, brand_model_map = fetch_metadata()

normalized_brands = normalize_brands(unique_brands)
normalized_model_map = normalize_brand_model_map(brand_model_map, normalized_brands)

st.header("Введіть характеристики авто")

col1, col2 = st.columns([1, 3])  

with col1:
    selected_brand = st.selectbox("1. Оберіть марку:", normalized_brands)

    available_models = normalized_model_map.get(selected_brand, [])

    selected_model = st.selectbox("2. Оберіть модель:", available_models)

    if selected_brand and selected_model:
        auto_carbody = get_car_body_type(selected_brand.lower(), selected_model.lower())
        body_metrics = get_car_body_metrics(auto_carbody)
        
        st.subheader("📋 Автоматично визначено")
        st.info(f"**Тип кузова:** {auto_carbody.title()}")
        st.info(f"**Колісна база:** {body_metrics['wheelbase']} дюймів")
        st.info(f"**Довжина:** {body_metrics['carlength']} дюймів") 
        st.info(f"**Ширина:** {body_metrics['carwidth']} дюймів")
        st.info(f"**Висота:** {body_metrics['carheight']} дюймів")
        st.info(f"**Маса:** {body_metrics['curbweight']} lbs")

with col2:
    if selected_brand and selected_model:
        auto_carbody = get_car_body_type(selected_brand.lower(), selected_model.lower())
        form_data, submitted = car_form(auto_carbody)
    else:
        form_data, submitted = car_form("sedan")  

if submitted:
    try:
        car_df = form_data.copy()
        car_df['brand'] = selected_brand
        car_df['model'] = selected_model

        try:
            payload = car_df.iloc[0].to_dict()
            endpoint = f"{API_URL.rstrip('/')}/predict/car"
            resp = requests.post(endpoint, json=payload, timeout=10)
            resp.raise_for_status()
            resp_json = resp.json()
            price = resp_json.get("price")
            if price is None:
                st.error(f"Помилка від бекенду: {resp.text}")
            else:
                display_price(price)
        except Exception as e:
            st.error(f"Помилка при зверненні до бекенду: {e}")

    except Exception as e:
        st.error(f"Помилка під час обробки: {e}")
        st.warning("Переконайтеся, що всі поля заповнені коректно.")
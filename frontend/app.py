# --- app.py ---
import streamlit as st
import requests
from forms import car_form
from processing import preprocess_car_input
from utils import display_price
from config import API_URL

# Try to get metadata (brands/model map) from backend API. If unavailable,
# fall back to minimal defaults to keep the UI running.
def fetch_metadata():
    try:
        resp = requests.get(f"{API_URL.rstrip('/')}/metadata", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return data.get("unique_brands", []), data.get("brand_model_map", {})
    except Exception:
        # fallback: a small default so UI still renders
        return ["toyota"], {"toyota": ["corolla"]}

st.set_page_config(layout="wide")
st.title("Прогноз ціни автомобіля 🚗")

# 1. Отримати карту брендів та моделей з бекенду (або fallback)
unique_brands, brand_model_map = fetch_metadata()

st.header("Введіть характеристики авто")

col1, col2 = st.columns([1, 3])  # Колонки для вибору

with col1:
    # 2. Вибір Бренду (ПОЗА ФОРМОЮ)
    selected_brand = st.selectbox("1. Оберіть Бренд", unique_brands)

    # 3. Отримуємо список моделей для обраного бренду
    available_models = brand_model_map.get(selected_brand, [])

    # 4. Вибір Моделі (ПОЗА ФОРМОЮ)
    selected_model = st.selectbox("2. Оберіть Модель", available_models)

with col2:
    # 5. Отримуємо решту даних з форми
    # (У forms.py більше не потрібно передавати списки)
    form_data, submitted = car_form()

if submitted:
    try:
        # 6. Комбінуємо дані
        car_df = form_data.copy()
        car_df['brand'] = selected_brand
        car_df['model'] = selected_model

        # 7. Надсилаємо дані на бекенд для прогнозу
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
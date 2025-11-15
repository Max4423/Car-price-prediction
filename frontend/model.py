# --- model.py ---
import pickle
import os
import streamlit as st


@st.cache_data
def load_car_model():
    '''
    Завантажує модель і всі необхідні артефакти.
    '''

    model_path = os.path.join(os.path.dirname(__file__), "..", "backend", "models", "car_price_model.pkl")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Не вдалося знайти файл моделі. Очікуваний шлях: {model_path}")

    with open(model_path, "rb") as f:
        data = pickle.load(f)

    model = data["model"]
    scaler = data["scaler"]
    encoders = data["label_encoders"]
    categorical = data["categorical_columns"]
    numerical = data["numerical_columns"]
    feature_cols = data["feature_columns"]

    # --- ОНОВЛЕНО ---
    unique_brands = data["unique_brands"]
    brand_model_map = data["brand_model_map"]  # Завантажуємо карту

    return model, scaler, encoders, categorical, numerical, feature_cols, unique_brands, brand_model_map
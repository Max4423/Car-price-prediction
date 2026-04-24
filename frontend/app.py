# --- app.py ---
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from forms import car_form
from utils import display_price
from config import API_URL

# Try to get metadata (brands/model map) from backend API. If unavailable,
# fall back to minimal defaults to keep the UI running.
def fetch_metadata():
    try:
        resp = requests.get(f"{API_URL.rstrip('/')}/metadata", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return (
            data.get("unique_brands", []),
            data.get("brand_model_map", {}),
            data.get("brand_model_engine_map", {}),
            data.get("ext_col_options", []),
            data.get("int_col_options", []),
            data.get("year_min"),
            data.get("year_max"),
        )
    except Exception:
        return (
            ["Toyota"],
            {"Toyota": ["Corolla"]},
            {"Toyota": {"Corolla": ["2.0L I4"]}},
            ["Black", "White", "Silver", "Unknown"],
            ["Black", "Gray", "Beige", "Unknown"],
            1980,
            2023,
        )


@st.cache_data
def load_analytics_data():
    candidate_paths = [
        "/app/data/used_cars2.csv",
        "../data/used_cars2.csv",
        "data/used_cars2.csv",
    ]
    for path in candidate_paths:
        try:
            df = pd.read_csv(path)
            if "price" in df.columns:
                df["price"] = pd.to_numeric(df["price"].astype(str).str.replace(r"[^0-9.]", "", regex=True), errors="coerce")
            if "milage" in df.columns:
                df["milage"] = pd.to_numeric(df["milage"].astype(str).str.replace(r"[^0-9]", "", regex=True), errors="coerce")
            if "model_year" in df.columns:
                df["model_year"] = pd.to_numeric(df["model_year"], errors="coerce")
            return df.dropna(subset=["price"]).copy()
        except Exception:
            continue
    return None


def render_analytics():
    st.header("Аналітика датасету")
    df = load_analytics_data()
    if df is None or df.empty:
        st.info("Датасет для аналітики недоступний. Перевірте наявність `used_cars2.csv`.")
        return

    q99 = df["price"].quantile(0.99)
    df["price_capped"] = df["price"].clip(upper=q99)

    c1, c2 = st.columns(2)
    with c1:
        fig_hist = px.histogram(df, x="price_capped", nbins=40, title="Розподіл ціни")
        st.plotly_chart(fig_hist, use_container_width=True)
    with c2:
        model_price = (
            df.groupby("model", as_index=False)["price"]
            .mean()
            .sort_values("price", ascending=False)
            .head(15)
        )
        fig_top = px.bar(model_price, x="price", y="model", orientation="h", title="Топ-15 моделей за середньою ціною")
        st.plotly_chart(fig_top, use_container_width=True)

    if {"model_year", "price"}.issubset(df.columns):
        yearly = df.dropna(subset=["model_year"]).groupby("model_year", as_index=False)["price"].median()
        fig_year = px.line(yearly, x="model_year", y="price", title="Медіанна ціна за роком випуску")
        st.plotly_chart(fig_year, use_container_width=True)


def render_prediction_insights(predicted_price, payload):
    st.subheader("Аналітика для цього предікту")
    df = load_analytics_data()
    if df is None or df.empty:
        st.info("Локальна аналітика для конкретного предікту недоступна без `used_cars2.csv`.")
        return

    brand = payload.get("brand")
    model = payload.get("model")
    year = payload.get("model_year")
    milage = payload.get("milage")

    model_slice = df[(df["brand"] == brand) & (df["model"] == model)].copy()
    if model_slice.empty:
        st.info("Для обраної марки/моделі немає достатньо даних для персональної аналітики.")
        return

    model_mean = float(model_slice["price"].mean())
    model_median = float(model_slice["price"].median())
    diff_vs_mean = predicted_price - model_mean

    m1, m2, m3 = st.columns(3)
    m1.metric("Середня ціна моделі", f"${model_mean:,.0f}")
    m2.metric("Медіанна ціна моделі", f"${model_median:,.0f}")
    m3.metric("Різниця до середньої", f"${diff_vs_mean:,.0f}")

    compare_df = pd.DataFrame(
        {
            "Показник": ["Predicted price", "Середня ціна моделі", "Медіанна ціна моделі"],
            "Ціна": [predicted_price, model_mean, model_median],
        }
    )
    fig_compare = px.bar(compare_df, x="Показник", y="Ціна", title="Порівняння вашого предікту з ринком моделі")
    st.plotly_chart(fig_compare, use_container_width=True)

    fig_dist = px.histogram(
        model_slice,
        x="price",
        nbins=30,
        title=f"Розподіл цін для {brand} {model}",
    )
    fig_dist.add_vline(x=predicted_price, line_dash="dash", line_color="red")
    st.plotly_chart(fig_dist, use_container_width=True)

    if pd.notna(year) and "model_year" in model_slice.columns:
        year_slice = model_slice[model_slice["model_year"] == year]
        if len(year_slice) >= 3:
            year_mean = float(year_slice["price"].mean())
            year_compare = pd.DataFrame(
                {
                    "Показник": ["Predicted price", f"Середня для {int(year)}"],
                    "Ціна": [predicted_price, year_mean],
                }
            )
            fig_year_compare = px.bar(
                year_compare,
                x="Показник",
                y="Ціна",
                title=f"Порівняння з цінами цієї ж моделі за {int(year)} рік",
            )
            st.plotly_chart(fig_year_compare, use_container_width=True)

    if pd.notna(milage) and "milage" in model_slice.columns:
        scatter_slice = model_slice.dropna(subset=["milage", "price"]).copy()
        if len(scatter_slice) > 10:
            fig_scatter = px.scatter(
                scatter_slice,
                x="milage",
                y="price",
                title="Ціна vs пробіг для цієї моделі",
                opacity=0.5,
            )
            fig_scatter.add_scatter(
                x=[milage],
                y=[predicted_price],
                mode="markers",
                marker=dict(size=12, color="red"),
                name="Ваш предікт",
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

st.set_page_config(layout="wide")
st.title("Прогноз ціни автомобіля 🚗")

# 1. Отримати карту брендів та моделей з бекенду (або fallback)
(
    unique_brands,
    brand_model_map,
    brand_model_engine_map,
    ext_col_options,
    int_col_options,
    year_min,
    year_max,
) = fetch_metadata()

st.header("Введіть характеристики авто")

col1, col2 = st.columns([1, 3])  # Колонки для вибору

with col1:
    # 2. Вибір Бренду (ПОЗА ФОРМОЮ)
    selected_brand = st.selectbox("1. Оберіть Бренд", unique_brands)

    # 3. Отримуємо список моделей для обраного бренду
    available_models = brand_model_map.get(selected_brand, [])

    # 4. Вибір Моделі (ПОЗА ФОРМОЮ)
    selected_model = st.selectbox("2. Оберіть Модель", available_models)
    model_engine_options = (
        brand_model_engine_map.get(selected_brand, {}).get(selected_model, ["Unknown"])
        if selected_brand and selected_model
        else ["Unknown"]
    )

with col2:
    # 5. Отримуємо решту даних з форми
    # (У forms.py більше не потрібно передавати списки)
    form_data, submitted = car_form(
        ext_col_options=ext_col_options,
        int_col_options=int_col_options,
        engine_options=model_engine_options,
        year_min=year_min,
        year_max=year_max,
    )

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
                render_prediction_insights(float(price), payload)
        except Exception as e:
            st.error(f"Помилка при зверненні до бекенду: {e}")

    except Exception as e:
        st.error(f"Помилка під час обробки: {e}")
        st.warning("Переконайтеся, що всі поля заповнені коректно.")

st.markdown("---")
render_analytics()
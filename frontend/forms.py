# --- forms.py ---
import pandas as pd
import streamlit as st
import re


def car_form(
    ext_col_options=None,
    int_col_options=None,
    engine_options=None,
    year_min=None,
    year_max=None,
):
    """Відображає форму вводу для used_cars2.csv."""
    ext_col_options = ext_col_options or ["Black", "White", "Silver", "Gray", "Blue", "Red", "Unknown"]
    int_col_options = int_col_options or ["Black", "Gray", "Beige", "Brown", "White", "Unknown"]
    engine_options = engine_options or ["Unknown"]
    year_min = int(year_min) if year_min is not None else 1980
    year_max = int(year_max) if year_max is not None else 2026

    with st.form("car_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Базові характеристики")
            default_year = min(max(2020, year_min), year_max)
            model_year = st.number_input("Рік випуску", min_value=year_min, max_value=year_max, value=default_year)
            milage = st.number_input("Пробіг (miles)", min_value=0, max_value=1_000_000, value=50_000)
            fuel_type = st.selectbox("Тип палива", ["Gasoline", "Hybrid", "Diesel", "Electric", "E85 Flex Fuel", "Unknown"])
            transmission = st.selectbox(
                "Трансмісія",
                ["Automatic", "A/T", "M/T", "CVT", "6-Speed A/T", "8-Speed Automatic", "Unknown"],
            )
            clean_title = st.selectbox("Clean title", ["Yes", "No", "Unknown"])

        with col2:
            st.subheader("Додаткові поля")
            engine = st.selectbox("Двигун (для обраної марки/моделі)", engine_options)
            selected_engine_volume = "Unknown"
            if isinstance(engine, str):
                m = re.search(r"(\d+(?:\.\d+)?)\s*[lL]", engine)
                if m:
                    selected_engine_volume = f"{float(m.group(1)):.1f}L"
            st.caption(f"Об'єм двигуна: `{selected_engine_volume}`")
            ext_col = st.selectbox("Колір екстер'єру", ext_col_options)
            int_col = st.selectbox("Колір інтер'єру", int_col_options)
            accident = st.selectbox(
                "Історія ДТП",
                ["None reported", "At least 1 accident or damage reported", "Unknown"],
            )

        st.markdown("---")
        submitted = st.form_submit_button("3. Прогнозувати ціну")

    data = {
        "model_year": int(model_year),
        "milage": float(milage),
        "fuel_type": fuel_type,
        "engine": engine.strip() or "Unknown",
        "transmission": transmission,
        "ext_col": ext_col.strip() or "Unknown",
        "int_col": int_col.strip() or "Unknown",
        "accident": accident,
        "clean_title": clean_title,
    }

    return pd.DataFrame([data]), submitted
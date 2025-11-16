# --- app.py ---
import streamlit as st
from forms import car_form
from processing import preprocess_car_input
from model import load_car_model
from utils import display_price

st.set_page_config(layout="wide")
st.title("Прогноз ціни автомобіля 🚗")

try:
    # 1. Завантажити модель та карту брендів
    (
        model, scaler, encoders, cat_cols,
        num_cols, feat_cols, unique_brands, brand_model_map
    ) = load_car_model()

    st.header("Введіть характеристики авто")

    col1, col2 = st.columns([1, 3])  # Колонки для вибору

    with col1:
        # 2. Вибір Бренду (ПОЗА ФОРМОЮ)
        selected_brand = st.selectbox("1. Оберіть Бренд", unique_brands)

        # 3. Отримуємо список моделей для обраного бренду
        available_models = brand_model_map[selected_brand]

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

            # 7. Обробити вхідні дані
            processed = preprocess_car_input(
                car_df,
                encoders,
                scaler,
                cat_cols,
                num_cols,
                feat_cols
            )

            # 8. Зробити прогноз
            price = model.predict(processed)[0]

            # 9. Відобразити результат
            display_price(price)

        except Exception as e:
            st.error(f"Помилка під час обробки або прогнозування: {e}")
            st.warning("Переконайтеся, що всі поля заповнені коректно.")


except FileNotFoundError as e:
    st.error(f"Файл моделі (car_price_model.pkl) не знайдено.")
    st.info("Будь ласка, спочатку запустіть оновлений скрипт навчання (train_model.py), щоб згенерувати файл моделі.")
except KeyError as e:
    st.error(f"Помилка завантаження даних з моделі: {e}")
    st.info("Ймовірно, ваш .pkl файл застарів. Будь ласка, запустіть оновлений скрипт навчання.")
except Exception as e:
    st.error(f"Сталася непередбачена помилка: {e}")
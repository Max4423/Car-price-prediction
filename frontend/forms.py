# --- forms.py ---
import streamlit as st
import pandas as pd


def car_form():
    '''
    Відображає форму вводу ТІЛЬКИ для технічних характеристик.
    '''

    # Ми використовуємо st.columns для кращого компонування

    with st.form("car_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Кузов")
            carbody = st.selectbox("Тип кузова", ["sedan", "hatchback", "wagon", "hardtop", "convertible"])
            doornumber = st.selectbox("Кількість дверей", ["two", "four"])
            drivewheel = st.selectbox("Привід", ["fwd", "rwd", "4wd"])
            enginelocation = st.selectbox("Розташування двигуна", ["front", "rear"])

        with col2:
            st.subheader("Двигун")
            fueltype = st.selectbox("Тип палива", ["gas", "diesel"])
            aspiration = st.selectbox("Наддув", ["std", "turbo"])
            enginetype = st.selectbox("Тип двигуна", sorted(["ohc", "ohcf", "ohcv", "l", "rotor", "dohc", "dohcv"]))
            cylindernumber = st.selectbox("Кількість циліндрів",
                                          ["two", "three", "four", "five", "six", "eight", "twelve"])
            fuelsystem = st.selectbox("Паливна система",
                                      sorted(["mpfi", "2bbl", "mfi", "1bbl", "spfi", "spdi", "4bbl", "idi"]))
            enginesize = st.number_input("Розмір двигуна (куб. дюйми)", min_value=50, max_value=500, value=150)
            boreratio = st.number_input("Bore Ratio", min_value=2.0, max_value=5.0, value=3.0, step=0.01)
            stroke = st.number_input("Stroke", min_value=1.5, max_value=5.0, value=3.0, step=0.01)

        with col3:
            st.subheader("Характеристики")
            curbweight = st.number_input("Маса авто (lbs)", min_value=1000, max_value=5000, value=2500)
            horsepower = st.number_input("Потужність (к.с.)", min_value=40, max_value=300, value=100)
            peakrpm = st.number_input("Макс. RPM", min_value=3000, max_value=7000, value=5500)
            compressionratio = st.number_input("Compression Ratio", min_value=5.0, max_value=25.0, value=10.0, step=0.1)
            citympg = st.number_input("Витрата (місто) MPG", min_value=10, max_value=60, value=25)
            highwaympg = st.number_input("Витрата (траса) MPG", min_value=10, max_value=60, value=30)
            wheelbase = st.number_input("Колісна база (дюйми)", min_value=80.0, max_value=150.0, value=100.0)
            carlength = st.number_input("Довжина авто (дюйми)", min_value=140.0, max_value=210.0, value=170.0)
            carwidth = st.number_input("Ширина авто (дюйми)", min_value=60.0, max_value=80.0, value=65.0)
            carheight = st.number_input("Висота авто (дюйми)", min_value=45.0, max_value=65.0, value=55.0)

        # Кнопка відправки
        st.markdown("---")
        submitted = st.form_submit_button("3. Прогнозувати ціну")

    # Створюємо DataFrame (БЕЗ 'brand' та 'model')
    data = {
        'fueltype': fueltype,
        'aspiration': aspiration,
        'doornumber': doornumber,
        'carbody': carbody,
        'drivewheel': drivewheel,
        'enginelocation': enginelocation,
        'enginetype': enginetype,
        'cylindernumber': cylindernumber,
        'fuelsystem': fuelsystem,
        'wheelbase': wheelbase,
        'carlength': carlength,
        'carwidth': carwidth,
        'carheight': carheight,
        'curbweight': curbweight,
        'enginesize': enginesize,
        'boreratio': boreratio,
        'stroke': stroke,
        'compressionratio': compressionratio,
        'horsepower': horsepower,
        'peakrpm': peakrpm,
        'citympg': citympg,
        'highwaympg': highwaympg
    }

    df = pd.DataFrame([data])

    return df, submitted
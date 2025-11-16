import streamlit as st
import pandas as pd
from car_metrics import get_car_body_metrics, format_car_body_name

def car_form(auto_carbody="sedan"):
    '''
    Відображає форму вводу ТІЛЬКИ для технічних характеристик.
    Тип кузова передається автоматично.
    '''
    
    DOOR_NUMBER_MAP = {"two": "2", "four": "4"}
    DRIVEWHEEL_MAP = {"fwd": "Передній", "rwd": "Задній", "4wd": "Повний"}
    FUELTYPE_MAP = {"gas": "Бензин", "diesel": "Дизель"}
    ASPIRATION_MAP = {"std": "Без наддуву", "turbo": "Турбо"}
    ENGINELOCATION_MAP = {"front": "Переднє", "rear": "Заднє"}
    
    ENGINETYPE_MAP = {
        "ohc": "Один верхній розподільний вал (OHC)",
        "ohcf": "Один верхній розподільний вал (OHC-F)",
        "ohcv": "Один верхній розподільний вал (OHC-V)",
        "l": "Рядний (L)",
        "rotor": "Роторний",
        "dohc": "Два верхніх розподільних вали (DOHC)",
        "dohcv": "Два верхніх розподільних вали (DOHC-V)"
    }
    
    CYLINDERNUMBER_MAP = {
        "two": "2", "three": "3", "four": "4", "five": "5", 
        "six": "6", "eight": "8", "twelve": "12"
    }
    
    FUELSYSTEM_MAP = {
        "mpfi": "Мульти-точкове впорскування (MPFI)",
        "2bbl": "Дво-камерний карбюратор (2BBL)",
        "mfi": "Механічне впорскування (MFI)",
        "1bbl": "Одно-камерний карбюратор (1BBL)",
        "spfi": "Одно-точкове впорскування (SPFI)",
        "spdi": "Пряме впорскування (SPDI)",
        "4bbl": "Чотири-камерний карбюратор (4BBL)",
        "idi": "Непряме впорскування дизеля (IDI)"
    }

    with st.form("car_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("🚗 Кузов")
            display_carbody = format_car_body_name(auto_carbody)
            st.info(f"**Тип кузова:** {display_carbody} (автоматично)")
            
            doornumber_display = st.selectbox("Кількість дверей", list(DOOR_NUMBER_MAP.values()))
            drivewheel_display = st.selectbox("Тип приводу", list(DRIVEWHEEL_MAP.values()))
            enginelocation_display = st.selectbox("Розташування двигуна", list(ENGINELOCATION_MAP.values()))

        with col2:
            st.subheader("⚙️ Двигун")
            fueltype_display = st.selectbox("Тип палива", list(FUELTYPE_MAP.values()))
            aspiration_display = st.selectbox("Тип наддуву", list(ASPIRATION_MAP.values()))
            enginetype_display = st.selectbox("Тип двигуна", sorted(list(ENGINETYPE_MAP.values())))
            cylindernumber_display = st.selectbox("Кількість циліндрів", list(CYLINDERNUMBER_MAP.values()))
            fuelsystem_display = st.selectbox("Паливна система", sorted(list(FUELSYSTEM_MAP.values())))
            enginesize = st.number_input("Об'єм двигуна (куб. дюйми)", min_value=50, max_value=500, value=150, 
                                       help="Об'єм двигуна в кубічних дюймах")
            boreratio = st.number_input("Діаметр циліндра (Bore Ratio)", min_value=2.0, max_value=5.0, value=3.0, step=0.01,
                                      help="Співвідношення діаметра циліндра")
            stroke = st.number_input("Хід поршня (Stroke)", min_value=1.5, max_value=5.0, value=3.0, step=0.01,
                                   help="Хід поршня в двигуні")

        with col3:
            st.subheader("📊 Характеристики")
            horsepower = st.number_input("Потужність (к.с.)", min_value=40, max_value=300, value=100,
                                       help="Потужність двигуна в кінських силах")
            peakrpm = st.number_input("Максимальні оберти (RPM)", min_value=3000, max_value=7000, value=5500,
                                    help="Максимальна кількість обертів в хвилину")
            compressionratio = st.number_input("Ступінь стиснення", min_value=5.0, max_value=25.0, value=10.0, step=0.1,
                                             help="Співвідношення ступеня стиснення двигуна")
            citympg = st.number_input("Витрата палива (місто) MPG", min_value=10, max_value=60, value=25,
                                    help="Витрата палива в місті (миль на галон)")
            highwaympg = st.number_input("Витрата палива (траса) MPG", min_value=10, max_value=60, value=30,
                                       help="Витрата палива на трасі (миль на галон)")

        st.markdown("---")
        submitted = st.form_submit_button("🎯 Прогнозувати ціну")

    doornumber = [k for k, v in DOOR_NUMBER_MAP.items() if v == doornumber_display][0]
    drivewheel = [k for k, v in DRIVEWHEEL_MAP.items() if v == drivewheel_display][0]
    fueltype = [k for k, v in FUELTYPE_MAP.items() if v == fueltype_display][0]
    aspiration = [k for k, v in ASPIRATION_MAP.items() if v == aspiration_display][0]
    enginelocation = [k for k, v in ENGINELOCATION_MAP.items() if v == enginelocation_display][0]
    enginetype = [k for k, v in ENGINETYPE_MAP.items() if v == enginetype_display][0]
    cylindernumber = [k for k, v in CYLINDERNUMBER_MAP.items() if v == cylindernumber_display][0]
    fuelsystem = [k for k, v in FUELSYSTEM_MAP.items() if v == fuelsystem_display][0]

    body_metrics = get_car_body_metrics(auto_carbody)

    data = {
        'fueltype': fueltype,
        'aspiration': aspiration,
        'doornumber': doornumber,
        'carbody': auto_carbody,  
        'drivewheel': drivewheel,
        'enginelocation': enginelocation,
        'enginetype': enginetype,
        'cylindernumber': cylindernumber,
        'fuelsystem': fuelsystem,
        'wheelbase': body_metrics['wheelbase'],  
        'carlength': body_metrics['carlength'],  
        'carwidth': body_metrics['carwidth'],    
        'carheight': body_metrics['carheight'],  
        'curbweight': body_metrics['curbweight'], 
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
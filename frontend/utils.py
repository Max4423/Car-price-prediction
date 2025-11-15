# --- utils.py ---
import streamlit as st


def display_price(price):
    st.subheader("Прогнозована вартість авто")

    # Додаємо базову перевірку
    if price < 0:
        st.warning(f"Модель спрогнозувала нереалістичну (негативну) ціну: ${price:,.2f}")
        st.info("Це може статися, якщо введено екстремальні або нетипові характеристики.")
    else:
        st.success(f"Орієнтовна ціна: **${price:,.2f}**")
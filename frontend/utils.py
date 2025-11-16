import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def display_price(price):
    """
    Відображає прогнозовану ціну з додатковими функціями.
    """
    st.subheader("💰 Прогнозована вартість авто")
    
    if price < 0:
        st.warning(f"Модель спрогнозувала нереалістичну (негативну) ціну: ${price:,.2f}")
        st.info("Це може статися, якщо введено екстремальні або нетипові характеристики.")
        return

    st.success(f"Орієнтовна ціна: **${price:,.2f}**")
    
    display_price_comparison(price)
    display_financial_breakdown(price)
    display_recommendations(price)

def display_price_comparison(price):
    """
    Порівнює ціну з ринковими сегментами.
    """
    st.markdown("---")
    st.subheader("📊 Порівняння з ринком")
    
    price_segments = {
        "Економ-клас": (5000, 15000),
        "Середній клас": (15000, 35000),
        "Преміум": (35000, 70000),
        "Люкс": (70000, 150000),
        "Супер-кар": (150000, float('inf'))
    }

    current_segment = "Невідомий"
    for segment, (min_price, max_price) in price_segments.items():
        if min_price <= price <= max_price:
            current_segment = segment
            break
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Ціновий сегмент", current_segment)
    
    with col2:
        premium_mid = (35000 + 70000) / 2
        premium_percent = (price / premium_mid) * 100
        st.metric("Відсоток від преміум-класу", f"{premium_percent:.1f}%")
    
    with col3:
        if price < 10000:
            recommendation = "🟢 Вигідна пропозиція"
        elif price < 30000:
            recommendation = "🟡 Середня ціна"
        else:
            recommendation = "🔴 Преміум вартість"
        st.metric("Рекомендація/ціна", recommendation)

    fig = create_price_segment_chart(price, price_segments, current_segment)
    st.plotly_chart(fig, use_container_width=True)

def create_price_segment_chart(price, segments, current_segment):
    """
    Створює графік порівняння ціни з ринковими сегментами.
    """
    fig = go.Figure()

    segment_data = []
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']
    
    for i, (segment, (min_price, max_price)) in enumerate(segments.items()):
        if max_price == float('inf'):
            display_max = max(price * 1.5, 200000)
        else:
            display_max = max_price
            
        segment_data.append({
            'segment': segment,
            'min_price': min_price,
            'max_price': display_max,
            'width': display_max - min_price,
            'midpoint': (min_price + display_max) / 2,
            'color': colors[i % len(colors)],
            'is_current': segment == current_segment
        })

    for data in segment_data:
        opacity = 0.8 if data['is_current'] else 0.4
        
        fig.add_trace(go.Bar(
            x=[data['width']],
            y=[data['segment']],
            base=[data['min_price']], 
            orientation='h',
            name=data['segment'],
            marker_color=data['color'],
            opacity=opacity,
            hovertemplate=f"{data['segment']}<br>${data['min_price']:,.0f} - ${data['max_price']:,.0f}<extra></extra>"
        ))

    fig.add_vline(x=price, line_dash="dash", line_color="red", line_width=3,
                  annotation_text=f"Ваша ціна: ${price:,.0f}",
                  annotation_position="top right")

    max_display_price = max([data['max_price'] for data in segment_data])
    
    fig.update_layout(
        title="Порівняння з ринковими сегментами",
        xaxis_title="Ціна ($)",
        yaxis_title="Сегмент",
        showlegend=False,
        height=400,
        xaxis=dict(
            range=[0, max_display_price * 1.1],  
            tickformat=",",
            tickmode='linear',
            dtick=25000 
        )
    )
    
    return fig

def display_financial_breakdown(price):
    """
    Показує фінансову розбивку ціни.
    """
    st.markdown("---")
    st.subheader("💳 Фінансові розрахунки")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        down_payment = price * 0.2
        st.metric("Перший внесок (20%)", f"${down_payment:,.0f}")
    
    with col2:
        loan_3_years = (price - down_payment) / 36
        st.metric("Платежі (3 роки)", f"${loan_3_years:,.0f}/міс")
    
    with col3:
        loan_5_years = (price - down_payment) / 60
        st.metric("Платежі (5 років)", f"${loan_5_years:,.0f}/міс")
    
    st.info("""
    **💡 Додаткові витрати:**
    - Страхування: ~$100-300/міс
    - Паливо: ~$150-300/міс  
    - Обслуговування: ~$50-150/міс
    """)

def display_recommendations(price):
    """
    Показує рекомендації на основі ціни.
    """
    st.markdown("---")
    st.subheader("🎯 Рекомендації")
    
    if price < 10000:
        st.success("""
        **🟢 Вигідна пропозиція!**
        - Ідеально для першого авто
        - Низькі витрати на страхування
        - Легко знайти запчастини
        - Рекомендуємо: Toyota Corolla, Honda Civic, Hyundai Elantra
        """)
    elif price < 25000:
        st.warning("""
        **🟡 Золота середина**
        - Хороше співвідношення ціна/якість
        - Сучасні технології та безпека
        - Помірні експлуатаційні витрати
        - Рекомендуємо: Mazda3, Kia Optima, Volkswagen Jetta
        """)
    elif price < 50000:
        st.info("""
        **🔵 Преміум рівень**
        - Високий комфорт та продуктивність
        - Передові технології
        - Вища якість матеріалів
        - Рекомендуємо: BMW 3 Series, Audi A4, Mercedes C-Class
        """)
    else:
        st.error("""
        **🔴 Люкс сегмент**
        - Ексклюзивність та високі технології
        - Значні витрати на обслуговування
        - Рекомендуємо консультацію з експертом
        - Ретельна перевірка технічного стану
        """)
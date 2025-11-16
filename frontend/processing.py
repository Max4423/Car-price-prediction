# --- processing.py ---
import pandas as pd
import numpy as np


def preprocess_car_input(df, encoders, scaler, cat_cols, num_cols, feature_cols):
    '''
    Перетворює DataFrame з вхідними даними у формат,
    придатний для моделі.
    '''

    # Копіюємо, щоб уникнути SettingWithCopyWarning
    df_processed = df.copy()

    # 1. Label Encoding
    # cat_cols = ['fueltype', ..., 'brand', 'model']
    # 'df_processed' має колонки 'brand' and 'model' (з forms.py)

    for col in cat_cols:
        val = df_processed[col].iloc[0]

        try:
            # Трансформуємо значення (яке є рядком із selectbox)
            # у його числовий еквівалент (int)
            encoded_val = encoders[col].transform([str(val)])[0]
            df_processed[col] = encoded_val
        except ValueError:
            # Ця помилка не має виникати, оскільки ми використовуємо
            # selectbox зі списками, згенерованими при навчанні.
            print(f"ПОМИЛКА: Не вдалося знайти '{val}' у енкодері для '{col}'.")
            # На випадок непередбаченої помилки, можна встановити 0
            df_processed[col] = 0

            # 2. Feature engineering (як у backend)
    df_processed['power_to_weight_ratio'] = df_processed['horsepower'] / df_processed['curbweight']
    for col in num_cols:
        df_processed[f'{col}_squared'] = df_processed[col] ** 2
    df_processed['log_enginesize'] = np.log(df_processed['enginesize'] + 1)

    # 3. Масштабування
    # Переконуємось, що передаємо scaler'у колонки в тому ж порядку
    df_processed[num_cols] = scaler.transform(df_processed[num_cols])

    # 4. Відповідність колонок
    # (Переконуємось, що всі колонки, які бачила модель, тут є,
    # включно з _squared, log_, etc.)
    df_processed = df_processed.reindex(columns=feature_cols, fill_value=0)

    # Повертаємо тільки ті колонки, які очікує модель (у правильному порядку)
    return df_processed[feature_cols]
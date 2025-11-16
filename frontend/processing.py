import pandas as pd
import numpy as np


def preprocess_car_input(df, encoders, scaler, cat_cols, num_cols, feature_cols):
    '''
    Перетворює DataFrame з вхідними даними у формат,
    придатний для моделі.
    '''

    df_processed = df.copy()

    for col in cat_cols:
        val = df_processed[col].iloc[0]

        try:
            encoded_val = encoders[col].transform([str(val)])[0]
            df_processed[col] = encoded_val
        except ValueError:
            print(f"ПОМИЛКА: Не вдалося знайти '{val}' у енкодері для '{col}'.")
            df_processed[col] = 0

    df_processed['power_to_weight_ratio'] = df_processed['horsepower'] / df_processed['curbweight']
    for col in num_cols:
        df_processed[f'{col}_squared'] = df_processed[col] ** 2
    df_processed['log_enginesize'] = np.log(df_processed['enginesize'] + 1)

    df_processed[num_cols] = scaler.transform(df_processed[num_cols])

    df_processed = df_processed.reindex(columns=feature_cols, fill_value=0)

    return df_processed[feature_cols]
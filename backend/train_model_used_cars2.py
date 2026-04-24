import os
import pickle
import re

import numpy as np
import pandas as pd
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler


def parse_milage(value):
    if pd.isna(value):
        return np.nan
    digits = re.sub(r"[^0-9]", "", str(value))
    return float(digits) if digits else np.nan


def parse_price(value):
    if pd.isna(value):
        return np.nan
    cleaned = re.sub(r"[^0-9.]", "", str(value))
    if cleaned.count(".") > 1:
        return np.nan
    return float(cleaned) if cleaned else np.nan


def main():
    df = pd.read_csv("../data/used_cars2.csv")

    categorical_columns = [
        "brand",
        "model",
        "fuel_type",
        "engine",
        "transmission",
        "ext_col",
        "int_col",
        "accident",
        "clean_title",
    ]
    numerical_columns = ["model_year", "milage", "car_age"]

    for col in categorical_columns:
        df[col] = df[col].astype(str).str.strip()

    df["clean_title"] = df["clean_title"].replace({"": "Unknown", "nan": "Unknown", "None": "Unknown"})
    df["fuel_type"] = df["fuel_type"].replace({"": "Unknown", "nan": "Unknown", "None": "Unknown"})
    df["accident"] = df["accident"].replace({"": "Unknown", "nan": "Unknown", "None": "Unknown"})

    df["milage"] = df["milage"].apply(parse_milage)
    df["price"] = df["price"].apply(parse_price)
    df["model_year"] = pd.to_numeric(df["model_year"], errors="coerce")
    df["car_age"] = (pd.Timestamp.now().year - df["model_year"]).clip(lower=0)

    for col in numerical_columns:
        df[col] = df[col].fillna(df[col].median())
    for col in categorical_columns:
        df[col] = df[col].fillna("Unknown").astype(str)
    df = df.dropna(subset=["price"]).copy()

    brand_model_map = df.groupby("brand")["model"].apply(lambda x: sorted(list(x.astype(str).unique()))).to_dict()
    unique_brands = sorted(df["brand"].astype(str).unique().tolist())

    label_encoders_dict = {}
    for col in categorical_columns:
        le = LabelEncoder()
        df[col] = df[col].astype(str)
        le.fit(df[col])
        label_encoders_dict[col] = le
        df[col] = le.transform(df[col])

    df["milage_per_year"] = df["milage"] / (df["car_age"] + 1)
    for col in numerical_columns:
        df[f"{col}_squared"] = df[col] ** 2

    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    for col in numerical_columns + ["milage_per_year"]:
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median())

    scaler = StandardScaler()
    df[numerical_columns] = scaler.fit_transform(df[numerical_columns])

    X = df.drop(["price"], axis=1)
    y = df["price"]
    feature_columns = X.columns.tolist()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = Lasso(alpha=100.0, random_state=42, max_iter=5000)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print(f"R2: {r2_score(y_test, y_pred):.4f}")
    print(f"MSE: {mean_squared_error(y_test, y_pred):.2f}")

    payload = {
        "model": model,
        "scaler": scaler,
        "label_encoders": label_encoders_dict,
        "categorical_columns": categorical_columns,
        "numerical_columns": numerical_columns,
        "feature_columns": feature_columns,
        "unique_brands": unique_brands,
        "brand_model_map": brand_model_map,
        "year_min": int(df["model_year"].min()),
        "year_max": int(df["model_year"].max()),
    }

    out_path = os.path.join("models", "car_price_model.pkl")
    os.makedirs("models", exist_ok=True)
    with open(out_path, "wb") as f:
        pickle.dump(payload, f)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()

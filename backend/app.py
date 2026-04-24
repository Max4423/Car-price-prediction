from flask import Flask, request, jsonify
import pickle
import os
import pandas as pd
import numpy as np
import re

app = Flask(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "car_price_model.pkl")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"car_price_model.pkl not found at {MODEL_PATH}")

with open(MODEL_PATH, "rb") as f:
    data = pickle.load(f)

model = data["model"]
scaler = data["scaler"]
encoders = data["label_encoders"]
categorical_cols = data["categorical_columns"]
numerical_cols = data["numerical_columns"]
feature_cols = data["feature_columns"]
unique_brands = data.get("unique_brands", [])
brand_model_map = data.get("brand_model_map", {})
ext_col_options = data.get("ext_col_options")
int_col_options = data.get("int_col_options")
year_min = data.get("year_min")
year_max = data.get("year_max")

if not ext_col_options and "ext_col" in encoders:
    ext_col_options = sorted([str(v) for v in encoders["ext_col"].classes_.tolist()])
if not int_col_options and "int_col" in encoders:
    int_col_options = sorted([str(v) for v in encoders["int_col"].classes_.tolist()])


def extract_engine_volume(engine_value: str):
    if engine_value is None:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)\s*[lL]", str(engine_value))
    if not match:
        return None
    try:
        return round(float(match.group(1)), 1)
    except Exception:
        return None


engine_volume_map = {}
if "engine" in encoders:
    for engine_name in encoders["engine"].classes_.tolist():
        vol = extract_engine_volume(str(engine_name))
        key = f"{vol:.1f}L" if vol is not None else "Unknown"
        engine_volume_map.setdefault(key, []).append(str(engine_name))
for k in list(engine_volume_map.keys()):
    engine_volume_map[k] = sorted(list(set(engine_volume_map[k])))
engine_volume_options = sorted(engine_volume_map.keys(), key=lambda x: (x == "Unknown", x))


def build_brand_model_engine_map():
    candidate_paths = [
        os.path.join(os.path.dirname(__file__), "..", "data", "used_cars2.csv"),
        "/app/data/used_cars2.csv",
    ]
    for path in candidate_paths:
        try:
            if not os.path.exists(path):
                continue
            raw = pd.read_csv(path, usecols=["brand", "model", "engine"])
            raw["brand"] = raw["brand"].astype(str).str.strip()
            raw["model"] = raw["model"].astype(str).str.strip()
            raw["engine"] = raw["engine"].astype(str).str.strip()
            raw = raw[(raw["brand"] != "") & (raw["model"] != "")]

            nested = {}
            for (brand, model), grp in raw.groupby(["brand", "model"]):
                engines = sorted(list(set(grp["engine"].dropna().astype(str).tolist())))
                if len(engines) == 0:
                    engines = ["Unknown"]
                nested.setdefault(brand, {})[model] = engines
            return nested
        except Exception:
            continue
    return {}


brand_model_engine_map = build_brand_model_engine_map()


def detect_year_bounds_from_data():
    candidate_paths = [
        os.path.join(os.path.dirname(__file__), "..", "data", "used_cars2.csv"),
        "/app/data/used_cars2.csv",
    ]
    for path in candidate_paths:
        try:
            if not os.path.exists(path):
                continue
            raw = pd.read_csv(path, usecols=["model_year"])
            years = pd.to_numeric(raw["model_year"], errors="coerce").dropna()
            if len(years) > 0:
                return int(years.min()), int(years.max())
        except Exception:
            continue
    return None, None


if year_min is None or year_max is None:
    detected_min, detected_max = detect_year_bounds_from_data()
    year_min = year_min if year_min is not None else detected_min
    year_max = year_max if year_max is not None else detected_max


def preprocess_input(df: pd.DataFrame) -> pd.DataFrame:
    df_processed = df.copy()

    if "model_year" in df_processed.columns:
        df_processed["model_year"] = pd.to_numeric(df_processed["model_year"], errors="coerce")
        if year_min is not None:
            df_processed["model_year"] = df_processed["model_year"].clip(lower=year_min)
        if year_max is not None:
            df_processed["model_year"] = df_processed["model_year"].clip(upper=year_max)

    if "milage" in df_processed.columns:
        df_processed["milage"] = pd.to_numeric(df_processed["milage"], errors="coerce")

    if "car_age" in numerical_cols and "car_age" not in df_processed.columns and "model_year" in df_processed.columns:
        current_year = pd.Timestamp.now().year
        df_processed["car_age"] = (current_year - df_processed["model_year"]).clip(lower=0)

    for col in categorical_cols:
        if col in df_processed.columns:
            val = df_processed[col].iloc[0]
            try:
                df_processed[col] = encoders[col].transform([str(val)])[0]
            except Exception:
                df_processed[col] = 0

    if "milage_per_year" in feature_cols:
        try:
            milage_series = pd.to_numeric(df_processed.get("milage", 0), errors="coerce").fillna(0)
            car_age_series = pd.to_numeric(df_processed.get("car_age", 0), errors="coerce").fillna(0)
            df_processed["milage_per_year"] = milage_series / (car_age_series + 1)
        except Exception:
            df_processed["milage_per_year"] = 0

    for col in numerical_cols:
        if col in df_processed.columns:
            df_processed[f"{col}_squared"] = df_processed[col] ** 2

    for col in numerical_cols:
        if col in df_processed.columns:
            df_processed[col] = pd.to_numeric(df_processed[col], errors="coerce")
            df_processed[col] = df_processed[col].fillna(0)

    # Preserve scaler training order and ensure all required numeric columns exist.
    for col in numerical_cols:
        if col not in df_processed.columns:
            df_processed[col] = 0
    df_processed[numerical_cols] = scaler.transform(df_processed[numerical_cols])

    df_processed = df_processed.reindex(columns=feature_cols, fill_value=0)

    return df_processed[feature_cols]


@app.route("/predict/car", methods=["POST"])
def predict_car():
    try:
        data_json = request.get_json()
        if data_json is None:
            return jsonify({"error": "No JSON payload provided"}), 400

        df = pd.DataFrame([data_json])
        X = preprocess_input(df)

        price = model.predict(X)[0]
        price = max(0.0, float(price))
        return jsonify({"price": price})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/metadata", methods=["GET"])
def metadata():
    """Return small metadata for frontend (brand lists, model mapping)."""
    try:
        return jsonify({
            "unique_brands": unique_brands,
            "brand_model_map": brand_model_map,
            "brand_model_engine_map": brand_model_engine_map,
            "ext_col_options": ext_col_options or [],
            "int_col_options": int_col_options or [],
            "engine_volume_options": engine_volume_options,
            "engine_volume_map": engine_volume_map,
            "year_min": year_min,
            "year_max": year_max,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

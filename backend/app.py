from flask import Flask, request, jsonify
import pickle
import os
import pandas as pd
import numpy as np

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


def preprocess_input(df: pd.DataFrame) -> pd.DataFrame:
    df_processed = df.copy()

    for col in categorical_cols:
        if col in df_processed.columns:
            val = df_processed[col].iloc[0]
            try:
                df_processed[col] = encoders[col].transform([str(val)])[0]
            except Exception:
                df_processed[col] = 0

    if "horsepower" in df_processed and "curbweight" in df_processed:
        try:
            df_processed["power_to_weight_ratio"] = df_processed["horsepower"] / df_processed["curbweight"]
        except Exception:
            df_processed["power_to_weight_ratio"] = 0

    for col in numerical_cols:
        if col in df_processed.columns:
            df_processed[f"{col}_squared"] = df_processed[col] ** 2

    if "enginesize" in df_processed:
        df_processed["log_enginesize"] = np.log(df_processed["enginesize"] + 1)

    num_present = [c for c in numerical_cols if c in df_processed.columns]
    if len(num_present) > 0:
        df_processed[num_present] = scaler.transform(df_processed[num_present])

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
        return jsonify({"price": float(price)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/metadata", methods=["GET"])
def metadata():
    """Return small metadata for frontend (brand lists, model mapping)."""
    try:
        return jsonify({
            "unique_brands": unique_brands,
            "brand_model_map": brand_model_map
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

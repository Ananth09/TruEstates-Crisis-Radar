import os
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# 1. DIRECTORY SETUP
# ============================================================
VERSION = "v_2_3"
BASE_PATH = Path(__file__).parent 
MODEL_DIR = BASE_PATH / "models"
COL_DIR = BASE_PATH / "trained_columns"

# ============================================================
# 2. CONFIGURATION
# ============================================================
DIRECT_MODEL_AREAS = {
    "Al Barsha South Fourth", "Business Bay", "Al Merkadh", "Burj Khalifa",
    "Hadaeq Sheikh Mohammed Bin Rashid", "Al Khairan First", "Wadi Al Safa 5",
    "Al Thanyah Fifth", "Al Barshaa South Third", "Jabal Ali First",
    "Madinat Al Mataar", "Madinat Dubai Almelaheyah", "Me'Aisem First",
    "Al Hebiah Fourth", "Al Barsha South Fifth", "Al Hebiah First",
    "Nadd Hessa", "Palm Jumeirah", "Al Barshaa South Second",
    "Al Yelayiss 2", "Al Warsan First", "Marsa Dubai"
}

PROXY_MAPPING = {
    "Al Kifaf": "G1", "Wadi Al Safa 4": "G1",
    "Warsan Fourth": "G3", "Jabal Ali": "G3",
    "Zaabeel Second": "G4", "Zaabeel First": "G4",
    "Al Barsha First": "Proxy1", "Al Hebiah Second": "Proxy1", 
    "Al Hebiah Sixth": "Proxy1", "Al Hebiah Third": "Proxy1",
    "Madinat Hind 4": "Proxy1", "Wadi Al Safa 3": "Proxy1", 
    "Wadi Al Safa 7": "Proxy1",
    "Bukadra": "Proxy2", "Ras Al Khor Industrial First": "Proxy2",
    "Jumeirah First": "Proxy2", "Palm Deira": "Proxy2",
    "Al Thanyah Third": "Proxy3", "Jabal Ali Industrial Second": "Proxy3"
}

def get_slug(name):
    return name.replace(" ", "_").replace("'", "").lower()

def load_assets(model_key):
    slug = get_slug(model_key)
    model_path = MODEL_DIR / f"model_{VERSION}_{slug}.joblib"
    col_path = COL_DIR / f"trained_columns_{VERSION}_{slug}.joblib"
    
    if not model_path.exists():
        raise FileNotFoundError(f"Missing Model: {model_path}")
    if not col_path.exists():
        raise FileNotFoundError(f"Missing Columns: {col_path}")
        
    return joblib.load(model_path), joblib.load(col_path)

# ============================================================
# 3. PREDICTION LOGIC
# ============================================================

def predict_property_price(input_data, forecast_df, historic_df):
    area = input_data["area_name"]

    # 1. Determine Model Key
    if area in DIRECT_MODEL_AREAS:
        model_key = area
    elif area in PROXY_MAPPING:
        model_key = PROXY_MAPPING[area]
    else:
        raise ValueError(f"No model/proxy mapping found for: {area}")

    # 2. Load Assets
    model, train_columns = load_assets(model_key)

    # 3. Feature Engineering
    categorical_features = [
        "reg_type_en", "rooms_en", "land_type_en",
        "floor_bin", "developer_cat", "project_cat"
    ]
    
    # Create DF and handle numeric booleans
    temp = pd.DataFrame([input_data])
    
    # 4. Align Features with Training Columns
    # We manually create the dummy columns to avoid issues with missing categories
    final_input_row = pd.DataFrame(0, index=[0], columns=train_columns)
    
    # Fill numeric/continuous features
    for col in ['procedure_area', 'has_parking', 'swimming_pool', 'balcony', 'elevator', 'metro']:
        if col in train_columns:
            final_input_row[col] = input_data.get(col, 0)

    # Fill categorical dummies
    for cat in categorical_features:
        val = input_data.get(cat)
        dummy_col = f"{cat}_{val}"
        if dummy_col in train_columns:
            final_input_row[dummy_col] = 1

    # 5. Predict 
    base_prediction = float(model.predict(final_input_row)[0])

    # 6. Time Series Integration
    # Ensure date columns are datetime
    forecast_df["month"] = pd.to_datetime(forecast_df["month"])
    historic_df["month"] = pd.to_datetime(historic_df["month"])
    
    gf_slice = forecast_df[forecast_df["area"] == model_key].copy()
    hist_slice = historic_df[historic_df["area"] == model_key].copy()

    if gf_slice.empty and hist_slice.empty:
        return pd.DataFrame({"month": [pd.Timestamp.now()], "median_price": [base_prediction], "area": [area]})

    # Apply Growth Factors to the base prediction
    if not gf_slice.empty:
        gf_slice = gf_slice.sort_values("month")
        # Assuming growth_factor is cumulative or relative to the base
        gf_slice["median_price"] = base_prediction * gf_slice["growth_factor"]

    # Update history
    if not hist_slice.empty:
        hist_slice = hist_slice.sort_values("month")
        # We replace the last historic point (pivot) with our actual prediction
        hist_slice.loc[hist_slice.index[-1], "median_price"] = base_prediction

    combined = pd.concat([hist_slice, gf_slice], ignore_index=True)
    combined["area"] = area
    
    return combined[["month", "median_price", "area"]].sort_values("month")
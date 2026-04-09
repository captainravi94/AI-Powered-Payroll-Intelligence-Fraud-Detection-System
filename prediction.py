import pickle
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Load models + columns
def load_models():
    fraud_model = pickle.load(open(os.path.join(BASE_DIR, "models/fraud_model.pkl"), "rb"))
    reg_model = pickle.load(open(os.path.join(BASE_DIR, "models/reg_model.pkl"), "rb"))
    cols = pickle.load(open(os.path.join(BASE_DIR, "models/feature_columns.pkl"), "rb"))
    
    return fraud_model, reg_model, cols


# Create correct input dataframe (MATCH TRAINING FEATURES ONLY)
def make_input_df(input_data, cols):
    df = pd.DataFrame(columns=cols)
    df.loc[0] = 0

    # Only training features
    df["Salary"] = input_data["Salary"]
    df["Bonus"] = input_data["Bonus"]
    df["Overtime"] = input_data["Overtime"]
    df["Attendance"] = input_data["Attendance"]
    df["Experience"] = input_data["Experience"]
    df["Leaves"] = input_data["Leaves"]

    # categorical encoding
    country_col = "Country_" + input_data["Country"]
    dept_col = "Department_" + input_data["Department"]

    if country_col in df.columns:
        df[country_col] = 1

    if dept_col in df.columns:
        df[dept_col] = 1

    return df


# Prediction functions
def predict_pay(model, df):
    return model.predict(df)[0]

def predict_fraud(model, df):
    return model.predict(df)[0]
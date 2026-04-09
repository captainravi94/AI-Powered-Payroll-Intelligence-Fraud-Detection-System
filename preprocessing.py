import pandas as pd

def load_data(path):
    df = pd.read_csv(path)
    return df

def feature_engineering(df):
    df["Total_Pay"] = df["Salary"] + df["Bonus"] + df["Overtime"]
    df["Risk_Score"] = (
        0.4*(df["Bonus"]/df["Salary"]) +
        0.3*(df["Overtime"]/df["Salary"]) +
        0.3*(df["Net_Pay"]/df["Salary"])
    )
    return df
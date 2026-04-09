import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pdfplumber
import re
import time

from utils.prediction import load_models, make_input_df

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Payroll AI", layout="wide")

# -----------------------------
# CLEAN PROFESSIONAL UI
# -----------------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #0b1a2f;
    color: #e6edf3;
}
.stMetric {
    background-color: #16263f;
    border-radius: 10px;
    padding: 12px;
    border: 1px solid #223a5e;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOAD MODEL
# -----------------------------
fraud_model, reg_model, cols = load_models()

# -----------------------------
# HEADER
# -----------------------------
st.title("💼 Payroll Intelligence Dashboard")
st.caption("AI-powered payroll analytics, fraud detection & insights")

# -----------------------------
# SIDEBAR INPUT
# -----------------------------
st.sidebar.header("⚙️ Input Controls")

salary = st.sidebar.slider("Salary", 10000, 200000, 50000)
bonus = st.sidebar.slider("Bonus", 0, 50000, 10000)
overtime = st.sidebar.slider("Overtime", 0, 20000, 2000)

attendance = st.sidebar.slider("Attendance", 20, 31, 26)
experience = st.sidebar.slider("Experience", 1, 25, 5)
leaves = st.sidebar.slider("Leaves", 0, 10, 2)

country = st.sidebar.selectbox("Country", ["India","USA","UK"])
department = st.sidebar.selectbox("Department", ["HR","IT","Sales"])

# -----------------------------
# INPUT DATA
# -----------------------------
data = {
    "Salary": salary,
    "Bonus": bonus,
    "Overtime": overtime,
    "Attendance": attendance,
    "Experience": experience,
    "Leaves": leaves,
    "Country": country,
    "Department": department
}

df = make_input_df(data, cols)

# -----------------------------
# PREDICTION
# -----------------------------
with st.spinner("Analyzing..."):
    time.sleep(0.8)

pay = reg_model.predict(df)[0]
risk = fraud_model.predict_proba(df)[0][1]

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard",
    "🚨 Risk Analysis",
    "📈 Insights",
    "🔮 Simulation",
    "📄 Upload Slip"
])

# =============================
# TAB 1: DASHBOARD
# =============================
with tab1:
    st.subheader("Overview")

    c1, c2, c3 = st.columns(3)
    c1.metric("Predicted Pay", f"{pay:.0f}")
    c2.metric("Fraud Risk", f"{risk*100:.2f}%")
    c3.metric("Status", "Fraud" if risk > 0.7 else "Normal")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            x=["Salary", "Bonus", "Overtime"],
            y=[salary, bonus, overtime],
            title="Compensation Breakdown",
            labels={'x': 'Component', 'y': 'Amount'}
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.pie(
            names=["Salary", "Bonus", "Overtime"],
            values=[salary, bonus, overtime],
            title="Salary Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

# =============================
# TAB 2: RISK ANALYSIS
# =============================
with tab2:
    st.subheader("Fraud Risk Analysis")

    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk * 100,
        title={'text': "Risk %"},
        gauge={
            'axis': {'range': [0, 100]},
            'steps': [
                {'range': [0, 30], 'color': "#2ecc71"},
                {'range': [30, 70], 'color': "#f1c40f"},
                {'range': [70, 100], 'color': "#e74c3c"}
            ]
        }
    ))

    st.plotly_chart(gauge, use_container_width=True)

    st.divider()

    if risk > 0.7:
        st.error("🚨 High fraud risk detected")
    elif risk > 0.4:
        st.warning("⚠️ Moderate risk detected")
    else:
        st.success("✅ Low risk")

# =============================
# TAB 3: INSIGHTS + AI
# =============================
with tab3:
    st.subheader("Insights & Recommendations")

    st.info(f"Bonus Ratio: {round(bonus/salary*100,2)}%")
    st.info(f"Overtime Ratio: {round(overtime/salary*100,2)}%")

    st.divider()

    st.subheader("AI Recommendations")

    if risk > 0.7:
        st.error("Reduce bonus and overtime immediately")
    elif bonus > salary * 0.3:
        st.warning("Bonus too high compared to salary")
    elif overtime > salary * 0.25:
        st.warning("Overtime unusually high")
    else:
        st.success("Payroll structure is healthy")

# =============================
# TAB 4: SIMULATION
# =============================
with tab4:
    st.subheader("Simulation")

    inc = st.slider("Increase Salary (%)", 0, 50, 10)

    new_salary = salary * (1 + inc/100)
    new_total = new_salary + bonus + overtime

    c1, c2 = st.columns(2)
    c1.metric("New Salary", f"{new_salary:.0f}")
    c2.metric("New Total Pay", f"{new_total:.0f}")

# =============================
# TAB 5: UPLOAD SLIP
# =============================
def extract_salary_data(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for p in pdf.pages:
            t = p.extract_text()
            if t:
                text += t

    st.text_area("Extracted Text", text, height=150)

    def find(keywords):
        for k in keywords:
            m = re.search(rf"{k}.*?([\d,]+)", text, re.IGNORECASE)
            if m:
                return int(m.group(1).replace(",", ""))
        return None

    return {
        "Salary": find(["salary","basic"]) or 50000,
        "Bonus": find(["bonus"]) or 0,
        "Overtime": find(["overtime"]) or 0,
        "Attendance": 26,
        "Experience": 5,
        "Leaves": 2,
        "Country": "India",
        "Department": "IT"
    }

with tab5:
    st.subheader("Upload Salary Slip")

    file = st.file_uploader("Upload PDF", type=["pdf"])

    if file:
        extracted = extract_salary_data(file)

        st.json(extracted)

        df2 = make_input_df(extracted, cols)

        pay2 = reg_model.predict(df2)[0]
        risk2 = fraud_model.predict_proba(df2)[0][1]

        st.metric("Predicted Pay", f"{pay2:.0f}")
        st.metric("Fraud Risk", f"{risk2*100:.2f}%")

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.caption("Final Professional Payroll AI Dashboard")

import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import pdfplumber
import re

from utils.prediction import load_models, make_input_df

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Enterprise Payroll AI", layout="wide")

# -----------------------------
# DATABASE (SQL)
# -----------------------------
conn = sqlite3.connect("payroll.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY,
    name TEXT,
    salary REAL,
    bonus REAL,
    overtime REAL
)
""")

conn.commit()

# -----------------------------
# TAX ENGINE
# -----------------------------
def calculate_tax(salary):
    if salary < 50000:
        return salary * 0.05
    elif salary < 100000:
        return salary * 0.1
    else:
        return salary * 0.2

# -----------------------------
# API FUNCTIONS
# -----------------------------
def add_employee(name, salary, bonus, overtime):
    c.execute("INSERT INTO employees (name, salary, bonus, overtime) VALUES (?,?,?,?)",
              (name, salary, bonus, overtime))
    conn.commit()

def get_employees():
    return pd.read_sql("SELECT * FROM employees", conn)

# -----------------------------
# LOAD MODELS
# -----------------------------
fraud_model, reg_model, cols = load_models()

# -----------------------------
# ROLE SYSTEM
# -----------------------------
role = st.sidebar.selectbox("Select Role", ["HR", "Admin"])

st.title("💼 Enterprise Payroll Intelligence")

# -----------------------------
# ADMIN PANEL
# -----------------------------
if role == "Admin":
    st.sidebar.subheader("Add Employee")

    name = st.sidebar.text_input("Name")
    salary = st.sidebar.number_input("Salary", 10000, 200000, 50000)
    bonus = st.sidebar.number_input("Bonus", 0, 50000, 10000)
    overtime = st.sidebar.number_input("Overtime", 0, 20000, 2000)

    if st.sidebar.button("Add Employee"):
        add_employee(name, salary, bonus, overtime)
        st.sidebar.success("Employee Added")

# -----------------------------
# LOAD EMPLOYEE DATA
# -----------------------------
df_emp = get_employees()

if len(df_emp) == 0:
    st.warning("No employees in database")
    st.stop()

selected_emp = st.sidebar.selectbox("Select Employee", df_emp["name"])

emp = df_emp[df_emp["name"] == selected_emp].iloc[0]

salary = emp["salary"]
bonus = emp["bonus"]
overtime = emp["overtime"]

# -----------------------------
# CALCULATIONS
# -----------------------------
tax = calculate_tax(salary)
net_pay = salary + bonus + overtime - tax

# -----------------------------
# ML INPUT
# -----------------------------
data = {
    "Salary": salary,
    "Bonus": bonus,
    "Overtime": overtime,
    "Attendance": 26,
    "Experience": 5,
    "Leaves": 2,
    "Country": "India",
    "Department": "IT"
}

df = make_input_df(data, cols)

predicted_pay = reg_model.predict(df)[0]
fraud_prob = fraud_model.predict_proba(df)[0][1]

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Dashboard",
    "Analytics",
    "Upload Slip",
    "Reports"
])

# =============================
# DASHBOARD
# =============================
with tab1:
    st.subheader(f"Employee: {selected_emp}")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Salary", salary)
    c2.metric("Tax", round(tax,2))
    c3.metric("Net Pay", round(net_pay,2))
    c4.metric("Fraud Risk", f"{fraud_prob*100:.2f}%")

    fig = px.bar(
        x=["Salary","Bonus","Overtime","Tax"],
        y=[salary,bonus,overtime,tax],
        title="Payroll Structure"
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("### 🤖 AI Recommendations")

recs = generate_recommendations(salary, bonus, overtime, tax, fraud_prob)

for r in recs:
    st.write(r)

# =============================
# ANALYTICS
# =============================
with tab2:
    st.subheader("Employee Comparison")

    fig = px.bar(df_emp, x="name", y="salary", color="name")
    st.plotly_chart(fig, use_container_width=True)

# =============================
# PDF EXTRACTION
# =============================
def extract_salary_data(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for p in pdf.pages:
            t = p.extract_text()
            if t:
                text += t

    def find(keywords):
        for k in keywords:
            m = re.search(rf"{k}.*?([\d,]+)", text, re.IGNORECASE)
            if m:
                return int(m.group(1).replace(",", ""))
        return None

    return {
        "Salary": find(["salary"]) or 50000,
        "Bonus": find(["bonus"]) or 0,
        "Overtime": find(["overtime"]) or 0
    }

# =============================
# UPLOAD
# =============================
with tab3:
    st.subheader("Upload Salary Slip")

    file = st.file_uploader("Upload PDF", type=["pdf"])

    if file:
        data = extract_salary_data(file)

        st.write(data)

# =============================
# REPORT
# =============================
with tab4:
    report = pd.DataFrame([{
        "Employee": selected_emp,
        "Salary": salary,
        "Tax": tax,
        "Net Pay": net_pay,
        "Fraud Risk": fraud_prob
    }])

    st.dataframe(report)

    st.download_button(
        "Download Report",
        report.to_csv(index=False),
        "report.csv"
    )

def generate_recommendations(salary, bonus, overtime, tax, fraud_prob):
    recs = []

    # Fraud-based recommendations
    if fraud_prob > 0.7:
        recs.append("🚨 High fraud risk — immediate audit required")
    elif fraud_prob > 0.4:
        recs.append("⚠️ Moderate risk — review payroll carefully")

    # Bonus analysis
    if bonus > salary * 0.3:
        recs.append("⚠️ Bonus too high compared to salary")

    # Overtime analysis
    if overtime > salary * 0.25:
        recs.append("⚠️ Overtime unusually high — verify entries")

    # Tax optimization
    if tax > salary * 0.2:
        recs.append("💡 Tax is high — consider optimizing salary structure")

    # Healthy case
    if fraud_prob < 0.3 and bonus < salary * 0.3 and overtime < salary * 0.2:
        recs.append("✅ Payroll structure is healthy")

    if not recs:
        recs.append("ℹ️ No major issues detected")

    return recs
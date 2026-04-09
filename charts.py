import plotly.express as px

def salary_distribution(df):
    fig = px.histogram(df, x="Salary")
    return fig
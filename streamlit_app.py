import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION & CUSTOM STYLING
# ---------------------------------------------------------
st.set_page_config(
    page_title="Nutrition Data Analysis Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #f7f7e8;
    }
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #0e6b1c;
        color: white;
    }
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p {
        color: white !important;
    }
    /* Dashboard Header */
    .main-header {
        background-color: white;
        padding: 12px;
        border-radius: 6px;
        text-align: center;
        font-size: 28px;
        font-weight: 700;
        color: #1f2937;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        margin-bottom: 18px;
    }
    /* KPI Cards */
    .kpi-card {
        padding: 16px 10px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.12);
        border: 1px solid rgba(0,0,0,0.1);
        color: #111827;
    }
    .kpi-title {
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 26px;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. DATA LOADING (CSV UPLOAD OR SAMPLE DATA)
# ---------------------------------------------------------
@st.cache_data
def generate_sample_data():
    np.random.seed(42)
    categories = [
        "Proteins", "Vegetables", "Grains", "Fruits",
        "Dairy", "Snacks", "Fats & Oils", "Beverages"
    ]
    base_foods = [
        "Almond Milk (Enriched)", "Eggs", "Tofu", "Turkey Breast",
        "Beef", "Chickpeas", "Chicken Breast", "Oatmeal", "Greek Yogurt", "Salmon"
    ]
    n_rows = 1000
    foods = [f"{np.random.choice(base_foods)} (Batch #{np.random.randint(1000, 1600)})" for _ in range(n_rows)]
    cats = np.random.choice(categories, size=n_rows, p=[0.20, 0.16, 0.14, 0.12, 0.11, 0.10, 0.09, 0.08])

    df = pd.DataFrame({
        "Food_Name": foods,
        "Category": cats,
        "Protein_g": np.round(np.random.uniform(1.0, 28.0, n_rows), 2),
        "Sugar_g": np.round(np.random.uniform(0.5, 18.0, n_rows), 2),
        "Calories_kcal": np.round(np.random.uniform(50, 420, n_rows), 2),
        "Fat_g": np.round(np.random.uniform(0.5, 30.0, n_rows), 2),
        "Carbohydrates_g": np.round(np.random.uniform(2.0, 55.0, n_rows), 2),
        "Fiber_g": np.round(np.random.uniform(0.0, 12.0, n_rows), 2),
        "Nutrient_Density_Score": np.round(np.random.uniform(1.5, 9.5, n_rows), 2)
    })
    return df

st.sidebar.title("Filters")

uploaded_file = st.sidebar.file_uploader(" Nutrition CSV ", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(nutrition_data.csv)
else:
    df = generate_sample_data()

# ---------------------------------------------------------
# 3. SIDEBAR FILTERS
# ---------------------------------------------------------
st.sidebar.markdown("### Select category")
all_categories = sorted(df["Category"].dropna().unique().tolist())
selected_categories = st.sidebar.multiselect(
    "Category",
    options=all_categories,
    default=all_categories,
    label_visibility="collapsed"
)

filtered_df = df[df["Category"].isin(selected_categories)]

st.sidebar.markdown("### Select Food")
all_foods = sorted(filtered_df["Food_Name"].dropna().unique().tolist())
selected_foods = st.sidebar.multiselect(
    "Food",
    options=all_foods,
    default=[],
    placeholder="All Foods (or pick specific items)",
    label_visibility="collapsed"
)

if selected_foods:
    filtered_df = filtered_df[filtered_df["Food_Name"].isin(selected_foods)]

# ---------------------------------------------------------
# 4. HEADER & KPI CARDS
# ---------------------------------------------------------
st.markdown('<div class="main-header">Nutrition Data Analysis Dashboard</div>', unsafe_allow_html=True)

total_foods = len(filtered_df)
total_display = f"{total_foods/1000:.1f}K" if total_foods >= 1000 else str(total_foods)
avg_protein = filtered_df["Protein_g"].mean() if total_foods else 0
avg_sugar = filtered_df["Sugar_g"].mean() if total_foods else 0
avg_calories = filtered_df["Calories_kcal"].mean() if total_foods else 0
avg_fat = filtered_df["Fat_g"].mean() if total_foods else 0
avg_nd = filtered_df["Nutrient_Density_Score"].mean() if total_foods else 0

kpi_cols = st.columns(6)
kpis = [
    ("Total No of Foods", total_display, "#b7d7b8"),
    ("Avg Protein", f"{avg_protein:.2f}", "#9bc6e8"),
    ("Avg Sugar", f"{avg_sugar:.2f}", "#b3cfb3"),
    ("Avg calories", f"{avg_calories:.2f}", "#bce0fd"),
    ("Avg Fat", f"{avg_fat:.2f}", "#77b5e5"),
    ("Avg Nutrient Density", f"{avg_nd:.2f}", "#3ea4f0"),
]

for col, (title, val, bg_color) in zip(kpi_cols, kpis):
    col.markdown(
        f"""
        <div class="kpi-card" style="background-color: {bg_color};">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{val}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")

# ---------------------------------------------------------
# 5. ROW 1 CHARTS (DONUT, HORIZONTAL BAR, LINE)
# ---------------------------------------------------------
r1_c1, r1_c2, r1_c3 = st.columns(3)

with r1_c1:
    cat_counts = filtered_df["Category"].value_counts().reset_index()
    cat_counts.columns = ["Category", "Count"]
    fig_donut = px.pie(
        cat_counts,
        names="Category",
        values="Count",
        hole=0.55,
        title="Food Items by Category",
        color_discrete_sequence=px.colors.sequential.Blues_r + px.colors.sequential.Greens_r
    )
    fig_donut.update_traces(textinfo="value+percent", textposition="inside")
    fig_donut.update_layout(height=360, margin=dict(t=45, b=20, l=20, r=20), paper_bgcolor="white")
    st.plotly_chart(fig_donut, use_container_width=True)

with r1_c2:
    top_nd = filtered_df.nlargest(10, "Nutrient_Density_Score").sort_values("Nutrient_Density_Score")
    fig_nd = px.bar(
        top_nd,
        x="Nutrient_Density_Score",
        y="Food_Name",
        orientation="h",
        title="Top 10 Foods by Nutrient Density",
        color_discrete_sequence=["#7aa87c"]
    )
    fig_nd.update_layout(
        height=360,
        margin=dict(t=45, b=20, l=20, r=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        yaxis_title="",
        xaxis_title="Nutrient Density Score"
    )
    st.plotly_chart(fig_nd, use_container_width=True)

with r1_c3:
    top_fat = filtered_df.nlargest(10, "Fat_g")
    fig_fat = px.line(
        top_fat,
        x="Food_Name",
        y="Fat_g",
        markers=True,
        title="Top 10 Foods by Fat",
        color_discrete_sequence=["#4b5563"]
    )
    fig_fat.update_layout(
        height=360,
        margin=dict(t=45, b=20, l=20, r=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis_title="Food Name",
        yaxis_title="Fat (g)"
    )
    fig_fat.update_xaxes(tickangle=0, tickfont=dict(size=9))
    st.plotly_chart(fig_fat, use_container_width=True)

# ---------------------------------------------------------
# 6. ROW 2 CHARTS (MULTI-LINE, AREA, FUNNEL)
# ---------------------------------------------------------
r2_c1, r2_c2, r2_c3 = st.columns(3)

with r2_c1:
    cat_sums = filtered_df.groupby("Category")[["Carbohydrates_g", "Calories_kcal", "Fiber_g"]].sum().reset_index()
    fig_multi = go.Figure()
    fig_multi.add_trace(go.Scatter(x=cat_sums["Category"], y=cat_sums["Calories_kcal"], mode="lines+markers", name="Calories (kcal)", line=dict(color="#1d4ed8")))
    fig_multi.add_trace(go.Scatter(x=cat_sums["Category"], y=cat_sums["Carbohydrates_g"], mode="lines+markers", name="Carbohydrates (g)", line=dict(color="#60a5fa")))
    fig_multi.add_trace(go.Scatter(x=cat_sums["Category"], y=cat_sums["Fiber_g"], mode="lines+markers", name="Fiber (g)", line=dict(color="#15803d")))
    fig_multi.update_layout(
        title="Comparison of Carbs, Calories & Fiber by Category",
        height=360,
        margin=dict(t=45, b=20, l=20, r=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_multi, use_container_width=True)

with r2_c2:
    top_prot = filtered_df.nlargest(10, "Protein_g")
    fig_area = px.area(
        top_prot,
        x="Food_Name",
        y="Protein_g",
        title="Top 10 Foods by Protein",
        color_discrete_sequence=["#b7d7b8"]
    )
    fig_area.update_layout(
        height=360,
        margin=dict(t=45, b=20, l=20, r=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis_title="Food Name",
        yaxis_title="Protein (g)"
    )
    fig_area.update_xaxes(tickfont=dict(size=9))
    st.plotly_chart(fig_area, use_container_width=True)

with r2_c3:
    top_sugar = filtered_df.nlargest(10, "Sugar_g")
    fig_funnel = px.funnel(
        top_sugar,
        x="Sugar_g",
        y="Food_Name",
        title="Top 10 Foods by Sugar",
        color_discrete_sequence=["#6b9e6d"]
    )
    fig_funnel.update_layout(
        height=360,
        margin=dict(t=45, b=20, l=20, r=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        yaxis_title=""
    )
    st.plotly_chart(fig_funnel, use_container_width=True)

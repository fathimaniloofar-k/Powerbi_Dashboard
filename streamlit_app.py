import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Nutrition Dashboard")

st.title("Nutrition Dashboard")
st.markdown("This dashboard displays interactive data from your exported Power BI file.")

try:
    # Fix: Added sep=r'\s+' to properly handle your space-separated data file
    df = pd.read_csv("nutrition_data.csv", sep=r'\s+')
    
    # Clean up column headers if any formatting artifacts exist
    df.columns = df.columns.str.strip()

    # Sidebar Filter using 'Category' if it exists, otherwise fall back gracefully
    if "Category" in df.columns:
        categories = df["Category"].unique()
        selected_category = st.sidebar.selectbox("Select Food Category", categories)
        filtered_df = df[df["Category"] == selected_category]
    else:
        filtered_df = df

    # 1. Dataset Explorer
    st.subheader("📋 Dataset Explorer")
    st.dataframe(filtered_df, use_container_width=True)
    
    # 2. Numerical Visualizations
    st.subheader("📈 Numerical Visualizations")
    
    # Automatically convert numerical columns to proper numeric types
    for col in df.columns:
        if col not in ["Food_ID", "Food_Name", "Category"]:
            filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')
            
    numeric_cols = filtered_df.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) > 0:
        # Default chart metrics
        y_metric = "Calories_kcal" if "Calories_kcal" in numeric_cols else numeric_cols[0]
        x_metric = "Food_Name" if "Food_Name" in filtered_df.columns else None
        
        st.write(f"Showing **{y_metric}** across items:")
        st.bar_chart(data=filtered_df.head(20), x=x_metric, y=y_metric)
    else:
        st.warning("Could not convert values to numbers. Double check your data file structure.")

except Exception as e:
    st.error(f"An error occurred while loading data: {e}")

    
   

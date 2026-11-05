import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="Nutrition Dashboard")

st.title("Nutrition Dashboard")
st.markdown("This dashboard displays interactive data from your exported Power BI file.")

try:
    # 2. Load the dataset (using your exact filename)
    df = pd.read_csv("nutrition_data.csv")
    
    # 3. Dynamic Category Filtering
    # Looks for a 'Category' column; falls back to the first text column if not found
    text_cols = df.select_dtypes(include=['object']).columns.tolist()
    category_col = "Category" if "Category" in df.columns else (text_cols[0] if text_cols else None)
    
    if category_col:
        categories = df[category_col].dropna().unique()
        selected_category = st.sidebar.selectbox(f"Select {category_col}", categories)
        filtered_df = df[df[category_col] == selected_category]
    else:
        filtered_df = df

    # 4. Interactive Data Table View
    st.subheader("📋 Dataset Explorer")
    st.dataframe(filtered_df, use_container_width=True)
    
    # 5. Interactive Bar Chart
    st.subheader("📈 Numerical Visualizations")
    numeric_cols = filtered_df.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) > 0:
        # Automatically select the first numeric column to plot
        chosen_metric = numeric_cols[0]
        
        # Determine a safe label/index column for the X-axis
        x_axis_col = "Food_Name" if "Food_Name" in filtered_df.columns else (text_cols[0] if text_cols else None)
        
        if x_axis_col:
            st.bar_chart(data=filtered_df.head(20), x=x_axis_col, y=chosen_metric)
        else:
            st.bar_chart(data=filtered_df.head(20)[numeric_cols])
    else:
        st.warning("No numeric columns found in the dataset to plot a chart.")

except FileNotFoundError:
    st.error("Error: Could not find 'nutrition_data.csv'. Verify the filename matches exactly on GitHub.")
except Exception as e:
    st.error(f"An error occurred: {e}")


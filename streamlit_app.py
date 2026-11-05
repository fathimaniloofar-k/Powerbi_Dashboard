import streamlit as st
import pandas as pd
import csv

st.set_page_config(layout="wide", page_title="Nutrition Dashboard")

st.title("🥗 Student Project Nutrition Dashboard")
st.markdown("This dashboard displays interactive data from your exported Power BI file.")

try:
    # Safe Line-by-Line Reading to handle messy whitespace cleanly
    cleaned_rows = []
    with open("nutrition_data.csv", "r", encoding="utf-8") as f:
        # Split purely by tabs or multiple spaces, treating strings gracefully
        reader = csv.reader(f, delimiter='\t')
        for row in f:
            # Split line by whitespace but merge trailing artifacts if necessary
            parts = row.strip().split()
            if parts:
                cleaned_rows.append(parts)
                
    if len(cleaned_rows) > 1:
        headers = cleaned_rows[0]
        data_rows = cleaned_rows[1:]
        
        # Adjust rows dynamically if lengths don't match the header count
        standardized_rows = []
        for r in data_rows:
            if len(r) > len(headers):
                # If there are extra fields, combine the food name items together
                # This fixes names like "Cucumbers (Batch #1019)" being broken up
                diff = len(r) - len(headers)
                name_idx = 1
                combined_name = " ".join(r[name_idx : name_idx + diff + 1])
                new_row = r[:name_idx] + [combined_name] + r[name_idx + diff + 1:]
                standardized_rows.append(new_row)
            elif len(r) == len(headers):
                standardized_rows.append(r)
            else:
                # Pad shorter rows with empty values so pandas doesn't break
                standardized_rows.append(r + [""] * (len(headers) - len(r)))
                
        df = pd.DataFrame(standardized_rows, columns=headers)
    else:
        # Fallback to direct reading if file layout structure is standard
        df = pd.read_csv("nutrition_data.csv", sep=r'\s+', on_bad_lines='skip')

    # Convert numeric metrics safely
    for col in df.columns:
        if col not in ["Food_ID", "Food_Name", "Category"]:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Sidebar Filter using 'Category' column
    category_col = "Category" if "Category" in df.columns else df.columns[2]
    categories = df[category_col].dropna().unique()
    selected_category = st.sidebar.selectbox(f"Select {category_col}", categories)
    filtered_df = df[df[category_col] == selected_category]

    # 1. Dataset Explorer Table
    st.subheader("📋 Dataset Explorer")
    st.dataframe(filtered_df, use_container_width=True)
    
    # 2. Bar Chart Visualization
    st.subheader("📈 Numerical Visualizations")
    numeric_cols = filtered_df.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) > 0:
        y_metric = "Calories_kcal" if "Calories_kcal" in numeric_cols else numeric_cols[0]
        x_metric = "Food_Name" if "Food_Name" in filtered_df.columns else df.columns[1]
        
        st.write(f"Showing **{y_metric}** across filtered items:")
        st.bar_chart(data=filtered_df.head(20), x=x_metric, y=y_metric)
    else:
        st.warning("No numeric data columns could be generated. Please review formatting.")

except Exception as e:
    st.error(f"An error occurred while loading data: {e}")


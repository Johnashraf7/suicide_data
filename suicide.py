import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Set page configuration
st.set_page_config(
    page_title="Suicide Rates Analysis",
    page_icon="📊",
    layout="wide"
)


def load_data():
    df = pd.read_csv('master.csv')
    
    
    df = df.drop('HDI for year', axis=1)
    
    def label_age_group(age):
        if '5-14' in age:
            return 'Child'
        elif '15-24' in age:
            return 'Youth'
        elif '25-34' in age:
            return 'Young Adult'
        elif '35-54' in age:
            return 'Adult'
        elif '55-74' in age:
            return 'Older Adult'
        elif '75+' in age:
            return 'Senior'
        else:
            return 'Unknown'
    
    df['age_group'] = df['age'].apply(label_age_group)
    return df

df = load_data()


st.sidebar.title("📊 Navigation")
page = st.sidebar.radio("Go to", ["Data Overview", "Descriptive Analysis", "Data Analysis"])

# Page 1: Data Overview
if page == "Data Overview":
    st.title("📈 Suicide Rates Data Overview")
    
    st.header("Dataset Preview")
    st.dataframe(df.head(10))
    
    st.header("Dataset Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Basic Info")
        st.write(f"**Number of rows:** {df.shape[0]}")
        st.write(f"**Number of columns:** {df.shape[1]}")
        st.write(f"**Data types:**")
        st.write(df.dtypes.value_counts())
    
    with col2:
        st.subheader("Missing Values")
        missing_data = df.isnull().sum()
        st.write(missing_data[missing_data > 0])
    
    st.header("🧾 Column Description Table")
    
    column_descriptions = {
        'country': 'Name of the country where the data was recorded.',
        'year': 'Year in which the data was collected.',
        'sex': 'Gender of the individuals in the recorded group (male or female).',
        'age': 'Age group category of the individuals.',
        'suicides_no': 'Total number of suicides reported for the given group.',
        'population': 'Total population of the given group.',
        'suicides/100k pop': 'Suicide rate per 100,000 people in the given group.',
        'country-year': 'Combined identifier for country and year (used as a unique key).',
        'gdp_for_year ($)': 'Total Gross Domestic Product for the country in that year (in USD).',
        'gdp_per_capita ($)': 'GDP per capita for the country in that year (in USD).',
        'generation': 'Generation cohort of the individuals (e.g., Generation X, Boomers).',
        'age_group': 'Simplified age group category (derived from age column).'
    }
    
    desc_df = pd.DataFrame(list(column_descriptions.items()), columns=['Column', 'Description'])
    st.table(desc_df)

# Page 2: Descriptive Analysis
elif page == "Descriptive Analysis":
    st.title("📊 Descriptive Analysis")
    
    st.header("Basic Statistics")
    
    # Numerical columns statistics
    numerical_cols = ['year', 'suicides_no', 'population', 'suicides/100k pop', 'gdp_per_capita ($)']
    st.subheader("Numerical Variables Summary")
    st.dataframe(df[numerical_cols].describe())
    
    # Categorical columns statistics
    st.subheader("Categorical Variables Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Countries Count:**", df['country'].nunique())
        st.write("**Years Range:**", f"{df['year'].min()} - {df['year'].max()}")
    
    with col2:
        st.write("**Gender Distribution:**")
        st.write(df['sex'].value_counts())
    
    with col3:
        st.write("**Age Group Distribution:**")
        st.write(df['age_group'].value_counts())
    
    st.header("Data Quality Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Missing Values")
        missing_percent = (df.isnull().sum() / len(df)) * 100
        missing_df = pd.DataFrame({'Missing Count': df.isnull().sum(),'Missing Percentage': missing_percent})
        st.dataframe(missing_df[missing_df['Missing Count'] > 0])
    
    with col2:
        st.subheader("Duplicate Records")
        st.write(f"**Number of duplicate rows:** {df.duplicated().sum()}")

# Page 3: Data Analysis 
elif page == "Data Analysis":
    st.title("🔍 Data Analysis with Interactive Visualizations")
    
    st.header("Global Suicide Rates Analysis")
    
    # Question 1: Global suicide rate over time
    st.subheader("1. How have suicide rates changed from year to year globally?")
    
    yearly = df.groupby('year', as_index=False).agg({'suicides_no': 'sum','population': 'sum'})
    yearly['suicides_per_100k'] = (yearly['suicides_no'] / yearly['population']) * 100000
    
    linegraph = px.line(yearly, x='year', y='suicides_per_100k', title='Global Suicide Rate per 100k Over Time (1985-2016)',labels={'suicides_per_100k': 'Suicides per 100k', 'year': 'Year'})
    linegraph.update_traces(mode='markers+lines', line=dict(width=3))
    st.plotly_chart(linegraph, use_container_width=True)
    
    # Question 2: Suicide rates by age group
    st.subheader("2. Which age group has the highest average suicide rate globally?")
    
    age_grp = df.groupby('age_group', as_index=False).agg({'suicides_no': 'sum','population': 'sum'})
    age_grp['suicides_per_100k'] = (age_grp['suicides_no'] / age_grp['population']) * 100000
    age_grp = age_grp.sort_values('suicides_per_100k', ascending=False)
    
    bargarph = px.bar(age_grp, x='age_group', y='suicides_per_100k', title='Suicide Rate per 100k by Age Group (Global)', labels={'suicides_per_100k': 'Suicides per 100k', 'age_group': 'Age Group'}, color='suicides_per_100k',color_continuous_scale='Viridis')
    st.plotly_chart(bargarph, use_container_width=True)
    
    # Question 3: Suicide rates by age group and gender
    st.subheader("3. Within each age group, do males or females have higher suicide rates?")
    
    age_sex = df.groupby(['age_group', 'sex'], as_index=False).agg({'suicides_no': 'sum', 'population': 'sum'})
    age_sex['suicides_per_100k'] = (age_sex['suicides_no'] / age_sex['population']) * 100000
    
    bargarph2 = px.bar(age_sex, x='age_group', y='suicides_per_100k', color='sex', barmode='group', title='Suicide Rate per 100k by Age Group and Gender', labels={'suicides_per_100k': 'Suicides per 100k'}, color_discrete_map={'male': 'blue', 'female': 'red'})
    st.plotly_chart(bargarph2, use_container_width=True)
    
    # Question 4: Top countries by suicide rates with slider
    st.subheader("4. Which countries have the highest average suicide rates?")

    # Add a slider for number of countries
    num_countries = st.slider("Select number of countries to display:", min_value=5,max_value=30, value=15,step=1,help="Choose how many top countries to show in the bar chart")

    country_stats = df.groupby('country', as_index=False).agg({'suicides_no': 'sum','population': 'sum'})
    country_stats['suicides_per_100k'] = (country_stats['suicides_no'] / country_stats['population']) * 100000
    top_countries = country_stats.sort_values('suicides_per_100k', ascending=False).head(num_countries)

    # Display the number of countries selected
    st.write(f"Showing top **{num_countries}** countries by suicide rate")

    bargarph3 = px.bar(top_countries, x='country', y='suicides_per_100k', title=f'Top {num_countries} Countries by Suicide Rate per 100k', labels={'suicides_per_100k': 'Suicides per 100k', 'country': 'Country'}, color='suicides_per_100k', color_continuous_scale='Reds')
    bargarph3.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(bargarph3 , use_container_width=True)

    # Optional: Add a data table below the chart
    with st.expander("View detailed data table"):
        display_table = top_countries[['country', 'suicides_per_100k', 'suicides_no', 'population']].copy()
        display_table['suicides_per_100k'] = display_table['suicides_per_100k'].round(2)
        st.dataframe(display_table.sort_values('suicides_per_100k', ascending=False))
        
    # Question 5: Suicide rates by generation over time
    st.subheader("5. How have suicide rates changed by generation?")
        
    if 'generation' in df.columns:
        gen_df = df.groupby(['year', 'generation'], as_index=False).agg({'suicides_no': 'sum','population': 'sum'})
        gen_df['suicides_per_100k'] = (gen_df['suicides_no'] / gen_df['population']) * 100000
            
        linechart = px.line(gen_df, x='year', y='suicides_per_100k', color='generation', title='Suicide Rate per 100k by Generation Over Time', labels={'suicides_per_100k': 'Suicides per 100k'}, color_discrete_sequence=px.colors.qualitative.Set1)
        st.plotly_chart(linechart, use_container_width=True)
        
    # Question 6: Heatmap of suicide rates by age and gender
    st.subheader("6. Which age and gender combinations have the highest rates?")
        
    heat_df = df.groupby(['age_group', 'sex'], as_index=False).agg({'suicides_no': 'sum','population': 'sum'})
    heat_df['suicides_per_100k'] = (heat_df['suicides_no'] / heat_df['population']) * 100000
    heat_pivot = heat_df.pivot(index='age_group', columns='sex', values='suicides_per_100k').fillna(0)
        
    heatmap = px.imshow(heat_pivot, title='Heatmap of Suicide Rate per 100k by Age Group and Gender', labels={'x': 'Gender', 'y': 'Age Group', 'color': 'Suicides per 100k'},color_continuous_scale='Viridis', aspect="auto")
    st.plotly_chart(heatmap, use_container_width=True)
        
    # Additional insights
    st.header("🔍 Key Insights")
    
    insights = """
    - **Global Trend**: Suicide rates showed significant variation over the years with notable peaks and declines
    - **Age Pattern**: Older adults and seniors typically show higher suicide rates
    - **Gender Gap**: Males consistently show higher suicide rates across all age groups
    - **Geographic Variation**: Eastern European countries like Lithuania and Russia show particularly high rates
    - **Generational Differences**: Different generations show distinct patterns over time
    """
    
    st.markdown(insights)


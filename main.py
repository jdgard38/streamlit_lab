import pandas as pd
import zipfile
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from io import BytesIO
import streamlit as st

## LOAD DATA DIRECTLY FROM SS WEBSITE
@st.cache_data
def load_name_data():
    names_file = 'https://www.ssa.gov/oact/babynames/names.zip'
    response = requests.get(names_file)
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        dfs = []
        files = [file for file in z.namelist() if file.endswith('.txt')]
        for file in files:
            with z.open(file) as f:
                df = pd.read_csv(f, header=None)
                df.columns = ['name','sex','count']
                df['year'] = int(file[3:7])
                dfs.append(df)
        data = pd.concat(dfs, ignore_index=True)
    data['pct'] = data['count'] / data.groupby(['year', 'sex'])['count'].transform('sum')
    return data

df = load_name_data()



df['total_births'] = df.groupby(['year', 'sex'])['count'].transform('sum')
df['prop'] = df['count'] / df['total_births']

st.title('My Name App')


tab1, tab2, tab3 = st.tabs(['Overall', 'By Name', 'By Year'])

with tab1:
    st.write('Here is stuff about all the data')

with tab2:
    st.write('Name')
    # pick a name
    noi = st.text_input('Enter a name')
    plot_female = st.checkbox('Plot female line')
    plot_male = st.checkbox('Plot male line')
    name_df = df[df['name']==noi]

    fig = plt.figure(figsize=(15, 8))

    if plot_female:
        sns.lineplot(data=name_df[name_df['sex'] == 'F'], x='year', y='prop', label='Female')

    if plot_male:
        sns.lineplot(data=name_df[name_df['sex'] == 'M'], x='year', y='prop', label='Male')

    plt.title(f'Popularity of {noi} over time')
    plt.xlim(1880, 2025)
    plt.xlabel('Year')
    plt.ylabel('Proportion')
    plt.xticks(rotation=90)
    plt.legend()
    plt.tight_layout()

    st.pyplot(fig)

with tab3: 
    st.write('Year')
    noi3 = st.text_input('Enter a name', key='name3')
    year_selection = st.slider("Select a year or range of years", 1880, 2025, (1880, 2025))

    # Filter data based on name and year range
    name_data = df[(df['name'] == noi3) & (df['year'].between(year_selection[0], year_selection[1]))]

    if not name_data.empty:
        sex_counts = name_data.groupby('sex').sum()['count']
        male_count = sex_counts.get('M', 0)
        female_count = sex_counts.get('F', 0)
        total_count = male_count + female_count
        
        if total_count > 0:
            male_ratio = male_count / total_count
            female_ratio = female_count / total_count

            fig, ax = plt.subplots(figsize=(10, 2))

            # Create stacked bar representing male and female ratios
            ax.barh(0, male_ratio, label='Male', color='blue')
            ax.barh(0, female_ratio, left=male_ratio, label='Female', color='pink')

            # Customize the chart
            ax.set_xlim(0, 1)
            ax.set_xticks([0, 0.5, 1])
            ax.set_xticklabels(['0%', '50%', '100%'])
            ax.set_yticks([])  # Hide y-axis ticks

            # Add labels to display the ratios
            ax.text(male_ratio / 2, 0, f"{male_ratio * 100:.1f}%", va='center', 
                    ha='center', color='white', fontweight='bold', fontsize=20)
            ax.text(male_ratio / 2, -0.25, "Male", va='center', 
                    ha='center', color='white', fontweight='bold', fontsize=20)
            ax.text(male_ratio + female_ratio / 2, 0, f"{female_ratio * 100:.1f}%", va='center', 
                    ha='center', color='white', fontweight='bold', fontsize=20)
            ax.text(male_ratio + female_ratio / 2, -0.25, "Female", va='center', 
                    ha='center', color='white', fontweight='bold', fontsize=20)

            plt.title(f"Sex Balance of '{noi3}' ({year_selection[0]}-{year_selection[1]})")
            st.pyplot(fig)
        else:
            st.write(f"No data available for '{noi3}' in the selected year range.")
    else:
        st.write(f"No data available for '{noi3}'.")


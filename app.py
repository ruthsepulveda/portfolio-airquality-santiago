import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Page config
st.set_page_config(
    page_title='Aire Santiago',
    page_icon='🌬️',
    layout='wide'
)

# Load data
@st.cache_data
def load_data():
    return pd.read_parquet('data/interim/air_quality_daily.parquet')

df = load_data()

# Sidebar controls
st.sidebar.title('Filters')
stations = sorted(df['station'].unique())
selected_station = st.sidebar.selectbox('Station', stations)

# Get date range for the selected station
station_dates = df[df['station'] == selected_station]['date']
station_min_date = station_dates.min().date()
station_max_date = station_dates.max().date()

st.sidebar.markdown('**Date range**')
preset = st.sidebar.radio(
    'Quick select',
    ['Full period', 'Last 3 years', 'Last 2 years', 'Last year', 'Custom'],
    index=0
)

if preset == 'Full period':
    start_date, end_date = station_min_date, station_max_date
elif preset == 'Last 3 years':
    start_date = max(station_min_date, (pd.Timestamp(station_max_date) - pd.DateOffset(years=3)).date())
    end_date = station_max_date
elif preset == 'Last 2 years':
    start_date = max(station_min_date, (pd.Timestamp(station_max_date) - pd.DateOffset(years=2)).date())
    end_date = station_max_date
elif preset == 'Last year':
    start_date = max(station_min_date, (pd.Timestamp(station_max_date) - pd.DateOffset(years=1)).date())
    end_date = station_max_date
elif preset == 'Custom':
    date_range = st.sidebar.date_input(
        'Select dates',
        value=(station_min_date, station_max_date),
        min_value=station_min_date,
        max_value=station_max_date
    )
    start_date, end_date = date_range[0], date_range[1]

st.sidebar.caption(f'Data available: {station_min_date} to {station_max_date}')

# Filter data
df_filtered = df[
    (df['station'] == selected_station) &
    (df['date'].dt.date >= start_date) &
    (df['date'].dt.date <= end_date)
].copy()

# Title
st.title('🌬️ Aire Santiago — PM2.5 Air Quality Explorer')
st.markdown('PM2.5 air quality data from SINCA monitoring stations across Santiago\'s Región Metropolitana (2020–2025).')

tab1, tab2, tab3 = st.tabs(['📈 Tendencia', '📅 Estacionalidad', '📊 Comparación'])

# Tab 1 - Tendencia
with tab1:
    st.subheader(f'PM2.5 Trend — {selected_station}')
    
    compare_mode = st.checkbox('Compare with another station')
    
    if compare_mode:
        compare_station = st.selectbox(
            'Compare with',
            [s for s in stations if s != selected_station]
        )
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric('Mean PM2.5', f'{df_filtered["pm25_mean"].mean():.1f} µg/m³')
    col2.metric('Max recorded', f'{df_filtered["pm25_mean"].max():.1f} µg/m³')
    col3.metric('Days over norm', f'{df_filtered["exceeds_norm"].mean()*100:.1f}%')
    
    # Rolling average
    df_filtered['rolling_7d'] = df_filtered['pm25_mean'].rolling(window=7).mean()
    
    fig1 =go.Figure()
    if compare_mode:
        df_compare = df[
            (df['station'] == compare_station) &
            (df['date'].dt.date >= start_date) &
            (df['date'].dt.date <= end_date)
        ].copy()
        df_compare['rolling_7d'] = df_compare['pm25_mean'].rolling(window=7).mean()

    if not compare_mode:
        fig1.add_trace(go.Scatter(
            x=df_filtered['date'], y=df_filtered['pm25_mean'],
            name=f'{selected_station} — Daily',
            line=dict(color='#888888', width=0.8),
            opacity=0.4
        ))

    fig1.add_trace(go.Scatter(
        x=df_filtered['date'], y=df_filtered['rolling_7d'],
        name=f'{selected_station} — 7-day avg',
        line=dict(color='#e63946', width=2.5)
    ))

    # Highlight days over norm
    df_exceeds = df_filtered[df_filtered['exceeds_norm'] == True]
    fig1.add_trace(go.Scatter(
        x=df_exceeds['date'],
        y=df_exceeds['pm25_mean'],
        mode='markers',
        name='Exceeds norm',
        marker=dict(color='#f4a261', size=4, opacity=0.8)
    ))

    if compare_mode:
        fig1.add_trace(go.Scatter(
            x=df_compare['date'], y=df_compare['rolling_7d'],
            name=f'{compare_station} — 7-day avg',
            line=dict(color='#3a7dbf', width=2.5)
        ))

    fig1.add_hline(y=50, line_dash='dash', line_color='gray',
                   annotation_text='Legal standard (50 µg/m³)')
    fig1.update_layout(xaxis_title='Date', yaxis_title='PM2.5 (µg/m³)', height=400)
    st.plotly_chart(fig1, use_container_width=True)

    if compare_mode:
        mean_selected = df_filtered['pm25_mean'].mean()
        mean_compare = df_compare['pm25_mean'].mean()
        diff = abs(mean_selected - mean_compare)
        worse = selected_station if mean_selected > mean_compare else compare_station
        
        st.markdown(f"""
        **Comparison summary:** {selected_station} averaged **{mean_selected:.1f} µg/m³** 
        vs {compare_station} at **{mean_compare:.1f} µg/m³** over the selected period, 
        a difference of **{diff:.1f} µg/m³**. {worse} recorded worse air quality on average.
        """)

# Tab 2 - Estacionalidad
with tab2:
    st.subheader(f'Seasonal Pattern — {selected_station}')
    
    monthly = df_filtered.groupby('month')['pm25_mean'].mean().reset_index()
    month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                   7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    monthly['month_name'] = monthly['month'].map(month_names)
    
    fig2 = px.bar(
        monthly,
        x='month_name',
        y='pm25_mean',
        title=f'Average PM2.5 by Month — {selected_station}',
        labels={'month_name': 'Month', 'pm25_mean': 'Mean PM2.5 (µg/m³)'},
        color_discrete_sequence=['#2d6a4f']
    )
    fig2.add_hline(y=50, line_dash='dash', line_color='gray',
                   annotation_text='Legal standard (50 µg/m³)')
    
    fig2.add_vrect(
        x0=4.5, x1=7.5,
        fillcolor='#457b9d',
        opacity=0.08,
        layer='below',
        line_width=0
    )

    fig2.add_annotation(
        x=6, y=monthly['pm25_mean'].max() * 1.05,
        text='Winter',
        showarrow=False,
        font=dict(size=11, color='#2d6a4f')
    )

    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("""
    **Why is winter worse?** Santiago sits in a basin surrounded by mountains. 
    During winter, cold air near the ground gets trapped under warmer air above 
    (temperature inversion), preventing pollution from dispersing. Combined with 
    wood-burning heating, this creates the PM2.5 peaks seen in June–August.
    """)

# Tab 3 - Comparación
with tab3:
    st.subheader('Station Comparison — All Stations (2020–2025)')
    
    st.info("""
    **Note on data coverage:** Not all stations cover the full 2020–2025 period. 
    Cerrillos II has data from April 2022 only, Talagante from mid-2021, and 
    El Bosque and Cerrillos II through early March 2025. Stations with partial 
    coverage may show lower means due to missing winter months.
    """)

    station_means = df.groupby('station')['pm25_mean'].mean().sort_values(
        ascending=True).reset_index()
    
    fig3 = px.bar(
        station_means,
        x='pm25_mean',
        y='station',
        orientation='h',
        title='Mean PM2.5 by Station',
        labels={'pm25_mean': 'Mean PM2.5 (µg/m³)', 'station': 'Station'},
        color_discrete_sequence=['#2d6a4f']
    )
    fig3.add_vline(x=50, line_dash='dash', line_color='gray',
                   annotation_text='Legal standard')
    fig3.update_layout(height=450)
    st.plotly_chart(fig3, use_container_width=True)
    
    st.dataframe(
        station_means.sort_values('pm25_mean', ascending=False).reset_index(drop=True),
        use_container_width=True
    )

# Footer
st.markdown('---')
st.markdown('Data source: [SINCA](https://sinca.mma.gob.cl) — Ministerio del Medio Ambiente, Chile')
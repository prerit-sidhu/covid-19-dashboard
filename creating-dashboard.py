import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
import numpy as np
from datetime import datetime, timedelta

# Load your cleaned dataset
df = pd.read_csv('./data/cleaned_covid_data.csv')

# Enhanced Streamlit App Configuration
st.set_page_config(
    page_title="🌍 COVID-19 Global Analytics Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .main-title {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        text-align: center;
        margin-top: 0.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        margin: 1rem 0;
    }
    .stSelectbox > div > div > div {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 10px;
    }
    .section-header {
        background: linear-gradient(90deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-weight: bold;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced Header
st.markdown("""
<div class="main-header">
    <h1 class="main-title">🌍 COVID-19 Global Analytics Dashboard</h1>
    <p class="subtitle">Real-time insights and trends from around the world</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for controls
with st.sidebar:
    st.markdown("### 🎛️ Dashboard Controls")
    
    # Country selection with search
    countries = df['location'].dropna().unique()
    country = st.selectbox(
        "🌍 Select a Country",
        sorted(countries),
        help="Choose a country to analyze COVID-19 data"
    )
    
    # Date range filter
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        min_date = df['date'].min()
        max_date = df['date'].max()
        
        date_range = st.date_input(
            "📅 Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    
    st.markdown("---")
    st.markdown("### 📊 Visualization Options")
    show_trends = st.checkbox("Show trend lines", True)
    show_moving_avg = st.checkbox("Show moving averages", False)

# Filter data
filtered_df = df[df['location'] == country].sort_values('date')
if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df['date'] >= pd.to_datetime(date_range[0])) &
        (filtered_df['date'] <= pd.to_datetime(date_range[1]))
    ]

# Key Metrics Cards
if not filtered_df.empty:
    latest_data = filtered_df.iloc[-1]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_cases = latest_data.get('total_cases', 0)
        st.markdown(f"""
        <div class="metric-card">
            <h3>📈 Total Cases</h3>
            <h2>{total_cases:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_deaths = latest_data.get('total_deaths', 0)
        st.markdown(f"""
        <div class="metric-card">
            <h3>💔 Total Deaths</h3>
            <h2>{total_deaths:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        new_cases = latest_data.get('new_cases', 0)
        st.markdown(f"""
        <div class="metric-card">
            <h3>🆕 New Cases</h3>
            <h2>{new_cases:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        vaccination_rate = 0
        if pd.notna(latest_data.get('people_vaccinated')) and pd.notna(latest_data.get('population')):
            vaccination_rate = (latest_data['people_vaccinated'] / latest_data['population']) * 100
        st.markdown(f"""
        <div class="metric-card">
            <h3>💉 Vaccination Rate</h3>
            <h2>{vaccination_rate:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)

# Enhanced Main Trend Chart
st.markdown('<div class="section-header">📊 COVID-19 Trend Analysis</div>', unsafe_allow_html=True)

fig_main = make_subplots(
    rows=2, cols=1,
    subplot_titles=('Total Cases & Deaths Over Time', 'Daily New Cases & Deaths'),
    vertical_spacing=0.12,
    specs=[[{"secondary_y": True}], [{"secondary_y": True}]]
)

# Total cases and deaths
fig_main.add_trace(
    go.Scatter(
        x=filtered_df['date'], 
        y=filtered_df['total_cases'],
        mode='lines',
        name='Total Cases',
        line=dict(color='#4facfe', width=3),
        fill='tonexty' if show_trends else None,
        hovertemplate='<b>Total Cases</b><br>Date: %{x}<br>Cases: %{y:,.0f}<extra></extra>'
    ),
    row=1, col=1
)

fig_main.add_trace(
    go.Scatter(
        x=filtered_df['date'], 
        y=filtered_df['total_deaths'],
        mode='lines',
        name='Total Deaths',
        line=dict(color='#ff6b6b', width=3),
        yaxis='y2',
        hovertemplate='<b>Total Deaths</b><br>Date: %{x}<br>Deaths: %{y:,.0f}<extra></extra>'
    ),
    row=1, col=1, secondary_y=True
)

# Daily new cases and deaths
fig_main.add_trace(
    go.Bar(
        x=filtered_df['date'], 
        y=filtered_df['new_cases'],
        name='New Cases',
        marker_color='rgba(79, 172, 254, 0.7)',
        hovertemplate='<b>New Cases</b><br>Date: %{x}<br>Cases: %{y:,.0f}<extra></extra>'
    ),
    row=2, col=1
)

fig_main.add_trace(
    go.Bar(
        x=filtered_df['date'], 
        y=filtered_df['new_deaths'],
        name='New Deaths',
        marker_color='rgba(255, 107, 107, 0.7)',
        yaxis='y4',
        hovertemplate='<b>New Deaths</b><br>Date: %{x}<br>Deaths: %{y:,.0f}<extra></extra>'
    ),
    row=2, col=1, secondary_y=True
)

# Moving averages if enabled
if show_moving_avg and len(filtered_df) > 7:
    filtered_df['new_cases_ma'] = filtered_df['new_cases'].rolling(window=7).mean()
    filtered_df['new_deaths_ma'] = filtered_df['new_deaths'].rolling(window=7).mean()
    
    fig_main.add_trace(
        go.Scatter(
            x=filtered_df['date'], 
            y=filtered_df['new_cases_ma'],
            mode='lines',
            name='7-day avg (Cases)',
            line=dict(color='#1e3d59', width=2, dash='dash')
        ),
        row=2, col=1
    )

fig_main.update_layout(
    height=800,
    showlegend=True,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family="Arial, sans-serif", size=12),
    hovermode='x unified'
)

fig_main.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
fig_main.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')

st.plotly_chart(fig_main, use_container_width=True)

# Case Fatality Rate with enhanced styling
st.markdown('<div class="section-header">⚠️ Case Fatality Rate Analysis</div>', unsafe_allow_html=True)

filtered_df_copy = filtered_df.copy()
filtered_df_copy['cfr'] = (filtered_df_copy['total_deaths'] / filtered_df_copy['total_cases'].replace(0, pd.NA)) * 100

fig_cfr = go.Figure()
fig_cfr.add_trace(go.Scatter(
    x=filtered_df_copy['date'], 
    y=filtered_df_copy['cfr'],
    mode='lines+markers',
    name='CFR (%)',
    line=dict(color='#ff6b6b', width=3),
    marker=dict(size=6, color='#ff6b6b', line=dict(width=2, color='white')),
    fill='tonexty',
    hovertemplate='<b>Case Fatality Rate</b><br>Date: %{x}<br>CFR: %{y:.2f}%<extra></extra>'
))

fig_cfr.update_layout(
    title=dict(text='Case Fatality Rate Over Time', font=dict(size=20)),
    xaxis_title='Date',
    yaxis_title='CFR (%)',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    showlegend=False,
    height=400
)

st.plotly_chart(fig_cfr, use_container_width=True)

# Enhanced Vaccination Visualization
st.markdown('<div class="section-header">💉 Vaccination Progress</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    # Vaccination pie chart with better styling
    if pd.notna(latest_data.get('people_vaccinated')) and pd.notna(latest_data.get('population')):
        vaccinated = latest_data['people_vaccinated']
        unvaccinated = latest_data['population'] - vaccinated
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=['Vaccinated', 'Unvaccinated'], 
            values=[vaccinated, unvaccinated],
            hole=0.4,
            marker=dict(colors=['#4facfe', '#ff9a9e']),
            textinfo='label+percent',
            textfont=dict(size=14),
            hovertemplate='<b>%{label}</b><br>Count: %{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig_pie.update_layout(
            title=dict(text="Vaccination Distribution", font=dict(size=18)),
            showlegend=True,
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    # Vaccination progress gauge (replacing radar chart)
    vaccination_percentage = vaccination_rate
    
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = vaccination_percentage,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Vaccination Progress"},
        delta = {'reference': 50, 'position': "top"},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#4facfe"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 25], 'color': '#ff9a9e'},
                {'range': [25, 50], 'color': '#feca57'},
                {'range': [50, 75], 'color': '#48dbfb'},
                {'range': [75, 100], 'color': '#0abde3'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig_gauge.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "darkblue", 'family': "Arial"}
    )
    
    st.plotly_chart(fig_gauge, use_container_width=True)

# Stringency Index with area chart
st.markdown('<div class="section-header">🏛️ Government Response Stringency</div>', unsafe_allow_html=True)

fig_stringency = go.Figure()
fig_stringency.add_trace(go.Scatter(
    x=filtered_df['date'], 
    y=filtered_df['stringency_index'],
    mode='lines',
    name='Stringency Index',
    line=dict(color='#9c88ff', width=3),
    fill='tonexty',
    hovertemplate='<b>Stringency Index</b><br>Date: %{x}<br>Index: %{y:.1f}<extra></extra>'
))

fig_stringency.update_layout(
    title=dict(text="Government Response Stringency Over Time", font=dict(size=20)),
    xaxis_title='Date',
    yaxis_title='Stringency Index (0-100)',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    showlegend=False,
    height=400
)

fig_stringency.update_yaxes(range=[0, 100])
st.plotly_chart(fig_stringency, use_container_width=True)

# Country Profile Cards (replacing radar chart)
st.markdown('<div class="section-header">🌍 Country Profile Overview</div>', unsafe_allow_html=True)

if not filtered_df.empty:
    latest = filtered_df.dropna(subset=['median_age', 'population_density', 'gdp_per_capita']).iloc[-1] if len(filtered_df.dropna(subset=['median_age', 'population_density', 'gdp_per_capita'])) > 0 else None
    
    if latest is not None:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            median_age = latest.get('median_age', 0)
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); padding: 1.5rem; border-radius: 15px; text-align: center; margin: 0.5rem;">
                <h4>👥 Median Age</h4>
                <h2>{median_age:.1f} years</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            pop_density = latest.get('population_density', 0)
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); padding: 1.5rem; border-radius: 15px; text-align: center; margin: 0.5rem;">
                <h4>🏘️ Population Density</h4>
                <h2>{pop_density:.1f}/km²</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            gdp_per_capita = latest.get('gdp_per_capita', 0)
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%); padding: 1.5rem; border-radius: 15px; text-align: center; margin: 0.5rem;">
                <h4>💰 GDP per Capita</h4>
                <h2>${gdp_per_capita:,.0f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            hdi = latest.get('human_development_index', 0)
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 1.5rem; border-radius: 15px; text-align: center; margin: 0.5rem;">
                <h4>📊 HDI</h4>
                <h2>{hdi:.3f}</h2>
            </div>
            """, unsafe_allow_html=True)

# Enhanced Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-top: 2rem;">
    <h3 style="color: white; margin-bottom: 1rem;">🚀 Built with Modern Technologies</h3>
    <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem;">
        Powered by <strong>Streamlit</strong> & <strong>Plotly</strong> | 
        Data visualization that tells a story | 
        Real-time COVID-19 analytics
    </p>
    <p style="color: rgba(255,255,255,0.8); margin-top: 1rem;">
        Made with ❤️ for better data understanding
    </p>
</div>
""", unsafe_allow_html=True)
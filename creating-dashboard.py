import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Enhanced Streamlit App Configuration
st.set_page_config(
    page_title="COVID-19 Global Analytics Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data with caching
@st.cache_data
def load_data():
    df = pd.read_csv('./data/cleaned_covid_data.csv')
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

# Custom CSS for Deep Blue and Gold/Yellow Theme
st.markdown("""
<style>
    /* Global Background and text color adjustments */
    .stApp {
        background-color: #0A192F;
        color: #E6F1FF;
    }
    .main-header {
        background: linear-gradient(135deg, #112240 0%, #0A192F 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 1px solid #233554;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .main-title {
        color: #FFD700;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin: 0;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
    }
    .subtitle {
        color: #8892B0;
        font-size: 1.2rem;
        text-align: center;
        margin-top: 0.5rem;
    }
    .metric-card {
        background: rgba(17, 34, 64, 0.8);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #FFD700;
        color: #E6F1FF;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        margin: 1rem 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(255, 215, 0, 0.2);
    }
    .metric-card h3 {
        color: #8892B0;
        margin-bottom: 0.5rem;
    }
    .metric-card h2 {
        color: #FFD700;
        font-size: 2.5rem;
        margin: 0;
        text-shadow: 0 0 15px rgba(255, 215, 0, 0.4);
    }
    .section-header {
        background: linear-gradient(90deg, #112240 0%, #233554 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 2rem 0 1rem 0;
        text-align: center;
        font-weight: bold;
        color: #FFD700;
        border-left: 5px solid #FFD700;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* Sidebar customization */
    [data-testid="stSidebar"] {
        background-color: #112240;
    }
    .stSelectbox > div > div > div {
        background-color: #233554;
        color: #E6F1FF;
        border: 1px solid #FFD700;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: #112240;
        padding: 10px 20px;
        border-radius: 10px;
        border: 1px solid #233554;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 5px;
        color: #8892B0;
        font-size: 1.1rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(255, 215, 0, 0.1) !important;
        color: #FFD700 !important;
        font-weight: bold;
        border-bottom: 3px solid #FFD700 !important;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced Header
st.markdown("""
<div class="main-header">
    <h1 class="main-title">COVID-19 Global Analytics Dashboard</h1>
    <p class="subtitle">Real-time insights and trends from around the world</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for controls
with st.sidebar:
    st.markdown("### Dashboard Controls")
    
    countries = df['location'].dropna().unique()
    country = st.selectbox(
        "Select a Country",
        sorted(countries),
        help="Choose a country to analyze COVID-19 data"
    )
    
    min_date = df['date'].min()
    max_date = df['date'].max()
    
    date_range = st.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    st.markdown("---")
    st.markdown("### Visualization Options")
    show_trends = st.checkbox("Show trend lines", True)
    show_moving_avg = st.checkbox("Show moving averages", False)

# Filter data
filtered_df = df[df['location'] == country].sort_values('date')
if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df['date'] >= pd.to_datetime(date_range[0])) &
        (filtered_df['date'] <= pd.to_datetime(date_range[1]))
    ]

# Common plot settings
plot_layout_kwargs = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family="Arial, sans-serif", size=12, color='#E6F1FF'),
    hovermode='x unified',
    legend=dict(font=dict(color='#E6F1FF'), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

axes_kwargs = dict(showgrid=True, gridwidth=1, gridcolor='rgba(136, 146, 176, 0.2)')

latest_data = pd.Series(dtype='float64')
vaccination_rate = 0
if not filtered_df.empty:
    latest_data = filtered_df.ffill().iloc[-1]
    if pd.notna(latest_data.get('people_vaccinated')) and pd.notna(latest_data.get('population')):
        vaccination_rate = (latest_data['people_vaccinated'] / latest_data['population']) * 100

# Tabs Layout
tab1, tab2, tab3 = st.tabs(["Executive Overview", "Deep Dive Trends", "Policy & Demographics"])

# ==========================================
# TAB 1: EXECUTIVE OVERVIEW
# ==========================================
with tab1:
    if not filtered_df.empty:
        # Key Metrics Cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metric-card"><h3>Total Cases</h3><h2>{latest_data.get("total_cases", 0):,.0f}</h2></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><h3>Total Deaths</h3><h2>{latest_data.get("total_deaths", 0):,.0f}</h2></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><h3>New Cases</h3><h2>{latest_data.get("new_cases", 0):,.0f}</h2></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card"><h3>Vaccination Rate</h3><h2>{vaccination_rate:.1f}%</h2></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # 7-3 layout for main charts
        col_overview_left, col_overview_right = st.columns([7, 3])
        
        with col_overview_left:
            st.markdown('<div class="section-header">Cumulative Cases & Deaths</div>', unsafe_allow_html=True)
            fig_cumulative = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig_cumulative.add_trace(go.Scatter(
                x=filtered_df['date'], y=filtered_df['total_cases'],
                mode='lines', name='Total Cases',
                line=dict(color='#4facfe', width=3),
                fill='tozeroy' if show_trends else None, fillcolor='rgba(79, 172, 254, 0.2)',
                hovertemplate='<b>Total Cases</b><br>Date: %{x}<br>Cases: %{y:,.0f}<extra></extra>'
            ), secondary_y=False)
            
            fig_cumulative.add_trace(go.Scatter(
                x=filtered_df['date'], y=filtered_df['total_deaths'],
                mode='lines', name='Total Deaths',
                line=dict(color='#FFD700', width=3),
                hovertemplate='<b>Total Deaths</b><br>Date: %{x}<br>Deaths: %{y:,.0f}<extra></extra>'
            ), secondary_y=True)
            
            fig_cumulative.update_layout(height=450, **plot_layout_kwargs)
            fig_cumulative.update_xaxes(**axes_kwargs)
            fig_cumulative.update_yaxes(**axes_kwargs)
            st.plotly_chart(fig_cumulative, use_container_width=True)
            
        with col_overview_right:
            st.markdown('<div class="section-header">Vaccination Progress</div>', unsafe_allow_html=True)
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = vaccination_rate,
                domain = {'x': [0, 1], 'y': [0, 1]},
                number = {'font': {'color': '#E6F1FF'}, 'suffix': '%'},
                gauge = {
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#E6F1FF"},
                    'bar': {'color': "#FFD700"},
                    'bgcolor': "#112240",
                    'borderwidth': 2,
                    'bordercolor': "#233554",
                    'steps': [
                        {'range': [0, 25], 'color': '#0A192F'},
                        {'range': [25, 50], 'color': '#112240'},
                        {'range': [50, 75], 'color': '#233554'},
                        {'range': [75, 100], 'color': '#4facfe'}
                    ],
                }
            ))
            fig_gauge.update_layout(height=450, margin=dict(l=20, r=20, t=50, b=20), **plot_layout_kwargs)
            st.plotly_chart(fig_gauge, use_container_width=True)

# ==========================================
# TAB 2: DEEP DIVE TRENDS
# ==========================================
with tab2:
    if not filtered_df.empty:
        st.markdown('<div class="section-header">Daily New Cases & Deaths</div>', unsafe_allow_html=True)
        
        fig_daily = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_daily.add_trace(go.Bar(
            x=filtered_df['date'], y=filtered_df['new_cases'],
            name='New Cases', marker_color='rgba(79, 172, 254, 0.7)',
            hovertemplate='<b>New Cases</b><br>Date: %{x}<br>Cases: %{y:,.0f}<extra></extra>'
        ), secondary_y=False)
        
        fig_daily.add_trace(go.Bar(
            x=filtered_df['date'], y=filtered_df['new_deaths'],
            name='New Deaths', marker_color='rgba(255, 215, 0, 0.7)',
            hovertemplate='<b>New Deaths</b><br>Date: %{x}<br>Deaths: %{y:,.0f}<extra></extra>'
        ), secondary_y=True)
        
        if show_moving_avg and len(filtered_df) > 7:
            filtered_df['new_cases_ma'] = filtered_df['new_cases'].rolling(window=7).mean()
            fig_daily.add_trace(go.Scatter(
                x=filtered_df['date'], y=filtered_df['new_cases_ma'],
                mode='lines', name='7-day avg (Cases)',
                line=dict(color='#FFFFFF', width=2, dash='dash')
            ), secondary_y=False)
            
        fig_daily.update_layout(height=400, **plot_layout_kwargs)
        fig_daily.update_xaxes(**axes_kwargs)
        fig_daily.update_yaxes(**axes_kwargs)
        st.plotly_chart(fig_daily, use_container_width=True)

        st.markdown('<div class="section-header">Case Fatality Rate Over Time</div>', unsafe_allow_html=True)
        filtered_df_copy = filtered_df.copy()
        filtered_df_copy['cfr'] = (filtered_df_copy['total_deaths'] / filtered_df_copy['total_cases'].replace(0, pd.NA)) * 100
        
        fig_cfr = go.Figure()
        fig_cfr.add_trace(go.Scatter(
            x=filtered_df_copy['date'], y=filtered_df_copy['cfr'],
            mode='lines+markers', name='CFR (%)',
            line=dict(color='#FFD700', width=3),
            marker=dict(size=4, color='#FFD700', line=dict(width=1, color='#0A192F')),
            fill='tonexty', fillcolor='rgba(255, 215, 0, 0.1)',
            hovertemplate='<b>Case Fatality Rate</b><br>Date: %{x}<br>CFR: %{y:.2f}%<extra></extra>'
        ))
        fig_cfr.update_layout(height=400, **plot_layout_kwargs)
        fig_cfr.update_xaxes(**axes_kwargs)
        fig_cfr.update_yaxes(**axes_kwargs)
        st.plotly_chart(fig_cfr, use_container_width=True)

# ==========================================
# TAB 3: POLICY & DEMOGRAPHICS
# ==========================================
with tab3:
    if not filtered_df.empty:
        st.markdown('<div class="section-header">Country Profile</div>', unsafe_allow_html=True)
        
        latest = filtered_df.dropna(subset=['median_age', 'population_density', 'gdp_per_capita']).iloc[-1] if len(filtered_df.dropna(subset=['median_age', 'population_density', 'gdp_per_capita'])) > 0 else None
        
        if latest is not None:
            c1, c2, c3, c4 = st.columns(4)
            card_style = """
            <div style="background: rgba(17, 34, 64, 0.8); backdrop-filter: blur(10px); padding: 1.5rem; border-radius: 15px; border: 1px solid #4facfe; text-align: center; margin: 0.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                <h4 style="color: #8892B0; margin-bottom: 0.5rem;">{title}</h4>
                <h2 style="color: #4facfe; font-size: 2rem; margin: 0;">{value}</h2>
            </div>
            """
            with c1: st.markdown(card_style.format(title="Median Age", value=f"{latest.get('median_age', 0):.1f} yrs"), unsafe_allow_html=True)
            with c2: st.markdown(card_style.format(title="Pop. Density", value=f"{latest.get('population_density', 0):.1f}/km²"), unsafe_allow_html=True)
            with c3: st.markdown(card_style.format(title="GDP per Capita", value=f"${latest.get('gdp_per_capita', 0):,.0f}"), unsafe_allow_html=True)
            with c4: st.markdown(card_style.format(title="HDI", value=f"{latest.get('human_development_index', 0):.3f}"), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_policy_left, col_policy_right = st.columns(2)
        
        with col_policy_left:
            st.markdown('<div class="section-header">Vaccination Distribution</div>', unsafe_allow_html=True)
            if pd.notna(latest_data.get('people_vaccinated')) and pd.notna(latest_data.get('population')):
                vaccinated = latest_data['people_vaccinated']
                unvaccinated = latest_data['population'] - vaccinated
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=['Vaccinated', 'Unvaccinated'], values=[vaccinated, unvaccinated],
                    hole=0.4, marker=dict(colors=['#FFD700', '#233554']),
                    textinfo='label+percent', textfont=dict(size=14, color='#ffffff'),
                    hovertemplate='<b>%{label}</b><br>Count: %{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
                )])
                fig_pie.update_layout(height=400, **plot_layout_kwargs)
                st.plotly_chart(fig_pie, use_container_width=True)
                
        with col_policy_right:
            st.markdown('<div class="section-header">Government Response Stringency</div>', unsafe_allow_html=True)
            fig_stringency = go.Figure()
            fig_stringency.add_trace(go.Scatter(
                x=filtered_df['date'], y=filtered_df['stringency_index'],
                mode='lines', name='Stringency Index',
                line=dict(color='#4facfe', width=3),
                fill='tonexty', fillcolor='rgba(79, 172, 254, 0.2)',
                hovertemplate='<b>Stringency Index</b><br>Date: %{x}<br>Index: %{y:.1f}<extra></extra>'
            ))
            fig_stringency.update_layout(height=400, yaxis_title='Stringency Index (0-100)', **plot_layout_kwargs)
            fig_stringency.update_xaxes(**axes_kwargs)
            fig_stringency.update_yaxes(range=[0, 100], **axes_kwargs)
            st.plotly_chart(fig_stringency, use_container_width=True)

# Enhanced Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #112240 0%, #0A192F 100%); border-radius: 15px; margin-top: 2rem; border: 1px solid #FFD700; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
    <h3 style="color: #FFD700; margin-bottom: 1rem; text-shadow: 0 0 10px rgba(255, 215, 0, 0.3);">Built with Modern Technologies</h3>
    <p style="color: #E6F1FF; font-size: 1.1rem;">
        Powered by <strong style="color: #4facfe;">Streamlit</strong> & <strong style="color: #4facfe;">Plotly</strong> | 
        Data visualization that tells a story | 
        Real-time COVID-19 analytics
    </p>
</div>
""", unsafe_allow_html=True)
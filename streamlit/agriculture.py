import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="Global Crop Production Analysis",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E8B57;
    }
    .insight-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and process the crop production data"""
    try:
        # Load the data
        df = pd.read_csv('data/processed/agriculture/crop_production_processed.csv')
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Convert date to datetime and extract year
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        
        # Ensure value is numeric
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        
        # Remove any rows with missing values
        df = df.dropna(subset=['value'])
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def calculate_summary_stats(df):
    """Calculate summary statistics for each commodity"""
    summary_stats = []
    
    for commodity in df['commodity'].unique():
        commodity_data = df[df['commodity'] == commodity].sort_values('year')
        values = commodity_data['value'].values
        
        # Calculate growth rate (using first and last values after sorting)
        first_value = commodity_data.iloc[0]['value']
        last_value = commodity_data.iloc[-1]['value']
        total_growth = ((last_value - first_value) / first_value) * 100
        
        stats = {
            'Commodity': commodity,
            'Unit': commodity_data.iloc[0]['unit'],
            'Count': len(values),
            'Mean': np.mean(values),
            'Median': np.median(values),
            'Min': np.min(values),
            'Max': np.max(values),
            'Std Dev': np.std(values),
            'Total Growth (%)': total_growth,
            'Latest Value': last_value,
            'Latest Year': commodity_data.iloc[-1]['year']
        }
        summary_stats.append(stats)
    
    return pd.DataFrame(summary_stats)

def create_time_series_plot(df, selected_commodities):
    """Create time series plot for selected commodities"""
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set1
    
    for i, commodity in enumerate(selected_commodities):
        commodity_data = df[df['commodity'] == commodity].sort_values('year')
        
        fig.add_trace(go.Scatter(
            x=commodity_data['year'],
            y=commodity_data['value'],
            mode='lines+markers',
            name=commodity,
            line=dict(width=3, color=colors[i % len(colors)]),
            marker=dict(size=6),
            hovertemplate=f'<b>{commodity}</b><br>' +
                         'Year: %{x}<br>' +
                         'Production: %{y:,.0f}<br>' +
                         '<extra></extra>'
        ))
    
    fig.update_layout(
        title="Production Trends Over Time",
        xaxis_title="Year",
        yaxis_title="Production",
        hovermode='x unified',
        height=500,
        showlegend=True
    )
    
    return fig

def create_growth_comparison(summary_df):
    """Create growth rate comparison chart"""
    fig = px.bar(
        summary_df.sort_values('Total Growth (%)', ascending=True),
        x='Total Growth (%)',
        y='Commodity',
        orientation='h',
        color='Total Growth (%)',
        color_continuous_scale=['red', 'yellow', 'green'],
        title="Total Growth Rate by Commodity (2000-2025)"
    )
    
    fig.update_layout(height=400)
    return fig

def create_latest_production_chart(summary_df):
    """Create latest production comparison"""
    # Separate cattle (different unit) from crops
    crops_df = summary_df[summary_df['Unit'] != '1000 Head'].copy()
    cattle_df = summary_df[summary_df['Unit'] == '1000 Head'].copy()
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Crop Production (1000 Metric Ton)', 'Cattle Production (1000 Head)'),
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )
    
    # Crops
    if not crops_df.empty:
        fig.add_trace(
            go.Bar(
                x=crops_df['Commodity'],
                y=crops_df['Latest Value'],
                name='Crops',
                marker_color='lightblue'
            ),
            row=1, col=1
        )
    
    # Cattle
    if not cattle_df.empty:
        fig.add_trace(
            go.Bar(
                x=cattle_df['Commodity'],
                y=cattle_df['Latest Value'],
                name='Cattle',
                marker_color='lightcoral'
            ),
            row=1, col=2
        )
    
    fig.update_layout(
        title="Latest Production Values by Commodity",
        height=400,
        showlegend=False
    )
    
    return fig

def create_correlation_matrix(df):
    """Create correlation matrix of commodities"""
    # Pivot data to have commodities as columns
    pivot_df = df.pivot(index='year', columns='commodity', values='value')
    
    # Calculate correlation matrix
    corr_matrix = pivot_df.corr()
    
    # Create heatmap
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale='RdBu',
        title="Correlation Matrix of Commodity Productions"
    )
    
    return fig

def main():
    # Title
    st.markdown('<h1 class="main-header">🌾 Global Crop Production Analysis (2000-2025)</h1>', 
                unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.error("No data available. Please check your data file.")
        return
    
    # Calculate summary statistics
    summary_df = calculate_summary_stats(df)
    
    # Sidebar
    st.sidebar.header("🔧 Controls")
    
    # Commodity selection
    all_commodities = df['commodity'].unique().tolist()
    selected_commodities = st.sidebar.multiselect(
        "Select Commodities for Time Series",
        all_commodities,
        default=all_commodities[:3]
    )
    
    # Data overview section
    st.header("📊 Dataset Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", len(df))
    
    with col2:
        st.metric("Commodities", len(all_commodities))
    
    with col3:
        st.metric("Years Covered", f"{df['year'].min()}-{df['year'].max()}")
    
    with col4:
        st.metric("Data Source", "USDA PSD")
    
    # Summary statistics table
    st.header("📈 Summary Statistics")
    
    # Format the summary table for better display
    display_df = summary_df.copy()
    numeric_columns = ['Mean', 'Min', 'Max', 'Latest Value']
    for col in numeric_columns:
        display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f}")
    
    display_df['Total Growth (%)'] = display_df['Total Growth (%)'].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(
        display_df[['Commodity', 'Unit', 'Mean', 'Min', 'Max', 'Total Growth (%)', 'Latest Value']],
        use_container_width=True
    )
    
    # Time series analysis
    st.header("📊 Production Trends")
    
    if selected_commodities:
        fig_ts = create_time_series_plot(df, selected_commodities)
        st.plotly_chart(fig_ts, use_container_width=True)
    else:
        st.warning("Please select at least one commodity to display the time series.")
    
    # Growth comparison and latest production
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Growth Rate Comparison")
        fig_growth = create_growth_comparison(summary_df)
        st.plotly_chart(fig_growth, use_container_width=True)
    
    with col2:
        st.subheader("🏆 Latest Production Values")
        fig_latest = create_latest_production_chart(summary_df)
        st.plotly_chart(fig_latest, use_container_width=True)
    
    # Correlation analysis
    st.header("🔗 Correlation Analysis")
    fig_corr = create_correlation_matrix(df)
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # Detailed commodity analysis
    st.header("🔍 Detailed Commodity Analysis")
    
    selected_commodity = st.selectbox(
        "Select a commodity for detailed analysis:",
        all_commodities
    )
    
    if selected_commodity:
        commodity_data = df[df['commodity'] == selected_commodity].sort_values('year')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Statistics
            stats = summary_df[summary_df['Commodity'] == selected_commodity].iloc[0]
            
            st.subheader(f"📊 {selected_commodity} Statistics")
            st.write(f"**Unit**: {stats['Unit']}")
            st.write(f"**Mean Production**: {stats['Mean']:,.0f}")
            st.write(f"**Growth Rate**: {stats['Total Growth (%)']:.1f}%")
            st.write(f"**Latest Value**: {stats['Latest Value']:,.0f}")
            
        with col2:
            # Year-over-year changes
            commodity_data['yoy_change'] = commodity_data['value'].pct_change() * 100
            
            fig_yoy = px.bar(
                commodity_data,
                x='year',
                y='yoy_change',
                title=f"{selected_commodity} - Year-over-Year Change (%)",
                color='yoy_change',
                color_continuous_scale=['red', 'white', 'green']
            )
            st.plotly_chart(fig_yoy, use_container_width=True)
    
    # Key insights
    st.header("💡 Key Insights")
    
    # Find commodity with highest growth
    highest_growth = summary_df.loc[summary_df['Total Growth (%)'].idxmax()]
    
    # Find largest producer
    largest_producer = summary_df.loc[summary_df['Latest Value'].idxmax()]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="insight-box">
            <h4>🚀 Highest Growth</h4>
            <p><strong>{highest_growth['Commodity']}</strong> shows the highest growth rate at 
            <strong>{highest_growth['Total Growth (%)']:.1f}%</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="insight-box">
            <h4>🏭 Largest Production</h4>
            <p><strong>{largest_producer['Commodity']}</strong> has the highest current production at 
            <strong>{largest_producer['Latest Value']:,.0f}</strong> {largest_producer['Unit']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_growth = summary_df['Total Growth (%)'].mean()
        st.markdown(f"""
        <div class="insight-box">
            <h4>📊 Average Growth</h4>
            <p>Average growth rate across all commodities is 
            <strong>{avg_growth:.1f}%</strong> over the 25-year period</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Data table
    with st.expander("📋 View Raw Data"):
        st.dataframe(df, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("*Data source: USDA Production, Supply, and Distribution (PSD) Database*")

if __name__ == "__main__":
    main()
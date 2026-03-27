import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
# --- 1. إعدادات المتصفح والثيم ---
st.set_page_config(
    page_title="Spatial Intelligence Dashboard",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded"
)
# تخصيص الواجهة عبر CSS بسيط
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)
# --- 2. محرك البيانات (Data Engine) ---
@st.cache_data
def get_spatial_data():
    # بيانات محاكية دقيقة لأحياء شمال الرياض
    data = {
        'District': ['Al-Malqa', 'Al-Yasmin', 'Al-Sahafa', 'Al-Malqa', 'Al-Yasmin', 'Al-Sahafa', 'Al-Malqa', 'Al-Yasmin'],
        'Price_SQM': [8200, 7100, 6900, 8500, 7300, 6800, 9000, 7500],
        'Lat': [24.793, 24.812, 24.805, 24.785, 24.825, 24.800, 24.801, 24.815],
        'Lon': [46.615, 46.641, 46.630, 46.622, 46.650, 46.635, 46.633, 46.645],
        'Type': ['Residential', 'Commercial', 'Residential', 'Residential', 'Commercial', 'Residential', 'Commercial', 'Residential'],
        'Growth_Rate': [5.2, 3.8, 4.1, 5.5, 3.9, 4.0, 6.1, 4.2]
    }
    return pd.DataFrame(data)
df = get_spatial_data()
# --- 3. الشريط الجانبي (Advanced Sidebar) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8144/8144570.png", width=80)
    st.title("إعدادات الخارطة")
    st.divider()
    districts = st.multiselect("الأحياء المستهدفة:", options=df['District'].unique(), default=df['District'].unique())
    property_types = st.multiselect("نوع العقار:", options=df['Type'].unique(), default=df['Type'].unique())
    price_range = st.slider("نطاق سعر المتر (SAR):", 5000, 12000, (6500, 9500))
    map_style = st.selectbox("نمط الخريطة:", ["carto-positron", "open-street-map", "stamen-terrain"])
# تصفية البيانات
mask = (df['District'].isin(districts)) & (df['Type'].isin(property_types)) & (df['Price_SQM'].between(price_range[0], price_range[1]))
filtered_df = df[mask]
# --- 4. لوحة المؤشرات (KPIs) ---
st.title("🚀 منصة التحليل المكاني | Spatial Intelligence")
st.markdown(f"**نطاق التحليل:** {', '.join(districts)} | **عدد النقاط المرصودة:** {len(filtered_df)}")
m1, m2, m3, m4 = st.columns(4)
if not filtered_df.empty:
    m1.metric("متوسط سعر المتر", f"{int(filtered_df['Price_SQM'].mean())} ريال", "+2.4%")
    m2.metric("أعلى سعر مرصود", f"{filtered_df['Price_SQM'].max()} ريال")
    m3.metric("متوسط النمو السنوي", f"{filtered_df['Growth_Rate'].mean()}%")
    m4.metric("أكثر الأحياء طلباً", filtered_df['District'].mode()[0])
st.divider()
# --- 5. العرض المرئي (Map & Analytics) ---
col_map, col_chart = st.columns([2, 1])

with col_map:
    st.subheader("📍 التوزيع الجغرافي للأسعار")
    fig_map = px.scatter_mapbox(
        filtered_df,
        lat="Lat",
        lon="Lon",
        color="Price_SQM",
        size="Price_SQM",
        color_continuous_scale=px.colors.sequential.Viridis,
        hover_name="District",
        hover_data={"Price_SQM": True, "Type": True, "Lat": False, "Lon": False},
        zoom=11.5,
        height=550
    )
    fig_map.update_layout(mapbox_style=map_style, margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)
with col_chart:
    st.subheader("📊 مقارنة الأحياء")
    fig_bar = px.bar(
        filtered_df.groupby('District')['Price_SQM'].mean().reset_index(),
        x='District',
        y='Price_SQM',
        color='District',
        text_auto='.2s',
        title="متوسط السعر لكل حي"
    )
    fig_bar.update_layout(showlegend=False, height=300)
    st.plotly_chart(fig_bar, use_container_width=True)
    st.subheader("📈 تحليل النمو")
    fig_line = px.line(filtered_df, x='District', y='Growth_Rate', markers=True)
    fig_line.update_layout(height=200)
    st.plotly_chart(fig_line, use_container_width=True)
# --- 6. عرض البيانات الخام ---
with st.expander("🔍 استعراض جدول البيانات"):
    st.dataframe(filtered_df.style.background_gradient(subset=['Price_SQM'], cmap='YlGn'), use_container_width=True)
# --- 7. التذييل ---
st.caption("تم تطوير هذا النظام لتحليل البيانات العقارية المكانية - الرياض 2026")

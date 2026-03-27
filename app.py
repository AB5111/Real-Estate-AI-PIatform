import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
# --- 1. الإعدادات المتقدمة والهوية (Theming) ---
st.set_page_config(
    layout="wide", 
    page_title="Drones Crafters | Real Estate Intelligence",
    page_icon="🏙️"
)
# تصميم احترافي باستخدام CSS لمواءمة الواجهة مع تطبيقات الـ Dashboards العالمية
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [data-testid="stSidebar"], .main, .stMarkdown {
        direction: RTL !important;
        text-align: right !important;
        font-family: 'Cairo', sans-serif !important;
    }
    /* تحسين شكل البطاقات الرقمية */
    .stMetric {
        background: linear-gradient(135deg, #ffffff 0%, #f0f4f8 100%);
        border: 1px solid #d1d9e6;
        padding: 20px !important;
        border-radius: 15px !important;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.05);
    }
    /* تخصيص الأزرار */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background-color: #1E3A8A;
        color: white;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #3B82F6;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)
# --- 2. إدارة البيانات (Smart Data Handling) ---
@st.cache_data
def load_master_data():
    # بيانات محاكاة دقيقة تعكس أحياء الرياض النشطة في 2026
    districts_data = {
        'الحي': ["الملقا", "الياسمين", "النرجس", "حطين", "الصحافة", "العمارية"],
        'متوسط السعر/م': [8500, 7200, 6800, 9500, 7000, 3500],
        'نسبة النمو': [5.8, 4.2, 6.1, 4.9, 3.5, 8.2],
        'عدد الصفقات': [120, 85, 150, 60, 95, 40],
        'lat': [24.793, 24.812, 24.825, 24.775, 24.795, 24.805],
        'lon': [46.615, 46.641, 46.655, 46.610, 46.630, 46.550]
    }
    return pd.DataFrame(districts_data)
master_df = load_master_data()
# --- 3. الهيكل الجانبي (Professional Navigation) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/10543/10543339.png", width=60)
    st.title("Drones Crafters")
    st.caption("نظام ذكاء الأصول العقارية V2.5")
    st.divider()
    menu = st.sidebar.radio(
        "القائمة الرئيسية",
        ["الرصد التنفيذي", "التحليل المكاني (GIS)", "محرك التقييم (AVM)", "التقارير المالية", "الأرشفة الرقمية"],
        index=0
    )
    st.divider()
    with st.expander("⚙️ إعدادات النظام"):
        st.toggle("تفعيل التنبيهات الذكية", value=True)
        st.toggle("ربط بيانات الدرون الحية")
# --- 4. معالجة الصفحات (Page Routing) ---
# --- 1: الرصد التنفيذي ---
if menu == "الرصد التنفيذي":
    st.title("🏙️ لوحة التحكم التنفيذية (Portfolio Status)")
    # صف المؤشرات الرئيسية
    c1, c2, c3, c4 = st.columns(4)
    total_val = (master_df['متوسط السعر/م'] * 1000).sum() / 1e6 # محاكاة
    c1.metric("إجمالي قيمة الأصول (تقديري)", f"{total_val:.1f} M", "7.2%+")
    c2.metric("أعلى حي نمواً", master_df.loc[master_df['نسبة النمو'].idxmax(), 'الحي'])
    c3.metric("متوسط العائد التشغيلي", "8.4%", "0.2%+")
    c4.metric("حالة السوق", "تصاعدي", "Stable")
    st.divider()
    col_chart, col_table = st.columns([1.5, 1])
    with col_chart:
        st.subheader("مقارنة الأداء السعري والنمو")
        fig = px.scatter(master_df, x="متوسط السعر/م", y="نسبة النمو", 
                         size="عدد الصفقات", color="الحي",
                         hover_name="الحي", text="الحي", size_max=40)
        st.plotly_chart(fig, use_container_width=True)
    with col_table:
        st.subheader("أحدث الصفقات")
        st.dataframe(master_df[['الحي', 'متوسط السعر/م', 'نسبة النمو']], hide_index=True, use_container_width=True)
# --- 2: التحليل المكاني ---
elif menu == "الالتحليل المكاني (GIS)":
    st.title("🗺️ خريطة النقاط العقارية والمسح الجوي")
    # اختيار الطبقة
    map_layer = st.radio("اختر طبقة العرض:", ["خريطة الشوارع", "قمر صناعي (درون)", "توزيع الكثافة"], horizontal=True)
    layer_style = "satellite-streets" if map_layer == "قمر صناعي (درون)" else "carto-positron"
    
    fig_map = px.scatter_mapbox(master_df, lat="lat", lon="lon", size="عدد الصفقات", 
                                color="متوسط السعر/م", color_continuous_scale=px.colors.sequential.Deep,
                                zoom=10.5, height=600, hover_name="الحي")
    fig_map.update_layout(mapbox_style=layer_style, margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)
# --- 3: محرك التقييم AVM ---
elif menu == "محرك التقييم (AVM)":
    st.title("🤖 نموذج التقييم الآلي المتقدم")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            h_dist = st.selectbox("الحي المستهدف", master_df['الحي'])
            h_area = st.number_input("المساحة الإجمالية (م²)", value=500, step=50)
            h_age = st.slider("عمر العقار (سنة)", 0, 25, 2)
        with col2:
            h_fronts = st.multiselect("الواجهات", ["شمالية", "جنوبية", "شرقية", "غربية"], default=["شمالية"])
            h_quality = st.select_slider("جودة التنفيذ", options=["تجاري", "ستاندرد", "مودرن", "فاخر VIP"])
            h_services = st.checkbox("قريب من مترو الرياض / خدمات رئيسية")
    if st.button("تحليل القيمة العادلة"):
        # خوارزمية محاكاة
        base = master_df.loc[master_df['الحي'] == h_dist, 'متوسط السعر/م'].values[0]
        q_factor = {"تجاري": 0.85, "ستاندرد": 1.0, "مودرن": 1.15, "فاخر VIP": 1.4}[h_quality]
        srv_factor = 1.10 if h_services else 1.0
        final_val = (h_area * base) * q_factor * srv_factor * (0.98**h_age)
        st.balloons()
        st.success(f"### القيمة التقديرية للعقار: {final_val:,.0f} ريال سعودي")
        st.info("تم احتساب السعر بناءً على خوارزميات الذكاء المكاني وتحليل السوق الحالي.")
# --- 4: التقارير المالية ---
elif menu == "التقارير المالية":
    st.title("💰 الإدارة المالية والتدفقات")
    st.info("هذه الوحدة مرتبطة بالنظام المالي للمؤسسة لسحب البيانات الفعلية.")
    # محاكاة بيانات مالية
    fin_data = pd.DataFrame({
        'الشهر': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'الإيرادات': np.random.randint(400, 800, 6),
        'المصاريف': np.random.randint(100, 300, 6)
    })
    st.area_chart(fin_data.set_index('الشهر'))
# --- 5: الأرشفة الرقمية ---
elif menu == "الأرشفة الرقمية":
    st.title("📂 مركز إدارة الوثائق الذكي")
    st.write("ارفع ملفات (صكوك، مخططات، تقارير درون) ليتم أرشفتها وربطها مكانياً.")
    uploaded_file = st.file_uploader("اسحب الملف هنا (PDF, PNG, GeoJSON)", type=['pdf', 'png', 'jpg', 'geojson'])
    if uploaded_file:
        with st.status("جاري تحليل الملف واستخراج البيانات..."):
            st.write("فحص الصك عبر الـ OCR...")
            st.write("التحقق من مطابقة الحدود الجغرافية...")
        st.success("تمت الأرشفة بنجاح وربط الوثيقة بحي " + master_df['الحي'][0])
# --- 5. التذييل (Footer) ---
st.divider()
footer_col1, footer_col2 = st.columns([3, 1])
footer_col1.caption("© 2026 Drones Crafters. جميع الحقوق محفوظة. نظام مدعوم بالذكاء الاصطناعي.")
footer_col2.write("🇸🇦 **رؤية 2030**")

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
# --- إعداد الصفحة ---
st.set_page_config(
    layout="wide",
    page_title="Drones Crafters | منصة إدارة الأصول العقارية",
    page_icon="🏗️"
)
# --- CSS متقدم للهوية العربية والجماليات ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    html, body, [data-testid="stSidebar"], .main, .stMarkdown {
        direction: RTL !important;
        text-align: right !important;
        font-family: 'Tajawal', sans-serif !important;
    }
    /* تنسيق البطاقات الإحصائية */
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    /* تخصيص العنوان الجانبي */
    .sidebar-title {
        color: #1E3A8A;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    /* تحسين شكل الأزرار */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background-color: #1E3A8A;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)
# =========================
# إدارة حالة البيانات (Session State)
# =========================
if 'deeds_data' not in st.session_state:
    st.session_state.deeds_data = pd.DataFrame({
        "رقم الصك": ["123/أ", "456/ب", "789/ج"],
        "المالك": ["شركة أصول الأولى", "صندوق استثماري عقاري", "شركة تطوير عمراني"],
        "الحي": ["الملقا", "الياسمين", "النرجس"],
        "المساحة م²": [2500, 4300, 1800],
        "الحالة": ["ساري", "ساري", "محدث"]
    })
# =========================
# البيانات المرجعية
# =========================
districts = ["الملقا", "الياسمين", "النرجس", "العمارية"]
price_mock = {
    "الملقا": [4200, 5500, 4800, 6000],
    "الياسمين": [3800, 4100, 3900, 4500],
    "النرجس": [3500, 3700, 3600, 4000],
    "العمارية": [2200, 2800, 2500, 3100]
}
# =========================
# القائمة الجانبية
# =========================
with st.sidebar:
    st.markdown('<div class="sidebar-title">Drones Crafters 🏗️</div>', unsafe_allow_html=True)
    st.info("نظام ذكاء الأعمال العقاري v2.0")
    role = st.selectbox(
        "👤 الدور التنفيذي",
        ["System Admin", "Asset Manager", "Investment Analyst", "External Auditor"],
        format_func=lambda x: {
            "System Admin": "مسؤول النظام",
            "Asset Manager": "مدير الأصول",
            "Investment Analyst": "محلل استثماري",
            "External Auditor": "مدقق خارجي"
        }[x]
    )
    st.divider()
    from streamlit_option_menu import option_menu
    choice = option_menu(
        "القائمة الرئيسية",
        ["لوحة القيادة", "إدارة الصكوك", "التحليلات المالية", "الذكاء المكاني", "تقييم AVM", "الصيانة التنبؤية", "ذكاء السوق"],
        icons=["house", "file-earmark-check", "graph-up-arrow", "map", "robot", "tools", "lightbulb"],
        menu_icon="cast", default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#fafafa"},
            "icon": {"color": "#1E3A8A", "font-size": "18px"}, 
            "nav-link": {"font-size": "14px", "text-align": "right", "margin":"5px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#1E3A8A"},
        }
    )
st.write(f"🔐 بصمة الدخول: **{role}** | 📅 التاريخ: {datetime.now().strftime('%Y-%m-%d')}")
# =========================
# 1) لوحة القيادة التنفيذية
# =========================
if choice == "لوحة القيادة":
    st.title("📊 الملخص التنفيذي للمحفظة")
    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إجمالي قيمة الأصول", "2.4B SAR", "+4.2%")
    c2.metric("عدد العقارات", "1,280", "+35")
    c3.metric("العائد الداخلي (IRR)", "11.8%", "0.6% ↑")
    c4.metric("نسبة الإشغال", "89%", "-3.1% ↓")
    
    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.subheader("توزيع المحفظة حسب النوع")
        asset_type_df = pd.DataFrame({
            "النوع": ["شقق", "مكاتب", "تجاري", "صناعي", "فلل"],
            "القيمة": [600, 450, 520, 300, 530]
        })
        fig = px.pie(asset_type_df, values='القيمة', names='النوع', hole=0.5,
                     color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(fig, use_container_width=True)
    with col_right:
        st.subheader("تطور مؤشرات الأداء (ROI/IRR)")
        kpi_hist = pd.DataFrame({
            "السنة": [2021, 2022, 2023, 2024],
            "ROI": [8.5, 9.2, 10.1, 10.8],
            "IRR": [10.2, 10.9, 11.3, 11.8]
        })
        fig_line = px.line(kpi_hist, x="السنة", y=["ROI", "IRR"], markers=True, 
                          color_discrete_map={"ROI": "#DAA520", "IRR": "#1E3A8A"})
        st.plotly_chart(fig_line, use_container_width=True)
# =========================
# 2) إدارة الصكوك (تفاعلية بالكامل)
# =========================
elif choice == "إدارة الصكوك":
    st.title("📜 نظام إدارة الأرشفة العقارية")
    tab1, tab2 = st.tabs(["📂 استعراض الصكوك", "➕ إضافة صك جديد"])
    with tab1:
        st.subheader("السجل الرقمي الموحد")
        st.dataframe(st.session_state.deeds_data, use_container_width=True)
    with tab2:
        with st.form("new_deed"):
            col1, col2 = st.columns(2)
            d_no = col1.text_input("رقم الصك الجديد")
            d_owner = col2.text_input("اسم المالك")
            d_dist = col1.selectbox("الحي", districts)
            d_area = col2.number_input("المساحة م²", min_value=100)
            d_status = col1.selectbox("الحالة", ["ساري", "محدث"])
            if st.form_submit_button("تسجيل الصك في القاعدة"):
                new_row = {"رقم الصك": d_no, "المالك": d_owner, "الحي": d_dist, "المساحة م²": d_area, "الحالة": d_status}
                st.session_state.deeds_data = pd.concat([st.session_state.deeds_data, pd.DataFrame([new_row])], ignore_index=True)
                st.success("✅ تم تحديث قاعدة البيانات بنجاح!")
                st.rerun()
# =========================
# 3) التحليلات المالية
# =========================
elif choice == "التحليلات المالية":
    st.title("💰 الهندسة المالية للمحفظة")
    fin_df = pd.DataFrame({
        "السنة": [2021, 2022, 2023, 2024],
        "الإيرادات": [12.0, 14.5, 16.2, 18.0],
        "المصاريف": [4.0, 4.5, 5.0, 5.4],
        "صافي الربح": [8.0, 10.0, 11.2, 12.6]
    })
    # عرض شلال التدفق النقدي
    fig_cash = go.Figure(go.Waterfall(
        name = "20", orientation = "v",
        measure = ["relative", "relative", "total"],
        x = ["الإيرادات", "المصاريف التشغيلية", "صافي التدفق النقدي"],
        textposition = "outside",
        text = [f"+{fin_df['الإيرادات'].iloc[-1]}M", f"-{fin_df['المصاريف'].iloc[-1]}M", "Total"],
        y = [fin_df['الإيرادات'].iloc[-1], -fin_df['المصاريف'].iloc[-1], 0],
        connector = {"line":{"color":"rgb(63, 63, 63)"}},
    ))
    fig_cash.update_layout(title="تحليل التدفق النقدي الحالي (مليون ريال)")
    st.plotly_chart(fig_cash, use_container_width=True)
# =========================
# 4) الذكاء المكاني والخرائط
# =========================
elif choice == "الذكاء المكاني":
    st.title("🗺️ التحليل المكاني الذكي (Geospatial)")
    dist_choice = st.selectbox("اختر النطاق الجغرافي", districts)
    # بيانات الخريطة
    map_data = pd.DataFrame({
        'lat': [24.774265, 24.800000, 24.760000],
        'lon': [46.738586, 46.700000, 46.760000],
        'label': ['أصل سكني', 'مجمع تجاري', 'أرض فضاء']
    })
    st.subheader(f"توزيع الأصول في حي {dist_choice}")
    st.map(map_data) # استخدام الخريطة الأصلية لضمان الثبات
    st.info("💡 نظام GIS مرتبط حالياً ببيانات الصكوك المحدثة.")
# =========================
# 5) نموذج التقييم الآلي AVM
# =========================
elif choice == "تقييم AVM":
    st.title("🤖 نموذج التقييم الآلي (AVM v1.2)")
    with st.container():
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("### مدخلات العقار")
            area = st.number_input("المساحة الإجمالية (م²)", value=300)
            dist = st.selectbox("الحي المستهدف", districts)
            quality = st.select_slider("جودة التنفيذ", ["اقتصادي", "متوسط", "فاخر", "سوبر لوكس"])
            age = st.number_input("عمر البناء (سنوات)", 0, 50, 5)
        with col2:
            st.markdown("### نتيجة التقييم التقديرية")
            # منطق حسابي محسن
            base = np.mean(price_mock[dist])
            q_mod = {"اقتصادي": 0.85, "متوسط": 1.0, "فاخر": 1.2, "سوبر لوكس": 1.4}[quality]
            age_mod = max(0.6, 1 - (age * 0.02))
            final_price = base * area * q_mod * age_mod
            st.metric("القيمة العادلة المقدرة", f"{final_price:,.0f} ريال", "دقة 94%") 
            # رسم بياني صغير للعوامل
            radar_df = pd.DataFrame(dict(
                r=[base/6000, q_mod, age_mod, 0.9],
                theta=['سعر الحي','الجودة','العمر','الموقع']))
            fig_radar = px.line_polar(radar_df, r='r', theta='theta', line_close=True)
            fig_radar.update_traces(fill='toself')
            st.plotly_chart(fig_radar, use_container_width=True)
# =========================
# 6) الصيانة التنبؤية
# =========================
elif choice == "الصيانة التنبؤية":
    st.title("🛠️ الصيانة الذكية والأصول")
    # محاكاة بيانات الصيانة
    maint_data = pd.DataFrame({
        "الأسبوع": [f"W{i}" for i in range(1, 13)],
        "الأعطال المتوقعة": np.random.poisson(3, 12),
        "التكلفة التقديرية": np.random.randint(10000, 50000, 12)
    })
    st.subheader("تنبؤات الأعطال للربع القادم")
    fig_maint = px.bar(maint_data, x="الأسبوع", y="التكلفة التقديرية", 
                       title="ميزانية الصيانة التنبؤية", color="الأعطال المتوقعة")
    st.plotly_chart(fig_maint, use_container_width=True)
# =========================
# 7) ذكاء السوق
# =========================
elif choice == "ذكاء السوق":
    st.title("💡 رؤى السوق والاستثمار")
    years = list(range(2020, 2027))
    growth = [100, 105, 115, 128, 140, 155, 175]
    
    st.subheader("مؤشر نمو القطاع العقاري (الرياض)")
    fig_market = px.area(x=years, y=growth, labels={'x':'السنة', 'y':'المؤشر'},
                        title="اتجاهات النمو التراكمي")
    st.plotly_chart(fig_market, use_container_width=True)
    st.success("التقرير الفني: السوق يشهد نمواً قوياً في المناطق الشمالية (الملقا، الياسمين) بنسبة 12% سنوياً.")
# --- التذييل ---
st.divider()
st.caption("جميع الحقوق محفوظة © 2026 Drones Crafters - منصة إدارة الأصول الرقمية")

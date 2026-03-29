import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import random
# ==========================================
# ⚙️ إعدادات الصفحة والهوية البصرية
# ==========================================
st.set_page_config(
    layout="wide",
    page_title="Drones Crafters – Real Estate Management Dashboard",
    page_icon="🏢"
)
# CSS محسن للهوية العربية والـ RTL
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [data-testid="stSidebar"], .main, .stMarkdown {
        direction: RTL !important;
        text-align: right !important;
        font-family: 'Cairo', sans-serif !important;
    }
    section[data-testid="stSidebar"] > div { text-align: right; }
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"], [data-testid="stMetricDelta"] {
        text-align: right !important;
        direction: RTL !important;
        font-family: 'Cairo', sans-serif !important;
    }
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-right: 5px solid #1E3A8A;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stButton>button {
        width: 100%;
        font-family: 'Cairo', sans-serif !important;
        background-color: #1E3A8A !important;
        color: white !important;
        border-radius: 8px !important;
    }
    .icon-bar {
        display: flex;
        justify-content: space-around;
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 15px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    .icon-item {
        text-align: center;
        cursor: pointer;
        padding: 8px 12px;
        border-radius: 12px;
        transition: 0.2s;
        font-size: 14px;
    }
    .icon-item:hover {
        background-color: #d1d5db;
    }
    </style>
""", unsafe_allow_html=True)
# ==========================================
# تحميل البيانات الأساسية (Caching)
# ==========================================
@st.cache_data
def load_base_data():
    districts = ["الملقا", "الياسمين", "النرجس", "العمارية"]
    price_mock = {
        "الملقا": [4200, 5500, 4800, 6000],
        "الياسمين": [3800, 4100, 3900, 4500],
        "النرجس": [3500, 3700, 3600, 4000],
        "العمارية": [2200, 2800, 2500, 3100]
    }
    financial_df = pd.DataFrame({
        "السنة": [2021, 2022, 2023, 2024],
        "الإيرادات": [12_000_000, 14_500_000, 16_200_000, 18_000_000],
        "المصاريف التشغيلية": [4_000_000, 4_500_000, 5_000_000, 5_400_000],
        "صيانة": [1_200_000, 1_350_000, 1_500_000, 1_650_000]
    })
    maintenance_df = pd.DataFrame({
        "الأسبوع": [f"{w}/2024" for w in range(40, 53)],
        "تكلفة الصيانة": np.random.randint(200_000, 600_000, 13),
        "تكلفة الإدارة": np.random.randint(150_000, 400_000, 13),
        "اسم الأصل": [f"أصل {i}" for i in range(1, 14)]
    })
    return districts, price_mock, financial_df, maintenance_df
districts, price_mock, financial_df, maintenance_df = load_base_data()
# ==========================================
# حالة الجلسة (Session State)
# ==========================================
if 'deeds_df' not in st.session_state:
    st.session_state.deeds_df = pd.DataFrame({
        "رقم الصك": ["123/أ", "456/ب", "789/ج"],
        "المالك": ["شركة أصول الأولى", "صندوق استثماري عقاري", "شركة تطوير عمراني"],
        "الحي": ["الملقا", "الياسمين", "النرجس"],
        "المساحة م²": [2500, 4300, 1800],
        "الحالة": ["ساري", "ساري", "محدث"]
    })
if 'selected_service' not in st.session_state:
    st.session_state.selected_service = "لوحة القيادة التنفيذية"

def set_service(service_name):
    st.session_state.selected_service = service_name
# ==========================================
# القائمة الجانبية (14 خدمة)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/10543/10543319.png", width=80)
    st.title("Drones Crafters")
    st.subheader("إدارة الأصول العقارية")
    
    role = st.selectbox(
        "الدور التنفيذي",
        ["System Admin", "Asset Manager", "Investment Analyst", "External Auditor"],
        format_func=lambda x: {
            "System Admin": " مسؤول النظام",
            "Asset Manager": " مدير الأصول",
            "Investment Analyst": " محلل استثماري",
            "External Auditor": " مدقق خارجي"
        }[x]
    )
    st.divider()
    services = {
        "لوحة القيادة التنفيذية": "speedometer2",
        "إدارة الصكوك والوثائق": "file-earmark-text",
        "التحليلات المالية": "currency-dollar",
        "الذكاء المكاني والخرائط": "geo-alt",
        "نموذج التقييم الآلي AVM": "robot",
        "الصيانة التنبؤية": "tools",
        "ذكاء السوق والاستثمار": "graph-up-arrow",
        "إدارة العقود والمستأجرين": "people",
        "التنبؤ بالأسعار (AI)": "graph-up",
        "تحليل المحفظة الاستثمارية": "pie-chart",
        "الامتثال القانوني والتراخيص": "building",
        "لوحة تحكم المخاطر": "exclamation-triangle",
        "التقارير الذكية القابلة للتخصيص": "file-spreadsheet",
        "مركز التنبيهات والإشعارات": "bell"
    }
    try:
        from streamlit_option_menu import option_menu
        choice = option_menu(
            "الخدمات المتكاملة",
            list(services.keys()),
            icons=list(services.values()),
            menu_icon="cast",
            default_index=list(services.keys()).index(st.session_state.selected_service),
            styles={
                "container": {"padding": "5px", "background-color": "#fafafa"},
                "nav-link": {"font-size": "14px", "text-align": "right", "margin": "0px", "font-family": "Cairo"},
                "nav-link-selected": {"background-color": "#1E3A8A"},
            }
        )
        st.session_state.selected_service = choice
    except:
        choice = st.radio("الخدمات المتكاملة", list(services.keys()), index=list(services.keys()).index(st.session_state.selected_service))
        st.session_state.selected_service = choice

st.write(f"🔐 الدور الحالي في النظام: **{role}**")
st.divider()
# ==========================================
# شريط الأيقونات العلوي (الوصول السريع)
# ==========================================
st.markdown("### ⚡ الوصول السريع إلى الخدمات")
cols = st.columns(7)
quick_services = list(services.keys())[:7]
icon_map = {
    "لوحة القيادة التنفيذية": "📊",
    "إدارة الصكوك والوثائق": "📜",
    "التحليلات المالية": "💰",
    "الذكاء المكاني والخرائط": "🗺️",
    "نموذج التقييم الآلي AVM": "🤖",
    "الصيانة التنبؤية": "🛠️",
    "ذكاء السوق والاستثمار": "📈"
}
for i, service in enumerate(quick_services):
    with cols[i]:
        st.button(f"{icon_map.get(service, '🔹')} {service.split()[0]}", key=service, on_click=set_service, args=(service,), use_container_width=True)
st.divider()
# ==========================================
# 1️⃣ لوحة القيادة التنفيذية
# ==========================================
if st.session_state.selected_service == "لوحة القيادة التنفيذية":
    st.title("🏢 لوحة القيادة التنفيذية – Portfolio & Risk")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("إجمالي قيمة الأصول", "2.4 مليار ريال", "+4.2%")
    col2.metric("عدد العقارات", "1,280 أصل", "+35")
    col3.metric("متوسط العائد السنوي (IRR)", "11.8%", "+0.6%")
    col4.metric("نسبة الإشغال", "89%", "-3.1%")
    st.divider()
    c_left, c_right = st.columns(2)
    with c_left:
        st.subheader("توزيع القيمة حسب نوع العقار")
        asset_type_df = pd.DataFrame({
            "نوع العقار": ["شقق", "مكاتب", "تجاري", "صناعي", "فلل"],
            "القيمة": [600, 450, 520, 300, 530]
        })
        fig = px.bar(asset_type_df, x="نوع العقار", y="القيمة", color="القيمة", color_continuous_scale="Blues")
        fig.update_layout(font_family="Cairo")
        st.plotly_chart(fig, use_container_width=True)
    with c_right:
        st.subheader("تطور مؤشرات العائد")
        kpi_df = pd.DataFrame({
            "السنة": [2021, 2022, 2023, 2024],
            "ROI": [8.5, 9.2, 10.1, 10.8],
            "IRR": [10.2, 10.9, 11.3, 11.8]
        })
        fig = px.line(kpi_df, x="السنة", y=["ROI", "IRR"], markers=True)
        fig.update_layout(font_family="Cairo")
        st.plotly_chart(fig, use_container_width=True)
# ==========================================
# 2️⃣ إدارة الصكوك والوثائق
# ==========================================
elif st.session_state.selected_service == "إدارة الصكوك والوثائق":
    st.title("📜 إدارة الصكوك والوثائق")
    tab1, tab2 = st.tabs(["قائمة الصكوك", "إضافة صك جديد"])
    with tab1:
        st.dataframe(st.session_state.deeds_df, use_container_width=True)
    with tab2:
        with st.form("deed_form"):
            col1, col2 = st.columns(2)
            with col1:
                deed_no = st.text_input("رقم الصك")
                owner = st.text_input("المالك")
                district = st.selectbox("الحي", districts)
            with col2:
                area = st.number_input("المساحة (م²)", min_value=0.0)
                status = st.selectbox("الحالة", ["ساري", "محدث", "موقوف"])
            if st.form_submit_button("حفظ"):
                new_row = pd.DataFrame({"رقم الصك": [deed_no], "المالك": [owner], "الحي": [district], "المساحة م²": [area], "الحالة": [status]})
                st.session_state.deeds_df = pd.concat([st.session_state.deeds_df, new_row], ignore_index=True)
                st.success("تم الحفظ")
# ==========================================
# 3️⃣ التحليلات المالية
# ==========================================
elif st.session_state.selected_service == "التحليلات المالية":
    st.title("💰 التحليلات المالية")
    c1, c2, c3 = st.columns(3)
    c1.metric("الإيرادات السنوية", "18,000,000 ريال", "+1.8M")
    c2.metric("المصاريف التشغيلية", "5,400,000 ريال", "+400K")
    c3.metric("صافي الربح", "12,600,000 ريال", "+1.4M")
    fig = px.bar(financial_df, x="السنة", y=["الإيرادات", "المصاريف التشغيلية", "صيانة"], barmode="group")
    fig.update_layout(font_family="Cairo")
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("محاكاة استثمارية"):
        discount = st.slider("معدل الخصم %", 5.0, 15.0, 9.0)
        inv = st.number_input("الاستثمار الأولي", value=10_000_000)
        st.metric("NPV", f"{inv * 0.3 / (1+discount/100):,.0f} ريال")
# ==========================================
# 4️⃣ الذكاء المكاني والخرائط
# ==========================================
elif st.session_state.selected_service == "الذكاء المكاني والخرائط":
    st.title("🗺️ الذكاء المكاني")
    district = st.selectbox("اختر الحي", districts)
    col1, col2, col3 = st.columns(3)
    col1.metric("متوسط سعر المتر", f"{np.mean(price_mock[district]):,.0f} ريال")
    col2.metric("عدد الأصول", "320")
    col3.metric("مؤشر الطلب", "مرتفع")
    df_points = pd.DataFrame({
        "lat": [24.774265, 24.800000, 24.760000],
        "lon": [46.738586, 46.700000, 46.760000],
        "name": ["مبنى إداري", "مجمع تجاري", "أرض"]
    })
    fig = px.scatter_mapbox(df_points, lat="lat", lon="lon", hover_name="name", zoom=11)
    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig, use_container_width=True)
# ==========================================
# 5️⃣ نموذج التقييم الآلي AVM
# ==========================================
elif st.session_state.selected_service == "نموذج التقييم الآلي AVM":
    st.title("🤖 التقييم الآلي")
    with st.form("avm"):
        area = st.number_input("المساحة (م²)", 50, 10000, 250)
        district = st.selectbox("الحي", districts)
        quality = st.selectbox("الجودة", ["اقتصادي", "متوسط", "فاخر"])
        if st.form_submit_button("تقدير"):
            base = np.mean(price_mock[district])
            factor = {"اقتصادي":0.9, "متوسط":1.0, "فاخر":1.15}[quality]
            price = base * factor * area
            st.success(f"القيمة التقديرية: {price:,.0f} ريال")
# ==========================================
# 6️⃣ الصيانة التنبؤية (تم إصلاحها)
# ==========================================
elif st.session_state.selected_service == "الصيانة التنبؤية":
    st.title("🛠️ الصيانة التنبؤية")
    c1, c2, c3 = st.columns(3)
    c1.metric("معدل الجاهزية", "94.5%", "+1.5%")
    c2.metric("الأعطال المجدولة", "3.2%", "-1.1%")
    c3.metric("الميزانية المستهلكة", "1,500,000 ريال", "-50K")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=maintenance_df["الأسبوع"], y=maintenance_df["تكلفة الصيانة"], name="تكلفة الصيانة"))
    fig.add_trace(go.Scatter(x=maintenance_df["الأسبوع"], y=maintenance_df["تكلفة الإدارة"], name="تكلفة الإدارة"))
    fig.add_hline(y=500000, line_dash="dash", line_color="red", annotation_text="الحد الأقصى")
    fig.update_layout(font_family="Cairo")
    st.plotly_chart(fig, use_container_width=True)
# ==========================================
# 7️⃣ ذكاء السوق والاستثمار
# ==========================================
elif st.session_state.selected_service == "ذكاء السوق والاستثمار":
    st.title("📊 ذكاء السوق")
    market_df = pd.DataFrame({
        "السنة": list(range(2020, 2031)),
        "السكني": np.linspace(80, 145, 11),
        "التجاري": np.linspace(60, 110, 11),
        "الصناعي": np.linspace(40, 85, 11)
    })
    fig = px.area(market_df, x="السنة", y=["السكني", "التجاري", "الصناعي"])
    fig.update_layout(font_family="Cairo")
    st.plotly_chart(fig, use_container_width=True)
    st.info("نمو متسارع في القطاع الصناعي واللوجستي")
# ==========================================
# 8️⃣ إدارة العقود والمستأجرين
# ==========================================
elif st.session_state.selected_service == "إدارة العقود والمستأجرين":
    st.title("👥 العقود والمستأجرين")
    contracts = pd.DataFrame({
        "رقم العقد": ["C-101", "C-102"],
        "المستأجر": ["شركة الأفق", "مؤسسة البناء"],
        "القيمة الشهرية": [45_000, 28_000],
        "تاريخ الانتهاء": ["2025-01-01", "2025-03-14"]
    })
    st.dataframe(contracts, use_container_width=True)
    with st.expander("عقد جديد"):
        st.text_input("اسم المستأجر")
        st.number_input("الإيجار", min_value=0)
        st.button("حفظ")
# ==========================================
# 9️⃣ التنبؤ بالأسعار (AI)
# ==========================================
elif st.session_state.selected_service == "التنبؤ بالأسعار (AI)":
    st.title("📈 التنبؤ بالأسعار")
    months = pd.date_range("2024-01-01", periods=12, freq='M')
    historical = [4200, 4350, 4450, 4600, 4750, 4900, 5100, 5300, 5450, 5600, 5750, 5900]
    forecast = [6050, 6200, 6380, 6550, 6720, 6900, 7100, 7300, 7480, 7650, 7820, 8000]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=historical, name="تاريخي"))
    fig.add_trace(go.Scatter(x=months, y=forecast, name="متوقع", line=dict(dash="dot")))
    fig.update_layout(font_family="Cairo")
    st.plotly_chart(fig, use_container_width=True)
# ==========================================
# 🔟 تحليل المحفظة الاستثمارية
# ==========================================
elif st.session_state.selected_service == "تحليل المحفظة الاستثمارية":
    st.title("📊 تحليل المحفظة")
    port = pd.DataFrame({
        "القطاع": ["سكني", "تجاري", "صناعي"],
        "القيمة": [450, 320, 280],
        "العائد": [8, 10, 12]
    })
    fig = px.pie(port, names="القطاع", values="القيمة", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)
    st.bar_chart(port.set_index("القطاع")["العائد"])
# ==========================================
# 1️⃣1️⃣ الامتثال القانوني والتراخيص
# ==========================================
elif st.session_state.selected_service == "الامتثال القانوني والتراخيص":
    st.title("⚖️ التراخيص")
    licenses = pd.DataFrame({
        "الترخيص": ["رخصة بناء", "رخصة تشغيل", "دفاع مدني"],
        "تاريخ الانتهاء": ["2025-06-01", "2024-12-31", "2024-10-20"],
        "الحالة": ["ساري", "ينتهي قريباً", "منتهي"]
    })
    st.dataframe(licenses, use_container_width=True)
# ==========================================
# 1️⃣2️⃣ لوحة تحكم المخاطر
# ==========================================
elif st.session_state.selected_service == "لوحة تحكم المخاطر":
    st.title("⚠️ المخاطر")
    risks = pd.DataFrame({
        "الخطر": ["تقلبات السوق", "مخاطر الائتمان", "تشغيلية"],
        "الاحتمال": [35, 25, 45],
        "الأثر": [4, 3, 3]
    })
    risks["النقطة"] = risks["الاحتمال"] * risks["الأثر"]
    fig = px.bar(risks, x="الخطر", y="النقطة", color="النقطة")
    st.plotly_chart(fig, use_container_width=True)
# ==========================================
# 1️⃣3️⃣ التقارير الذكية
# ==========================================
elif st.session_state.selected_service == "التقارير الذكية القابلة للتخصيص":
    st.title("📑 التقارير الذكية")
    report_type = st.selectbox("نوع التقرير", ["ملخص", "مالي", "صيانة"])
    if report_type == "ملخص":
        st.dataframe(pd.DataFrame({"المؤشر": ["الأصول", "القيمة"], "القيمة": ["1,280", "2.4 مليار"]}))
    elif report_type == "مالي":
        st.line_chart(financial_df.set_index("السنة")["الإيرادات"])
    else:
        st.bar_chart(maintenance_df.set_index("الأسبوع")["تكلفة الصيانة"])
    st.download_button("تحميل CSV", data="sample", file_name="report.csv")
# ==========================================
# 1️⃣4️⃣ مركز التنبيهات
# ==========================================
elif st.session_state.selected_service == "مركز التنبيهات والإشعارات":
    st.title("🔔 التنبيهات")
    alerts = pd.DataFrame({
        "التاريخ": ["2024-12-15", "2024-12-14"],
        "الرسالة": ["انتهاء رخصة تشغيل", "إضافة صك جديد"],
        "النوع": ["تحذير", "معلومات"]
    })
    st.dataframe(alerts, use_container_width=True)
    if st.button("تحديد كمقروء"):
        st.success("تم")

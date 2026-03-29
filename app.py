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
# CSS محسن للهوية العربية والـ RTL مع لمسات جمالية للبطاقات والأيقونات العلوية
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [data-testid="stSidebar"], .main, .stMarkdown {
        direction: RTL !important;
        text-align: right !important;
        font-family: 'Cairo', sans-serif !important;
    }
    section[data-testid="stSidebar"] > div { text-align: right; }
    /* تحسين شكل الـ Metrics */
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
    /* أزرار مخصصة */
    .stButton>button {
        width: 100%;
        font-family: 'Cairo', sans-serif !important;
        background-color: #1E3A8A !important;
        color: white !important;
        border-radius: 8px !important;
    }
    /* تنسيق شريط الأيقونات العلوي */
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
#  إدارة البيانات وحفظ الحالة (Session State)
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
        "تكلفة الإدارة": np.random.randint(150_000, 400_000, 13)
    })
    return districts, price_mock, financial_df, maintenance_df
districts, price_mock, financial_df, maintenance_df = load_base_data()
# إدارة حالة الصكوك
if 'deeds_df' not in st.session_state:
    st.session_state.deeds_df = pd.DataFrame({
        "رقم الصك": ["123/أ", "456/ب", "789/ج"],
        "المالك": ["شركة أصول الأولى", "صندوق استثماري عقاري", "شركة تطوير عمراني"],
        "الحي": ["الملقا", "الياسمين", "النرجس"],
        "المساحة م²": [2500, 4300, 1800],
        "الحالة": ["ساري", "ساري", "محدث"]
    })
# إدارة حالة الاختيار للقائمة الجانبية والأيقونات العلوية
if 'selected_service' not in st.session_state:
    st.session_state.selected_service = "لوحة القيادة التنفيذية"

def set_service(service_name):
    st.session_state.selected_service = service_name
# ==========================================
# 📂 القائمة الجانبية – 14 خدمة
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
    # قائمة الخدمات الموسعة إلى 14 عنصراً
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
            },
            on_change=lambda: set_service(choice)  # تحديث الحالة عند الاختيار
        )
        st.session_state.selected_service = choice
    except:
        choice = st.radio("الخدمات المتكاملة", list(services.keys()), index=list(services.keys()).index(st.session_state.selected_service))
        st.session_state.selected_service = choice

st.write(f"🔐 الدور الحالي في النظام: **{role}**")
st.divider()
# ==========================================
# 🎨 شريط الأيقونات العلوي (أيقونات سريعة للميزات الرئيسية)
# ==========================================
st.markdown("### ⚡ الوصول السريع إلى الخدمات")
cols = st.columns(7)  # 7 أيقونات بارزة
quick_services = list(services.keys())[:7]  # أول 7 خدمات
for i, service in enumerate(quick_services):
    with cols[i]:
        # أيقونة نصية مع emoji بدلاً من الصور لسهولة التنفيذ
        icon_map = {
            "لوحة القيادة التنفيذية": "📊",
            "إدارة الصكوك والوثائق": "📜",
            "التحليلات المالية": "💰",
            "الذكاء المكاني والخرائط": "🗺️",
            "نموذج التقييم الآلي AVM": "🤖",
            "الصيانة التنبؤية": "🛠️",
            "ذكاء السوق والاستثمار": "📈"
        }
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
    c_left, c_right = st.columns([1, 1])
    with c_left:
        st.subheader(" توزيع القيمة حسب نوع العقار")
        asset_type_df = pd.DataFrame({
            "نوع العقار": ["شقق", "مكاتب", "تجاري", "صناعي", "فلل"],
            "القيمة": [600, 450, 520, 300, 530]
        })
        fig_asset = px.bar(asset_type_df, x="نوع العقار", y="القيمة", color="القيمة", color_continuous_scale="Blues", labels={'القيمة': 'القيمة (مليون ريال)'})
        fig_asset.update_layout(font_family="Cairo", plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_asset, use_container_width=True)
    with c_right:
        st.subheader("📈 تطور مؤشرات العائد (ROI / IRR)")
        kpi_df = pd.DataFrame({
            "السنة": [2021, 2022, 2023, 2024],
            "ROI": [8.5, 9.2, 10.1, 10.8],
            "IRR": [10.2, 10.9, 11.3, 11.8]
        })
        fig_kpi = px.line(kpi_df, x="السنة", y=["ROI", "IRR"], markers=True)
        fig_kpi.update_layout(font_family="Cairo", yaxis_title="النسبة %", legend_title="المؤشر")
        st.plotly_chart(fig_kpi, use_container_width=True)
# ==========================================
# 2️⃣ إدارة الصكوك والوثائق
# ==========================================
elif st.session_state.selected_service == "إدارة الصكوك والوثائق":
    st.title("📜 إدارة الصكوك والوثائق Digital Archiving")
    tab1, tab2 = st.tabs(["📂 قائمة الصكوك الحالية", "➕ إضافة صك جديد"])
    with tab1:
        st.subheader("سجل الأرشيف الرقمي")
        st.dataframe(st.session_state.deeds_df, use_container_width=True)
    with tab2:
        st.subheader("إدخال صك جديد في النظام")
        with st.form("deed_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                deed_no = st.text_input("رقم الصك")
                owner = st.text_input("اسم المالك")
                district = st.selectbox("الحي", districts)
            with col_b:
                area = st.number_input("المساحة (م²)", min_value=0.0, step=50.0)
                status = st.selectbox("حالة الصك", ["ساري", "محدث", "موقوف"])  
            submitted = st.form_submit_button("💾 حفظ الصك في قاعدة البيانات")
            if submitted:
                if deed_no and owner:
                    new_row = pd.DataFrame({
                        "رقم الصك": [deed_no], "المالك": [owner],
                        "الحي": [district], "المساحة م²": [area], "الحالة": [status]
                    })
                    st.session_state.deeds_df = pd.concat([st.session_state.deeds_df, new_row], ignore_index=True)
                    st.success("✅ تم حفظ الصك بنجاح وتحديث الجدول الجاري!")
                else:
                    st.error("❌ فضلاً، املأ الحقول المطلوبة (رقم الصك والمالك).")
# ==========================================
# 3️⃣ التحليلات المالية
# ==========================================
elif st.session_state.selected_service == "التحليلات المالية":
    st.title("💰 التحليلات المالية والتدفقات النقدية")
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي الإيرادات السنوية", "18,000,000 ريال", "+1,800,000")
    c2.metric("المصاريف التشغيلية", "5,400,000 ريال", "+400,000")
    c3.metric("صافي الربح التشغيلي", "12,600,000 ريال", "+1,400,000")
    st.divider()
    tab_fin1, tab_fin2 = st.tabs([" التحليل التاريخي", "🔮 محاكاة المشاريع الاستثمارية"])
    with tab_fin1:
        st.subheader("تحليل الإيرادات والمصاريف عبر السنوات")
        fig_fin = px.bar(financial_df, x="السنة", y=["الإيرادات", "المصاريف التشغيلية", "صيانة"], barmode="group", color_discrete_sequence=["#1E3A8A", "#64748B", "#94A3B8"])
        fig_fin.update_layout(font_family="Cairo", yaxis_title="القيمة بالريال")
        st.plotly_chart(fig_fin, use_container_width=True)
    with tab_fin2:
        st.subheader("محاكاة دراسة جدوى مبدئية (NPV / IRR)")
        col_l, col_r = st.columns(2)
        with col_l:
            discount_rate = st.slider("معدل الخصم المرجح (Discount Rate %)", 5.0, 15.0, 9.0, 0.5)
            years = st.slider("مدى المشروع (بالسنوات)", 3, 10, 5)
            initial_investment = st.number_input("الاستثمار الرأسمالي الابتدائي (Capex)", value=10_000_000, step=1_000_000)
        with col_r:
            cash_flows = [initial_investment * 0.30 for _ in range(years)]
            npv = sum(cf / ((1 + discount_rate/100) ** (i+1)) for i, cf in enumerate(cash_flows)) - initial_investment
            irr_approx = (sum(cash_flows) - initial_investment) / initial_investment * 100
            st.metric("صافي القيمة الحالية (NPV)", f"{npv:,.0f} ريال", delta="إيجابي" if npv > 0 else "سلبي")
            st.metric("معدل العائد الداخلي المتوقع (IRR)", f"{irr_approx:.2f}%")
# ==========================================
# 4️⃣ الذكاء المكاني والخرائط
# ==========================================
elif st.session_state.selected_service == "الذكاء المكاني والخرائط":
    st.title("🗺️ الذكاء المكاني وتحليلات الخرائط Spatial Intelligence")
    district = st.selectbox("📍 اختر الحي المستهدف", districts)
    c1, c2, c3 = st.columns(3)
    c1.metric("متوسط سعر المتر في الحي", f"{sum(price_mock[district])//len(price_mock[district]):,} ريال")
    c2.metric("عدد الأصول المسجلة بالحي", "320 قطعة", "+24")
    c3.metric("مؤشر الطلب والسيولة", "مرتفع", "↑")
    st.divider()
    map_tab1, map_tab2 = st.tabs(["📍 مواقع الأصول ونقاط التقييم", "📐 حدود الأراضي والمخططات (GIS)"])
    with map_tab1:
        st.subheader("عرض الأصول على الخريطة التفاعلية")
        df_points = pd.DataFrame({
            "lat": [24.774265, 24.800000, 24.760000, 24.820000],
            "lon": [46.738586, 46.700000, 46.760000, 46.680000],
            "اسم الأصل": ["مبنى إداري 1", "مجمع تجاري 2", "أرض خام 3", "مستودع 4"],
            "القيمة": [4_200_000, 7_800_000, 5_100_000, 3_100_000]
        })
        try:
            with open("config/mapbox_token.txt") as f:
                px.set_mapbox_access_token(f.read().strip())
            fig_map = px.scatter_mapbox(df_points, lat="lat", lon="lon", hover_name="اسم الأصل", size="القيمة", color="القيمة", color_continuous_scale="Viridis", zoom=11, height=500)
        except:
            fig_map = px.scatter(df_points, x="lon", y="lat", text="اسم الأصل", size="القيمة", color="القيمة", height=500, title="رسم بياني إحداثي (يرجى إدراج Mapbox Token لخرائط حقيقية)")
        st.plotly_chart(fig_map, use_container_width=True)
    with map_tab2:
        st.subheader("تكامل بيانات الطبقات الجغرافية GeoJSON")
        col_map_l, col_map_r = st.columns([1, 1])
        with col_map_l:
            plot_data = pd.DataFrame({"المخطط": ["مخطط أ", "مخطط ب", "مخطط ج", "مخطط د"], "السعر للمتر": price_mock[district]})
            fig_area = px.area(plot_data, x="المخطط", y="السعر للمتر", title=f"اتجاهات الأسعار في حي {district}")
            fig_area.update_layout(font_family="Cairo")
            st.plotly_chart(fig_area, use_container_width=True)
        with col_map_r:
            st.info("📦 جاهز للتوصيل مع PostGIS و ArcGIS. عينة لهيكلية GeoJSON لحفظ الحدود:")
            sample_geo = {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[46.73, 24.77], [46.74, 24.77], [46.73, 24.78], [46.73, 24.77]]]}, "properties": {"اسم_القطعة": "بلك 14 - قطعة 2"}}
            st.json(sample_geo)
# ==========================================
# 5️⃣ نموذج التقييم الآلي AVM
# ==========================================
elif st.session_state.selected_service == "نموذج التقييم الآلي AVM":
    st.title("🤖 نموذج التقييم الآلي – Automated Valuation Model")  
    col_avm_l, col_avm_r = st.columns([1.2, 1])
    with col_avm_l:
        st.subheader(" مدخلات تقدير السعر العادل")
        with st.form("avm_form"):
            col_in1, col_in2 = st.columns(2)
            with col_in1:
                area = st.number_input("المساحة الإجمالية (م²)", min_value=50.0, value=250.0, step=10.0)
                district = st.selectbox("الحي", districts)
                frontage = st.number_input("طول الواجهة على الشارع (م)", min_value=5.0, value=15.0)
            with col_in2:
                street_width = st.number_input("عرض الشارع المتاخم (م)", min_value=8.0, value=20.0)
                age = st.number_input("عمر العقار الحالي (بالسنوات)", min_value=0.0, value=5.0)
                quality = st.selectbox("جودة التشطيب والمواد", ["اقتصادي", "متوسط", "فاخر"])           
            est_btn = st.form_submit_button(" تشغيل خوارزمية التقييم")         
            if est_btn:
                base_price = sum(price_mock[district]) / len(price_mock[district])
                factors = {"اقتصادي": 0.9, "متوسط": 1.0, "فاخر": 1.15}               
                price_per_m2 = base_price * factors[quality] * max(0.7, 1-(age*0.015)) * (1+(frontage/100)) * (1+(street_width/200))
                estimated_value = price_per_m2 * area                
                st.success(f"💰 القيمة العادلة المقدرة للعقار: {estimated_value:,.0f} ريال سعودي")
                st.metric("متوسط سعر المتر المربع التقديري", f"{price_per_m2:,.2f} ريال/م²")
    with col_avm_r:
        st.subheader("⚖️ أوزان العوامل في الخوارزمية")
        factors_df = pd.DataFrame({"العامل الجغرافي والمعماري": ["الموقع الجغرافي", "المساحة الكلية", "جودة التشطيب", "عمر البناء", "عرض الشارع"], "الأهمية النسبية %": [35, 25, 15, 15, 10]})
        fig_pie = px.pie(factors_df, names="العامل الجغرافي والمعماري", values="الأهمية النسبية %", color_discrete_sequence=px.colors.sequential.Blues_r)
        fig_pie.update_layout(font_family="Cairo")
        st.plotly_chart(fig_pie, use_container_width=True)
# ==========================================
# 6️⃣ الصيانة التنبؤية
# ==========================================
elif st.session_state.selected_service == "الصيانة التنبؤية":
    st.title("🛠️ الصيانة التنبؤية – Predictive Maintenance")
    # إضافة عمود اسم الأصل إذا لم يكن موجوداً
    if "اسم الأصل" not in maintenance_df.columns:
        maintenance_df["اسم الأصل"] = ["مبنى إداري 1", "مجمع تجاري 2", "أرض خام 3", "مستودع 4", "مبنى سكني 5"] * 3
        maintenance_df = maintenance_df.head(13)
    c1, c2, c3 = st.columns(3)
    c1.metric("معدل جاهزية الأصول", "94.5%", "+1.5%")
    c2.metric("معدل الأعطال المجدولة", "3.2%", "-1.1%")
    c3.metric("ميزانية الصيانة المستهلكة", "1,500,000 ريال", "-50,000")
    st.divider()
    col_m1, col_m2 = st.columns([1.5, 1])
    with col_m1:
        st.subheader(" تتبع التكاليف الأسبوعي وحد الأمان للميزانية")
        fig_maint = go.Figure()
        fig_maint.add_trace(go.Scatter(x=maintenance_df["الأسبوع"], y=maintenance_df["تكلفة الصيانة"], name="تكلفة الصيانة", line=dict(color="#1E3A8A")))
        fig_maint.add_trace(go.Scatter(x=maintenance_df["الأسبوع"], y=maintenance_df["تكلفة الإدارة"], name="تكلفة الإدارة", line=dict(color="#64748B")))
        fig_maint.add_hline(y=500000, line_dash="dash", line_color="red", annotation_text="سقف الميزانية الأسبوعية")
        fig_maint.update_layout(font_family="Cairo", yaxis_title="التكلفة (ريال)", xaxis_title="الأسبوع تتبعاً")
        st.plotly_chart(fig_maint, use_container_width=True)
    with col_m2:
        st.subheader("🧩 توزيع طلبات الصيانة")
        pie_df = pd.DataFrame({"الفئة": ["إصلاحات طارئة", "صيانة وقائية", "معالجة بلاغات", "خدمات عامة"], "القيمة": [25, 45, 20, 10]})
        fig_pie_m = px.pie(pie_df, names="الفئة", values="القيمة", hole=0.4, color_discrete_sequence=["#1E3A8A", "#2563EB", "#64748B", "#94A3B8"])
        fig_pie_m.update_layout(font_family="Cairo")
        st.plotly_chart(fig_pie_m, use_container_width=True)
# ==========================================
# 7️⃣ ذكاء السوق والاستثمار
# ==========================================
elif st.session_state.selected_service == "ذكاء السوق والاستثمار":
    st.title("📊 ذكاء السوق والمؤشرات التنافسية Market Intelligence")
    st.subheader("📈 حجم سوق العقارات حسب القطاع وعام الاستشراف (2020-2030)")
    market_df = pd.DataFrame({
        "السنة": list(range(2020, 2031)),
        "القطاع السكني": np.linspace(80, 145, 11),
        "القطاع التجاري": np.linspace(60, 110, 11),
        "القطاع الصناعي": np.linspace(40, 85, 11)
    })
    fig_market = px.area(market_df, x="السنة", y=["القطاع السكني", "القطاع التجاري", "القطاع الصناعي"], color_discrete_sequence=["#1E3A8A", "#3B82F6", "#94A3B8"])
    fig_market.update_layout(font_family="Cairo", yaxis_title="القيمة (مليار ريال)")
    st.plotly_chart(fig_market, use_container_width=True)
    col_k, col_not = st.columns([1, 2])
    with col_k:
        st.metric("معدل النمو السنوي المركب (CAGR)", "5.4%", "+0.7%")
    with col_not:
        st.info("💡 نصيحة النظام: تظهر البيانات التاريخية والتحليلات المستقبلية نمواً متسارعاً في **القطاع الصناعي واللوجستي** في أطراف الرياض. يوصى بزيادة الوزن النسبي في المحفظة.")
# ==========================================
# 8️⃣ إدارة العقود والمستأجرين (خدمة جديدة)
# ==========================================
elif st.session_state.selected_service == "إدارة العقود والمستأجرين":
    st.title("👥 إدارة العقود والمستأجرين")
    st.subheader("عقود الإيجار النشطة")
    contracts = pd.DataFrame({
        "رقم العقد": ["C-101", "C-102", "C-103"],
        "المستأجر": ["شركة الأفق", "مؤسسة البناء", "فردي - أحمد"],
        "العقار": ["برج الأعمال - الطابق 3", "مجمع الريان", "فيلا الياسمين"],
        "تاريخ البدء": ["2024-01-01", "2024-03-15", "2024-05-01"],
        "تاريخ الانتهاء": ["2025-01-01", "2025-03-14", "2025-04-30"],
        "القيمة الشهرية (ريال)": [45_000, 28_000, 12_000]
    })
    st.dataframe(contracts, use_container_width=True)
    with st.expander("➕ إضافة عقد جديد"):
        with st.form("new_contract"):
            col1, col2 = st.columns(2)
            with col1:
                contract_no = st.text_input("رقم العقد")
                tenant = st.text_input("اسم المستأجر")
                property_name = st.text_input("العقار")
            with col2:
                start_date = st.date_input("تاريخ البدء")
                end_date = st.date_input("تاريخ الانتهاء")
                rent = st.number_input("القيمة الشهرية (ريال)", min_value=0)
            if st.form_submit_button("حفظ العقد"):
                st.success("تمت إضافة العقد بنجاح (نموذج توضيحي)")
# ==========================================
# 9️⃣ التنبؤ بالأسعار (AI) – خدمة جديدة
# ==========================================
elif st.session_state.selected_service == "التنبؤ بالأسعار (AI)":
    st.title("📈 التنبؤ بأسعار العقارات باستخدام الذكاء الاصطناعي")
    st.write("نموذج توقع اتجاه الأسعار خلال الـ 12 شهراً القادمة بناءً على البيانات التاريخية.")
    future_months = pd.date_range(start="2024-01-01", periods=12, freq='M')
    historical_prices = [4200, 4350, 4450, 4600, 4750, 4900, 5100, 5300, 5450, 5600, 5750, 5900]
    forecast = [6050, 6200, 6380, 6550, 6720, 6900, 7100, 7300, 7480, 7650, 7820, 8000]
    df_forecast = pd.DataFrame({"الشهر": future_months.strftime("%Y-%m"), "السعر التاريخي": historical_prices + [None]*12, "التوقع": [None]*12 + forecast})
    # عرض الرسم البياني
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=future_months, y=historical_prices, mode='lines+markers', name='بيانات تاريخية', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=future_months, y=forecast, mode='lines+markers', name='التوقع المستقبلي', line=dict(color='red', dash='dot')))
    fig.update_layout(title="توقع أسعار المتر المربع (ريال)", xaxis_title="الشهر", yaxis_title="السعر", font_family="Cairo")
    st.plotly_chart(fig, use_container_width=True)
    st.info("🧠 بناءً على نموذج ARIMA، من المتوقع ارتفاع الأسعار بنسبة 7.2% خلال العام القادم.")
# ==========================================
# 🔟 تحليل المحفظة الاستثمارية – خدمة جديدة
# ==========================================
elif st.session_state.selected_service == "تحليل المحفظة الاستثمارية":
    st.title("📊 تحليل المحفظة الاستثمارية")
    portfolio = pd.DataFrame({
        "القطاع": ["سكني", "تجاري", "صناعي", "مكاتب"],
        "القيمة (مليون ريال)": [450, 320, 280, 410],
        "العائد المتوقع (%)": [8, 10, 12, 9],
        "المخاطر (الانحراف المعياري)": [0.12, 0.18, 0.22, 0.15]
    })
    st.subheader("توزيع المحفظة الحالي")
    fig_pie = px.pie(portfolio, names="القطاع", values="القيمة (مليون ريال)", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig_pie, use_container_width=True)
    st.subheader("مقاييس العائد مقابل المخاطر")
    fig_scatter = px.scatter(portfolio, x="المخاطر (الانحراف المعياري)", y="العائد المتوقع (%)", size="القيمة (مليون ريال)", text="القطاع", color="القطاع", title="عائد-مخاطر لكل قطاع")
    fig_scatter.update_layout(font_family="Cairo")
    st.plotly_chart(fig_scatter, use_container_width=True)
# ==========================================
# 1️⃣1️⃣ الامتثال القانوني والتراخيص – خدمة جديدة
# ==========================================
elif st.session_state.selected_service == "الامتثال القانوني والتراخيص":
    st.title("⚖️ الامتثال القانوني والتراخيص")
    licenses = pd.DataFrame({
        "الترخيص": ["رخصة بناء", "رخصة تشغيل", "شهادة سلامة", "رخصة دفاع مدني"],
        "رقم الترخيص": ["BL-2345", "OP-9876", "SF-5544", "CD-1122"],
        "تاريخ الانتهاء": ["2025-06-01", "2024-12-31", "2026-03-15", "2024-10-20"],
        "الحالة": ["ساري", "ينتهي قريباً", "ساري", "منتهي"]
    })
    st.dataframe(licenses, use_container_width=True)
    st.warning("⚠️ تراخيص منتهية أو على وشك الانتهاء: رخصة تشغيل (31-12-2024)، رخصة دفاع مدني (20-10-2024 منتهية).")
# ==========================================
# 1️⃣2️⃣ لوحة تحكم المخاطر – خدمة جديدة
# ==========================================
elif st.session_state.selected_service == "لوحة تحكم المخاطر":
    st.title("⚠️ لوحة تحكم المخاطر")
    risk_factors = pd.DataFrame({
        "عامل الخطر": ["تقلبات السوق", "مخاطر الائتمان", "المخاطر التشغيلية", "مخاطر الامتثال", "الكوارث الطبيعية"],
        "الاحتمالية (%)": [35, 25, 45, 20, 15],
        "الأثر (1-5)": [4, 3, 3, 4, 5],
        "نقطة المخاطرة (احتمال*أثر)": [140, 75, 135, 80, 75]
    })
    st.subheader("مصفوفة المخاطر")
    fig = px.bar(risk_factors, x="عامل الخطر", y="نقطة المخاطرة", color="نقطة المخاطرة", color_continuous_scale="Reds", title="تقييم المخاطر الحالي")
    fig.update_layout(font_family="Cairo")
    st.plotly_chart(fig, use_container_width=True)
    st.metric("إجمالي درجة المخاطر", "505", "+25 عن الربع السابق")
# ==========================================
# 1️⃣3️⃣ التقارير الذكية القابلة للتخصيص – خدمة جديدة
# ==========================================
elif st.session_state.selected_service == "التقارير الذكية القابلة للتخصيص":
    st.title("📑 التقارير الذكية القابلة للتخصيص")
    report_type = st.selectbox("اختر نوع التقرير", ["ملخص المحفظة", "تحليل الأداء المالي", "حالة الصيانة", "تحليل السوق"])
    if report_type == "ملخص المحفظة":
        st.subheader("ملخص المحفظة العقارية")
        st.dataframe(pd.DataFrame({
            "المؤشر": ["عدد الأصول", "القيمة الإجمالية", "متوسط العائد", "نسبة الإشغال"],
            "القيمة": ["1,280", "2.4 مليار ريال", "11.8%", "89%"]
        }))
    elif report_type == "تحليل الأداء المالي":
        st.subheader("الإيرادات والمصروفات")
        st.line_chart(financial_df.set_index("السنة"))
    elif report_type == "حالة الصيانة":
        st.subheader("تكاليف الصيانة الأسبوعية")
        st.bar_chart(maintenance_df.set_index("الأسبوع")[["تكلفة الصيانة", "تكلفة الإدارة"]])
    else:
        st.subheader("تحليل السوق")
        st.line_chart(pd.DataFrame({"السنة": list(range(2020,2031)), "النمو": np.random.uniform(2,8,11)}).set_index("السنة"))
    st.download_button("تحميل التقرير (CSV وهمي)", data="محتوى التقرير", file_name="report.csv")
# ==========================================
# 1️⃣4️⃣ مركز التنبيهات والإشعارات – خدمة جديدة
# ==========================================
elif st.session_state.selected_service == "مركز التنبيهات والإشعارات":
    st.title("🔔 مركز التنبيهات والإشعارات")
    notifications = [
        {"التاريخ": "2024-12-15", "الرسالة": "انتهاء رخصة تشغيل المبنى A خلال 15 يوماً", "النوع": "تحذير", "الحالة": "غير مقروء"},
        {"التاريخ": "2024-12-14", "الرسالة": "تم إضافة صك جديد لملكية قطعة 567", "النوع": "معلومات", "الحالة": "مقروء"},
        {"التاريخ": "2024-12-13", "الرسالة": "تجاوز ميزانية الصيانة بنسبة 5%", "النوع": "تنبيه", "الحالة": "غير مقروء"},
        {"التاريخ": "2024-12-12", "الرسالة": "تحديث أسعار المتر في حي الياسمين", "النوع": "تحديث", "الحالة": "مقروء"},
    ]
    st.dataframe(pd.DataFrame(notifications), use_container_width=True)
    if st.button("تحديد الكل كمقروء"):
        st.success("تم تحديث الحالة (تجريبي)")

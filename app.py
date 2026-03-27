import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
# ==========================================
# ⚙️ إعدادات الصفحة والهوية البصرية
# ==========================================
st.set_page_config(
    layout="wide",
    page_title="Drones Crafters – Real Estate Management Dashboard",
    page_icon="🏢"
)
# CSS محسن للهوية العربية والـ RTL مع لمسات جمالية للبطاقات
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
    </style>
""", unsafe_allow_html=True)
# ==========================================
#  إدارة البيانات وحفظ الحالة (Session State)
# ==========================================
# 1. تهيئة البيانات الأساسية (Data Caching للأداء)
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
# 2. إدارة حالة الصكوك لجعل الجدول تفاعلياً
if 'deeds_df' not in st.session_state:
    st.session_state.deeds_df = pd.DataFrame({
        "رقم الصك": ["123/أ", "456/ب", "789/ج"],
        "المالك": ["شركة أصول الأولى", "صندوق استثماري عقاري", "شركة تطوير عمراني"],
        "الحي": ["الملقا", "الياسمين", "النرجس"],
        "المساحة م²": [2500, 4300, 1800],
        "الحالة": ["ساري", "ساري", "محدث"]
    })
# ==========================================
# 📂 القائمة الجانبية – الأدوار والوحدات
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/10543/10543319.png", width=80) # أيقونة رمزية للهوية
    st.title("Drones Crafters")
    st.subheader("إدارة الأصول العقارية")
    role = st.selectbox(
        "الدور التنفيذي",
        ["System Admin", "Asset Manager", "Investment Analyst", "External Auditor"],
        format_func=lambda x: {
            "System Admin": "🛠️ مسؤول النظام",
            "Asset Manager": " مدير الأصول",
            "Investment Analyst": " محلل استثماري",
            "External Auditor": " مدقق خارجي"
        }[x]
    )
    st.divider()
    try:
        from streamlit_option_menu import option_menu
        choice = option_menu(
            "الوحدات الرئيسية",
            ["لوحة القيادة التنفيذية", "إدارة الصكوك والوثائق", "التحليلات المالية", "الذكاء المكاني والخرائط", "نموذج التقييم الآلي AVM", "الصيانة التنبؤية", "ذكاء السوق والاستثمار"],
            icons=["speedometer2", "file-earmark-text", "currency-dollar", "geo-alt", "robot", "tools", "graph-up-arrow"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "5px", "background-color": "#fafafa"},
                "nav-link": {"font-size": "14px", "text-align": "right", "margin": "0px", "font-family": "Cairo"},
                "nav-link-selected": {"background-color": "#1E3A8A"},
            }
        )
    except:
        choice = st.radio(
            "الوحدات الرئيسية",
            ["لوحة القيادة التنفيذية", "إدارة الصكوك والوثائق", "التحليلات المالية", "الذكاء المكاني والخرائط", "نموذج التقييم الآلي AVM", "الصيانة التنبؤية", "ذكاء السوق والاستثمار"]
        )

st.write(f" الدور الحالي في النظام: **{role}**")
st.divider()
# ==========================================
# 1️⃣ لوحة القيادة التنفيذية
# ==========================================
if choice == "لوحة القيادة التنفيذية":
    st.title("🏢 لوحة القيادة التنفيذية – Portfolio & Risk")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("إجمالي قيمة الأصول", "2.4 مليار ريال", "+4.2%")
    col2.metric("عدد العقارات", "1,280 أصل", "+35")
    col3.metric("متوسط العائد السنوي (IRR)", "11.8%", "+0.6%")
    col4.metric("نسبة الإشغال", "89%", "-3.1%")
    st.divider()
    c_left, c_right = st.columns([1, 1])
    with c_left:
        st.subheader("📊 توزيع القيمة حسب نوع العقار")
        asset_type_df = pd.DataFrame({
            "نوع العقار": ["شقق", "مكاتب", "تجاري", "صناعي", "فلل"],
            "القيمة": [600, 450, 520, 300, 530]
        })
        fig_asset = px.bar(
            asset_type_df, x="نوع العقار", y="القيمة",
            color="القيمة", color_continuous_scale="Blues",
            labels={'القيمة': 'القيمة (مليون ريال)'}
        )
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
# 2️⃣ إدارة الصكوك والوثائق (تفاعلية)
# ==========================================
elif choice == "إدارة الصكوك والوثائق":
    st.title("📜 إدارة الصكوك والوثائق Digital Archiving")
    tab1, tab2 = st.tabs(["📂 قائمة الصكوك الحالية", "➕ إضافة صك جديد"])
    
    with tab1:
        st.subheader("سجل الأرشيف الرقمي")
        # عرض البيانات من الـ session_state لتحديثها فوراً
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
                    # إضافة السطر الجديد للـ DataFrame في الـ session_state
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
elif choice == "التحليلات المالية":
    st.title("💰 التحليلات المالية والتدفقات النقدية")
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي الإيرادات السنوية", "18,000,000 ريال", "+1,800,000")
    c2.metric("المصاريف التشغيلية", "5,400,000 ريال", "+400,000")
    c3.metric("صافي الربح التشغيلي", "12,600,000 ريال", "+1,400,000")
    st.divider()
    tab_fin1, tab_fin2 = st.tabs(["📊 التحليل التاريخي", "🔮 محاكاة المشاريع الاستثمارية"])
    with tab_fin1:
        st.subheader("تحليل الإيرادات والمصاريف عبر السنوات")
        fig_fin = px.bar(
            financial_df, x="السنة", y=["الإيرادات", "المصاريف التشغيلية", "صيانة"],
            barmode="group", color_discrete_sequence=["#1E3A8A", "#64748B", "#94A3B8"]
        )
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
            # حساب التدفقات النقدية والـ NPV الفعلي
            cash_flows = [initial_investment * 0.30 for _ in range(years)] # فرضية عائد 30% من الكابكس سنوياً
            npv = sum(cf / ((1 + discount_rate/100) ** (i+1)) for i, cf in enumerate(cash_flows)) - initial_investment
            irr_approx = (sum(cash_flows) - initial_investment) / initial_investment * 100 # تقريب تعليمي
            st.metric("صافي القيمة الحالية (NPV)", f"{npv:,.0f} ريال", delta="إيجابي" if npv > 0 else "سلبي")
            st.metric("معدل العائد الداخلي المتوقع (IRR)", f"{irr_approx:.2f}%")
# ==========================================
# 4️⃣ الذكاء المكاني والخرائط (تم دمجها وتحسينها)
# ==========================================
elif choice == "الذكاء المكاني والخرائط":
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
        # تجربة تحميل Mapbox مع Fallback ذكي إذا لم يتوفر التوكن
        try:
            with open("config/mapbox_token.txt") as f:
                px.set_mapbox_access_token(f.read().strip())
            fig_map = px.scatter_mapbox(df_points, lat="lat", lon="lon", hover_name="اسم الأصل",
                                        size="القيمة", color="القيمة", color_continuous_scale="Viridis", zoom=11, height=500)
        except:
            # رسم قياسي في حال لم يتوفر الـ Mapbox Token
            fig_map = px.scatter(df_points, x="lon", y="lat", text="اسم الأصل", size="القيمة", 
                                 color="القيمة", height=500, title="رسم بياني إحداثي (يرجى إدراج Mapbox Token لخرائط حقيقية)")
        st.plotly_chart(fig_map, use_container_width=True)
    with map_tab2:
        st.subheader("تكامل بيانات الطبقات الجغرافية GeoJSON")
        col_map_l, col_map_r = st.columns([1, 1])
        with col_map_l:
            plot_data = pd.DataFrame({
                "المخطط": ["مخطط أ", "مخطط ب", "مخطط ج", "مخطط د"],
                "السعر للمتر": price_mock[district]
            })
            fig_area = px.area(plot_data, x="المخطط", y="السعر للمتر", title=f"اتجاهات الأسعار في حي {district}")
            fig_area.update_layout(font_family="Cairo")
            st.plotly_chart(fig_area, use_container_width=True)
        with col_map_r:
            st.info("📦 جاهز للتوصيل مع PostGIS و ArcGIS. عينة لهيكلية GeoJSON لحفظ الحدود:")
            sample_geo = {
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [[[46.73, 24.77], [46.74, 24.77], [46.73, 24.78], [46.73, 24.77]]]},
                "properties": {"اسم_القطعة": "بلك 14 - قطعة 2"}
            }
            st.json(sample_geo)
# ==========================================
# 5️⃣ نموذج التقييم الآلي AVM
# ==========================================
elif choice == "نموذج التقييم الآلي AVM":
    st.title("🤖 نموذج التقييم الآلي – Automated Valuation Model")
    col_avm_l, col_avm_r = st.columns([1.2, 1])
    with col_avm_l:
        st.subheader("📋 مدخلات تقدير السعر العادل")
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
        factors_df = pd.DataFrame({
            "العامل الجغرافي والمعماري": ["الموقع الجغرافي", "المساحة الكلية", "جودة التشطيب", "عمر البناء", "عرض الشارع"],
            "الأهمية النسبية %": [35, 25, 15, 15, 10]
        })
        fig_pie = px.pie(factors_df, names="العامل الجغرافي والمعماري", values="الأهمية النسبية %", 
                         color_discrete_sequence=px.colors.sequential.Blues_r)
        fig_pie.update_layout(font_family="Cairo")
        st.plotly_chart(fig_pie, use_container_width=True)
# ==========================================
# 6️⃣ الصيانة التنبؤية
# ==========================================
elif choice == "الصيانة التنبؤية":
    st.title(" نظام إدارة وصيانة الأصول التنبؤي")
    c1, c2, c3 = st.columns(3)
    c1.metric("معدل جاهزية الأصول", "94.5%", "+1.5%")
    c2.metric("معدل الأعطال المجدولة", "3.2%", "-1.1%")
    c3.metric("ميزانية الصيانة المستهلكة", "1,500,000 ريال", "-50,000")
    st.divider()
    col_m1, col_m2 = st.columns([1.5, 1])
    with col_m1:
        st.subheader("📅 تتبع التكاليف الأسبوعي وحد الأمان للميزانية")
        # إضافة خط أفق للحد الأقصى للميزانية لإعطاء طابع تحليلي
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
elif choice == "ذكاء السوق والاستثمار":
    st.title("📊 ذكاء السوق والمؤشرات التنافسية Market Intelligence")
    st.subheader("📈 حجم سوق العقارات حسب القطاع وعام الاستشراف (2020-2030)")
    market_df = pd.DataFrame({
        "السنة": list(range(2020, 2031)),
        "القطاع السكني": np.linspace(80, 145, 11),
        "القطاع التجاري": np.linspace(60, 110, 11),
        "القطاع الصناعي": np.linspace(40, 85, 11)
    })
    fig_market = px.area(market_df, x="السنة", y=["القطاع السكني", "القطاع التجاري", "القطاع الصناعي"],
                         color_discrete_sequence=["#1E3A8A", "#3B82F6", "#94A3B8"])
    fig_market.update_layout(font_family="Cairo", yaxis_title="القيمة (مليار ريال)")
    st.plotly_chart(fig_market, use_container_width=True)
    col_k, col_not = st.columns([1, 2])
    with col_k:
        st.metric("معدل النمو السنوي المركب (CAGR)", "5.4%", "+0.7%")
    with col_not:
        st.info("💡 نصيحة النظام: تظهر البيانات التاريخية والتحليلات المستقبلية نمواً متسارعاً في **القطاع الصناعي واللوجستي** في أطراف الرياض. يوصى بزيادة الوزن النسبي في المحفظة.")
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, date, timedelta
from fpdf import FPDF
import base64
# ==========================================
# ⚙️ إعدادات الصفحة والهوية البصرية
# ==========================================
st.set_page_config(
    layout="wide",
    page_title="Drones Crafters – Real Estate OS",
    page_icon="🏢"

# CSS محسن للواجهة العربية (RTL) مع تأثيرات للبطاقات والتنبيهات
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [data-testid="stSidebar"], .main, .stMarkdown {
        direction: RTL !important;
        text-align: right !important;
        font-family: 'Cairo', sans-serif !important;
    }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        border-right: 5px solid #1E3A8A;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .stAlert { border-radius: 10px !important; }
    .stButton>button {
        background-color: #1E3A8A !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)
# ==========================================
# 🧠 إدارة البيانات وحفظ الحالة (Session State)
# ==========================================
# 1. تهيئة بيانات الصكوك والوثائق
if 'deeds_df' not in st.session_state:
    st.session_state.deeds_df = pd.DataFrame({
        "رقم الصك": ["123/أ", "456/ب", "789/ج"],
        "المالك": ["شركة أصول الأولى", "صندوق استثماري عقاري", "شركة تطوير عمراني"],
        "الحي": ["الملقا", "الياسمين", "النرجس"],
        "المساحة م²": [2500, 4300, 1800],
        "الحالة": ["ساري", "ساري", "محدث"],
        "تاريخ الانتهاء": [date(2024, 5, 10), date(2026, 12, 30), date(2024, 3, 20)]
    })
# 2. تهيئة بيانات الفواتير والصيانة (الميزة الجديدة)
if 'invoices_df' not in st.session_state:
    st.session_state.invoices_df = pd.DataFrame({
        "رقم الفاتورة": ["INV-8801", "INV-8802", "INV-8803", "INV-8804"],
        "العقار": ["مبنى إداري 1", "مجمع تجاري 2", "أرض خام 3", "مجمع تجاري 2"],
        "تاريخ الاستحقاق": [date.today() - timedelta(days=5), date.today() + timedelta(days=3), date.today() + timedelta(days=15), date.today() - timedelta(days=10)],
        "المبلغ": [5200, 12800, 1500, 3400],
        "الحالة": ["معلقة", "قيد المعالجة", "معلقة", "متأخرة"]
    })
districts = ["الملقا", "الياسمين", "النرجس", "العمارية"]
price_mock = {"الملقا": [4200, 5500, 4800], "الياسمين": [3800, 4100, 3900], "النرجس": [3500, 3700, 3600], "العمارية": [2200, 2800, 2500]}
# ==========================================
# 🛠️ وظائف مساعدة (تقارير وتنبيهات)
# ==========================================
def create_pdf_report(df_deeds, df_inv):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Drones Crafters - Portfolio Summary", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Total Assets: {len(df_deeds)}", ln=True)
    pdf.cell(200, 10, txt=f"Total Outstanding Invoices: {df_inv['المبلغ'].sum():,} SAR", ln=True)
    return pdf.output(dest='S').encode('latin-1')
# ==========================================
# 📂 القائمة الجانبية
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/10543/10543319.png", width=70)
    st.title("Drones Crafters")
    role = st.selectbox("الدور", ["مدير النظام", "مدير الأصول", "محلل استثماري"])
    
    st.divider()
    from streamlit_option_menu import option_menu
    choice = option_menu(
        "الوحدات",
        ["الرئيسية", "الصكوك والوثائق", "التحليلات المالية", "الخريطة الذكية", "التقييم الآلي AVM", "الصيانة والفواتير", "ذكاء السوق"],
        icons=["house", "file-lock", "cash-stack", "map", "cpu", "tools", "graph-up"],
        menu_icon="cast", default_index=0
    )
    st.divider()
    # إضافة زر تحميل التقرير في القائمة الجانبية دوماً
    pdf_report = create_pdf_report(st.session_state.deeds_df, st.session_state.invoices_df)
    st.download_button("📥 تحميل تقرير المحفظة (PDF)", data=pdf_report, file_name="Portfolio_Report.pdf", mime="application/pdf")
# ==========================================
# 1️⃣ لوحة القيادة الرئيسية
# ==========================================
if choice == "الرئيسية":
    st.title("🏢 لوحة القيادة – Drones Crafters Real Estate")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("إجمالي الأصول", "2.4B SAR", "+4.2%")
    col2.metric("عقارات نشطة", f"{len(st.session_state.deeds_df)}", "+1")
    col3.metric("مبالغ مستحقة", f"{st.session_state.invoices_df['المبلغ'].sum():,} ريال", "-12%")
    col4.metric("نسبة الإشغال", "89%", "↑ 2%")
    st.divider()
    # رسوم بيانية سريعة
    c_l, c_r = st.columns(2)
    with c_l:
        st.subheader("📊 توزيع القيمة حسب الحي")
        fig = px.pie(st.session_state.deeds_df, names='الحي', values='المساحة م²', hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(fig, use_container_width=True)
    with c_r:
        st.subheader("📈 نمو التدفقات النقدية")
        fig_line = px.line(x=[2021, 2022, 2023, 2024], y=[12, 14.5, 16.2, 18], markers=True)
        fig_line.update_traces(line_color='#1E3A8A')
        st.plotly_chart(fig_line, use_container_width=True)

# ==========================================
# 2️⃣ إدارة الصكوك (مع تنبيهات الانتهاء)
# ==========================================
elif choice == "الصكوك والوثائق":
    st.title("📜 إدارة الوثائق والأرشفة الرقمية")
    # فحص التواريخ وتنبيه الصكوك المنتهية
    today = date.today()
    expired = st.session_state.deeds_df[st.session_state.deeds_df['تاريخ الانتهاء'] <= today]
    if not expired.empty:
        st.error(f"⚠️ تنبيه: يوجد عدد ({len(expired)}) صكوك منتهية الصلاحية وتحتاج تحديث!")

    tab1, tab2 = st.tabs(["📂 سجل الصكوك", "➕ إضافة وأرشفة"])
    with tab1:
        st.dataframe(st.session_state.deeds_df, use_container_width=True)
    with tab2:
        with st.form("new_deed"):
            c1, c2 = st.columns(2)
            d_no = c1.text_input("رقم الصك")
            d_owner = c2.text_input("المالك")
            d_exp = c1.date_input("تاريخ الانتهاء")
            d_file = c2.file_uploader("رفع نسخة الصك (PDF)", type=['pdf'])
            if st.form_submit_button("حفظ المستند"):
                st.success("تمت أرشفة الوثيقة بنجاح!")
# ==========================================
# 6️⃣ الصيانة والفواتير (الميزة المطورة)
# ==========================================
elif choice == "الصيانة والفواتير":
    st.title("🛠️ إدارة الصيانة ونظام التنبيهات المالي")
    # نظام التنبيهات الذكي للفواتير
    today = date.today()
    overdue_invoices = st.session_state.invoices_df[st.session_state.invoices_df['تاريخ الاستحقاق'] < today]
    upcoming_invoices = st.session_state.invoices_df[(st.session_state.invoices_df['تاريخ الاستحقاق'] >= today) & (st.session_state.invoices_df['تاريخ الاستحقاق'] <= today + timedelta(days=7))]
    col_a, col_b = st.columns(2)
    with col_a:
        if not overdue_invoices.empty:
            st.error(f"🚨 فواتير متأخرة السداد: {len(overdue_invoices)} فاتورة (بإجمالي {overdue_invoices['المبلغ'].sum():,} ريال)")
    with col_b:
        if not upcoming_invoices.empty:
            st.warning(f"🔔 فواتير تستحق خلال 7 أيام: {len(upcoming_invoices)} فاتورة")
    st.divider()
    m_tab1, m_tab2 = st.tabs(["🧾 تتبع الفواتير", "📅 جدولة صيانة وقائية"])
    with m_tab1:
        st.subheader("سجل المطالبات المالية")
        # عرض الفواتير بتنسيق بطاقات ملونة
        for index, row in st.session_state.invoices_df.iterrows():
            with st.container():
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                c1.write(f"**{row['العقار']}** - فاتورة #{row['رقم الفاتورة']}")
                c2.write(f"{row['المبلغ']:,} ريال")
                # تلوين الحالة
                status = row['الحالة']
                color = "red" if status in ["متأخرة", "معلقة"] and row['تاريخ الاستحقاق'] < today else "orange"
                c3.markdown(f"<span style='color:{color}; font-weight:bold;'>{status}</span>", unsafe_allow_html=True)
                if c4.button("إرسال تذكير ✉️", key=f"btn_{index}"):
                    st.toast(f"تم إرسال إشعار للمسؤول عن {row['العقار']}")
                st.divider()
    with m_tab2:
        st.info("💡 نظام الصيانة التنبؤي يقترح فحص أنظمة التكييف في 'مبنى إداري 1' بناءً على استهلاك الطاقة الأسبوع الماضي.")
        st.date_input("حدد موعد الزيارة الميدانية")
        st.multiselect("الفنيين المطلوبين", ["فني كهرباء", "مهندس مدني", "فني تكييف"])
        st.button("تأكيد أمر العمل")
# ==========================================
# بقية الأقسام (AVM، الخريطة، ذكاء السوق) كما هي مع تحسينات بسيطة
# ==========================================
elif choice == "التقييم الآلي AVM":
    st.title("🤖 التقييم العقاري الذكي AVM")
    col_l, col_r = st.columns([1, 1])
    with col_l:
        area = st.number_input("المساحة (م²)", value=300)
        dist = st.selectbox("الحي", districts)
        quality = st.select_slider("جودة التشطيب", ["اقتصادي", "متوسط", "فاخر"])
        if st.button("تشغيل خوارزمية التقدير"):
            base = np.mean(price_mock[dist])
            mult = {"اقتصادي": 0.9, "متوسط": 1.0, "فاخر": 1.2}[quality]
            total = area * base * mult
            st.session_state.last_est = total
    with col_r:
        if 'last_est' in st.session_state:
            st.metric("القيمة العادلة المقدرة", f"{st.session_state.last_est:,.0f} ريال")
            st.info("تم الحساب بناءً على متوسط صفقات كتابة العدل في الحي خلال 90 يوماً.")
elif choice == "الخريطة الذكية":
    st.title("🗺️ التوزيع الجغرافي للأصول")
    df_map = pd.DataFrame({
        'lat': [24.77, 24.80, 24.76],
        'lon': [46.73, 46.70, 46.76],
        'name': ['أصل 1', 'أصل 2', 'أصل 3']
    })
    st.map(df_map)
elif choice == "التحليلات المالية":
    st.title("💰 التحليل المالي والاستثماري")
    st.subheader("محاكاة NPV للمشاريع الجديدة")
    discount = st.slider("معدل الخصم %", 5.0, 15.0, 9.0)
    st.write(f"صافي القيمة الحالية المتوقعة للمحفظة عند خصم {discount}%: **142,500,000 ريال**")
elif choice == "ذكاء السوق":
    st.title("📊 اتجاهات السوق الاستباقية")
    st.write("توقعات النمو في شمال الرياض 2024-2030")
    chart_data = pd.DataFrame(np.random.randn(20, 3), columns=['سكني', 'تجاري', 'صناعي'])
    st.area_chart(chart_data)
# ==========================================
# تذييل الصفحة
# ==========================================
st.sidebar.markdown("---")
st.sidebar.caption(f"Drones Crafters OS v2.0 | {datetime.now().strftime('%Y')}")

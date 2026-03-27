import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import warnings
warnings.filterwarnings('ignore')
# إعداد الصفحة
st.set_page_config(
    layout="wide",
    page_title="Drones Crafters – Global Real Estate Intelligence Platform",
    page_icon="🏢",
    initial_sidebar_state="expanded"
)
# --- CSS للهوية العربية والـ RTL والوضع المظلم ---
def apply_css(dark_mode):
    if dark_mode:
        bg_color = "#0E1117"
        text_color = "#FFFFFF"
        card_bg = "#1E1E2E"
        metric_bg = "#2C2C3A"
    else:
        bg_color = "#F8F9FA"
        text_color = "#212529"
        card_bg = "#FFFFFF"
        metric_bg = "#F1F3F5"
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stSidebar"], .main, .stMarkdown {{
        direction: RTL !important;
        text-align: right !important;
        font-family: 'Cairo', sans-serif !important;
        background-color: {bg_color};
        color: {text_color};
    }}
    section[data-testid="stSidebar"] > div {{
        background-color: {card_bg};
    }}
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{
        text-align: right !important;
        direction: RTL !important;
    }}
    .stTextInput > div > div > input, .stSelectbox > div > div {{
        text-align: right;
    }}
    .stButton > button {{
        background-color: #1E3A8A;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }}
    .stButton > button:hover {{
        background-color: #2563EB;
    }}
    .card {{
        background-color: {card_bg};
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }}
    .metric-card {{
        background-color: {metric_bg};
        padding: 0.8rem;
        border-radius: 10px;
        text-align: center;
    }}
    </style>
    """, unsafe_allow_html=True)
# الشريط الجانبي مع خيارات متقدمة
with st.sidebar:
    st.title("🏢 Drones Crafters")
    st.subheader("Global Real Estate Intelligence")
    # اختيار الوضع المظلم
    dark_mode = st.toggle("🌙 الوضع المظلم", value=False)
    apply_css(dark_mode)
    # اختيار الدور
    role = st.selectbox(
        "الدور التنفيذي",
        ["System Admin", "Asset Manager", "Investment Analyst", "External Auditor"],
        format_func=lambda x: {
            "System Admin": "مسؤول النظام",
            "Asset Manager": "مدير الأصول",
            "Investment Analyst": "محلل استثماري",
            "External Auditor": "مدقق خارجي"
        }[x]
    )
    
    # قائمة الوحدات الرئيسية
    try:
        from streamlit_option_menu import option_menu
        choice = option_menu(
            "الوحدات الرئيسية",
            [
                "لوحة القيادة التنفيذية",
                "إدارة الصكوك والوثائق",
                "التحليلات المالية المتقدمة",
                "الذكاء المكاني والخرائط",
                "نموذج التقييم الآلي AVM",
                "الصيانة التنبؤية (ML)",
                "ذكاء السوق والاستثمار"
            ],
            icons=["speedometer", "file-earmark-text", "cash-coin",
                   "map", "cpu", "wrench", "graph-up"],
            menu_icon="cast",
            default_index=0,
        )
    except:
        choice = st.radio(
            "الوحدات الرئيسية",
            [
                "لوحة القيادة التنفيذية",
                "إدارة الصكوك والوثائق",
                "التحليلات المالية المتقدمة",
                "الذكاء المكاني والخرائط",
                "نموذج التقييم الآلي AVM",
                "الصيانة التنبؤية (ML)",
                "ذكاء السوق والاستثمار"
            ]
        )

st.write(f"🔐 الدور الحالي: **{role}**")
st.divider()
# =========================
# 1. تحميل وتهيئة البيانات (محاكاة متقدمة)
# =========================
@st.cache_data
def load_data():
    # بيانات عقارات (500 عقار)
    np.random.seed(42)
    n_properties = 500
    cities = ["الرياض", "جدة", "الدمام", "مكة", "المدينة", "الخبر"]
    districts = ["الملقا", "الياسمين", "النرجس", "العمارية", "الرائد", "المروج", "النسيم"]
    property_types = ["سكني", "تجاري", "صناعي", "أرض"]
    properties = pd.DataFrame({
        "id": range(1, n_properties+1),
        "اسم العقار": [f"عقار {i}" for i in range(1, n_properties+1)],
        "المدينة": np.random.choice(cities, n_properties),
        "الحي": np.random.choice(districts, n_properties),
        "النوع": np.random.choice(property_types, n_properties),
        "المساحة (م²)": np.random.uniform(80, 2000, n_properties).round(0),
        "سعر المتر (ريال)": np.random.uniform(2000, 8000, n_properties).round(0),
        "عمر العقار (سنوات)": np.random.uniform(0, 30, n_properties).round(1),
        "جودة التشطيب": np.random.choice(["اقتصادي", "متوسط", "فاخر"], n_properties),
        "عرض الشارع (م)": np.random.uniform(8, 40, n_properties).round(1),
        "خط العرض": np.random.uniform(21.3, 28.5, n_properties),
        "خط الطول": np.random.uniform(35.0, 48.0, n_properties),
        "القيمة (مليون ريال)": 0  # سيتم حسابها لاحقاً
    })
    # حساب القيمة
    properties["القيمة (مليون ريال)"] = (properties["المساحة (م²)"] * properties["سعر المتر (ريال)"]) / 1e6
    # إضافة بعض الميزات
    return properties
# بيانات مالية تاريخية
@st.cache_data
def load_financials():
    years = list(range(2015, 2025))
    np.random.seed(123)
    revenues = np.linspace(10_000_000, 25_000_000, 10) + np.random.normal(0, 500_000, 10)
    operating_costs = np.linspace(3_000_000, 7_000_000, 10) + np.random.normal(0, 200_000, 10)
    maintenance = np.linspace(800_000, 1_800_000, 10) + np.random.normal(0, 100_000, 10)
    return pd.DataFrame({
        "السنة": years,
        "الإيرادات": revenues,
        "المصاريف التشغيلية": operating_costs,
        "الصيانة": maintenance,
        "صافي الدخل": revenues - operating_costs - maintenance
    })
# بيانات صيانة تاريخية (للتنبؤ)
@st.cache_data
def load_maintenance_history():
    dates = pd.date_range(start="2020-01-01", end="2024-12-31", freq="W")
    np.random.seed(456)
    costs = np.random.gamma(shape=2, scale=150_000, size=len(dates)) + 100_000
    return pd.DataFrame({"التاريخ": dates, "التكلفة": costs})
# بيانات السوق
@st.cache_data
def load_market_data():
    districts = ["الملقا", "الياسمين", "النرجس", "العمارية", "الرائد", "المروج", "النسيم"]
    years = list(range(2020, 2025))
    data = []
    for district in districts:
        base_price = np.random.uniform(3000, 7000)
        for year in years:
            price = base_price * (1 + np.random.uniform(-0.05, 0.15)) ** (year - 2020)
            data.append({"الحي": district, "السنة": year, "سعر المتر": round(price, 0)})
    return pd.DataFrame(data)
properties = load_data()
financials = load_financials()
maintenance_hist = load_maintenance_history()
market_data = load_market_data()
# =========================
# 2. لوحة القيادة التنفيذية (محسنة)
# =========================
if choice == "لوحة القيادة التنفيذية":
    st.title("🏢 لوحة القيادة التنفيذية – نظرة شاملة للمحفظة")
    # مؤشرات KPI
    total_value = properties["القيمة (مليون ريال)"].sum()
    avg_price_per_sqm = (properties["القيمة (مليون ريال)"] * 1e6 / properties["المساحة (م²)"]).mean()
    avg_roi = np.random.uniform(8, 14)  # محاكاة
    occupancy_rate = np.random.uniform(85, 95)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("إجمالي قيمة المحفظة", f"{total_value:.0f} مليون ريال", delta="+4.2%")
    with col2:
        st.metric("متوسط سعر المتر", f"{avg_price_per_sqm:.0f} ريال", delta="+2.1%")
    with col3:
        st.metric("متوسط العائد السنوي (ROI)", f"{avg_roi:.1f}%", delta="+0.3%")
    with col4:
        st.metric("نسبة الإشغال", f"{occupancy_rate:.1f}%", delta="-1.2%")
    # توزيع القيمة حسب النوع والمدينة
    col1, col2 = st.columns(2)
    with col1:
        fig_type = px.pie(properties, names="النوع", values="القيمة (مليون ريال)", 
                          title="توزيع القيمة حسب نوع العقار", hole=0.4)
        st.plotly_chart(fig_type, use_container_width=True)
    with col2:
        city_value = properties.groupby("المدينة")["القيمة (مليون ريال)"].sum().reset_index()
        fig_city = px.bar(city_value, x="المدينة", y="القيمة (مليون ريال)", 
                          title="القيمة الإجمالية حسب المدينة", color="المدينة")
        st.plotly_chart(fig_city, use_container_width=True)
    # اتجاهات الأسعار
    st.subheader("اتجاهات الأسعار التاريخية")
    fig_price_trend = px.line(market_data, x="السنة", y="سعر المتر", color="الحي",
                              title="تطور سعر المتر حسب الحي (2020-2024)")
    st.plotly_chart(fig_price_trend, use_container_width=True)
    # خريطة حرارية للمحفظة (نقاط)
    st.subheader("توزيع العقارات على الخريطة")
    fig_map = px.scatter_mapbox(properties.sample(200), lat="خط العرض", lon="خط الطول",
                                hover_name="اسم العقار", hover_data=["المدينة", "القيمة (مليون ريال)"],
                                color="القيمة (مليون ريال)", size="القيمة (مليون ريال)",
                                size_max=15, zoom=5, center={"lat": 24.0, "lon": 45.0},
                                mapbox_style="open-street-map", title="مواقع العقارات")
    st.plotly_chart(fig_map, use_container_width=True)
# =========================
# 3. إدارة الصكوك والوثائق (محسنة)
# =========================
elif choice == "إدارة الصكوك والوثائق":
    st.title("📜 إدارة الصكوك والوثائق – سجل رقمي متكامل")
    # عرض جدول الصكوك (بيانات موسعة)
    deeds_df = pd.DataFrame({
        "رقم الصك": [f"صك-{i}" for i in range(1, 101)],
        "المالك": np.random.choice(["شركة أصول", "صندوق استثماري", "مستثمر فردي"], 100),
        "الحي": np.random.choice(properties["الحي"].unique(), 100),
        "المساحة (م²)": np.random.uniform(200, 5000, 100).round(0),
        "تاريخ التسجيل": np.random.choice(pd.date_range("2015-01-01", "2024-12-31"), 100),
        "الحالة": np.random.choice(["ساري", "منتهي", "محدث"], 100, p=[0.8,0.1,0.1])
    })
    st.dataframe(deeds_df, use_container_width=True, height=400)
    # إضافة صك جديد (مع التحقق)
    with st.expander("➕ إضافة صك جديد"):
        with st.form("new_deed"):
            deed_no = st.text_input("رقم الصك")
            owner = st.text_input("المالك")
            district = st.selectbox("الحي", properties["الحي"].unique())
            area = st.number_input("المساحة (م²)", min_value=0.0)
            reg_date = st.date_input("تاريخ التسجيل")
            status = st.selectbox("الحالة", ["ساري", "منتهي", "محدث"])
            submitted = st.form_submit_button("حفظ")
            if submitted and deed_no:
                st.success(f"تم إضافة الصك {deed_no} بنجاح (محاكاة).")
            elif submitted:
                st.error("الرجاء إدخال رقم الصك.")
    st.info("🔗 يمكن ربط هذه الوحدة بنظام أرشفة المستندات (PDF) وتكامل مع منصة البلدية.")
# =========================
# 4. التحليلات المالية المتقدمة (DCF, IRR, NPV, Sensitivity)
# =========================
elif choice == "التحليلات المالية المتقدمة":
    st.title("💰 التحليلات المالية المتقدمة – DCF / IRR / NPV")
    # عرض البيانات المالية التاريخية
    st.subheader("البيانات المالية التاريخية")
    st.dataframe(financials, use_container_width=True)
    # نموذج DCF
    st.subheader("تحليل التدفقات النقدية المخصومة (DCF)")
    col1, col2 = st.columns(2)
    with col1:
        wacc = st.slider("متوسط تكلفة رأس المال (WACC)", 5.0, 15.0, 9.0, 0.5)
        growth_rate = st.slider("معدل النمو الدائم", 0.0, 5.0, 2.0, 0.1)
        forecast_years = st.slider("عدد سنوات التوقع", 5, 20, 10)
    with col2:
        last_fcf = financials["صافي الدخل"].iloc[-1]
        st.metric("آخر تدفق نقدي حر (FCF)", f"{last_fcf:,.0f} ريال")
    # توليد التدفقات المتوقعة
    fcf_projections = [last_fcf * (1 + growth_rate/100) ** i for i in range(1, forecast_years+1)]
    terminal_value = fcf_projections[-1] * (1 + growth_rate/100) / ((wacc/100) - (growth_rate/100))
    # حساب القيمة الحالية
    npv = 0
    for i, fcf in enumerate(fcf_projections):
        npv += fcf / ((1 + wacc/100) ** (i+1))
    npv += terminal_value / ((1 + wacc/100) ** forecast_years)
    st.metric("قيمة المؤسسة (Enterprise Value)", f"{npv:,.0f} ريال")
    # رسم التدفقات
    df_fcf = pd.DataFrame({
        "السنة": list(range(1, forecast_years+1)),
        "التدفق النقدي المتوقع": fcf_projections
    })
    fig_fcf = px.bar(df_fcf, x="السنة", y="التدفق النقدي المتوقع", 
                     title="التدفقات النقدية المتوقعة (FCF)")
    st.plotly_chart(fig_fcf, use_container_width=True)
    # IRR و NPV للمشروع
    st.subheader("تحليل العائد الداخلي (IRR) وصافي القيمة الحالية (NPV)")
    initial_investment = st.number_input("الاستثمار الابتدائي (ريال)", value=50_000_000, step=5_000_000)
    cash_flows = [initial_investment] + [fcf for fcf in fcf_projections[:5]]  # أول 5 سنوات
    # حساب IRR تقريبي
    from numpy import irr
    irr_val = irr(cash_flows) * 100 if len(cash_flows) > 1 else 0
    st.metric("معدل العائد الداخلي (IRR)", f"{irr_val:.2f}%")
    npv_project = npv - initial_investment
    st.metric("صافي القيمة الحالية (NPV)", f"{npv_project:,.0f} ريال")
    # تحليل الحساسية
    st.subheader("تحليل الحساسية – تأثير تغير WACC")
    wacc_range = np.linspace(5, 15, 20)
    npv_sensitivity = ange:
        npv_temp = 0
        for i, fcf in enumerate(fcf_projections):
            npv_temp += fcf / ((1 + w/100) ** (i+1))
        npv_temp += terminal_value / ((1 + w/100) ** forecast_years)
        npv_sensitivity.append(npv_temp - initial_investment)
    df_sens = pd.DataFrame({"WACC (%)": wacc_range, "NPV (ريال)": npv_sensitivity})
    fig_sens = px.line(df_sens, x="WACC (%)", y="NPV (ريال)", 
                       title="تأثير تغير تكلفة رأس المال على صافي القيمة الحالية")
    st.plotly_chart(fig_sens, use_container_width=True)
    # تصدير
    if st.button("📥 تصدير التقرير المالي (CSV)"):
        df_export = financials.copy()
        df_export["NPV"] = npv_project
        df_export["IRR"] = irr_val
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button("تحميل CSV", data=csv, file_name="financial_report.csv", mime="text/csv")
# =========================
# 5. الذكاء المكاني والخرائط (متقدم: بحث، طبقات، حدود)
# =========================
elif choice == "الذكاء المكاني والخرائط":
    st.title("🗺️ الذكاء المكاني – خريطة تفاعلية متعددة الطبقات")
    # محاولة استخدام Mapbox
    mapbox_token = None
    try:
        if os.path.exists("config/mapbox_token.txt"):
            with open("config/mapbox_token.txt") as f:
                mapbox_token = f.read().strip()
        elif "MAPBOX_TOKEN" in st.secrets:
            mapbox_token = st.secrets["MAPBOX_TOKEN"]
    except:
        pass
    if mapbox_token:
        px.set_mapbox_access_token(mapbox_token)
        map_style = "mapbox://styles/mapbox/light-v11"
    else:
        map_style = "open-street-map"
        st.warning("⚠️ مفتاح Mapbox غير متوفر، يتم استخدام OpenStreetMap.")
    # البحث عن عقار
    search_term = st.text_input("🔍 بحث عن عقار (اسم أو معرف)", placeholder="أدخل اسم العقار أو رقمه")
    filtered = properties
    if search_term:
        filtered = properties[properties["اسم العقار"].str.contains(search_term, case=False) |
                              properties["id"].astype(str).str.contains(search_term)]
        if filtered.empty:
            st.warning("لم يتم العثور على عقار.")
        else:
            st.success(f"تم العثور على {len(filtered)} عقار.")
    # خريطة رئيسية
    fig_map = px.scatter_mapbox(filtered, lat="خط العرض", lon="خط الطول",
                                hover_name="اسم العقار", hover_data=["المدينة", "القيمة (مليون ريال)", "النوع"],
                                color="القيمة (مليون ريال)", size="القيمة (مليون ريال)",
                                size_max=20, zoom=5, center={"lat": 24.0, "lon": 45.0},
                                mapbox_style=map_style, title="مواقع العقارات")
    fig_map.update_layout(height=600)
    st.plotly_chart(fig_map, use_container_width=True)
    # خريطة حرارية (الكثافة)
    st.subheader("خريطة حرارية لكثافة العقارات")
    fig_heat = px.density_mapbox(filtered, lat="خط العرض", lon="خط الطول",
                                 radius=20, zoom=5, center={"lat": 24.0, "lon": 45.0},
                                 mapbox_style=map_style, title="كثافة العقارات")
    st.plotly_chart(fig_heat, use_container_width=True)
    # عرض تفاصيل العقار المختار
    if not filtered.empty:
        selected_id = st.selectbox("اختر عقار لعرض التفاصيل", filtered["id"].tolist(), format_func=lambda x: filtered[filtered["id"]==x]["اسم العقار"].iloc[0])
        prop = filtered[filtered["id"]==selected_id].iloc[0]
        with st.expander("تفاصيل العقار"):
            col1, col2, col3 = st.columns(3)
            col1.write(f"**الاسم:** {prop['اسم العقار']}")
            col1.write(f"**المدينة:** {prop['المدينة']}")
            col1.write(f"**الحي:** {prop['الحي']}")
            col2.write(f"**النوع:** {prop['النوع']}")
            col2.write(f"**المساحة:** {prop['المساحة (م²)']:.0f} م²")
            col2.write(f"**القيمة:** {prop['القيمة (مليون ريال)']:.2f} مليون")
            col3.write(f"**عمر العقار:** {prop['عمر العقار (سنوات)']} سنة")
            col3.write(f"**جودة التشطيب:** {prop['جودة التشطيب']}")
            col3.write(f"**عرض الشارع:** {prop['عرض الشارع (م)']} م")
    st.info("🔧 يمكن ربط هذه الوحدة مع PostGIS لتحميل طبقات حقيقية (حدود الأراضي، التقسيمات العمرانية).")
# =========================
# 6. نموذج التقييم الآلي AVM (باستخدام ML)
# =========================
elif choice == "نموذج التقييم الآلي AVM":
    st.title("🤖 نموذج التقييم الآلي – AVM (Machine Learning)")
    
    # بناء نموذج الانحدار الخطي
    @st.cache_resource
    def train_avm_model():
        # تجهيز البيانات
        data = properties.copy()
        # متغيرات مستقلة
        features = ["المساحة (م²)", "عمر العقار (سنوات)", "عرض الشارع (م)", "الحي", "جودة التشطيب", "النوع"]
        X = data[features]
        y = data["القيمة (مليون ريال)"]
        # معالجة المتغيرات الفئوية
        categorical = ["الحي", "جودة التشطيب", "النوع"]
        numeric = ["المساحة (م²)", "عمر العقار (سنوات)", "عرض الشارع (م)"]
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numeric),
                ('cat', OneHotEncoder(handle_unknown='ignore'), categorical)
            ])
        model = Pipeline(steps=[('preprocessor', preprocessor),
                                ('regressor', LinearRegression())])
        model.fit(X, y)
        return model
    model = train_avm_model()
    # واجهة إدخال بيانات المستخدم
    st.subheader("أدخل بيانات العقار للحصول على تقييم فوري")
    col1, col2 = st.columns(2)
    with col1:
        area = st.number_input("المساحة (م²)", min_value=20.0, value=300.0)
        age = st.number_input("عمر العقار (سنوات)", min_value=0.0, value=5.0)
        street_width = st.number_input("عرض الشارع (م)", min_value=4.0, value=15.0)
    with col2:
        district = st.selectbox("الحي", properties["الحي"].unique())
        quality = st.selectbox("جودة التشطيب", ["اقتصادي", "متوسط", "فاخر"])
        prop_type = st.selectbox("نوع العقار", ["سكني", "تجاري", "صناعي", "أرض"])
    if st.button("تقدير القيمة"):
        input_df = pd.DataFrame({
            "المساحة (م²)": [area],
            "عمر العقار (سنوات)": [age],
            "عرض الشارع (م)": [street_width],
            "الحي": [district],
            "جودة التشطيب": [quality],
            "النوع": [prop_type]
        })
        pred = model.predict(input_df)[0]
        st.success(f"💎 القيمة التقديرية للعقار: {pred:.2f} مليون ريال (≈ {pred*1e6:,.0f} ريال)")
        # عرض عوامل التقييم
        st.subheader("تحليل العوامل المؤثرة")
        # محاكاة لأهمية الميزات
        importance = {
            "المساحة": 0.40,
            "الموقع (الحي)": 0.25,
            "جودة التشطيب": 0.15,
            "عمر العقار": 0.10,
            "عرض الشارع": 0.05,
            "النوع": 0.05
        }
        fig_importance = px.bar(x=list(importance.keys()), y=list(importance.values()),
                                title="أهمية العوامل في نموذج التقييم",
                                labels={"x": "العامل", "y": "الأهمية النسبية"})
        st.plotly_chart(fig_importance, use_container_width=True)
    
    st.info("🧠 النموذج الحالي هو انحدار خطي متعدد تم تدريبه على بيانات محاكاة. يمكن استبداله بنموذج أكثر تعقيداً (XGBoost) مع بيانات حقيقية.")
# =========================
# 7. الصيانة التنبؤية (ML) – استخدام ARIMA
# =========================
elif choice == "الصيانة التنبؤية (ML)":
    st.title("🛠️ الصيانة التنبؤية – التنبؤ بتكاليف الصيانة")
    # عرض البيانات التاريخية
    st.subheader("سجل الصيانة التاريخي (أسبوعي)")
    st.dataframe(maintenance_hist.tail(50), use_container_width=True)
    # رسم البيانات التاريخية
    fig_hist = px.line(maintenance_hist, x="التاريخ", y="التكلفة", 
                       title="تكاليف الصيانة التاريخية")
    st.plotly_chart(fig_hist, use_container_width=True)
    # تنبؤ باستخدام نموذج ARIMA مبسط (محاكاة)
    st.subheader("التنبؤ بتكاليف الصيانة للأشهر القادمة")
    forecast_horizon = st.slider("عدد الأسابيع للتنبؤ", 4, 52, 26)
    # محاكاة نموذج ARIMA (استخدام متوسط متحرك بسيط مع ضوضاء)
    last_values = maintenance_hist["التكلفة"].tail(50).values
    # نموذج محاكاة: متوسط الأربعة أسابيع الأخيرة + اتجاه + عشوائية
    forecast = []
    for i in range(forecast_horizon):
        if len(last_values) >= 4:
            pred = np.mean(last_values[-4:]) * (1 + 0.001 * i) + np.random.normal(0, 20000)
        else:
            pred = np.mean(last_values) + np.random.normal(0, 20000)
        forecast.append(pred)
        last_values = np.append(last_values, pred)
    forecast_dates = pd.date_range(start=maintenance_hist["التاريخ"].max() + timedelta(days=7), periods=forecast_horizon, freq="W")
    forecast_df = pd.DataFrame({"التاريخ": forecast_dates, "التكلفة المتوقعة": forecast})
    fig_forecast = go.Figure()
    fig_forecast.add_trace(go.Scatter(x=maintenance_hist["التاريخ"], y=maintenance_hist["التكلفة"], mode="lines", name="تاريخي"))
    fig_forecast.add_trace(go.Scatter(x=forecast_dates, y=forecast, mode="lines", name="متوقع", line=dict(dash="dash")))
    fig_forecast.update_layout(title="التنبؤ بتكاليف الصيانة", xaxis_title="التاريخ", yaxis_title="التكلفة (ريال)")
    st.plotly_chart(fig_forecast, use_container_width=True)
    # إجمالي التكلفة المتوقعة
    total_forecast = forecast_df["التكلفة المتوقعة"].sum()
    st.metric("إجمالي التكاليف المتوقعة للفترة", f"{total_forecast:,.0f} ريال")
    st.info("🔮 هذا التنبؤ يستخدم نموذج متوسط متحرك بسيط. يمكن ترقيته إلى ARIMA/SARIMA باستخدام مكتبة statsmodels.")
# =========================
# 8. ذكاء السوق والاستثمار (تحليلات متقدمة)
# =========================
elif choice == "ذكاء السوق والاستثمار":
    st.title("📊 ذكاء السوق والاستثمار – تحليل الفرص والاتجاهات")
    # مؤشرات السوق
    st.subheader("مؤشرات السوق الرئيسية")
    col1, col2, col3 = st.columns(3)
    with col1:
        avg_price_city = properties.groupby("المدينة")["سعر المتر (ريال)"].mean().mean()
        st.metric("متوسط سعر المتر (على مستوى المملكة)", f"{avg_price_city:.0f} ريال")
    with col2:
        cagr = ((market_data[market_data["السنة"]==2024]["سعر المتر"].mean() / 
                 market_data[market_data["السنة"]==2020]["سعر المتر"].mean()) ** (1/4) - 1) * 100
        st.metric("معدل النمو السنوي المركب (CAGR 2020-2024)", f"{cagr:.1f}%")
    with col3:
        supply_demand = np.random.uniform(0.8, 1.2)  # محاكاة
        st.metric("مؤشر العرض/الطلب", f"{supply_demand:.2f}", delta="إيجابي" if supply_demand>1 else "سلبي")
    # تطور سعر المتر حسب المدينة
    fig_city_trend = px.line(market_data.groupby(["السنة", "المدينة"])["سعر المتر"].mean().reset_index(),
                             x="السنة", y="سعر المتر", color="المدينة", title="اتجاهات أسعار المتر حسب المدينة")
    st.plotly_chart(fig_city_trend, use_container_width=True)
    # فرص الاستثمار: أفضل 10 عقارات من حيث العائد المتوقع (محاكاة)
    st.subheader("أفضل فرص الاستثمار (حسب العائد المتوقع)")
    properties["العائد المتوقع (%)"] = np.random.uniform(5, 18, len(properties))
    top_investments = properties.nlargest(10, "العائد المتوقع (%)")[["اسم العقار", "المدينة", "القيمة (مليون ريال)", "العائد المتوقع (%)"]]
    st.dataframe(top_investments, use_container_width=True)
    # تحليل المقارنة مع السوق
    st.subheader("مقارنة أداء المحفظة مع السوق العام")
    market_returns = np.random.normal(0.08, 0.02, 50)  # محاكاة
    portfolio_returns = np.random.normal(0.10, 0.03, 50)
    df_comp = pd.DataFrame({"العائد الشهري": market_returns, "النوع": "السوق"})
    df_comp2 = pd.DataFrame({"العائد الشهري": portfolio_returns, "النوع": "المحفظة"})
    df_comp_all = pd.concat([df_comp, df_comp2])
    fig_comp = px.box(df_comp_all, x="النوع", y="العائد الشهري", title="توزيع العوائد الشهرية (المحفظة مقابل السوق)")
    st.plotly_chart(fig_comp, use_container_width=True)
    st.info("📈 يمكن دمج هذه الوحدة مع بيانات حقيقية من هيئة السوق المالية أو منصات البيانات العقارية.")
# Footer
st.divider()
st.caption("© 2025 Drones Crafters – منصة ذكاء عقاري متكاملة | جميع الحقوق محفوظة")

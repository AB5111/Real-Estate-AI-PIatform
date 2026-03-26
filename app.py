import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
# إعداد الصفحة
st.set_page_config(
    layout="wide",
    page_title="Drones Crafters – Real Estate Management Dashboard"
)
# --- CSS للهوية العربية والـ RTL ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stSidebar"], .main, .stMarkdown {
        direction: RTL !important;
        text-align: right !important;
        font-family: 'Cairo', sans-serif !important;
    }
    section[data-testid="stSidebar"] > div { text-align: right; }
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        text-align: right !important;
        direction: RTL !important;
    }
    </style>
""", unsafe_allow_html=True)
# =========================
# بيانات وهمية (Mock) كبنية أولية
# =========================
districts = ["الملقا", "الياسمين", "النرجس", "العمارية"]
price_mock = {
    "الملقا": [4200, 5500, 4800, 6000],
    "الياسمين": [3800, 4100, 3900, 4500],
    "النرجس": [3500, 3700, 3600, 4000],
    "العمارية": [2200, 2800, 2500, 3100]
}
# بيانات مالية وهمية
financial_df = pd.DataFrame({
    "السنة": [2021, 2022, 2023, 2024],
    "الإيرادات": [12_000_000, 14_500_000, 16_200_000, 18_000_000],
    "المصاريف التشغيلية": [4_000_000, 4_500_000, 5_000_000, 5_400_000],
    "صيانة": [1_200_000, 1_350_000, 1_500_000, 1_650_000]
})
# بيانات صيانة تنبؤية وهمية
maintenance_df = pd.DataFrame({
    "الأسبوع": [f"{w}/2024" for w in range(40, 53)],
    "تكلفة الصيانة": np.random.randint(200_000, 600_000, 13),
    "تكلفة الإدارة": np.random.randint(150_000, 400_000, 13)
})
# بيانات صكوك وهمية
deeds_df = pd.DataFrame({
    "رقم الصك": ["123/أ", "456/ب", "789/ج"],
    "المالك": ["شركة أصول الأولى", "صندوق استثماري عقاري", "شركة تطوير عمراني"],
    "الحي": ["الملقا", "الياسمين", "النرجس"],
    "المساحة م²": [2500, 4300, 1800],
    "الحالة": ["ساري", "ساري", "محدث"]
})
# =========================
# القائمة الجانبية – الأدوار والوحدات
# =========================
with st.sidebar:
    st.title("Drones Crafters")
    st.subheader("منصة إدارة الأصول العقارية")
    # اختيار الدور (حوكمة الوصول)
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
    # القائمة الرئيسية
    try:
        from streamlit_option_menu import option_menu
        choice = option_menu(
            "الوحدات الرئيسية",
            [
                "لوحة القيادة التنفيذية",
                "إدارة الصكوك والوثائق",
                "التحليلات المالية",
                "الذكاء المكاني والخرائط",
                "نموذج التقييم الآلي AVM",
                "الصيانة التنبؤية",
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
                "التحليلات المالية",
                "الذكاء المكاني والخرائط",
                "نموذج التقييم الآلي AVM",
                "الصيانة التنبؤية",
                "ذكاء السوق والاستثمار"
            ]
        )
st.write(f"🔐 الدور الحالي: **{role}**")
st.divider()
# =========================
# 1) لوحة القيادة التنفيذية – Executive Dashboards
# =========================
if choice == "لوحة القيادة التنفيذية":
    st.title("🏢 لوحة القيادة التنفيذية – Portfolio & Risk")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("إجمالي قيمة الأصول", "2.4 مليار ريال", "+4.2%")
    col2.metric("عدد العقارات", "1,280 أصل", "+35")
    col3.metric("متوسط العائد السنوي (IRR)", "11.8%", "+0.6%")
    col4.metric("نسبة الإشغال", "89%", "-3.1%")
    st.subheader("توزيع الأصول حسب نوع العقار")
    asset_type_df = pd.DataFrame({
        "نوع العقار": ["شقق", "مكاتب", "تجاري", "صناعي", "فلل"],
        "القيمة": [600, 450, 520, 300, 530]
    })
    fig_asset = px.bar(
        asset_type_df,
        x="نوع العقار",
        y="القيمة",
        title="توزيع القيمة حسب نوع العقار (مليون ريال)",
        color="نوع العقار",
        color_discrete_sequence=px.colors.sequential.Blues
    )
    st.plotly_chart(fig_asset, use_container_width=True)
    st.subheader("مؤشرات أداء المحفظة – ROI / IRR / NPV (محاكاة)")
    kpi_df = pd.DataFrame({
        "السنة": [2021, 2022, 2023, 2024],
        "ROI": [8.5, 9.2, 10.1, 10.8],
        "IRR": [10.2, 10.9, 11.3, 11.8],
        "NPV (مليون ريال)": [120, 145, 168, 190]
    })
    fig_kpi = px.line(
        kpi_df,
        x="السنة",
        y=["ROI", "IRR"],
        markers=True,
        title="تطور مؤشرات العائد ROI / IRR"
    )
    st.plotly_chart(fig_kpi, use_container_width=True)
# =========================
# 2) إدارة الصكوك والوثائق – Deed Management
# =========================
elif choice == "إدارة الصكوك والوثائق":
    st.title("📜 إدارة الصكوك والوثائق – Deed Management")
    st.write("أرشفة رقمية للصكوك مع ربطها بالحدود الجغرافية والسجل التاريخي للملكية.")
    st.subheader("سجل الصكوك")
    st.dataframe(deeds_df, use_container_width=True)
    st.subheader("إضافة / تحديث صك")
    with st.form("deed_form"):
        deed_no = st.text_input("رقم الصك")
        owner = st.text_input("اسم المالك")
        district = st.selectbox("الحي", districts)
        area = st.number_input("المساحة (م²)", min_value=0.0, step=50.0)
        status = st.selectbox("حالة الصك", ["ساري", "محدث", "موقوف"])
        submitted = st.form_submit_button("حفظ")
        if submitted:
            st.success("تم حفظ بيانات الصك (محاكاة – تحتاج ربط بقاعدة بيانات فعلية).")
# =========================
# 3) التحليلات المالية – Financial Analytics
# =========================
elif choice == "التحليلات المالية":
    st.title("💰 التحليلات المالية – IRR / NPV / Cash Flows")
    st.write("متابعة التدفقات النقدية، المصاريف التشغيلية، ومؤشرات الأداء المالي للمحفظة.")
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي الإيرادات السنوية", "18,000,000 ريال", "+1,800,000")
    c2.metric("إجمالي المصاريف التشغيلية", "5,400,000 ريال", "+400,000")
    c3.metric("صافي الربح", "12,600,000 ريال", "+1,400,000")
    st.subheader("الإيرادات والمصاريف عبر السنوات")
    fig_fin = px.bar(
        financial_df,
        x="السنة",
        y=["الإيرادات", "المصاريف التشغيلية", "صيانة"],
        barmode="group",
        title="تحليل الإيرادات والمصاريف"
    )
    st.plotly_chart(fig_fin, use_container_width=True)
    st.subheader("محاكاة NPV / IRR لمشروع تطوير عقاري")
    col_l, col_r = st.columns(2)
    with col_l:
        discount_rate = st.slider("معدل الخصم (Discount Rate)", 5.0, 15.0, 9.0, 0.5)
        years = st.slider("عدد السنوات", 3, 10, 5)
        initial_investment = st.number_input("الاستثمار الابتدائي (ريال)", value=10_000_000)
    with col_r:
        cash_flows = [initial_investment * 0.35 for _ in range(years)]
        npv = sum(cf / ((1 + discount_rate/100) ** (i+1)) for i, cf in enumerate(cash_flows)) - initial_investment
        irr_approx = (sum(cash_flows) - initial_investment) / initial_investment * 100
        st.metric("NPV (تقريبي)", f"{npv:,.0f} ريال")
        st.metric("IRR (تقريبي)", f"{irr_approx:.2f}%")
# =========================
# 4) الذكاء المكاني والخرائط – Spatial Intelligence
# =========================
# 4) الذكاء المكاني والخرائط – Spatial Intelligence (Mapbox + PostGIS Ready)
# =========================
elif choice == "الذكاء المكاني والخرائط":
    st.title("🗺️ الذكاء المكاني – Spatial Intelligence")
    st.write("إدارة الحدود الجغرافية والمخططات وربطها بالأصول والصكوك.")
    # تحميل مفتاح Mapbox
    try:
        with open("config/mapbox_token.txt") as f:
            mapbox_token = f.read().strip()
        px.set_mapbox_access_token(mapbox_token)
    except:
        st.error("⚠️ لم يتم العثور على ملف mapbox_token.txt في مجلد config")
        st.stop()
    # اختيار الحي
    district = st.selectbox("اختر الحي", districts)
    # بيانات عقارات (محاكاة)
    df_points = pd.DataFrame({
        "lat": [24.774265, 24.800000, 24.760000],
        "lon": [46.738586, 46.700000, 46.760000],
        "اسم الأصل": ["أصل 1", "أصل 2", "أصل 3"],
        "القيمة": [4_200_000, 3_800_000, 5_100_000],
        "الحالة": ["سليم", "بحاجة صيانة", "مؤجر"]
    })
    # بيانات حدود أراضي (Polygon) — محاكاة
    df_polygons = pd.DataFrame({
        "اسم القطعة": ["قطعة 101", "قطعة 102"],
        "القيمة": [2_500_000, 3_200_000],
        "geojson": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[46.73, 24.77], [46.74, 24.77], [46.74, 24.78], [46.73, 24.78], [46.73, 24.77]]]
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[46.75, 24.76], [46.76, 24.76], [46.76, 24.77], [46.75, 24.77], [46.75, 24.76]]]
                }
            }
        ]
    })
    # عرض مؤشرات الحي
    c1, c2, c3 = st.columns(3)
    c1.metric("متوسط سعر المتر", f"{sum(price_mock[district])//4} ريال")
    c2.metric("عدد القطع المسجلة", "320 قطعة", "+24")
    c3.metric("مؤشر الطلب", "مرتفع", "↑")
    st.subheader("📍 مواقع العقارات على الخريطة")
    fig_points = px.scatter_mapbox(
        df_points,
        lat="lat",
        lon="lon",
        hover_name="اسم الأصل",
        hover_data=["القيمة", "الحالة"],
        color="القيمة",
        size="القيمة",
        zoom=11,
        height=600,
        color_continuous_scale=px.colors.sequential.Blues
    )
    st.plotly_chart(fig_points, use_container_width=True)
    st.subheader("🗂️ حدود الأراضي (Polygon Layers)")
    for _, row in df_polygons.iterrows():
        st.markdown(f"**{row['اسم القطعة']} – القيمة: {row['القيمة']:,} ريال**")
        st.json(row["geojson"])
    st.info("✔ جاهز للربط مع PostGIS — فقط استبدل بيانات المحاكاة ببيانات فعلية من قاعدة البيانات.")
# =========================
elif choice == "الذكاء المكاني والخرائط":
    st.title("🗺️ الذكاء المكاني – Spatial Analytics")
    st.write("إدارة الحدود الجغرافية والمخططات وربطها بالأصول والصكوك (محاكاة واجهة – تحتاج PostGIS فعلياً).")
    district = st.selectbox("اختر الحي", districts)
    plot_data = pd.DataFrame({
        "المخطط": ["مخطط 1", "مخطط 2", "مخطط 3", "مخطط 4"],
        "السعر للمتر": price_mock[district]
    })
    c1, c2, c3 = st.columns(3)
    c1.metric("متوسط سعر المتر", f"{sum(price_mock[district])//4} ريال")
    c2.metric("عدد القطع المسجلة", "320 قطعة", "+24")
    c3.metric("مؤشر الطلب في الحي", "مرتفع", "↑")
    st.subheader(f"اتجاهات الأسعار في حي {district}")
    fig_area = px.area(
        plot_data,
        x="المخطط",
        y="السعر للمتر",
        title=f"اتجاهات سعر المتر في {district}",
        line_shape="spline",
        color_discrete_sequence=['#1E3A8A']
    )
    st.plotly_chart(fig_area, use_container_width=True)
    st.info("يمكن ربط هذه الواجهة لاحقاً بطبقات خرائط فعلية (PostGIS / Mapbox / ArcGIS).")
# =========================
# 5) نموذج التقييم الآلي AVM – Automated Valuation
# =========================
elif choice == "نموذج التقييم الآلي AVM":
    st.title("🤖 نموذج التقييم الآلي – AVM")
    st.write("منطق التقييم: VALUATION_LOGIC = (BigData * ML_Weights) + CV_Anomalies")
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("مدخلات التقييم")
        area = st.number_input("المساحة (م²)", min_value=50.0, value=250.0, step=10.0)
        district = st.selectbox("الحي", districts)
        frontage = st.number_input("طول الواجهة (م)", min_value=5.0, value=15.0)
        street_width = st.number_input("عرض الشارع (م)", min_value=8.0, value=20.0)
        age = st.number_input("عمر العقار (سنة)", min_value=0.0, value=5.0)
        quality = st.selectbox("جودة التشطيب", ["اقتصادي", "متوسط", "فاخر"])
        if st.button("تقدير القيمة العادلة"):
            base_price = sum(price_mock[district]) / len(price_mock[district])
            quality_factor = {"اقتصادي": 0.9, "متوسط": 1.0, "فاخر": 1.15}[quality]
            age_factor = max(0.7, 1 - (age * 0.01))
            frontage_factor = 1 + (frontage / 100)
            street_factor = 1 + (street_width / 200)
            price_per_m2 = base_price * quality_factor * age_factor * frontage_factor * street_factor
            estimated_value = price_per_m2 * area
            st.success(f"القيمة التقديرية للعقار: {estimated_value:,.0f} ريال")
            st.caption("هذه محاكاة AVM أولية – يمكن لاحقاً ربطها بنموذج تعلم عميق فعلي.")
    with col_r:
        st.subheader("عوامل التقييم الرئيسية")
        factors_df = pd.DataFrame({
            "العامل": ["الموقع", "المساحة", "جودة التشطيب", "عمر العقار", "عرض الشارع"],
            "الأهمية النسبية": [0.35, 0.25, 0.15, 0.15, 0.10]
        })
        fig_factors = px.pie(
            factors_df,
            names="العامل",
            values="الأهمية النسبية",
            title="أوزان العوامل في نموذج التقييم"
        )
        st.plotly_chart(fig_factors, use_container_width=True)
# =========================
# 6) الصيانة التنبؤية – Predictive Maintenance
# =========================
elif choice == "الصيانة التنبؤية":
    st.title("🛠️ الصيانة التنبؤية – Predictive Maintenance")
    st.write("نمذجة تكاليف الصيانة مقابل الإدارة، مع مؤشرات معدل الأعطال المتوقع.")
    c1, c2, c3 = st.columns(3)
    c1.metric("معدل الإشغال", "85%", "-4.5%")
    c2.metric("معدل الأعطال السنوي", "6.1%", "-3.1%")
    c3.metric("متوسط تكلفة الصيانة السنوية", "1,500,000 ريال", "+120,000")
    st.subheader("تكاليف الصيانة والإدارة عبر الأسابيع")
    fig_maint = px.line(
        maintenance_df,
        x="الأسبوع",
        y=["تكلفة الصيانة", "تكلفة الإدارة"],
        markers=True,
        title="تكاليف الصيانة مقابل الإدارة"
    )
    st.plotly_chart(fig_maint, use_container_width=True)
    st.subheader("تصنيف فئات الصيانة")
    pie_df = pd.DataFrame({
        "الفئة": ["إصلاحات", "وقائي", "طوارئ", "رسوم إدارة"],
        "القيمة": [30, 35, 20, 15]
    })
    fig_pie = px.pie(
        pie_df,
        names="الفئة",
        values="القيمة",
        title="توزيع فئات الصيانة"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    st.info("يمكن لاحقاً ربط هذه الوحدة بنماذج تعلم آلي تتنبأ بالأعطال بناءً على بيانات تاريخية.")
# =========================
# 7) ذكاء السوق والاستثمار – Market Intelligence
# =========================
elif choice == "ذكاء السوق والاستثمار":
    st.title("📊 ذكاء السوق والاستثمار – Market Intelligence")
    st.write("تحليل اتجاهات السوق، أحجام السوق، ومؤشرات النمو.")
    st.subheader("محاكاة حجم سوق العقار حسب نوع الأصل")
    market_df = pd.DataFrame({
        "السنة": list(range(2020, 2031)),
        "سكني": np.linspace(80, 130, 11),
        "تجاري": np.linspace(60, 95, 11),
        "صناعي": np.linspace(40, 70, 11),
        "أراضي": np.linspace(30, 55, 11)
    })
    fig_market = px.area(
        market_df,
        x="السنة",
        y=["سكني", "تجاري", "صناعي", "أراضي"],
        title="حجم سوق العقار (محاكاة – مليار ريال)"
    )
    st.plotly_chart(fig_market, use_container_width=True)

    st.subheader("مؤشر نمو السوق (CAGR تقريبي)")
    st.metric("CAGR تقديري 2025–2030", "4.1%", "+0.3%")

    st.caption("يمكن لاحقاً ربط هذه الوحدة بمصادر بيانات خارجية (Market Data Providers / Open Data).")

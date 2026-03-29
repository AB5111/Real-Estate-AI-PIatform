import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import random
# ==========================================
# إعدادات الصفحة والهوية البصرية
# ==========================================
st.set_page_config(layout="wide", page_title="Drones Crafters – Real Estate Dashboard", page_icon="🏢")
# CSS محسن (كما هو سابقاً مع إضافات للتفاعلية)
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
    </style>
""", unsafe_allow_html=True)
# ==========================================
# تحميل البيانات الأساسية (قابلة للتحديث)
# ==========================================
@st.cache_data(ttl=60)  # تنتهي بعد 60 ثانية لتحديث البيانات بشكل دوري
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
        "الأسبوع": [f"الأسبوع {i}" for i in range(1, 14)],
        "تكلفة الصيانة": np.random.randint(200_000, 600_000, 13),
        "تكلفة الإدارة": np.random.randint(150_000, 400_000, 13),
        "اسم الأصل": [f"أصل {i}" for i in range(1, 14)]
    })
    return districts, price_mock, financial_df, maintenance_df
districts, price_mock, financial_df, maintenance_df = load_base_data()
# ==========================================
# حالة الجلسة للبيانات التفاعلية
# ==========================================
if 'deeds_df' not in st.session_state:
    st.session_state.deeds_df = pd.DataFrame({
        "رقم الصك": ["123/أ", "456/ب", "789/ج"],
        "المالك": ["شركة أصول الأولى", "صندوق استثماري عقاري", "شركة تطوير عمراني"],
        "الحي": ["الملقا", "الياسمين", "النرجس"],
        "المساحة م²": [2500, 4300, 1800],
        "الحالة": ["ساري", "ساري", "محدث"]
    })
if 'contracts_df' not in st.session_state:
    st.session_state.contracts_df = pd.DataFrame({
        "رقم العقد": ["C-101", "C-102", "C-103"],
        "المستأجر": ["شركة الأفق", "مؤسسة البناء", "فردي - أحمد"],
        "العقار": ["برج الأعمال", "مجمع الريان", "فيلا الياسمين"],
        "القيمة الشهرية": [45_000, 28_000, 12_000],
        "تاريخ الانتهاء": ["2025-01-01", "2025-03-14", "2025-04-30"]
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
    role = st.selectbox("الدور التنفيذي", ["System Admin", "Asset Manager", "Investment Analyst"], 
                        format_func=lambda x: {"System Admin":"مسؤول النظام","Asset Manager":"مدير الأصول","Investment Analyst":"محلل استثماري"}[x])
    st.divider()
    services = {
        "لوحة القيادة التنفيذية": "📊", "إدارة الصكوك والوثائق": "📜", "التحليلات المالية": "💰",
        "الذكاء المكاني والخرائط": "🗺️", "نموذج التقييم الآلي AVM": "🤖", "الصيانة التنبؤية": "🛠️",
        "ذكاء السوق والاستثمار": "📈", "إدارة العقود والمستأجرين": "👥", "التنبؤ بالأسعار (AI)": "📉",
        "تحليل المحفظة الاستثمارية": "🥧", "الامتثال القانوني والتراخيص": "⚖️", "لوحة تحكم المخاطر": "⚠️",
        "التقارير الذكية القابلة للتخصيص": "📑", "مركز التنبيهات والإشعارات": "🔔"
    }
    choice = st.radio("الخدمات المتكاملة", list(services.keys()), index=list(services.keys()).index(st.session_state.selected_service))
    st.session_state.selected_service = choice
st.write(f"🔐 الدور الحالي: **{role}**")
st.divider()
# ==========================================
# 1️⃣ لوحة القيادة التنفيذية (مطورة تفاعلياً)
# ==========================================
if st.session_state.selected_service == "لوحة القيادة التنفيذية":
    st.title("🏢 لوحة القيادة التنفيذية – نظرة عامة تفاعلية")
    # تحديث تلقائي للبيانات (محاكاة)
    if st.button("🔄 تحديث البيانات الحية"):
        st.cache_data.clear()
        st.rerun()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("إجمالي قيمة الأصول", "2.4 مليار ريال", "+4.2%")
    col2.metric("عدد العقارات", "1,280 أصل", "+35")
    col3.metric("متوسط العائد السنوي (IRR)", "11.8%", "+0.6%")
    col4.metric("نسبة الإشغال", "89%", "-3.1%")
    # رسم بياني تفاعلي مع تحديد النقاط
    asset_type_df = pd.DataFrame({"نوع العقار": ["شقق", "مكاتب", "تجاري", "صناعي", "فلل"], "القيمة": [600, 450, 520, 300, 530]})
    fig = px.bar(asset_type_df, x="نوع العقار", y="القيمة", color="القيمة", color_continuous_scale="Blues", title="توزيع القيمة حسب نوع العقار")
    fig.update_layout(font_family="Cairo", clickmode='event+select')
    event = st.plotly_chart(fig, use_container_width=True, key="bar_chart")
    # عرض تفاصيل عند النقر على بار (بسيط)
    st.caption("انقر على أي عمود لعرض تفاصيله (محاكاة)")
    # مؤشرات الأداء الرئيسية مع رسم خطي تفاعلي
    kpi_df = pd.DataFrame({"السنة": [2021,2022,2023,2024], "ROI": [8.5,9.2,10.1,10.8], "IRR": [10.2,10.9,11.3,11.8]})
    fig2 = px.line(kpi_df, x="السنة", y=["ROI","IRR"], markers=True, title="تطور العوائد")
    fig2.update_layout(font_family="Cairo")
    st.plotly_chart(fig2, use_container_width=True)
# ==========================================
# 2️⃣ إدارة الصكوك (جدول قابل للتحرير)
# ==========================================
elif st.session_state.selected_service == "إدارة الصكوك والوثائق":
    st.title("📜 إدارة الصكوك - تحرير مباشر")
    edited_df = st.data_editor(st.session_state.deeds_df, use_container_width=True, num_rows="dynamic")
    if st.button("💾 حفظ التغييرات"):
        st.session_state.deeds_df = edited_df
        st.success("تم حفظ البيانات!")
    with st.expander("➕ إضافة صك جديد"):
        with st.form("new_deed"):
            col1,col2=st.columns(2)
            with col1:
                new_no = st.text_input("رقم الصك")
                new_owner = st.text_input("المالك")
            with col2:
                new_dist = st.selectbox("الحي", districts)
                new_area = st.number_input("المساحة", min_value=0.0)
            if st.form_submit_button("إضافة"):
                new_row = pd.DataFrame({"رقم الصك":[new_no],"المالك":[new_owner],"الحي":[new_dist],"المساحة م²":[new_area],"الحالة":["ساري"]})
                st.session_state.deeds_df = pd.concat([st.session_state.deeds_df, new_row], ignore_index=True)
                st.rerun()
# ==========================================
# 3️⃣ التحليلات المالية (تفاعلية مع فلتر)
# ==========================================
elif st.session_state.selected_service == "التحليلات المالية":
    st.title("💰 التحليلات المالية")
    years = st.slider("اختر نطاق السنوات", 2021, 2024, (2021,2024))
    filtered = financial_df[(financial_df["السنة"]>=years[0]) & (financial_df["السنة"]<=years[1])]
    fig = px.bar(filtered, x="السنة", y=["الإيرادات","المصاريف التشغيلية","صيانة"], barmode="group", title="الإيرادات والمصاريف")
    st.plotly_chart(fig, use_container_width=True)
    
    # محاكاة NPV تفاعلية
    with st.expander("محاكاة استثمارية تفاعلية"):
        inv = st.number_input("الاستثمار الأولي (ريال)", value=10_000_000, step=1_000_000)
        rate = st.slider("معدل الخصم %", 5.0, 15.0, 9.0)
        years_sim = st.slider("عدد السنوات", 1, 10, 5)
        cf = [inv * 0.3] * years_sim
        npv = sum(cf[i]/((1+rate/100)**(i+1)) for i in range(years_sim)) - inv
        st.metric("صافي القيمة الحالية (NPV)", f"{npv:,.0f} ريال")
# ==========================================
# 4️⃣ الذكاء المكاني (خريطة تفاعلية)
# ==========================================
elif st.session_state.selected_service == "الذكاء المكاني والخرائط":
    st.title("🗺️ الخريطة التفاعلية")
    district = st.selectbox("اختر الحي", districts)
    col1,col2,col3 = st.columns(3)
    col1.metric("متوسط سعر المتر", f"{np.mean(price_mock[district]):,.0f} ريال")
    col2.metric("عدد الأصول", "320")
    col3.metric("مؤشر الطلب", "مرتفع")
    df_points = pd.DataFrame({
        "lat": [24.774265, 24.800000, 24.760000, 24.820000],
        "lon": [46.738586, 46.700000, 46.760000, 46.680000],
        "name": ["مبنى إداري", "مجمع تجاري", "أرض خام", "مستودع"],
        "value": [4.2, 7.8, 5.1, 3.1]
    })
    fig = px.scatter_mapbox(df_points, lat="lat", lon="lon", hover_name="name", size="value", zoom=11, title="مواقع الأصول")
    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig, use_container_width=True)
# ==========================================
# 5️⃣ نموذج التقييم الآلي AVM (تفاعلي فوري)
# ==========================================
elif st.session_state.selected_service == "نموذج التقييم الآلي AVM":
    st.title("🤖 التقييم الآلي الفوري")
    with st.form("avm_form"):
        area = st.number_input("المساحة (م²)", 50, 10000, 250)
        district = st.selectbox("الحي", districts)
        quality = st.selectbox("الجودة", ["اقتصادي", "متوسط", "فاخر"])
        age = st.slider("عمر العقار (سنوات)", 0, 50, 5)
        if st.form_submit_button("تقدير القيمة"):
            base = np.mean(price_mock[district])
            factor = {"اقتصادي":0.9, "متوسط":1.0, "فاخر":1.15}[quality]
            price = base * factor * (1 - age*0.01) * area
            st.success(f"💰 القيمة التقديرية: {price:,.0f} ريال")
            st.metric("سعر المتر المقدر", f"{price/area:,.0f} ريال/م²")
# ==========================================
# 6️⃣ الصيانة التنبؤية (مع فلتر)
# ==========================================
elif st.session_state.selected_service == "الصيانة التنبؤية":
    st.title("🛠️ الصيانة التنبؤية")
    asset_filter = st.multiselect("اختر الأصول", maintenance_df["اسم الأصل"].unique(), default=maintenance_df["اسم الأصل"].unique())
    filtered_maint = maintenance_df[maintenance_df["اسم الأصل"].isin(asset_filter)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=filtered_maint["الأسبوع"], y=filtered_maint["تكلفة الصيانة"], name="تكلفة الصيانة"))
    fig.add_trace(go.Scatter(x=filtered_maint["الأسبوع"], y=filtered_maint["تكلفة الإدارة"], name="تكلفة الإدارة"))
    fig.add_hline(y=500000, line_dash="dash", line_color="red", annotation_text="الحد الأقصى")
    fig.update_layout(title="اتجاه التكاليف", font_family="Cairo")
    st.plotly_chart(fig, use_container_width=True)
    col1,col2,col3 = st.columns(3)
    col1.metric("معدل الجاهزية", "94.5%")
    col2.metric("الأعطال المتوقعة", "3.2%")
    col3.metric("الميزانية المتبقية", "500,000 ريال")
# ==========================================
# 7️⃣ ذكاء السوق (تفاعلي)
# ==========================================
elif st.session_state.selected_service == "ذكاء السوق والاستثمار":
    st.title("📈 ذكاء السوق")
    sectors = st.multiselect("اختر القطاعات", ["سكني", "تجاري", "صناعي"], default=["سكني","تجاري","صناعي"])
    market_df = pd.DataFrame({"السنة":list(range(2020,2031)), "سكني":np.linspace(80,145,11), "تجاري":np.linspace(60,110,11), "صناعي":np.linspace(40,85,11)})
    fig = px.area(market_df, x="السنة", y=sectors, title="توقعات نمو القطاعات")
    st.plotly_chart(fig, use_container_width=True)
    st.info("نمو متسارع متوقع في القطاع الصناعي")
# ==========================================
# 8️⃣ إدارة العقود (جدول قابل للتحرير)
# ==========================================
elif st.session_state.selected_service == "إدارة العقود والمستأجرين":
    st.title("👥 العقود والمستأجرين")
    edited_contracts = st.data_editor(st.session_state.contracts_df, use_container_width=True, num_rows="dynamic")
    if st.button("حفظ تغييرات العقود"):
        st.session_state.contracts_df = edited_contracts
        st.success("تم الحفظ")
    with st.expander("عقد جديد"):
        with st.form("new_contract"):
            c_no = st.text_input("رقم العقد")
            tenant = st.text_input("المستأجر")
            prop = st.text_input("العقار")
            rent = st.number_input("القيمة الشهرية", min_value=0)
            end = st.date_input("تاريخ الانتهاء")
            if st.form_submit_button("إضافة"):
                new_c = pd.DataFrame({"رقم العقد":[c_no],"المستأجر":[tenant],"العقار":[prop],"القيمة الشهرية":[rent],"تاريخ الانتهاء":[str(end)]})
                st.session_state.contracts_df = pd.concat([st.session_state.contracts_df, new_c], ignore_index=True)
                st.rerun()
# ==========================================
# 9️⃣ التنبؤ بالأسعار (AI) – تفاعلي
# ==========================================
elif st.session_state.selected_service == "التنبؤ بالأسعار (AI)":
    st.title("📈 التنبؤ بالأسعار باستخدام AI")
    months = pd.date_range("2024-01-01", periods=12, freq='M')
    historical = [4200, 4350, 4450, 4600, 4750, 4900, 5100, 5300, 5450, 5600, 5750, 5900]
    forecast = [6050, 6200, 6380, 6550, 6720, 6900, 7100, 7300, 7480, 7650, 7820, 8000]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=historical, name="تاريخي", mode='lines+markers'))
    fig.add_trace(go.Scatter(x=months, y=forecast, name="توقع AI", line=dict(dash='dot', color='red')))
    fig.update_layout(title="توقع سعر المتر المربع", xaxis_title="الشهر", yaxis_title="سعر (ريال)", font_family="Cairo")
    st.plotly_chart(fig, use_container_width=True)
    st.metric("متوسط الزيادة المتوقعة", "7.2%")
# ==========================================
# 🔟 تحليل المحفظة الاستثمارية (تفاعلي)
# ==========================================
elif st.session_state.selected_service == "تحليل المحفظة الاستثمارية":
    st.title("📊 تحليل المحفظة")
    port = pd.DataFrame({"القطاع":["سكني","تجاري","صناعي","مكاتب"], "القيمة":[450,320,280,410], "العائد":[8,10,12,9]})
    fig_pie = px.pie(port, names="القطاع", values="القيمة", hole=0.4, title="توزيع المحفظة")
    st.plotly_chart(fig_pie, use_container_width=True)
    fig_scatter = px.scatter(port, x="العائد", y="القيمة", text="القطاع", size="القيمة", title="العائد مقابل القيمة")
    st.plotly_chart(fig_scatter, use_container_width=True)
# ==========================================
# 1️⃣1️⃣ الامتثال القانوني (مع تنبيهات)
# ==========================================
elif st.session_state.selected_service == "الامتثال القانوني والتراخيص":
    st.title("⚖️ التراخيص والامتثال")
    licenses = pd.DataFrame({
        "الترخيص":["رخصة بناء","رخصة تشغيل","دفاع مدني","بيئة"],
        "تاريخ الانتهاء":["2025-06-01","2024-12-31","2024-10-20","2025-03-01"],
        "الحالة":["ساري","ينتهي قريباً","منتهي","ساري"]
    })
    st.dataframe(licenses, use_container_width=True)
    expired = licenses[licenses["الحالة"]=="منتهي"]
    if len(expired)>0:
        st.warning(f"⚠️ هناك {len(expired)} ترخيص منتهي (أو على وشك الانتهاء)")
# ==========================================
# 1️⃣2️⃣ لوحة تحكم المخاطر (مصفوفة تفاعلية)
# ==========================================
elif st.session_state.selected_service == "لوحة تحكم المخاطر":
    st.title("⚠️ مصفوفة المخاطر")
    risks = pd.DataFrame({
        "الخطر":["تقلبات السوق","مخاطر الائتمان","تشغيلية","قانونية","طبيعية"],
        "الاحتمال":[35,25,45,20,15],
        "الأثر":[4,3,3,4,5]
    })
    risks["نقطة المخاطرة"] = risks["الاحتمال"] * risks["الأثر"]
    fig = px.bar(risks, x="الخطر", y="نقطة المخاطرة", color="نقطة المخاطرة", color_continuous_scale="Reds", title="تقييم المخاطر")
    st.plotly_chart(fig, use_container_width=True)
    st.metric("إجمالي درجة المخاطر", f"{risks['نقطة المخاطرة'].sum()}")
# ==========================================
# 1️⃣3️⃣ التقارير الذكية (مع فلتر وتنزيل)
# ==========================================
elif st.session_state.selected_service == "التقارير الذكية القابلة للتخصيص":
    st.title("📑 التقارير الذكية")
    report_type = st.selectbox("اختر نوع التقرير", ["ملخص المحفظة", "تحليل الأداء المالي", "حالة الصيانة"])
    if report_type == "ملخص المحفظة":
        df = pd.DataFrame({"المؤشر":["الأصول","القيمة","العائد"], "القيمة":["1,280","2.4 مليار","11.8%"]})
        st.dataframe(df)
    elif report_type == "تحليل الأداء المالي":
        st.line_chart(financial_df.set_index("السنة")["الإيرادات"])
    else:
        st.bar_chart(maintenance_df.set_index("الأسبوع")["تكلفة الصيانة"])
    csv = st.session_state.deeds_df.to_csv().encode()
    st.download_button("تحميل التقرير (CSV)", data=csv, file_name="report.csv")
# ==========================================
# 1️⃣4️⃣ مركز التنبيهات (تفاعلي)
# ==========================================
elif st.session_state.selected_service == "مركز التنبيهات والإشعارات":
    st.title("🔔 التنبيهات والإشعارات")
    alerts = pd.DataFrame({
        "التاريخ":[(datetime.now()-timedelta(days=i)).strftime("%Y-%m-%d") for i in range(5)],
        "الرسالة":["انتهاء رخصة تشغيل","صيانة دورية مستحقة","عقد إيجار على وشك الانتهاء","تحديث أسعار المنطقة","طلب صيانة جديد"],
        "النوع":["تحذير","تنبيه","تنبيه","معلومات","تحذير"]
    })
    st.dataframe(alerts, use_container_width=True)
    if st.button("تحديد الكمقروء"):
        st.success("تم تحديث حالة الإشعارات (محاكاة)")

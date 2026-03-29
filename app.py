import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

# ==========================================
# إعدادات الصفحة (يجب أن تكون الأولى)
# ==========================================
st.set_page_config(
    layout="wide",
    page_title="Drones Crafters – Real Estate Management",
    page_icon="🏢",
    initial_sidebar_state="expanded"
)

# ==========================================
# تهيئة حالة الجلسة (Session State)
# ==========================================
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'language' not in st.session_state:
    st.session_state.language = 'ar'
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'user_tenant' not in st.session_state:
    st.session_state.user_tenant = None
if 'current_tenant' not in st.session_state:
    st.session_state.current_tenant = 'tenant_1'
if 'selected_service' not in st.session_state:
    st.session_state.selected_service = "لوحة القيادة التنفيذية"

# بيانات المستخدمين والجهات (محاكاة قاعدة بيانات)
if 'users' not in st.session_state:
    st.session_state.users = {
        "admin@drones.com": {"password": "admin123", "role": "SuperAdmin", "tenant": None},
        "manager1@assets.com": {"password": "pass1", "role": "TenantAdmin", "tenant": "tenant_1"},
        "viewer1@assets.com": {"password": "view", "role": "Viewer", "tenant": "tenant_1"},
        "manager2@gulf.com": {"password": "pass2", "role": "TenantAdmin", "tenant": "tenant_2"}
    }

if 'tenants' not in st.session_state:
    st.session_state.tenants = {
        "tenant_1": {
            "name": "شركة أصول الرياض",
            "plan": "Enterprise",
            "properties_count": 1280,
            "assets_value": 2.4e9,
            "deeds": pd.DataFrame({
                "رقم الصك": ["123/أ", "456/ب"],
                "المالك": ["شركة أصول الأولى", "صندوق استثماري"],
                "الحي": ["الملقا", "الياسمين"],
                "المساحة م²": [2500, 4300],
                "الحالة": ["ساري", "ساري"]
            }),
            "contracts": pd.DataFrame({
                "رقم العقد": ["C-101", "C-102"],
                "المستأجر": ["شركة الأفق", "مؤسسة البناء"],
                "القيمة الشهرية": [45000, 28000],
                "تاريخ الانتهاء": ["2025-01-01", "2025-03-14"]
            }),
            "maintenance": pd.DataFrame({
                "الأسبوع": [f"الأسبوع {i}" for i in range(1, 14)],
                "تكلفة الصيانة": np.random.randint(200000, 600000, 13),
                "تكلفة الإدارة": np.random.randint(150000, 400000, 13),
                "اسم الأصل": [f"أصل {i}" for i in range(1, 14)]
            }),
            "financial": pd.DataFrame({
                "السنة": [2021, 2022, 2023, 2024],
                "الإيرادات": [12e6, 14.5e6, 16.2e6, 18e6],
                "المصاريف التشغيلية": [4e6, 4.5e6, 5e6, 5.4e6],
                "صيانة": [1.2e6, 1.35e6, 1.5e6, 1.65e6]
            }),
            "alerts": [
                {"التاريخ": "2024-12-15", "الرسالة": "انتهاء رخصة تشغيل", "النوع": "تحذير"},
                {"التاريخ": "2024-12-20", "الرسالة": "صيانة دورية مستحقة", "النوع": "تنبيه"}
            ]
        },
        "tenant_2": {
            "name": "مجموعة الخليج العقارية",
            "plan": "Professional",
            "properties_count": 540,
            "assets_value": 980e6,
            "deeds": pd.DataFrame({"رقم الصك": ["789/ج"], "المالك": ["مجموعة الخليج"], "الحي": ["النرجس"], "المساحة م²": [1800], "الحالة": ["محدث"]}),
            "contracts": pd.DataFrame({"رقم العقد": ["C-201"], "المستأجر": ["شركة الخدمات"], "القيمة الشهرية": [32000], "تاريخ الانتهاء": ["2025-06-01"]}),
            "maintenance": pd.DataFrame({"الأسبوع": [f"الأسبوع {i}" for i in range(1,8)], "تكلفة الصيانة": np.random.randint(100000, 400000, 7), "تكلفة الإدارة": np.random.randint(80000, 200000, 7), "اسم الأصل": [f"أصل {i}" for i in range(1,8)]}),
            "financial": pd.DataFrame({"السنة": [2021,2022,2023,2024], "الإيرادات": [5e6,6.2e6,7.1e6,8.5e6], "المصاريف التشغيلية": [1.8e6,2.1e6,2.4e6,2.9e6], "صيانة": [0.5e6,0.6e6,0.7e6,0.85e6]}),
            "alerts": []
        }
    }

# ==========================================
# دوال المساعدة
# ==========================================
def get_current_data():
    return st.session_state.tenants[st.session_state.current_tenant]

def update_tenant_data(key, value):
    st.session_state.tenants[st.session_state.current_tenant][key] = value

def t(text_ar, text_en=None):
    if text_en is None:
        text_en = text_ar
    return text_ar if st.session_state.language == 'ar' else text_en

def set_dark_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode

def toggle_lang():
    st.session_state.language = 'en' if st.session_state.language == 'ar' else 'ar'

def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_tenant = None

# ==========================================
# شاشة تسجيل الدخول
# ==========================================
def login_screen():
    st.title("🏢 Drones Crafters")
    st.subheader("تسجيل الدخول" if st.session_state.language == 'ar' else "Login")
    email = st.text_input("البريد الإلكتروني" if st.session_state.language == 'ar' else "Email")
    password = st.text_input("كلمة المرور" if st.session_state.language == 'ar' else "Password", type="password")
    if st.button("دخول" if st.session_state.language == 'ar' else "Login"):
        if email in st.session_state.users and st.session_state.users[email]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.user_role = st.session_state.users[email]["role"]
            st.session_state.user_tenant = st.session_state.users[email]["tenant"]
            if st.session_state.user_role == "SuperAdmin":
                st.session_state.current_tenant = "tenant_1"
            else:
                st.session_state.current_tenant = st.session_state.user_tenant
            st.rerun()
        else:
            st.error("بيانات الدخول غير صحيحة" if st.session_state.language == 'ar' else "Invalid credentials")
    st.markdown("---")
    st.caption("للتجربة: admin@drones.com / admin123  |  manager1@assets.com / pass1")

# ==========================================
# شريط الأدوات العلوي
# ==========================================
def top_bar():
    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
    with col1:
        st.markdown(f"### 🏢 {st.session_state.tenants[st.session_state.current_tenant]['name']}")
    with col2:
        icon = "🌙" if not st.session_state.dark_mode else "☀️"
        if st.button(icon):
            set_dark_mode()
            st.rerun()
    with col3:
        lang_text = "🇸🇦 عربي" if st.session_state.language == 'ar' else "🇬🇧 English"
        if st.button(lang_text):
            toggle_lang()
            st.rerun()
    with col4:
        st.markdown(f"👤 {st.session_state.user_role}")
    with col5:
        if st.button("تسجيل خروج" if st.session_state.language == 'ar' else "Logout"):
            logout()
            st.rerun()

# ==========================================
# القائمة الجانبية
# ==========================================
def sidebar_menu():
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/10543/10543319.png", width=80)
        st.title("Drones Crafters")
        if st.session_state.user_role == "SuperAdmin":
            tenants_list = list(st.session_state.tenants.keys())
            selected = st.selectbox("اختر الجهة" if st.session_state.language == 'ar' else "Select Tenant",
                                    tenants_list,
                                    format_func=lambda x: st.session_state.tenants[x]["name"])
            if selected != st.session_state.current_tenant:
                st.session_state.current_tenant = selected
                st.rerun()
        st.divider()
        
        services = [
            "لوحة القيادة التنفيذية",
            "إدارة الصكوك والوثائق",
            "التحليلات المالية",
            "الذكاء المكاني والخرائط",
            "نموذج التقييم الآلي AVM",
            "الصيانة التنبؤية",
            "ذكاء السوق والاستثمار",
            "إدارة العقود والمستأجرين",
            "التنبؤ بالأسعار (AI)",
            "تحليل المحفظة الاستثمارية",
            "الامتثال القانوني والتراخيص",
            "لوحة تحكم المخاطر",
            "التقارير الذكية القابلة للتخصيص",
            "مركز التنبيهات والإشعارات"
        ]
        # تحديد الخدمات المسموحة حسب الدور
        if st.session_state.user_role == "Viewer":
            allowed = services[:7] + [services[9], services[12], services[13]]  # جزء من الخدمات
        else:
            allowed = services
        
        choice = st.radio("الخدمات" if st.session_state.language == 'ar' else "Services", allowed,
                          index=allowed.index(st.session_state.selected_service) if st.session_state.selected_service in allowed else 0)
        st.session_state.selected_service = choice
        st.divider()
        st.caption("© 2025 Drones Crafters - v3.0")

# ==========================================
# CSS للوضع المظلم والفاتح
# ==========================================
def load_css():
    bg = "#0e1117" if st.session_state.dark_mode else "#ffffff"
    text = "#ffffff" if st.session_state.dark_mode else "#000000"
    card = "#1e1e2f" if st.session_state.dark_mode else "#f8f9fa"
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, .stApp, [data-testid="stSidebar"], .main {{
        direction: RTL;
        text-align: right;
        font-family: 'Cairo', sans-serif;
        background-color: {bg};
        color: {text};
    }}
    div[data-testid="stMetric"] {{
        background-color: {card};
        padding: 15px;
        border-radius: 15px;
        border-right: 5px solid #1E3A8A;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    .stButton>button {{
        background-color: #1E3A8A;
        color: white;
        border-radius: 10px;
        font-weight: bold;
    }}
    </style>
    """

# ==========================================
# وظائف الخدمات (مبسطة ومستقرة)
# ==========================================
def render_dashboard():
    data = get_current_data()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("إجمالي قيمة الأصول", f"{data['assets_value']/1e9:.1f} مليار ريال", "+4.2%")
    col2.metric("عدد العقارات", f"{data['properties_count']:,}", "+35")
    col3.metric("متوسط العائد السنوي", "11.8%", "+0.6%")
    col4.metric("نسبة الإشغال", "89%", "-3.1%")
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        df = pd.DataFrame({"نوع العقار": ["شقق","مكاتب","تجاري","صناعي","فلل"], "القيمة": [600,450,520,300,530]})
        fig = px.bar(df, x="نوع العقار", y="القيمة", color="القيمة", color_continuous_scale="Blues", title="توزيع القيمة")
        fig.update_layout(font_family="Cairo")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        kpi = pd.DataFrame({"السنة": [2021,2022,2023,2024], "ROI": [8.5,9.2,10.1,10.8], "IRR": [10.2,10.9,11.3,11.8]})
        fig = px.line(kpi, x="السنة", y=["ROI","IRR"], markers=True, title="تطور العوائد")
        fig.update_layout(font_family="Cairo")
        st.plotly_chart(fig, use_container_width=True)

def render_deeds():
    data = get_current_data()
    edited = st.data_editor(data["deeds"], use_container_width=True, num_rows="dynamic")
    if st.button("حفظ التغييرات"):
        update_tenant_data("deeds", edited)
        st.success("تم الحفظ")

def render_financial():
    data = get_current_data()
    years = st.slider("نطاق السنوات", 2021, 2024, (2021,2024))
    df = data["financial"]
    df = df[(df["السنة"]>=years[0]) & (df["السنة"]<=years[1])]
    fig = px.bar(df, x="السنة", y=["الإيرادات","المصاريف التشغيلية","صيانة"], barmode="group", title="الإيرادات والمصاريف")
    st.plotly_chart(fig, use_container_width=True)

def render_spatial():
    st.title("الذكاء المكاني")
    district = st.selectbox("الحي", ["الملقا","الياسمين","النرجس","العمارية"])
    st.metric("متوسط سعر المتر", f"{np.random.randint(3500,6000):,} ريال")
    points = pd.DataFrame({
        "lat": [24.774265, 24.800000, 24.760000],
        "lon": [46.738586, 46.700000, 46.760000],
        "name": ["مبنى إداري", "مجمع تجاري", "أرض"]
    })
    fig = px.scatter_mapbox(points, lat="lat", lon="lon", hover_name="name", zoom=11)
    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig, use_container_width=True)

def render_avm():
    st.title("نموذج التقييم الآلي")
    with st.form("avm"):
        area = st.number_input("المساحة (م²)", 50, 10000, 250)
        district = st.selectbox("الحي", ["الملقا","الياسمين","النرجس","العمارية"])
        quality = st.selectbox("الجودة", ["اقتصادي","متوسط","فاخر"])
        if st.form_submit_button("تقدير"):
            base = np.random.randint(3500,6000)
            factor = {"اقتصادي":0.9,"متوسط":1.0,"فاخر":1.15}[quality]
            price = base * factor * area
            st.success(f"القيمة التقديرية: {price:,.0f} ريال")

def render_maintenance():
    data = get_current_data()
    df = data["maintenance"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["الأسبوع"], y=df["تكلفة الصيانة"], name="تكلفة الصيانة"))
    fig.add_trace(go.Scatter(x=df["الأسبوع"], y=df["تكلفة الإدارة"], name="تكلفة الإدارة"))
    fig.add_hline(y=500000, line_dash="dash", line_color="red", annotation_text="الحد الأقصى")
    fig.update_layout(font_family="Cairo")
    st.plotly_chart(fig, use_container_width=True)

def render_market():
    st.title("ذكاء السوق")
    market_df = pd.DataFrame({"السنة":list(range(2020,2031)), "سكني":np.linspace(80,145,11), "تجاري":np.linspace(60,110,11), "صناعي":np.linspace(40,85,11)})
    fig = px.area(market_df, x="السنة", y=["سكني","تجاري","صناعي"], title="توقعات السوق")
    st.plotly_chart(fig, use_container_width=True)
    st.info("نمو متسارع متوقع في القطاع الصناعي")

def render_contracts():
    data = get_current_data()
    edited = st.data_editor(data["contracts"], use_container_width=True, num_rows="dynamic")
    if st.button("حفظ العقود"):
        update_tenant_data("contracts", edited)
        st.success("تم الحفظ")

def render_forecast():
    st.title("التنبؤ بالأسعار (AI)")
    months = pd.date_range("2024-01-01", periods=12, freq='M')
    historical = [4200,4350,4450,4600,4750,4900,5100,5300,5450,5600,5750,5900]
    forecast = [6050,6200,6380,6550,6720,6900,7100,7300,7480,7650,7820,8000]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=historical, name="تاريخي"))
    fig.add_trace(go.Scatter(x=months, y=forecast, name="متوقع", line=dict(dash="dot")))
    fig.update_layout(font_family="Cairo")
    st.plotly_chart(fig, use_container_width=True)
    st.metric("متوسط الزيادة المتوقعة", "7.2%")

def render_portfolio():
    port = pd.DataFrame({"القطاع":["سكني","تجاري","صناعي","مكاتب"], "القيمة":[450,320,280,410], "العائد":[8,10,12,9]})
    fig = px.pie(port, names="القطاع", values="القيمة", hole=0.4, title="توزيع المحفظة")
    st.plotly_chart(fig, use_container_width=True)
    fig2 = px.scatter(port, x="العائد", y="القيمة", text="القطاع", size="القيمة", title="العائد مقابل القيمة")
    st.plotly_chart(fig2, use_container_width=True)

def render_compliance():
    st.title("الامتثال القانوني")
    licenses = pd.DataFrame({
        "الترخيص":["رخصة بناء","رخصة تشغيل","دفاع مدني"],
        "تاريخ الانتهاء":["2025-06-01","2024-12-31","2024-10-20"],
        "الحالة":["ساري","ينتهي قريباً","منتهي"]
    })
    st.dataframe(licenses)
    if any(licenses["الحالة"] == "منتهي"):
        st.warning("يوجد تراخيص منتهية!")

def render_risk():
    risks = pd.DataFrame({"الخطر":["تقلبات السوق","مخاطر الائتمان","تشغيلية"], "الاحتمال":[35,25,45], "الأثر":[4,3,3]})
    risks["النقطة"] = risks["الاحتمال"] * risks["الأثر"]
    fig = px.bar(risks, x="الخطر", y="النقطة", color="النقطة", color_continuous_scale="Reds", title="مصفوفة المخاطر")
    st.plotly_chart(fig, use_container_width=True)

def render_reports():
    st.title("التقارير الذكية")
    report_type = st.selectbox("نوع التقرير", ["ملخص المحفظة", "التحليل المالي", "حالة الصيانة"])
    if report_type == "ملخص المحفظة":
        st.dataframe(pd.DataFrame({"المؤشر":["الأصول","القيمة"], "القيمة":["1,280","2.4 مليار"]}))
    elif report_type == "التحليل المالي":
        data = get_current_data()
        st.line_chart(data["financial"].set_index("السنة")["الإيرادات"])
    else:
        data = get_current_data()
        st.bar_chart(data["maintenance"].set_index("الأسبوع")["تكلفة الصيانة"])
    csv = get_current_data()["deeds"].to_csv().encode()
    st.download_button("تحميل CSV", csv, "report.csv")

def render_notifications():
    st.title("مركز التنبيهات")
    data = get_current_data()
    alerts = pd.DataFrame(data.get("alerts", []))
    if not alerts.empty:
        st.dataframe(alerts)
    else:
        st.info("لا توجد إشعارات حالية")
    if st.button("تحديد الكل كمقروء"):
        st.success("تم التحديث")

# ==========================================
# التطبيق الرئيسي
# ==========================================
def main():
    if not st.session_state.logged_in:
        login_screen()
        return

    st.markdown(load_css(), unsafe_allow_html=True)
    top_bar()
    sidebar_menu()

    service = st.session_state.selected_service
    if service == "لوحة القيادة التنفيذية":
        render_dashboard()
    elif service == "إدارة الصكوك والوثائق":
        render_deeds()
    elif service == "التحليلات المالية":
        render_financial()
    elif service == "الذكاء المكاني والخرائط":
        render_spatial()
    elif service == "نموذج التقييم الآلي AVM":
        render_avm()
    elif service == "الصيانة التنبؤية":
        render_maintenance()
    elif service == "ذكاء السوق والاستثمار":
        render_market()
    elif service == "إدارة العقود والمستأجرين":
        render_contracts()
    elif service == "التنبؤ بالأسعار (AI)":
        render_forecast()
    elif service == "تحليل المحفظة الاستثمارية":
        render_portfolio()
    elif service == "الامتثال القانوني والتراخيص":
        render_compliance()
    elif service == "لوحة تحكم المخاطر":
        render_risk()
    elif service == "التقارير الذكية القابلة للتخصيص":
        render_reports()
    elif service == "مركز التنبيهات والإشعارات":
        render_notifications()
    else:
        render_dashboard()

if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import random
import io
import base64
from streamlit_autorefresh import st_autorefresh
# ==========================================
# ⚙️ إعدادات الصفحة - يجب أن تكون أول أمر
# ==========================================
st.set_page_config(
    layout="wide",
    page_title="Drones Crafters Enterprise – Real Estate Management",
    page_icon="🏢",
    initial_sidebar_state="expanded"
)
# ==========================================
# 🎨 CSS احترافي (دعم الوضع المظلم والفاتح والتبديل)
# ==========================================
def load_css(dark_mode=False):
    bg_color = "#0e1117" if dark_mode else "#ffffff"
    text_color = "#ffffff" if dark_mode else "#000000"
    card_bg = "#1e1e2f" if dark_mode else "#f8f9fa"
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [data-testid="stSidebar"], .main, .stMarkdown {{
        direction: RTL !important;
        text-align: right !important;
        font-family: 'Cairo', sans-serif !important;
        background-color: {bg_color};
        color: {text_color};
    }}
    div[data-testid="stMetric"] {{
        background-color: {card_bg};
        padding: 20px;
        border-radius: 15px;
        border-right: 5px solid #1E3A8A;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: 0.3s;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-5px);
    }}
    .stButton>button {{
        background: linear-gradient(90deg, #1E3A8A, #3B82F6);
        color: white;
        border-radius: 12px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        transform: scale(1.02);
        background: linear-gradient(90deg, #1E3A8A, #2563EB);
    }}
    .css-1d391kg {{
        background-color: {card_bg};
    }}
    </style>
    """
# ==========================================
# 🧠 إدارة الحالة المتقدمة (محاكاة قاعدة بيانات متعددة الجهات)
# ==========================================
class RealEstateDB:
    """محاكاة قاعدة بيانات علائقية مع دعم متعدد الجهات والمستخدمين"""
    @staticmethod
    def init_session():
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
                        "الأسبوع": [f"الأسبوع {i}" for i in range(1,14)],
                        "تكلفة الصيانة": np.random.randint(200000, 600000, 13),
                        "تكلفة الإدارة": np.random.randint(150000, 400000, 13),
                        "اسم الأصل": [f"أصل {i}" for i in range(1,14)]
                    }),
                    "financial": pd.DataFrame({
                        "السنة": [2021,2022,2023,2024],
                        "الإيرادات": [12e6,14.5e6,16.2e6,18e6],
                        "المصاريف التشغيلية": [4e6,4.5e6,5e6,5.4e6],
                        "صيانة": [1.2e6,1.35e6,1.5e6,1.65e6]
                    }),
                    "alerts": [
                        {"date": "2024-12-15", "message": "انتهاء رخصة تشغيل", "type": "warning"},
                        {"date": "2024-12-20", "message": "صيانة دورية مستحقة", "type": "info"}
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
        if 'current_tenant' not in st.session_state:
            st.session_state.current_tenant = "tenant_1"
        if 'users' not in st.session_state:
            st.session_state.users = {
                "admin@drones.com": {"password": "admin123", "role": "SuperAdmin", "tenant": None},
                "manager1@assets.com": {"password": "pass1", "role": "TenantAdmin", "tenant": "tenant_1"},
                "viewer1@assets.com": {"password": "view", "role": "Viewer", "tenant": "tenant_1"},
                "manager2@gulf.com": {"password": "pass2", "role": "TenantAdmin", "tenant": "tenant_2"}
            }
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.session_state.user_tenant = None
        if 'dark_mode' not in st.session_state:
            st.session_state.dark_mode = False
        if 'language' not in st.session_state:
            st.session_state.language = "ar"  # ar/en
        if 'selected_service' not in st.session_state:
            st.session_state.selected_service = "لوحة القيادة التنفيذية"
    @staticmethod
    def get_current_tenant_data():
        return st.session_state.tenants[st.session_state.current_tenant]
    @staticmethod
    def update_tenant_data(tenant_id, key, value):
        st.session_state.tenants[tenant_id][key] = value
# تهيئة قاعدة البيانات المحاكاة
RealEstateDB.init_session()
# ==========================================
# 🌐 نظام الترجمة (عربي/إنجليزي)
# ==========================================
translations = {
    "ar": {
        "dashboard": "لوحة القيادة التنفيذية",
        "deeds": "إدارة الصكوك والوثائق",
        "financial": "التحليلات المالية",
        "spatial": "الذكاء المكاني والخرائط",
        "avm": "نموذج التقييم الآلي AVM",
        "maintenance": "الصيانة التنبؤية",
        "market": "ذكاء السوق والاستثمار",
        "contracts": "إدارة العقود والمستأجرين",
        "forecast": "التنبؤ بالأسعار (AI)",
        "portfolio": "تحليل المحفظة الاستثمارية",
        "compliance": "الامتثال القانوني والتراخيص",
        "risk": "لوحة تحكم المخاطر",
        "reports": "التقارير الذكية",
        "notifications": "مركز التنبيهات",
        "logout": "تسجيل الخروج",
        "login": "تسجيل الدخول",
        "username": "البريد الإلكتروني",
        "password": "كلمة المرور",
        "total_assets": "إجمالي قيمة الأصول",
        "properties_count": "عدد العقارات",
        "avg_roi": "متوسط العائد السنوي",
        "occupancy": "نسبة الإشغال",
        "select_tenant": "اختر الجهة:"
    },
    "en": {
        "dashboard": "Executive Dashboard",
        "deeds": "Deeds & Documents",
        "financial": "Financial Analytics",
        "spatial": "Spatial Intelligence",
        "avm": "AVM Valuation",
        "maintenance": "Predictive Maintenance",
        "market": "Market Intelligence",
        "contracts": "Contracts & Tenants",
        "forecast": "Price Forecast (AI)",
        "portfolio": "Portfolio Analysis",
        "compliance": "Compliance & Licenses",
        "risk": "Risk Dashboard",
        "reports": "Smart Reports",
        "notifications": "Notifications Center",
        "logout": "Logout",
        "login": "Login",
        "username": "Email",
        "password": "Password",
        "total_assets": "Total Asset Value",
        "properties_count": "Properties Count",
        "avg_roi": "Avg. Annual Return",
        "occupancy": "Occupancy Rate",
        "select_tenant": "Select Tenant:"
    }
}
def t(key):
    return translations[st.session_state.language].get(key, key)
# ==========================================
# 🔐 نظام المصادقة والصلاحيات
# ==========================================
def login_screen():
    st.title("🏢 Drones Crafters Enterprise")
    st.subheader(t("login"))
    email = st.text_input(t("username"))
    password = st.text_input(t("password"), type="password")
    if st.button(t("login")):
        if email in st.session_state.users and st.session_state.users[email]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.user_role = st.session_state.users[email]["role"]
            st.session_state.user_tenant = st.session_state.users[email]["tenant"]
            if st.session_state.user_role == "SuperAdmin":
                st.session_state.current_tenant = "tenant_1"  # الافتراضي
            else:
                st.session_state.current_tenant = st.session_state.user_tenant
            st.rerun()
        else:
            st.error("بيانات الدخول غير صحيحة")
    st.markdown("---")
    st.caption("للتجربة: admin@drones.com / admin123  |  manager1@assets.com / pass1")
def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_tenant = None
    st.rerun()
# ==========================================
# شريط الأدوات العلوي (إعدادات، تبديل اللغة، الوضع المظلم، مستخدم)
# ==========================================
def top_bar():
    col1, col2, col3, col4, col5 = st.columns([3,1,1,1,1])
    with col1:
        st.markdown(f"### 🏢 {st.session_state.tenants[st.session_state.current_tenant]['name']}")
    with col2:
        if st.button("🌙" if not st.session_state.dark_mode else "☀️"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    with col3:
        lang = "🇸🇦 عربي" if st.session_state.language == "ar" else "🇬🇧 English"
        if st.button(lang):
            st.session_state.language = "en" if st.session_state.language == "ar" else "ar"
            st.rerun()
    with col4:
        st.markdown(f"👤 {st.session_state.user_role}")
    with col5:
        if st.button(t("logout")):
            logout()
# ==========================================
# القائمة الجانبية الديناميكية حسب الصلاحية والجهة
# ==========================================
def sidebar_menu():
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/10543/10543319.png", width=80)
        st.title("Drones Crafters")
        if st.session_state.user_role == "SuperAdmin":
            tenants_list = list(st.session_state.tenants.keys())
            selected_tenant = st.selectbox(t("select_tenant"), tenants_list, format_func=lambda x: st.session_state.tenants[x]["name"])
            if selected_tenant != st.session_state.current_tenant:
                st.session_state.current_tenant = selected_tenant
                st.rerun()
        st.divider()
        
        services = {
            "dashboard": t("dashboard"),
            "deeds": t("deeds"),
            "financial": t("financial"),
            "spatial": t("spatial"),
            "avm": t("avm"),
            "maintenance": t("maintenance"),
            "market": t("market"),
            "contracts": t("contracts"),
            "forecast": t("forecast"),
            "portfolio": t("portfolio"),
            "compliance": t("compliance"),
            "risk": t("risk"),
            "reports": t("reports"),
            "notifications": t("notifications")
        }
        # تحديد الخدمات المسموحة حسب الدور
        allowed = list(services.keys())
        if st.session_state.user_role == "Viewer":
            allowed = ["dashboard", "financial", "spatial", "market", "portfolio", "reports", "notifications"]
        
        choice = st.radio("الخدمات", [services[k] for k in allowed if k in services], 
                          index=0 if st.session_state.selected_service not in [services[k] for k in allowed] else [services[k] for k in allowed].index(st.session_state.selected_service))
        # تعيين المفتاح
        for k,v in services.items():
            if v == choice:
                st.session_state.selected_service = v
                break
        st.divider()
        st.caption(f"© 2025 Drones Crafters - v3.0 Enterprise")
# ==========================================
# 📈 المحتوى الرئيسي لكل خدمة (تم تطويره بشكل احترافي)
# ==========================================
def render_dashboard():
    data = RealEstateDB.get_current_tenant_data()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(t("total_assets"), f"{data['assets_value']/1e9:.1f} مليار ريال", "+4.2%")
    col2.metric(t("properties_count"), f"{data['properties_count']:,}", "+35")
    col3.metric(t("avg_roi"), "11.8%", "+0.6%")
    col4.metric(t("occupancy"), "89%", "-3.1%")
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(pd.DataFrame({"نوع العقار":["شقق","مكاتب","تجاري","صناعي","فلل"], "القيمة":[600,450,520,300,530]}), x="نوع العقار", y="القيمة", color="القيمة", color_continuous_scale="Blues", title="توزيع القيمة")
        fig.update_layout(font_family="Cairo")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        kpi_df = pd.DataFrame({"السنة":[2021,2022,2023,2024], "ROI":[8.5,9.2,10.1,10.8], "IRR":[10.2,10.9,11.3,11.8]})
        fig = px.line(kpi_df, x="السنة", y=["ROI","IRR"], markers=True, title="تطور العوائد")
        fig.update_layout(font_family="Cairo")
        st.plotly_chart(fig, use_container_width=True)
def render_deeds():
    data = RealEstateDB.get_current_tenant_data()
    edited = st.data_editor(data["deeds"], use_container_width=True, num_rows="dynamic")
    if st.button("💾 حفظ الصكوك"):
        RealEstateDB.update_tenant_data(st.session_state.current_tenant, "deeds", edited)
        st.success("تم الحفظ")
def render_financial():
    data = RealEstateDB.get_current_tenant_data()
    years = st.slider("نطاق السنوات", 2021, 2024, (2021,2024))
    df = data["financial"]
    df = df[(df["السنة"]>=years[0]) & (df["السنة"]<=years[1])]
    fig = px.bar(df, x="السنة", y=["الإيرادات","المصاريف التشغيلية","صيانة"], barmode="group", title="الإيرادات والمصاريف")
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("محاكاة استثمارية"):
        inv = st.number_input("الاستثمار الأولي (ريال)", value=10_000_000)
        rate = st.slider("معدل الخصم %", 5.0, 15.0, 9.0)
        cf = [inv*0.3]*5
        npv = sum(cf[i]/((1+rate/100)**(i+1)) for i in range(5)) - inv
        st.metric("NPV", f"{npv:,.0f} ريال")
def render_spatial():
    st.title(t("spatial"))
    districts = ["الملقا","الياسمين","النرجس","العمارية"]
    district = st.selectbox("الحي", districts)
    st.metric("متوسط سعر المتر", f"{np.random.randint(3500,6000):,} ريال")
    df_points = pd.DataFrame({
        "lat": [24.774265, 24.800000, 24.760000],
        "lon": [46.738586, 46.700000, 46.760000],
        "name": ["مبنى إداري", "مجمع تجاري", "أرض"]
    })
    fig = px.scatter_mapbox(df_points, lat="lat", lon="lon", hover_name="name", zoom=11)
    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig, use_container_width=True)
def render_avm():
    st.title(t("avm"))
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
    data = RealEstateDB.get_current_tenant_data()
    df = data["maintenance"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["الأسبوع"], y=df["تكلفة الصيانة"], name="تكلفة الصيانة"))
    fig.add_trace(go.Scatter(x=df["الأسبوع"], y=df["تكلفة الإدارة"], name="تكلفة الإدارة"))
    fig.add_hline(y=500000, line_dash="dash", line_color="red")
    st.plotly_chart(fig, use_container_width=True)
def render_market():
    st.title(t("market"))
    market_df = pd.DataFrame({"السنة":list(range(2020,2031)), "سكني":np.linspace(80,145,11), "تجاري":np.linspace(60,110,11), "صناعي":np.linspace(40,85,11)})
    fig = px.area(market_df, x="السنة", y=["سكني","تجاري","صناعي"], title="توقعات السوق")
    st.plotly_chart(fig, use_container_width=True)
    st.info("نمو متسارع متوقع في القطاع الصناعي")
def render_contracts():
    data = RealEstateDB.get_current_tenant_data()
    edited = st.data_editor(data["contracts"], use_container_width=True, num_rows="dynamic")
    if st.button("حفظ العقود"):
        RealEstateDB.update_tenant_data(st.session_state.current_tenant, "contracts", edited)
        st.success("تم الحفظ")
def render_forecast():
    st.title(t("forecast"))
    months = pd.date_range("2024-01-01", periods=12, freq='M')
    historical = [4200,4350,4450,4600,4750,4900,5100,5300,5450,5600,5750,5900]
    forecast = [6050,6200,6380,6550,6720,6900,7100,7300,7480,7650,7820,8000]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=historical, name="تاريخي"))
    fig.add_trace(go.Scatter(x=months, y=forecast, name="متوقع", line=dict(dash="dot")))
    st.plotly_chart(fig, use_container_width=True)
    st.metric("متوسط الزيادة المتوقعة", "7.2%")
def render_portfolio():
    port = pd.DataFrame({"القطاع":["سكني","تجاري","صناعي","مكاتب"], "القيمة":[450,320,280,410], "العائد":[8,10,12,9]})
    fig = px.pie(port, names="القطاع", values="القيمة", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)
    fig2 = px.scatter(port, x="العائد", y="القيمة", text="القطاع", size="القيمة")
    st.plotly_chart(fig2, use_container_width=True)
def render_compliance():
    st.title(t("compliance"))
    licenses = pd.DataFrame({
        "الترخيص":["رخصة بناء","رخصة تشغيل","دفاع مدني"],
        "تاريخ الانتهاء":["2025-06-01","2024-12-31","2024-10-20"],
        "الحالة":["ساري","ينتهي قريباً","منتهي"]
    })
    st.dataframe(licenses)
    if any(licenses["الحالة"]=="منتهي"):
        st.warning("يوجد تراخيص منتهية!")
def render_risk():
    risks = pd.DataFrame({"الخطر":["تقلبات السوق","مخاطر الائتمان","تشغيلية"], "الاحتمال":[35,25,45], "الأثر":[4,3,3]})
    risks["النقطة"] = risks["الاحتمال"] * risks["الأثر"]
    fig = px.bar(risks, x="الخطر", y="النقطة", color="النقطة", color_continuous_scale="Reds")
    st.plotly_chart(fig, use_container_width=True)
def render_reports():
    st.title(t("reports"))
    report_type = st.selectbox("نوع التقرير", ["ملخص المحفظة", "التحليل المالي", "حالة الصيانة"])
    if report_type == "ملخص المحفظة":
        st.dataframe(pd.DataFrame({"المؤشر":["الأصول","القيمة"], "القيمة":["1,280","2.4 مليار"]}))
    elif report_type == "التحليل المالي":
        data = RealEstateDB.get_current_tenant_data()
        st.line_chart(data["financial"].set_index("السنة")["الإيرادات"])
    else:
        data = RealEstateDB.get_current_tenant_data()
        st.bar_chart(data["maintenance"].set_index("الأسبوع")["تكلفة الصيانة"])
    # تصدير
    csv = RealEstateDB.get_current_tenant_data()["deeds"].to_csv().encode()
    st.download_button("تحميل CSV", csv, "report.csv")
def render_notifications():
    st.title(t("notifications"))
    data = RealEstateDB.get_current_tenant_data()
    alerts = pd.DataFrame(data.get("alerts", []))
    if not alerts.empty:
        st.dataframe(alerts)
    else:
        st.info("لا توجد إشعارات حالية")
    if st.button("تحديد الكل كمقروء"):
        st.success("تم")
# ==========================================
# 🚀 التطبيق الرئيسي مع تحديث تلقائي كل 60 ثانية
# ==========================================
def main():
    # تحديث تلقائي للبيانات الحية (كل 60 ثانية)
    st_autorefresh(interval=60000, key="auto_refresh")
    
    if not st.session_state.logged_in:
        login_screen()
        return
    # تطبيق الوضع المظلم
    st.markdown(load_css(st.session_state.dark_mode), unsafe_allow_html=True)
    top_bar()
    sidebar_menu()
    # عرض الخدمة المختارة
    service = st.session_state.selected_service
    if service == t("dashboard"):
        render_dashboard()
    elif service == t("deeds"):
        render_deeds()
    elif service == t("financial"):
        render_financial()
    elif service == t("spatial"):
        render_spatial()
    elif service == t("avm"):
        render_avm()
    elif service == t("maintenance"):
        render_maintenance()
    elif service == t("market"):
        render_market()
    elif service == t("contracts"):
        render_contracts()
    elif service == t("forecast"):
        render_forecast()
    elif service == t("portfolio"):
        render_portfolio()
    elif service == t("compliance"):
        render_compliance()
    elif service == t("risk"):
        render_risk()
    elif service == t("reports"):
        render_reports()
    elif service == t("notifications"):
        render_notifications()
    else:
        render_dashboard()
if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import time

# ==========================================
# إعدادات الصفحة
# ==========================================
st.set_page_config(layout="wide", page_title="Drones Crafters - Real Estate", page_icon="🏢")

# ==========================================
# تهيئة حالة الجلسة
# ==========================================
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'language' not in st.session_state:
    st.session_state.language = 'ar'
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'current_tenant' not in st.session_state:
    st.session_state.current_tenant = 'tenant_1'
if 'selected_service' not in st.session_state:
    st.session_state.selected_service = "لوحة القيادة التنفيذية"
if 'notifications' not in st.session_state:
    st.session_state.notifications = []
if 'filters' not in st.session_state:
    st.session_state.filters = {'year_range': (2021, 2024), 'district': 'الملقا'}

# ==========================================
# بيانات تجريبية ثابتة (محاكاة قاعدة بيانات)
# ==========================================
tenants_data = {
    "tenant_1": {
        "name": "شركة أصول الرياض",
        "assets_value": 2.4e9,
        "properties_count": 1280,
        "deeds": pd.DataFrame({"رقم الصك": ["123/أ","456/ب"], "المالك": ["شركة أصول الأولى","صندوق استثماري"], "الحي": ["الملقا","الياسمين"], "المساحة م²": [2500,4300], "الحالة": ["ساري","ساري"]}),
        "contracts": pd.DataFrame({"رقم العقد": ["C-101","C-102"], "المستأجر": ["شركة الأفق","مؤسسة البناء"], "القيمة الشهرية": [45000,28000], "تاريخ الانتهاء": ["2025-01-01","2025-03-14"]}),
        "maintenance": pd.DataFrame({"الأسبوع": [f"الأسبوع {i}" for i in range(1,14)], "تكلفة الصيانة": np.random.randint(200000,600000,13), "تكلفة الإدارة": np.random.randint(150000,400000,13), "اسم الأصل": [f"أصل {i}" for i in range(1,14)]}),
        "financial": pd.DataFrame({"السنة": [2021,2022,2023,2024], "الإيرادات": [12e6,14.5e6,16.2e6,18e6], "المصاريف التشغيلية": [4e6,4.5e6,5e6,5.4e6], "صيانة": [1.2e6,1.35e6,1.5e6,1.65e6]}),
        "alerts": [{"التاريخ":"2024-12-15","الرسالة":"انتهاء رخصة تشغيل","النوع":"تحذير"}]
    },
    "tenant_2": {
        "name": "مجموعة الخليج العقارية",
        "assets_value": 980e6,
        "properties_count": 540,
        "deeds": pd.DataFrame({"رقم الصك":["789/ج"],"المالك":["مجموعة الخليج"],"الحي":["النرجس"],"المساحة م²":[1800],"الحالة":["محدث"]}),
        "contracts": pd.DataFrame({"رقم العقد":["C-201"],"المستأجر":["شركة الخدمات"],"القيمة الشهرية":[32000],"تاريخ الانتهاء":["2025-06-01"]}),
        "maintenance": pd.DataFrame({"الأسبوع":[f"الأسبوع {i}" for i in range(1,8)], "تكلفة الصيانة":np.random.randint(100000,400000,7),"تكلفة الإدارة":np.random.randint(80000,200000,7),"اسم الأصل":[f"أصل {i}" for i in range(1,8)]}),
        "financial": pd.DataFrame({"السنة":[2021,2022,2023,2024],"الإيرادات":[5e6,6.2e6,7.1e6,8.5e6],"المصاريف التشغيلية":[1.8e6,2.1e6,2.4e6,2.9e6],"صيانة":[0.5e6,0.6e6,0.7e6,0.85e6]}),
        "alerts": []
    }
}
users_data = {
    "admin@drones.com": {"password": "admin123", "role": "SuperAdmin", "tenant": None},
    "manager1@assets.com": {"password": "pass1", "role": "TenantAdmin", "tenant": "tenant_1"},
    "viewer1@assets.com": {"password": "view", "role": "Viewer", "tenant": "tenant_1"},
}

# دمج البيانات مع session_state
if 'tenants' not in st.session_state:
    st.session_state.tenants = tenants_data
if 'users' not in st.session_state:
    st.session_state.users = users_data

# ==========================================
# دوال المساعدة
# ==========================================
def get_current_data():
    return st.session_state.tenants[st.session_state.current_tenant]

def add_notification(msg, typ="info"):
    st.session_state.notifications.insert(0, {"message": msg, "type": typ, "time": datetime.now().strftime("%H:%M:%S")})
    st.session_state.notifications = st.session_state.notifications[:20]

def t(ar, en=None):
    return ar if st.session_state.language == 'ar' else (en if en else ar)

def toggle_dark():
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()

def toggle_lang():
    st.session_state.language = 'en' if st.session_state.language == 'ar' else 'ar'
    st.rerun()

def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.rerun()

def refresh_data():
    # تحديث عشوائي لبيانات الصيانة
    for tid in st.session_state.tenants:
        df = st.session_state.tenants[tid]["maintenance"]
        df["تكلفة الصيانة"] = np.random.randint(200000, 600000, len(df))
        df["تكلفة الإدارة"] = np.random.randint(150000, 400000, len(df))
    add_notification("تم تحديث البيانات الحية", "success")
    st.rerun()

# ==========================================
# CSS
# ==========================================
def load_css():
    bg = "#0a0c10" if st.session_state.dark_mode else "#f4f6f9"
    card = "#1e1e2e" if st.session_state.dark_mode else "#ffffff"
    text = "#ffffff" if st.session_state.dark_mode else "#1e293b"
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    * {{ font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }}
    .stApp {{ background-color: {bg}; color: {text}; }}
    div[data-testid="stMetric"] {{
        background: {card};
        padding: 1rem;
        border-radius: 1rem;
        border-right: 5px solid #3b82f6;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    .stButton>button {{
        background-color: #1e3a8a;
        color: white;
        border-radius: 8px;
    }}
    </style>
    """

# ==========================================
# شاشة تسجيل الدخول
# ==========================================
def login_screen():
    st.title("🏢 Drones Crafters")
    email = st.text_input("البريد الإلكتروني")
    pwd = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if email in st.session_state.users and st.session_state.users[email]["password"] == pwd:
            st.session_state.logged_in = True
            st.session_state.user_role = st.session_state.users[email]["role"]
            st.session_state.current_tenant = st.session_state.users[email]["tenant"] if st.session_state.users[email]["tenant"] else "tenant_1"
            st.rerun()
        else:
            st.error("بيانات غير صحيحة")
    st.caption("Demo: admin@drones.com / admin123   |   manager1@assets.com / pass1")

# ==========================================
# شريط علوي
# ==========================================
def top_bar():
    col1, col2, col3, col4, col5 = st.columns([2,1,1,1,1])
    with col1:
        st.markdown(f"### 🏢 {st.session_state.tenants[st.session_state.current_tenant]['name']}")
    with col2:
        st.button("🌙" if not st.session_state.dark_mode else "☀️", on_click=toggle_dark)
    with col3:
        st.button("🇸🇦" if st.session_state.language=='ar' else "🇬🇧", on_click=toggle_lang)
    with col4:
        unread = len([n for n in st.session_state.notifications if not n.get('read', False)])
        if st.button(f"🔔 {unread}" if unread else "🔔"):
            st.session_state.show_notif = not st.session_state.get('show_notif', False)
    with col5:
        st.button("🚪 خروج", on_click=logout)
    if st.session_state.get('show_notif', False):
        with st.expander("الإشعارات", expanded=True):
            for n in st.session_state.notifications[:10]:
                st.write(f"**{n['time']}** - {n['message']}")

# ==========================================
# القائمة الجانبية
# ==========================================
def sidebar_menu():
    with st.sidebar:
        st.title("Drones Crafters")
        if st.session_state.user_role == "SuperAdmin":
            tenants = list(st.session_state.tenants.keys())
            sel = st.selectbox("الجهة", tenants, format_func=lambda x: st.session_state.tenants[x]["name"])
            if sel != st.session_state.current_tenant:
                st.session_state.current_tenant = sel
                st.rerun()
        st.divider()
        services = [
            "لوحة القيادة التنفيذية", "إدارة الصكوك والوثائق", "التحليلات المالية",
            "الذكاء المكاني والخرائط", "نموذج التقييم الآلي AVM", "الصيانة التنبؤية",
            "ذكاء السوق والاستثمار", "إدارة العقود والمستأجرين", "التنبؤ بالأسعار (AI)",
            "تحليل المحفظة الاستثمارية", "الامتثال القانوني والتراخيص", "لوحة تحكم المخاطر",
            "التقارير الذكية", "مركز التنبيهات والإشعارات"
        ]
        choice = st.radio("الخدمات", services, index=services.index(st.session_state.selected_service))
        st.session_state.selected_service = choice
        if st.button("🔄 تحديث البيانات"):
            refresh_data()
        st.caption("© 2025 Drones Crafters")

# ==========================================
# وظائف الخدمات (جميعها تعمل)
# ==========================================
def render_dashboard():
    data = get_current_data()
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("إجمالي الأصول", f"{data['assets_value']/1e9:.1f} مليار")
    c2.metric("عدد العقارات", f"{data['properties_count']:,}")
    c3.metric("متوسط العائد", "11.8%")
    c4.metric("نسبة الإشغال", "89%")
    st.divider()
    df = pd.DataFrame({"نوع العقار": ["شقق","مكاتب","تجاري","صناعي","فلل"], "القيمة": [600,450,520,300,530]})
    fig = px.bar(df, x="نوع العقار", y="القيمة", color="القيمة")
    st.plotly_chart(fig, use_container_width=True)

def render_deeds():
    data = get_current_data()
    edited = st.data_editor(data["deeds"], use_container_width=True, num_rows="dynamic")
    if st.button("حفظ"):
        st.session_state.tenants[st.session_state.current_tenant]["deeds"] = edited
        st.success("تم الحفظ")

def render_financial():
    data = get_current_data()
    yr = st.slider("نطاق السنوات", 2021, 2024, st.session_state.filters['year_range'])
    df = data["financial"][(data["financial"]["السنة"]>=yr[0]) & (data["financial"]["السنة"]<=yr[1])]
    fig = px.bar(df, x="السنة", y=["الإيرادات","المصاريف التشغيلية","صيانة"], barmode="group")
    st.plotly_chart(fig, use_container_width=True)

def render_spatial():
    st.subheader("الخريطة التفاعلية")
    points = pd.DataFrame({"lat":[24.774,24.800,24.760],"lon":[46.738,46.700,46.760],"name":["مبنى","مجمع","أرض"]})
    fig = px.scatter_mapbox(points, lat="lat", lon="lon", hover_name="name", zoom=11)
    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig, use_container_width=True)

def render_avm():
    with st.form("avm"):
        area = st.number_input("المساحة م²", 50, 10000, 250)
        quality = st.selectbox("الجودة", ["اقتصادي","متوسط","فاخر"])
        if st.form_submit_button("تقدير"):
            base = 4500
            factor = {"اقتصادي":0.9,"متوسط":1.0,"فاخر":1.15}[quality]
            price = base * factor * area
            st.success(f"القيمة: {price:,.0f} ريال")

def render_maintenance():
    data = get_current_data()
    df = data["maintenance"]
    fig = px.line(df, x="الأسبوع", y=["تكلفة الصيانة","تكلفة الإدارة"], markers=True)
    st.plotly_chart(fig, use_container_width=True)

def render_market():
    market = pd.DataFrame({"السنة":range(2020,2031),"سكني":np.linspace(80,145,11),"تجاري":np.linspace(60,110,11)})
    fig = px.area(market, x="السنة", y=["سكني","تجاري"])
    st.plotly_chart(fig, use_container_width=True)

def render_contracts():
    data = get_current_data()
    edited = st.data_editor(data["contracts"], use_container_width=True, num_rows="dynamic")
    if st.button("حفظ العقود"):
        st.session_state.tenants[st.session_state.current_tenant]["contracts"] = edited
        st.success("تم")

def render_forecast():
    months = pd.date_range("2024-01-01", periods=12, freq='M')
    hist = [4200,4350,4450,4600,4750,4900,5100,5300,5450,5600,5750,5900]
    fcast = [6050,6200,6380,6550,6720,6900,7100,7300,7480,7650,7820,8000]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=hist, name="تاريخي"))
    fig.add_trace(go.Scatter(x=months, y=fcast, name="متوقع", line=dict(dash="dot")))
    st.plotly_chart(fig, use_container_width=True)

def render_portfolio():
    port = pd.DataFrame({"القطاع":["سكني","تجاري","صناعي"], "القيمة":[450,320,280]})
    fig = px.pie(port, names="القطاع", values="القيمة", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

def render_compliance():
    lic = pd.DataFrame({"الترخيص":["رخصة بناء","رخصة تشغيل"], "تاريخ الانتهاء":["2025-06-01","2024-12-31"], "الحالة":["ساري","ينتهي قريباً"]})
    st.dataframe(lic)

def render_risk():
    risks = pd.DataFrame({"الخطر":["سوق","ائتمان","تشغيل"], "النقطة":[140,75,135]})
    fig = px.bar(risks, x="الخطر", y="النقطة")
    st.plotly_chart(fig, use_container_width=True)

def render_reports():
    typ = st.selectbox("نوع التقرير", ["ملخص", "مالي"])
    if typ == "ملخص":
        st.dataframe(pd.DataFrame({"المؤشر":["الأصول"], "القيمة":["1,280"]}))
    else:
        st.line_chart(get_current_data()["financial"].set_index("السنة")["الإيرادات"])
    csv = get_current_data()["deeds"].to_csv().encode()
    st.download_button("تحميل CSV", csv, "report.csv")

def render_notifications():
    data = get_current_data()
    alerts = pd.DataFrame(data.get("alerts", []))
    if not alerts.empty:
        st.dataframe(alerts)
    else:
        st.info("لا توجد إشعارات")

# ==========================================
# التشغيل الرئيسي
# ==========================================
def main():
    if not st.session_state.logged_in:
        login_screen()
        return
    st.markdown(load_css(), unsafe_allow_html=True)
    top_bar()
    sidebar_menu()
    service = st.session_state.selected_service
    mapping = {
        "لوحة القيادة التنفيذية": render_dashboard,
        "إدارة الصكوك والوثائق": render_deeds,
        "التحليلات المالية": render_financial,
        "الذكاء المكاني والخرائط": render_spatial,
        "نموذج التقييم الآلي AVM": render_avm,
        "الصيانة التنبؤية": render_maintenance,
        "ذكاء السوق والاستثمار": render_market,
        "إدارة العقود والمستأجرين": render_contracts,
        "التنبؤ بالأسعار (AI)": render_forecast,
        "تحليل المحفظة الاستثمارية": render_portfolio,
        "الامتثال القانوني والتراخيص": render_compliance,
        "لوحة تحكم المخاطر": render_risk,
        "التقارير الذكية": render_reports,
        "مركز التنبيهات والإشعارات": render_notifications,
    }
    mapping.get(service, render_dashboard)()

if __name__ == "__main__":
    main()

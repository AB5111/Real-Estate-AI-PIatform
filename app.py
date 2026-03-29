import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import time
import io
import base64
from sklearn.linear_model import LinearRegression  # نموذج بسيط للتنبؤ

# ==========================================
# إعدادات الصفحة - متقدمة
# ==========================================
st.set_page_config(
    layout="wide",
    page_title="Drones Crafters - Real Estate Enterprise Suite",
    page_icon="🏢",
    initial_sidebar_state="expanded"
)

# ==========================================
# تهيئة الحالة المتقدمة
# ==========================================
def init_session():
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
    if 'filters' not in st.session_state:
        st.session_state.filters = {'year_range': (2021,2024), 'district': 'الملقا', 'asset': 'الكل'}
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []
    if 'fullscreen_map' not in st.session_state:
        st.session_state.fullscreen_map = False
    if 'maintenance_prediction' not in st.session_state:
        st.session_state.maintenance_prediction = None

init_session()

# ==========================================
# بيانات تجريبية (محاكاة قاعدة بيانات)
# ==========================================
@st.cache_data(ttl=3600)
def load_tenant_data():
    return {
        "tenant_1": {
            "name": "شركة أصول الرياض", "plan": "Enterprise", "properties_count": 1280, "assets_value": 2.4e9,
            "deeds": pd.DataFrame({"رقم الصك": ["123/أ","456/ب"], "المالك": ["شركة أصول الأولى","صندوق استثماري"], "الحي": ["الملقا","الياسمين"], "المساحة م²": [2500,4300], "الحالة": ["ساري","ساري"]}),
            "contracts": pd.DataFrame({"رقم العقد": ["C-101","C-102"], "المستأجر": ["شركة الأفق","مؤسسة البناء"], "القيمة الشهرية": [45000,28000], "تاريخ الانتهاء": ["2025-01-01","2025-03-14"]}),
            "maintenance": pd.DataFrame({"الأسبوع": [f"الأسبوع {i}" for i in range(1,14)], "تكلفة الصيانة": np.random.randint(200000,600000,13), "تكلفة الإدارة": np.random.randint(150000,400000,13), "اسم الأصل": [f"أصل {i}" for i in range(1,14)]}),
            "financial": pd.DataFrame({"السنة": [2021,2022,2023,2024], "الإيرادات": [12e6,14.5e6,16.2e6,18e6], "المصاريف التشغيلية": [4e6,4.5e6,5e6,5.4e6], "صيانة": [1.2e6,1.35e6,1.5e6,1.65e6]}),
            "alerts": [{"التاريخ":"2024-12-15","الرسالة":"انتهاء رخصة تشغيل","النوع":"تحذير","مقروء":False},{"التاريخ":"2024-12-20","الرسالة":"صيانة دورية مستحقة","النوع":"تنبيه","مقروء":False}]
        },
        "tenant_2": {
            "name": "مجموعة الخليج العقارية", "plan": "Professional", "properties_count": 540, "assets_value": 980e6,
            "deeds": pd.DataFrame({"رقم الصك":["789/ج"],"المالك":["مجموعة الخليج"],"الحي":["النرجس"],"المساحة م²":[1800],"الحالة":["محدث"]}),
            "contracts": pd.DataFrame({"رقم العقد":["C-201"],"المستأجر":["شركة الخدمات"],"القيمة الشهرية":[32000],"تاريخ الانتهاء":["2025-06-01"]}),
            "maintenance": pd.DataFrame({"الأسبوع":[f"الأسبوع {i}" for i in range(1,8)], "تكلفة الصيانة":np.random.randint(100000,400000,7),"تكلفة الإدارة":np.random.randint(80000,200000,7),"اسم الأصل":[f"أصل {i}" for i in range(1,8)]}),
            "financial": pd.DataFrame({"السنة":[2021,2022,2023,2024],"الإيرادات":[5e6,6.2e6,7.1e6,8.5e6],"المصاريف التشغيلية":[1.8e6,2.1e6,2.4e6,2.9e6],"صيانة":[0.5e6,0.6e6,0.7e6,0.85e6]}),
            "alerts": []
        }
    }

@st.cache_data(ttl=3600)
def load_users():
    return {
        "admin@drones.com": {"password": "admin123", "role": "SuperAdmin", "tenant": None},
        "manager1@assets.com": {"password": "pass1", "role": "TenantAdmin", "tenant": "tenant_1"},
        "viewer1@assets.com": {"password": "view", "role": "Viewer", "tenant": "tenant_1"},
        "manager2@gulf.com": {"password": "pass2", "role": "TenantAdmin", "tenant": "tenant_2"}
    }

# تحميل البيانات المخزنة مؤقتاً
tenants_data = load_tenant_data()
users_data = load_users()

# دمج مع session_state للتعديل
if 'tenants' not in st.session_state:
    st.session_state.tenants = tenants_data
if 'users' not in st.session_state:
    st.session_state.users = users_data

# ==========================================
# دوال مساعدة متقدمة
# ==========================================
def get_current_data():
    return st.session_state.tenants[st.session_state.current_tenant]

def update_tenant_data(key, value):
    st.session_state.tenants[st.session_state.current_tenant][key] = value
    add_notification(f"تم تحديث {key}", "success")

def add_notification(msg, typ="info"):
    st.session_state.notifications.insert(0, {"message": msg, "type": typ, "timestamp": datetime.now().strftime("%H:%M:%S"), "read": False})
    st.session_state.notifications = st.session_state.notifications[:20]

def t(ar, en=None):
    return ar if st.session_state.language=='ar' else (en if en else ar)

def toggle_dark():
    st.session_state.dark_mode = not st.session_state.dark_mode
    add_notification(f"المظهر: {'مظلم' if st.session_state.dark_mode else 'فاتح'}", "info")
    st.rerun()

def toggle_lang():
    st.session_state.language = 'en' if st.session_state.language=='ar' else 'ar'
    add_notification(f"اللغة: {'English' if st.session_state.language=='en' else 'العربية'}", "info")
    st.rerun()

def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_tenant = None
    add_notification("تم تسجيل الخروج", "info")

def refresh_live_data():
    """تحديث البيانات الحية (محاكاة)"""
    for tid in st.session_state.tenants:
        df = st.session_state.tenants[tid]["maintenance"]
        df["تكلفة الصيانة"] = np.random.randint(200000, 600000, len(df))
        df["تكلفة الإدارة"] = np.random.randint(150000, 400000, len(df))
    add_notification("تم تحديث البيانات الحية", "success")
    st.rerun()

def predict_maintenance_cost(weeks_ahead=4):
    """نموذج تنبؤ بسيط باستخدام LinearRegression"""
    data = get_current_data()["maintenance"]
    X = np.arange(len(data)).reshape(-1,1)
    y = data["تكلفة الصيانة"].values
    model = LinearRegression().fit(X, y)
    future_X = np.arange(len(data), len(data)+weeks_ahead).reshape(-1,1)
    pred = model.predict(future_X)
    return pred

# ==========================================
# CSS احترافي مع أنيميشن
# ==========================================
def load_css():
    bg = "#0a0c10" if st.session_state.dark_mode else "#f4f6f9"
    card_bg = "#1e1e2e" if st.session_state.dark_mode else "#ffffff"
    text = "#ffffff" if st.session_state.dark_mode else "#1e293b"
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    * {{ font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }}
    .stApp {{ background-color: {bg}; color: {text}; }}
    div[data-testid="stMetric"] {{
        background: linear-gradient(135deg, {card_bg}, {card_bg}dd);
        padding: 1.2rem;
        border-radius: 1.5rem;
        border-right: 5px solid #3b82f6;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-5px);
        box-shadow: 0 12px 28px rgba(0,0,0,0.15);
    }}
    .stButton>button {{
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        border: none;
        border-radius: 12px;
        padding: 0.5rem 1rem;
        font-weight: 700;
        color: white;
        transition: all 0.2s;
    }}
    .stButton>button:hover {{
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(59,130,246,0.4);
    }}
    .stDataFrame, .stTable {{
        border-radius: 1rem;
        overflow: hidden;
    }}
    </style>
    """

# ==========================================
# شاشة تسجيل الدخول المتطورة
# ==========================================
def login_screen():
    st.markdown("<style>.login-container{display:flex;justify-content:center;align-items:center;height:80vh;}</style>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/10543/10543319.png", width=120)
        st.title("🏢 Drones Crafters")
        st.caption("Real Estate Enterprise Asset Management")
        email = st.text_input(t("البريد الإلكتروني", "Email"))
        pwd = st.text_input(t("كلمة المرور", "Password"), type="password")
        if st.button(t("دخول", "Login"), use_container_width=True):
            if email in st.session_state.users and st.session_state.users[email]["password"] == pwd:
                st.session_state.logged_in = True
                st.session_state.user_role = st.session_state.users[email]["role"]
                st.session_state.user_tenant = st.session_state.users[email]["tenant"]
                st.session_state.current_tenant = st.session_state.user_tenant if st.session_state.user_role != "SuperAdmin" else "tenant_1"
                add_notification(f"مرحباً {email}", "success")
                st.rerun()
            else:
                st.error(t("بيانات غير صحيحة", "Invalid credentials"))
        st.markdown("---")
        st.caption("Demo: admin@drones.com / admin123   |   manager1@assets.com / pass1")

# ==========================================
# شريط علوي مع إحصائيات سريعة
# ==========================================
def top_bar():
    col1, col2, col3, col4, col5, col6 = st.columns([2.5,1,1,1,1,1])
    with col1:
        st.markdown(f"### 🏢 {st.session_state.tenants[st.session_state.current_tenant]['name']}")
    with col2:
        st.caption(f"🕒 {datetime.now().strftime('%H:%M:%S')}")
    with col3:
        st.button("🌙" if not st.session_state.dark_mode else "☀️", on_click=toggle_dark)
    with col4:
        st.button("🇸🇦" if st.session_state.language=='ar' else "🇬🇧", on_click=toggle_lang)
    with col5:
        unread = sum(1 for n in st.session_state.notifications if not n.get("read", False))
        if st.button(f"🔔 {unread}" if unread else "🔔"):
            st.session_state.show_notif = not st.session_state.get("show_notif", False)
    with col6:
        st.markdown(f"👤 {st.session_state.user_role}")
    if st.session_state.get("show_notif", False):
        with st.expander("📢 الإشعارات", expanded=True):
            for n in st.session_state.notifications[:10]:
                st.markdown(f"**{n['timestamp']}** - {n['message']}")
            if st.button("تحديد الكل كمقروء"):
                for n in st.session_state.notifications:
                    n["read"] = True
                st.rerun()

# ==========================================
# القائمة الجانبية مع بحث متقدم
# ==========================================
def sidebar_menu():
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/10543/10543319.png", width=80)
        st.title("Drones Crafters")
        if st.session_state.user_role == "SuperAdmin":
            tenants = list(st.session_state.tenants.keys())
            sel = st.selectbox("اختر الجهة", tenants, format_func=lambda x: st.session_state.tenants[x]["name"])
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
        search = st.text_input("🔍 بحث", placeholder="اسم الخدمة")
        if search:
            services = [s for s in services if search in s]
        if st.session_state.user_role == "Viewer":
            services = services[:7] + [services[9], services[12], services[13]]
        choice = st.radio("الخدمات", services, index=services.index(st.session_state.selected_service) if st.session_state.selected_service in services else 0)
        st.session_state.selected_service = choice
        st.divider()
        if st.button("🔄 تحديث البيانات الحية", use_container_width=True):
            refresh_live_data()
        st.caption("© 2025 Drones Crafters - Enterprise v5.0")

# ==========================================
# مكونات متقدمة (Gauge, تنبؤ)
# ==========================================
def create_gauge(value, title, min_val=0, max_val=100):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 20}},
        gauge={"axis": {"range": [min_val, max_val]}, "bar": {"color": "#3b82f6"},
               "steps": [{"range": [0, 50], "color": "#ef4444"}, {"range": [50, 80], "color": "#eab308"}, {"range": [80, 100], "color": "#22c55e"}],
               "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.75, "value": value}}))
    fig.update_layout(height=250, margin=dict(l=20,r=20,t=40,b=20))
    return fig

# ==========================================
# وظائف الخدمات الأربعة عشر (كل خدمة محسنة لأقصى حد)
# ==========================================
def render_dashboard():
    data = get_current_data()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 إجمالي الأصول", f"{data['assets_value']/1e9:.1f} مليار", "+4.2%")
    col2.metric("🏢 عدد العقارات", f"{data['properties_count']:,}", "+35")
    col3.metric("📈 متوسط العائد", "11.8%", "+0.6%")
    col4.metric("🏠 الإشغال", "89%", "-3.1%")
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        df = pd.DataFrame({"نوع العقار": ["شقق","مكاتب","تجاري","صناعي","فلل"], "القيمة": [600,450,520,300,530]})
        fig = px.bar(df, x="نوع العقار", y="القيمة", color="القيمة", color_continuous_scale="Blues", title="توزيع القيمة")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        kpi = pd.DataFrame({"السنة":[2021,2022,2023,2024],"ROI":[8.5,9.2,10.1,10.8],"IRR":[10.2,10.9,11.3,11.8]})
        fig = px.line(kpi, x="السنة", y=["ROI","IRR"], markers=True, title="العوائد")
        st.plotly_chart(fig, use_container_width=True)

def render_deeds():
    data = get_current_data()
    st.subheader("📜 إدارة الصكوك")
    edited = st.data_editor(data["deeds"], use_container_width=True, num_rows="dynamic")
    if st.button("💾 حفظ"):
        update_tenant_data("deeds", edited)
        st.success("تم الحفظ")

def render_financial():
    data = get_current_data()
    yr = st.slider("نطاق السنوات", 2021, 2024, st.session_state.filters['year_range'])
    df = data["financial"][(data["financial"]["السنة"]>=yr[0]) & (data["financial"]["السنة"]<=yr[1])]
    fig = px.bar(df, x="السنة", y=["الإيرادات","المصاريف التشغيلية","صيانة"], barmode="group", title="الإيرادات والمصاريف")
    st.plotly_chart(fig, use_container_width=True)
    # Gauge لصافي الربح
    net_profit = df["الإيرادات"].sum() - df["المصاريف التشغيلية"].sum() - df["صيانة"].sum()
    st.plotly_chart(create_gauge(min(100, net_profit/1e6), "صافي الربح (مليون)", 0, 100), use_container_width=True)

def render_spatial():
    st.subheader("🗺️ الذكاء المكاني")
    district = st.selectbox("الحي", ["الملقا","الياسمين","النرجس","العمارية"], index=["الملقا","الياسمين","النرجس","العمارية"].index(st.session_state.filters['district']))
    st.session_state.filters['district'] = district
    points = pd.DataFrame({"lat":[24.774265,24.800000,24.760000,24.820000],"lon":[46.738586,46.700000,46.760000,46.680000],"name":["مبنى إداري","مجمع تجاري","أرض خام","مستودع"],"value":[4.2,7.8,5.1,3.1]})
    fig = px.scatter_mapbox(points, lat="lat", lon="lon", hover_name="name", size="value", zoom=11, title="مواقع الأصول")
    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig, use_container_width=True)
    if st.button("🗺️ ملء الشاشة"):
        st.session_state.fullscreen_map = not st.session_state.fullscreen_map
        st.rerun()

def render_avm():
    st.subheader("🤖 التقييم الآلي AVM")
    with st.form("avm"):
        col1,col2=st.columns(2)
        with col1:
            area=st.number_input("المساحة م²",50,10000,250)
            district=st.selectbox("الحي",["الملقا","الياسمين","النرجس","العمارية"])
        with col2:
            quality=st.selectbox("الجودة",["اقتصادي","متوسط","فاخر"])
            age=st.slider("العمر (سنوات)",0,50,5)
        if st.form_submit_button("تقدير"):
            base=np.random.randint(3500,6000)
            factor={"اقتصادي":0.9,"متوسط":1.0,"فاخر":1.15}[quality]
            price=base*factor*(1-age*0.01)*area
            st.success(f"### القيمة: {price:,.0f} ريال")
            st.metric("سعر المتر", f"{price/area:,.0f} ريال/م²")

def render_maintenance():
    data = get_current_data()
    st.subheader("🛠️ الصيانة التنبؤية")
    asset = st.selectbox("الأصل", ["الكل"]+list(data["maintenance"]["اسم الأصل"].unique()))
    df = data["maintenance"] if asset=="الكل" else data["maintenance"][data["maintenance"]["اسم الأصل"]==asset]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["الأسبوع"], y=df["تكلفة الصيانة"], name="الصيانة", mode='lines+markers'))
    fig.add_trace(go.Scatter(x=df["الأسبوع"], y=df["تكلفة الإدارة"], name="الإدارة", mode='lines+markers'))
    fig.add_hline(y=500000, line_dash="dash", line_color="red")
    st.plotly_chart(fig, use_container_width=True)
    # تنبؤ
    if st.button("🔮 توقع التكلفة للأربع أسابيع القادمة"):
        pred = predict_maintenance_cost(4)
        st.line_chart(pred)
        st.session_state.maintenance_prediction = pred

def render_market():
    st.subheader("📈 ذكاء السوق")
    market = pd.DataFrame({"السنة":list(range(2020,2031)),"سكني":np.linspace(80,145,11),"تجاري":np.linspace(60,110,11),"صناعي":np.linspace(40,85,11)})
    sectors = st.multiselect("القطاعات", ["سكني","تجاري","صناعي"], default=["سكني","تجاري","صناعي"])
    fig = px.area(market, x="السنة", y=sectors, title="توقعات النمو")
    st.plotly_chart(fig, use_container_width=True)
    st.info("💡 نصيحة: القطاع الصناعي الأسرع نمواً (CAGR 7.8%)")

def render_contracts():
    data = get_current_data()
    st.subheader("👥 العقود والمستأجرين")
    edited = st.data_editor(data["contracts"], use_container_width=True, num_rows="dynamic")
    if st.button("حفظ العقود"):
        update_tenant_data("contracts", edited)

def render_forecast():
    st.subheader("📈 التنبؤ بالأسعار (AI)")
    months = pd.date_range("2024-01-01", periods=12, freq='M')
    hist = [4200,4350,4450,4600,4750,4900,5100,5300,5450,5600,5750,5900]
    fcast = [6050,6200,6380,6550,6720,6900,7100,7300,7480,7650,7820,8000]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=hist, name="تاريخي"))
    fig.add_trace(go.Scatter(x=months, y=fcast, name="متوقع", line=dict(dash="dot")))
    st.plotly_chart(fig, use_container_width=True)
    st.metric("متوسط الزيادة المتوقعة", "7.2%")

def render_portfolio():
    st.subheader("📊 تحليل المحفظة")
    port = pd.DataFrame({"القطاع":["سكني","تجاري","صناعي","مكاتب"], "القيمة":[450,320,280,410], "العائد":[8,10,12,9]})
    fig = px.pie(port, names="القطاع", values="القيمة", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)
    fig2 = px.scatter(port, x="العائد", y="القيمة", text="القطاع", size="القيمة")
    st.plotly_chart(fig2, use_container_width=True)

def render_compliance():
    st.subheader("⚖️ الامتثال القانوني")
    lic = pd.DataFrame({"الترخيص":["رخصة بناء","رخصة تشغيل","دفاع مدني"], "تاريخ الانتهاء":["2025-06-01","2024-12-31","2024-10-20"], "الحالة":["ساري","ينتهي قريباً","منتهي"]})
    st.dataframe(lic)
    if any(lic["الحالة"]=="منتهي"):
        st.warning("تراخيص منتهية! يرجى التجديد")

def render_risk():
    st.subheader("⚠️ لوحة المخاطر")
    risks = pd.DataFrame({"الخطر":["تقلبات السوق","ائتمان","تشغيلية"], "الاحتمال":[35,25,45], "الأثر":[4,3,3]})
    risks["النقطة"] = risks["الاحتمال"] * risks["الأثر"]
    fig = px.bar(risks, x="الخطر", y="النقطة", color="النقطة", color_continuous_scale="Reds")
    st.plotly_chart(fig, use_container_width=True)

def render_reports():
    st.subheader("📑 التقارير الذكية")
    typ = st.selectbox("نوع التقرير", ["ملخص المحفظة", "التحليل المالي", "الصيانة"])
    if typ == "ملخص المحفظة":
        st.dataframe(pd.DataFrame({"المؤشر":["الأصول","القيمة"], "القيمة":["1,280","2.4 مليار"]}))
    elif typ == "التحليل المالي":
        st.line_chart(get_current_data()["financial"].set_index("السنة")["الإيرادات"])
    else:
        st.bar_chart(get_current_data()["maintenance"].set_index("الأسبوع")["تكلفة الصيانة"])
    csv = get_current_data()["deeds"].to_csv().encode()
    st.download_button("تحميل CSV", csv, "report.csv")

def render_notifications():
    st.subheader("🔔 مركز التنبيهات")
    data = get_current_data()
    alerts = pd.DataFrame(data.get("alerts", []))
    if not alerts.empty:
        st.dataframe(alerts)
    else:
        st.info("لا توجد إشعارات")
    if st.button("إضافة إشعار تجريبي"):
        add_notification("إشعار جديد", "info")
        st.rerun()

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
    services_map = {
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
        "مركز التنبيهات والإشعارات": render_notifications
    }
    render_func = services_map.get(service, render_dashboard)
    render_func()

if __name__ == "__main__":
    main()

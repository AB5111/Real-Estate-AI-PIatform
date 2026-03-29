import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import time

# ==========================================
# إعدادات الصفحة (يجب أن تكون الأولى)
# ==========================================
st.set_page_config(
    layout="wide",
    page_title="Drones Crafters – Real Estate Interactive Dashboard",
    page_icon="🏢",
    initial_sidebar_state="expanded"
)

# ==========================================
# تهيئة حالة الجلسة (Session State) - متقدمة
# ==========================================
def init_session_state():
    # إعدادات الواجهة
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    if 'language' not in st.session_state:
        st.session_state.language = 'ar'
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []
    
    # حالة المستخدم
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
    
    # تفضيلات التفاعل
    if 'filters' not in st.session_state:
        st.session_state.filters = {
            'year_range': (2021, 2024),
            'selected_district': 'الملقا',
            'maintenance_asset': 'الكل'
        }
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now()
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = False

init_session_state()

# ==========================================
# بيانات المستخدمين والجهات (محاكاة قاعدة بيانات)
# ==========================================
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
                {"التاريخ": "2024-12-15", "الرسالة": "انتهاء رخصة تشغيل", "النوع": "تحذير", "مقروء": False},
                {"التاريخ": "2024-12-20", "الرسالة": "صيانة دورية مستحقة", "النوع": "تنبيه", "مقروء": False}
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
# دوال المساعدة المحسنة
# ==========================================
def get_current_data():
    return st.session_state.tenants[st.session_state.current_tenant]

def update_tenant_data(key, value):
    st.session_state.tenants[st.session_state.current_tenant][key] = value
    add_notification(f"تم تحديث {key} بنجاح", "success")

def add_notification(message, type="info"):
    st.session_state.notifications.insert(0, {
        "message": message,
        "type": type,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "read": False
    })
    # الاحتفاظ بآخر 20 إشعار فقط
    st.session_state.notifications = st.session_state.notifications[:20]

def t(text_ar, text_en=None):
    if text_en is None:
        text_en = text_ar
    return text_ar if st.session_state.language == 'ar' else text_en

def toggle_dark_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode
    add_notification(f"تم تغيير المظهر إلى {'المظلم' if st.session_state.dark_mode else 'الفاتح'}", "info")

def toggle_lang():
    st.session_state.language = 'en' if st.session_state.language == 'ar' else 'ar'
    add_notification(f"تم تغيير اللغة إلى {'الإنجليزية' if st.session_state.language == 'en' else 'العربية'}", "info")

def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_tenant = None
    st.session_state.notifications = []
    add_notification("تم تسجيل الخروج بنجاح", "info")

def refresh_data():
    """تحديث البيانات مع إعادة توليد أرقام عشوائية لمحاكاة البيانات الحية"""
    for tenant in st.session_state.tenants.values():
        tenant["maintenance"]["تكلفة الصيانة"] = np.random.randint(200000, 600000, len(tenant["maintenance"]))
        tenant["maintenance"]["تكلفة الإدارة"] = np.random.randint(150000, 400000, len(tenant["maintenance"]))
    st.session_state.last_update = datetime.now()
    add_notification("تم تحديث البيانات الحية", "success")

# ==========================================
# شاشة تسجيل الدخول المحسنة
# ==========================================
def login_screen():
    st.markdown("""
        <style>
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 80vh;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/10543/10543319.png", width=120)
        st.title("🏢 Drones Crafters")
        st.subheader("نظام إدارة الأصول العقارية" if st.session_state.language == 'ar' else "Real Estate Asset Management")
        
        email = st.text_input("البريد الإلكتروني" if st.session_state.language == 'ar' else "Email", key="login_email")
        password = st.text_input("كلمة المرور" if st.session_state.language == 'ar' else "Password", type="password", key="login_password")
        
        if st.button("🚪 دخول" if st.session_state.language == 'ar' else "Login", use_container_width=True):
            if email in st.session_state.users and st.session_state.users[email]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.user_role = st.session_state.users[email]["role"]
                st.session_state.user_tenant = st.session_state.users[email]["tenant"]
                if st.session_state.user_role == "SuperAdmin":
                    st.session_state.current_tenant = "tenant_1"
                else:
                    st.session_state.current_tenant = st.session_state.user_tenant
                add_notification(f"مرحباً {email}", "success")
                st.rerun()
            else:
                st.error("بيانات الدخول غير صحيحة" if st.session_state.language == 'ar' else "Invalid credentials")
        
        st.markdown("---")
        st.caption("📝 بيانات تجريبية: admin@drones.com / admin123  |  manager1@assets.com / pass1")

# ==========================================
# شريط الأدوات العلوي المحسن (مع إشعارات)
# ==========================================
def top_bar():
    col1, col2, col3, col4, col5, col6 = st.columns([2.5, 1, 1, 1, 1, 1])
    with col1:
        st.markdown(f"### 🏢 {st.session_state.tenants[st.session_state.current_tenant]['name']}")
    with col2:
        st.caption(f"🕒 آخر تحديث: {st.session_state.last_update.strftime('%H:%M:%S')}")
    with col3:
        icon = "🌙" if not st.session_state.dark_mode else "☀️"
        if st.button(icon, help="تغيير المظهر"):
            toggle_dark_mode()
            st.rerun()
    with col4:
        lang_text = "🇸🇦 عربي" if st.session_state.language == 'ar' else "🇬🇧 English"
        if st.button(lang_text, help="تغيير اللغة"):
            toggle_lang()
            st.rerun()
    with col5:
        # زر الإشعارات مع عداد
        unread_count = sum(1 for n in st.session_state.notifications if not n.get("read", False))
        notif_icon = f"🔔 ({unread_count})" if unread_count > 0 else "🔔"
        if st.button(notif_icon, help="الإشعارات"):
            st.session_state.show_notifications = not st.session_state.get("show_notifications", False)
    with col6:
        st.markdown(f"👤 {st.session_state.user_role}")
    
    # عرض الإشعارات إذا كانت مفتوحة
    if st.session_state.get("show_notifications", False):
        with st.expander("📢 الإشعارات", expanded=True):
            if not st.session_state.notifications:
                st.info("لا توجد إشعارات")
            else:
                for n in st.session_state.notifications[:10]:
                    icon = "✅" if n["type"] == "success" else "⚠️" if n["type"] == "warning" else "ℹ️"
                    st.markdown(f"{icon} **{n['timestamp']}** - {n['message']}")
                if st.button("تحديد الكل كمقروء"):
                    for n in st.session_state.notifications:
                        n["read"] = True
                    st.rerun()

# ==========================================
# القائمة الجانبية المحسنة (مع بحث)
# ==========================================
def sidebar_menu():
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/10543/10543319.png", width=80)
        st.title("Drones Crafters")
        
        if st.session_state.user_role == "SuperAdmin":
            tenants_list = list(st.session_state.tenants.keys())
            selected = st.selectbox("🏢 اختر الجهة" if st.session_state.language == 'ar' else "Select Tenant",
                                    tenants_list,
                                    format_func=lambda x: st.session_state.tenants[x]["name"])
            if selected != st.session_state.current_tenant:
                st.session_state.current_tenant = selected
                add_notification(f"تم التبديل إلى {st.session_state.tenants[selected]['name']}", "info")
                st.rerun()
        st.divider()
        
        # قائمة الخدمات
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
        
        # بحث في الخدمات
        search = st.text_input("🔍 بحث", placeholder="ابحث عن خدمة...")
        if search:
            services = [s for s in services if search in s]
        
        if st.session_state.user_role == "Viewer":
            allowed = services[:7] + [services[9], services[12], services[13]]
        else:
            allowed = services
        
        choice = st.radio("📋 الخدمات" if st.session_state.language == 'ar' else "Services", allowed,
                          index=allowed.index(st.session_state.selected_service) if st.session_state.selected_service in allowed else 0)
        if choice != st.session_state.selected_service:
            st.session_state.selected_service = choice
            add_notification(f"انتقل إلى {choice}", "info")
        
        st.divider()
        
        # زر التحديث اليدوي
        if st.button("🔄 تحديث البيانات", use_container_width=True):
            with st.spinner("جاري تحديث البيانات..."):
                time.sleep(0.5)
                refresh_data()
                st.rerun()
        
        st.caption("© 2025 Drones Crafters - v4.0 Interactive")

# ==========================================
# CSS للوضع المظلم والفاتح (محسن)
# ==========================================
def load_css():
    bg = "#0e1117" if st.session_state.dark_mode else "#ffffff"
    text = "#ffffff" if st.session_state.dark_mode else "#000000"
    card = "#1e1e2f" if st.session_state.dark_mode else "#f8f9fa"
    secondary = "#2d2d44" if st.session_state.dark_mode else "#e9ecef"
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
        background: linear-gradient(135deg, {card}, {secondary});
        padding: 20px;
        border-radius: 20px;
        border-right: 5px solid #1E3A8A;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.2s;
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
        transition: all 0.3s;
        border: none;
    }}
    .stButton>button:hover {{
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(59,130,246,0.4);
    }}
    .stDataFrame {{
        background-color: {card};
        border-radius: 15px;
        padding: 10px;
    }}
    </style>
    """

# ==========================================
# وظائف الخدمات (محسنة بتفاعل أكبر)
# ==========================================
def render_dashboard():
    data = get_current_data()
    
    # تحديث تلقائي اختياري
    if st.session_state.auto_refresh:
        if (datetime.now() - st.session_state.last_update).seconds > 30:
            refresh_data()
            st.rerun()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 " + t("إجمالي قيمة الأصول"), f"{data['assets_value']/1e9:.1f} مليار ريال", "+4.2%")
    col2.metric("🏢 " + t("عدد العقارات"), f"{data['properties_count']:,}", "+35")
    col3.metric("📈 " + t("متوسط العائد السنوي"), "11.8%", "+0.6%")
    col4.metric("🏠 " + t("نسبة الإشغال"), "89%", "-3.1%")
    
    st.divider()
    
    # فلتر زمني للرسوم البيانية
    col_f1, col_f2 = st.columns([1, 3])
    with col_f1:
        year_range = st.slider("نطاق السنوات", 2021, 2024, st.session_state.filters['year_range'])
        st.session_state.filters['year_range'] = year_range
    
    with col_f2:
        st.caption("📊 انقر على أي عنصر في الرسم البياني لعرض التفاصيل")
    
    c1, c2 = st.columns(2)
    with c1:
        df = pd.DataFrame({"نوع العقار": ["شقق","مكاتب","تجاري","صناعي","فلل"], "القيمة": [600,450,520,300,530]})
        fig = px.bar(df, x="نوع العقار", y="القيمة", color="القيمة", color_continuous_scale="Blues", 
                     title="توزيع القيمة حسب نوع العقار", text="القيمة")
        fig.update_traces(textposition="outside")
        fig.update_layout(font_family="Cairo", clickmode='event+select')
        st.plotly_chart(fig, use_container_width=True, key="dashboard_bar")
    
    with c2:
        kpi = pd.DataFrame({"السنة": [2021,2022,2023,2024], "ROI": [8.5,9.2,10.1,10.8], "IRR": [10.2,10.9,11.3,11.8]})
        kpi_filtered = kpi[(kpi["السنة"] >= year_range[0]) & (kpi["السنة"] <= year_range[1])]
        fig = px.line(kpi_filtered, x="السنة", y=["ROI","IRR"], markers=True, title="تطور العوائد")
        fig.update_layout(font_family="Cairo")
        st.plotly_chart(fig, use_container_width=True, key="dashboard_line")

def render_deeds():
    data = get_current_data()
    st.subheader("📜 إدارة الصكوك - تحرير مباشر")
    edited = st.data_editor(data["deeds"], use_container_width=True, num_rows="dynamic", key="deeds_editor")
    if st.button("💾 حفظ التغييرات", use_container_width=True):
        update_tenant_data("deeds", edited)
        st.success("تم حفظ الصكوك بنجاح")
        st.balloons()

def render_financial():
    data = get_current_data()
    st.subheader("💰 التحليلات المالية")
    year_range = st.slider("نطاق السنوات", 2021, 2024, st.session_state.filters['year_range'], key="fin_year")
    df = data["financial"]
    df = df[(df["السنة"] >= year_range[0]) & (df["السنة"] <= year_range[1])]
    fig = px.bar(df, x="السنة", y=["الإيرادات","المصاريف التشغيلية","صيانة"], barmode="group", 
                 title="الإيرادات والمصاريف", text_auto=True)
    fig.update_layout(font_family="Cairo")
    st.plotly_chart(fig, use_container_width=True)

def render_spatial():
    st.subheader("🗺️ الذكاء المكاني")
    district = st.selectbox("اختر الحي", ["الملقا","الياسمين","النرجس","العمارية"], 
                            index=["الملقا","الياسمين","النرجس","العمارية"].index(st.session_state.filters['selected_district']))
    st.session_state.filters['selected_district'] = district
    st.metric("متوسط سعر المتر", f"{np.random.randint(3500,6000):,} ريال", delta="+5%")
    points = pd.DataFrame({
        "lat": [24.774265, 24.800000, 24.760000, 24.820000],
        "lon": [46.738586, 46.700000, 46.760000, 46.680000],
        "name": ["مبنى إداري", "مجمع تجاري", "أرض خام", "مستودع"],
        "القيمة": [4.2, 7.8, 5.1, 3.1]
    })
    fig = px.scatter_mapbox(points, lat="lat", lon="lon", hover_name="name", size="القيمة", 
                            zoom=11, title="مواقع الأصول", color="القيمة")
    fig.update_layout(mapbox_style="open-street-map", font_family="Cairo")
    st.plotly_chart(fig, use_container_width=True)

def render_avm():
    st.subheader("🤖 نموذج التقييم الآلي")
    with st.form("avm_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            area = st.number_input("المساحة (م²)", 50, 10000, 250, step=50)
            district = st.selectbox("الحي", ["الملقا","الياسمين","النرجس","العمارية"])
        with col2:
            quality = st.selectbox("الجودة", ["اقتصادي","متوسط","فاخر"])
            age = st.slider("عمر العقار (سنوات)", 0, 50, 5)
        if st.form_submit_button("💰 تقدير القيمة", use_container_width=True):
            with st.spinner("جاري حساب التقييم..."):
                time.sleep(0.8)
                base = np.random.randint(3500, 6000)
                factor = {"اقتصادي":0.9, "متوسط":1.0, "فاخر":1.15}[quality]
                price = base * factor * (1 - age*0.01) * area
                st.success(f"### القيمة التقديرية: {price:,.0f} ريال")
                st.metric("سعر المتر المقدر", f"{price/area:,.0f} ريال/م²")
                add_notification(f"تم تقييم عقار بقيمة {price:,.0f} ريال", "success")

def render_maintenance():
    data = get_current_data()
    st.subheader("🛠️ الصيانة التنبؤية")
    assets = ["الكل"] + list(data["maintenance"]["اسم الأصل"].unique())
    selected_asset = st.selectbox("اختر الأصل", assets, index=0)
    df = data["maintenance"] if selected_asset == "الكل" else data["maintenance"][data["maintenance"]["اسم الأصل"] == selected_asset]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["الأسبوع"], y=df["تكلفة الصيانة"], name="تكلفة الصيانة", mode='lines+markers'))
    fig.add_trace(go.Scatter(x=df["الأسبوع"], y=df["تكلفة الإدارة"], name="تكلفة الإدارة", mode='lines+markers'))
    fig.add_hline(y=500000, line_dash="dash", line_color="red", annotation_text="الحد الأقصى")
    fig.update_layout(font_family="Cairo", title="اتجاه التكاليف")
    st.plotly_chart(fig, use_container_width=True)
    
    # مقاييس سريعة
    col1, col2, col3 = st.columns(3)
    col1.metric("متوسط تكلفة الصيانة", f"{df['تكلفة الصيانة'].mean():,.0f} ريال")
    col2.metric("إجمالي التكاليف", f"{df['تكلفة الصيانة'].sum():,.0f} ريال")
    col3.metric("أعلى تكلفة", f"{df['تكلفة الصيانة'].max():,.0f} ريال")

def render_market():
    st.subheader("📈 ذكاء السوق")
    market_df = pd.DataFrame({
        "السنة": list(range(2020, 2031)),
        "سكني": np.linspace(80, 145, 11),
        "تجاري": np.linspace(60, 110, 11),
        "صناعي": np.linspace(40, 85, 11)
    })
    sectors = st.multiselect("اختر القطاعات", ["سكني", "تجاري", "صناعي"], default=["سكني", "تجاري", "صناعي"])
    fig = px.area(market_df, x="السنة", y=sectors, title="توقعات نمو القطاعات")
    fig.update_layout(font_family="Cairo")
    st.plotly_chart(fig, use_container_width=True)
    st.info("💡 نصيحة: القطاع الصناعي يحقق أعلى معدل نمو متوقع (CAGR 7.8%)")

def render_contracts():
    data = get_current_data()
    st.subheader("👥 إدارة العقود والمستأجرين")
    edited = st.data_editor(data["contracts"], use_container_width=True, num_rows="dynamic", key="contracts_editor")
    if st.button("حفظ العقود", use_container_width=True):
        update_tenant_data("contracts", edited)
        st.success("تم حفظ العقود")

def render_forecast():
    st.subheader("📈 التنبؤ بالأسعار (AI)")
    months = pd.date_range("2024-01-01", periods=12, freq='M')
    historical = [4200, 4350, 4450, 4600, 4750, 4900, 5100, 5300, 5450, 5600, 5750, 5900]
    forecast = [6050, 6200, 6380, 6550, 6720, 6900, 7100, 7300, 7480, 7650, 7820, 8000]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=historical, name="بيانات تاريخية", mode='lines+markers'))
    fig.add_trace(go.Scatter(x=months, y=forecast, name="توقع AI", line=dict(dash='dot', color='red'), mode='lines+markers'))
    fig.update_layout(font_family="Cairo", title="توقع سعر المتر المربع (ريال)", xaxis_title="الشهر")
    st.plotly_chart(fig, use_container_width=True)
    st.metric("متوسط الزيادة المتوقعة", "7.2%", delta="+1.1% عن الربع السابق")

def render_portfolio():
    st.subheader("📊 تحليل المحفظة الاستثمارية")
    port = pd.DataFrame({"القطاع": ["سكني", "تجاري", "صناعي", "مكاتب"], 
                         "القيمة": [450, 320, 280, 410], 
                         "العائد": [8, 10, 12, 9],
                         "المخاطر": [0.12, 0.18, 0.22, 0.15]})
    col1, col2 = st.columns(2)
    with col1:
        fig_pie = px.pie(port, names="القطاع", values="القيمة", hole=0.4, title="توزيع المحفظة")
        st.plotly_chart(fig_pie, use_container_width=True)
    with col2:
        fig_scatter = px.scatter(port, x="العائد", y="القيمة", text="القطاع", size="القيمة", 
                                 color="المخاطر", title="العائد مقابل المخاطر")
        st.plotly_chart(fig_scatter, use_container_width=True)

def render_compliance():
    st.subheader("⚖️ الامتثال القانوني والتراخيص")
    licenses = pd.DataFrame({
        "الترخيص": ["رخصة بناء", "رخصة تشغيل", "دفاع مدني", "بيئة"],
        "تاريخ الانتهاء": ["2025-06-01", "2024-12-31", "2024-10-20", "2025-03-01"],
        "الحالة": ["ساري", "ينتهي قريباً", "منتهي", "ساري"]
    })
    st.dataframe(licenses, use_container_width=True)
    if any(licenses["الحالة"] == "منتهي"):
        st.warning("⚠️ يوجد تراخيص منتهية! يرجى التجديد فوراً.")
    if any(licenses["الحالة"] == "ينتهي قريباً"):
        st.info("⏰ يوجد تراخيص على وشك الانتهاء خلال 30 يوماً.")

def render_risk():
    st.subheader("⚠️ لوحة تحكم المخاطر")
    risks = pd.DataFrame({
        "الخطر": ["تقلبات السوق", "مخاطر الائتمان", "تشغيلية", "قانونية", "طبيعية"],
        "الاحتمال": [35, 25, 45, 20, 15],
        "الأثر": [4, 3, 3, 4, 5]
    })
    risks["نقطة المخاطرة"] = risks["الاحتمال"] * risks["الأثر"]
    fig = px.bar(risks, x="الخطر", y="نقطة المخاطرة", color="نقطة المخاطرة", 
                 color_continuous_scale="Reds", title="مصفوفة المخاطر", text="نقطة المخاطرة")
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)
    st.metric("إجمالي درجة المخاطر", f"{risks['نقطة المخاطرة'].sum()}", delta="+15 عن الربع السابق")

def render_reports():
    st.subheader("📑 التقارير الذكية القابلة للتخصيص")
    report_type = st.selectbox("نوع التقرير", ["ملخص المحفظة", "التحليل المالي", "حالة الصيانة"])
    
    if report_type == "ملخص المحفظة":
        data = get_current_data()
        summary = pd.DataFrame({
            "المؤشر": ["عدد الأصول", "القيمة الإجمالية", "متوسط العائد", "نسبة الإشغال"],
            "القيمة": [f"{data['properties_count']:,}", f"{data['assets_value']/1e9:.1f} مليار", "11.8%", "89%"]
        })
        st.dataframe(summary)
    elif report_type == "التحليل المالي":
        data = get_current_data()
        st.line_chart(data["financial"].set_index("السنة")["الإيرادات"])
    else:
        data = get_current_data()
        st.bar_chart(data["maintenance"].set_index("الأسبوع")["تكلفة الصيانة"])
    
    csv = get_current_data()["deeds"].to_csv().encode()
    st.download_button("📥 تحميل التقرير (CSV)", data=csv, file_name=f"report_{datetime.now().strftime('%Y%m%d')}.csv", use_container_width=True)

def render_notifications():
    st.subheader("🔔 مركز التنبيهات والإشعارات")
    data = get_current_data()
    alerts = pd.DataFrame(data.get("alerts", []))
    if not alerts.empty:
        st.dataframe(alerts, use_container_width=True)
    else:
        st.info("✅ لا توجد إشعارات حالية - كل شيء تحت السيطرة")
    
    # إضافة إشعار تجريبي
    with st.expander("➕ إضافة إشعار تجريبي"):
        if st.button("إضافة إشعار تجريبي"):
            add_notification("هذا إشعار تجريبي من النظام", "info")
            st.rerun()

# ==========================================
# التطبيق الرئيسي المحسن
# ==========================================
def main():
    if not st.session_state.logged_in:
        login_screen()
        return
    
    st.markdown(load_css(), unsafe_allow_html=True)
    top_bar()
    sidebar_menu()
    
    # عرض الخدمة المختارة
    service = st.session_state.selected_service
    service_map = {
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
        "التقارير الذكية القابلة للتخصيص": render_reports,
        "مركز التنبيهات والإشعارات": render_notifications
    }
    
    render_func = service_map.get(service, render_dashboard)
    render_func()

if __name__ == "__main__":
    main()

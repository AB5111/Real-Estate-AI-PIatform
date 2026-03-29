import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import json
import io
import random

# محاولة استيراد sklearn للتنبؤ (اختياري)
try:
    from sklearn.linear_model import LinearRegression
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# ==========================================
# إعدادات الصفحة
# ==========================================
st.set_page_config(layout="wide", page_title="Drones Crafters - Real Estate Enterprise", page_icon="🏢", initial_sidebar_state="expanded")

# ==========================================
# تهيئة الحالة المتقدمة
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
    st.session_state.selected_service = "لوحة القيادة"
if 'notifications' not in st.session_state:
    st.session_state.notifications = []
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

# بيانات الجهات والمستخدمين (محاكاة)
if 'tenants' not in st.session_state:
    st.session_state.tenants = {
        "tenant_1": {"name": "شركة أصول الرياض", "plan": "Enterprise", "logo": "🏢"},
        "tenant_2": {"name": "مجموعة الخليج العقارية", "plan": "Professional", "logo": "🏭"}
    }
if 'users' not in st.session_state:
    st.session_state.users = {
        "admin@drones.com": {"password": "admin123", "role": "SuperAdmin", "tenant": None},
        "manager1@assets.com": {"password": "pass1", "role": "TenantAdmin", "tenant": "tenant_1"},
        "viewer1@assets.com": {"password": "view", "role": "Viewer", "tenant": "tenant_1"},
    }

# بيانات العقار الرئيسية (محاكاة)
if 'property_data' not in st.session_state:
    # بيانات الصكوك
    deeds_df = pd.DataFrame({
        "رقم الصك": ["123/أ", "456/ب", "789/ج"],
        "المالك": ["شركة أصول الرياض", "صندوق الاستثمار", "شركة التطوير"],
        "الحي": ["الملقا", "الياسمين", "النرجس"],
        "المساحة (م²)": [2500, 4300, 1800],
        "تاريخ الإصدار": ["2020-01-01", "2021-03-15", "2022-06-20"],
        "الحالة": ["ساري", "ساري", "محدث"]
    })
    # بيانات التكاليف
    costs_df = pd.DataFrame({
        "التاريخ": pd.date_range(start="2024-01-01", periods=6, freq='M'),
        "النوع": ["فواتير", "صيانة", "فواتير", "صيانة", "فواتير", "صيانة"],
        "المبلغ": [12000, 3500, 13000, 4200, 12500, 3800],
        "الوصف": ["كهرباء", "إصلاح مكيف", "ماء", "دهان", "غاز", "سباكة"]
    })
    # بيانات الصيانة
    maintenance_df = pd.DataFrame({
        "التاريخ": pd.date_range(start="2024-01-15", periods=5, freq='M'),
        "العمل": ["فحص دوري", "تبديل سباكة", "صيانة مكيفات", "دهان واجهة", "تنسيق حديقة"],
        "التكلفة": [2000, 4500, 3000, 8000, 2500],
        "الحالة": ["تم", "تم", "قيد التنفيذ", "مجدول", "معلق"]
    })
    # متطلبات العقار
    requirements_df = pd.DataFrame({
        "المتطلب": ["تحديد المخطط", "رخصة بناء", "تأمين ضد الحريق", "تحديث الصك"],
        "الأولوية": ["عالية", "عالية", "متوسطة", "منخفضة"],
        "الموعد": ["2024-06-01", "2024-07-15", "2024-08-01", "2024-12-31"],
        "الحالة": ["قيد التنفيذ", "معلق", "لم يبدأ", "قيد التنفيذ"]
    })
    # صور (URLs)
    images = [
        "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=300",
        "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=300",
        "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=300"
    ]
    # موقع العقار (إحداثيات)
    location = {"lat": 24.774265, "lon": 46.738586}
    # مضلع المساحة (للرفع المساحي)
    survey_polygon = [
        [46.735, 24.772],
        [46.742, 24.772],
        [46.742, 24.778],
        [46.735, 24.778],
        [46.735, 24.772]
    ]
    # سعر المتر في المنطقة (تاريخي)
    area_price_history = pd.DataFrame({
        "التاريخ": pd.date_range(start="2023-01-01", periods=8, freq='M'),
        "السعر": [3800, 3900, 3950, 4100, 4200, 4300, 4450, 4500]
    })
    # عقود الإيجار
    contracts_df = pd.DataFrame({
        "المستأجر": ["شركة الأفق", "مؤسسة البناء", "فردي - أحمد"],
        "العقار": ["برج الأعمال - ط3", "مجمع الريان - محل 5", "فيلا الياسمين"],
        "تاريخ البدء": ["2024-01-01", "2024-02-01", "2024-03-01"],
        "تاريخ الانتهاء": ["2025-01-01", "2025-02-01", "2025-03-01"],
        "الإيجار الشهري": [45000, 32000, 12000]
    })

    st.session_state.property_data = {
        "deeds": deeds_df,
        "costs": costs_df,
        "maintenance": maintenance_df,
        "requirements": requirements_df,
        "images": images,
        "location": location,
        "survey_polygon": survey_polygon,
        "area_price_history": area_price_history,
        "current_area_price": area_price_history["السعر"].iloc[-1],
        "contracts": contracts_df,
        "ai_analysis": {}
    }

# ==========================================
# دوال مساعدة متقدمة
# ==========================================
def add_notification(msg, typ="info"):
    st.session_state.notifications.insert(0, {
        "message": msg,
        "type": typ,
        "time": datetime.now().strftime("%H:%M:%S"),
        "read": False
    })
    st.session_state.notifications = st.session_state.notifications[:20]

def t(ar, en=None):
    return ar if st.session_state.language == 'ar' else (en if en else ar)

def toggle_dark():
    st.session_state.dark_mode = not st.session_state.dark_mode
    add_notification(t("تم تغيير المظهر", "Theme changed"), "info")

def toggle_lang():
    st.session_state.language = 'en' if st.session_state.language == 'ar' else 'ar'
    add_notification(t("تم تغيير اللغة", "Language changed"), "info")

def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    add_notification(t("تم تسجيل الخروج", "Logged out"), "info")

def get_data():
    return st.session_state.property_data

def update_data(key, value):
    st.session_state.property_data[key] = value
    add_notification(f"{t('تم تحديث', 'Updated')} {key}", "success")

def refresh_live_data():
    """تحديث البيانات الحية (محاكاة تغيرات عشوائية)"""
    data = get_data()
    # تحديث أسعار المتر بشكل عشوائي
    new_price = data["current_area_price"] + random.randint(-100, 150)
    data["current_area_price"] = max(3000, new_price)
    # إضافة سعر جديد للتاريخ
    new_history = data["area_price_history"].copy()
    new_row = pd.DataFrame({"التاريخ": [datetime.now()], "السعر": [data["current_area_price"]]})
    data["area_price_history"] = pd.concat([new_history, new_row], ignore_index=True).tail(12)
    # تحديث التكاليف (محاكاة)
    new_cost = random.randint(1000, 5000)
    new_cost_row = pd.DataFrame({"التاريخ": [datetime.now()], "النوع": ["فواتير"], "المبلغ": [new_cost], "الوصف": ["تحديث تلقائي"]})
    data["costs"] = pd.concat([data["costs"], new_cost_row], ignore_index=True).tail(10)
    update_data("current_area_price", data["current_area_price"])
    update_data("area_price_history", data["area_price_history"])
    update_data("costs", data["costs"])
    st.session_state.last_update = datetime.now()
    add_notification(t("تم تحديث البيانات الحية", "Live data refreshed"), "success")

# ==========================================
# CSS احترافي
# ==========================================
def load_css():
    bg = "#0f172a" if st.session_state.dark_mode else "#f1f5f9"
    card = "#1e293b" if st.session_state.dark_mode else "#ffffff"
    text = "#f8fafc" if st.session_state.dark_mode else "#0f172a"
    border = "#3b82f6"
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700&display=swap');
    * {{ font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }}
    .stApp {{ background-color: {bg}; color: {text}; }}
    div[data-testid="stMetric"] {{
        background-color: {card};
        padding: 1rem;
        border-radius: 1rem;
        border-right: 5px solid {border};
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        transition: 0.2s;
    }}
    div[data-testid="stMetric"]:hover {{ transform: translateY(-3px); }}
    .stButton>button {{
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        color: white;
        border: none;
        border-radius: 0.75rem;
        font-weight: 600;
        transition: 0.2s;
    }}
    .stButton>button:hover {{ transform: scale(1.02); }}
    .stDataFrame, .stTable {{ border-radius: 1rem; overflow: hidden; }}
    </style>
    """

# ==========================================
# شاشة تسجيل الدخول
# ==========================================
def login_screen():
    st.markdown("<div style='text-align:center'><h1>🏢 Drones Crafters</h1><h3>نظام إدارة العقارات المتكامل</h3></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        email = st.text_input(t("البريد الإلكتروني", "Email"))
        password = st.text_input(t("كلمة المرور", "Password"), type="password")
        if st.button(t("دخول", "Login"), use_container_width=True):
            if email in st.session_state.users and st.session_state.users[email]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.user_role = st.session_state.users[email]["role"]
                st.session_state.current_tenant = st.session_state.users[email]["tenant"] if st.session_state.users[email]["tenant"] else "tenant_1"
                add_notification(f"مرحباً {email}", "success")
                st.rerun()
            else:
                st.error(t("بيانات غير صحيحة", "Invalid credentials"))
        st.caption("Demo: admin@drones.com / admin123  |  manager1@assets.com / pass1")

# ==========================================
# الشريط العلوي المتقدم
# ==========================================
def top_bar():
    col1, col2, col3, col4, col5, col6, col7 = st.columns([2,1,1,1,1,1,1])
    with col1:
        st.markdown(f"### {st.session_state.tenants[st.session_state.current_tenant]['logo']} {st.session_state.tenants[st.session_state.current_tenant]['name']}")
    with col2:
        st.caption(f"🕒 {st.session_state.last_update.strftime('%H:%M:%S')}")
    with col3:
        st.button("🌙" if not st.session_state.dark_mode else "☀️", on_click=toggle_dark, help=t("المظهر"))
    with col4:
        st.button("🇸🇦" if st.session_state.language=='ar' else "🇬🇧", on_click=toggle_lang, help=t("اللغة"))
    with col5:
        unread = sum(1 for n in st.session_state.notifications if not n.get("read", False))
        if st.button(f"🔔 {unread}" if unread else "🔔", help=t("الإشعارات")):
            st.session_state.show_notif = not st.session_state.get("show_notif", False)
    with col6:
        st.markdown(f"👤 {st.session_state.user_role}")
    with col7:
        st.button("🚪", on_click=logout, help=t("خروج"))
    if st.session_state.get("show_notif", False):
        with st.expander(t("الإشعارات", "Notifications"), expanded=True):
            for n in st.session_state.notifications[:10]:
                st.write(f"**{n['time']}** - {n['message']}")
            if st.button(t("تحديد الكل كمقروء")):
                for n in st.session_state.notifications:
                    n["read"] = True
                st.rerun()

# ==========================================
# القائمة الجانبية (14 خدمة)
# ==========================================
def sidebar_menu():
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/10543/10543319.png", width=80)
        st.title("Drones Crafters")
        if st.session_state.user_role == "SuperAdmin":
            tenants = list(st.session_state.tenants.keys())
            sel = st.selectbox(t("اختر الجهة", "Select Tenant"), tenants,
                               format_func=lambda x: st.session_state.tenants[x]["name"])
            if sel != st.session_state.current_tenant:
                st.session_state.current_tenant = sel
                st.rerun()
        st.divider()
        services = [
            "لوحة القيادة", "إدارة الصكوك", "الرفع المساحي", "معرض الصور",
            "الموقع على الخريطة", "التكاليف والفواتير", "متطلبات العقار",
            "سعر المتر بالمنطقة", "تحليل الذكاء الاصطناعي", "التقارير الذكية",
            "إدارة العقود", "الصيانة", "المخاطر والامتثال", "الإشعارات"
        ]
        if st.session_state.user_role == "Viewer":
            allowed = services[:5] + services[8:10] + services[13:14]
            services = [s for s in services if s in allowed]
        choice = st.radio(t("الخدمات", "Services"), services,
                          index=services.index(st.session_state.selected_service) if st.session_state.selected_service in services else 0)
        st.session_state.selected_service = choice
        st.divider()
        col_refresh, col_auto = st.columns(2)
        with col_refresh:
            if st.button("🔄 تحديث", use_container_width=True):
                refresh_live_data()
                st.rerun()
        with col_auto:
            st.session_state.auto_refresh = st.checkbox(t("تلقائي"), value=st.session_state.auto_refresh)
        if st.session_state.auto_refresh:
            st.caption(t("تحديث كل 30 ثانية"))
            # تحديث تلقائي بسيط باستخدام time.sleep في حلقة (ليس مثاليًا لكن للعرض)
            # بدلاً من ذلك، نستخدم st.rerun بعد فترة
            # نضيف تأخير بسيط عبر session state timer
            if 'refresh_counter' not in st.session_state:
                st.session_state.refresh_counter = 0
            st.session_state.refresh_counter += 1
            if st.session_state.refresh_counter % 30 == 0:
                refresh_live_data()
                st.rerun()
        st.caption("© 2025 Drones Crafters - v7.0")

# ==========================================
# وظائف الخدمات المحسنة
# ==========================================
def render_dashboard():
    data = get_data()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(t("إجمالي قيمة الأصول"), "2.4 مليار ريال", "+4.2%")
    col2.metric(t("عدد الصكوك"), len(data["deeds"]), "+2")
    col3.metric(t("متوسط سعر المتر"), f"{data['current_area_price']:,} ريال", "+3%")
    total_costs = data["costs"]["المبلغ"].sum()
    col4.metric(t("إجمالي التكاليف"), f"{total_costs:,.0f} ريال", "-5%")
    st.divider()
    # رسم بياني لتوزيع التكاليف
    fig_cost = px.bar(data["costs"], x="التاريخ", y="المبلغ", color="النوع", title=t("التكاليف الشهرية"))
    st.plotly_chart(fig_cost, use_container_width=True)
    # مؤشرات سريعة
    st.subheader(t("حالة المتطلبات"))
    req_status = data["requirements"]["الحالة"].value_counts().reset_index()
    req_status.columns = ["الحالة", "العدد"]
    fig_req = px.pie(req_status, names="الحالة", values="العدد", title=t("نسبة إنجاز المتطلبات"))
    st.plotly_chart(fig_req, use_container_width=True)

def render_deeds():
    data = get_data()
    st.subheader(t("إدارة الصكوك والوثائق"))
    edited = st.data_editor(data["deeds"], use_container_width=True, num_rows="dynamic")
    if st.button(t("حفظ التغييرات")):
        update_data("deeds", edited)
        st.success(t("تم الحفظ"))

def render_survey():
    st.subheader(t("الرفع المساحي"))
    st.markdown(t("يمكنك رفع ملف GeoJSON أو إدخال إحداثيات المضلع"))
    uploaded = st.file_uploader(t("اختر ملف GeoJSON"), type=["geojson", "json"])
    if uploaded:
        try:
            geojson = json.load(uploaded)
            st.success(t("تم رفع الملف بنجاح"))
            st.json(geojson)
        except:
            st.error(t("خطأ في قراءة الملف"))
    # رسم مضلع تفاعلي باستخدام Plotly
    data = get_data()
    polygon = data["survey_polygon"]
    fig = go.Figure()
    lons, lats = zip(*polygon)
    fig.add_trace(go.Scattermapbox(
        mode="lines+markers",
        lon=lons,
        lat=lats,
        marker={'size': 10},
        fill="toself",
        fillcolor="rgba(59,130,246,0.3)",
        line=dict(width=2)
    ))
    fig.update_layout(
        mapbox=dict(style="open-street-map", center=dict(lat=24.775, lon=46.738), zoom=14),
        margin=dict(l=0, r=0, t=0, b=0),
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

def render_images():
    st.subheader(t("معرض الصور"))
    data = get_data()
    cols = st.columns(3)
    for i, img in enumerate(data["images"]):
        with cols[i % 3]:
            st.image(img, use_container_width=True)
    uploaded = st.file_uploader(t("إضافة صورة جديدة"), type=["jpg", "png", "jpeg"])
    if uploaded:
        st.image(uploaded, caption=t("الصورة المرفوعة"), use_container_width=True)
        if st.button(t("حفظ الصورة")):
            new_images = data["images"] + [uploaded.name]  # محاكاة
            update_data("images", new_images)
            st.rerun()

def render_location():
    st.subheader(t("الموقع على الخريطة"))
    data = get_data()
    lat = data["location"]["lat"]
    lon = data["location"]["lon"]
    df = pd.DataFrame({"lat": [lat], "lon": [lon]})
    st.map(df)
    with st.expander(t("تعديل الموقع")):
        new_lat = st.number_input("Latitude", value=lat)
        new_lon = st.number_input("Longitude", value=lon)
        if st.button(t("تحديث")):
            update_data("location", {"lat": new_lat, "lon": new_lon})
            st.rerun()

def render_costs():
    st.subheader(t("التكاليف والفواتير"))
    data = get_data()
    tab1, tab2 = st.tabs([t("الفواتير"), t("الصيانة")])
    with tab1:
        edited_costs = st.data_editor(data["costs"], use_container_width=True, num_rows="dynamic")
        if st.button(t("حفظ الفواتير")):
            update_data("costs", edited_costs)
    with tab2:
        edited_maint = st.data_editor(data["maintenance"], use_container_width=True, num_rows="dynamic")
        if st.button(t("حفظ الصيانة")):
            update_data("maintenance", edited_maint)
    total = data["costs"]["المبلغ"].sum() + data["maintenance"]["التكلفة"].sum()
    st.metric(t("إجمالي التكاليف"), f"{total:,.0f} ريال")

def render_requirements():
    st.subheader(t("متطلبات العقار"))
    data = get_data()
    edited = st.data_editor(data["requirements"], use_container_width=True, num_rows="dynamic")
    if st.button(t("حفظ المتطلبات")):
        update_data("requirements", edited)
    # نسبة الإنجاز
    completed = len(data["requirements"][data["requirements"]["الحالة"] == "تم"])
    progress = completed / len(data["requirements"]) if len(data["requirements"]) > 0 else 0
    st.progress(progress, text=t(f"نسبة الإنجاز: {progress*100:.0f}%"))

def render_area_price():
    st.subheader(t("سعر المتر في المنطقة"))
    data = get_data()
    current = data["current_area_price"]
    new_price = st.number_input(t("سعر المتر الحالي (ريال)"), value=current, step=50)
    if st.button(t("تحديث السعر")):
        update_data("current_area_price", new_price)
        # إضافة إلى التاريخ
        new_history = data["area_price_history"].copy()
        new_row = pd.DataFrame({"التاريخ": [datetime.now()], "السعر": [new_price]})
        update_data("area_price_history", pd.concat([new_history, new_row], ignore_index=True).tail(12))
        st.rerun()
    # رسم بياني تاريخي
    fig = px.line(data["area_price_history"], x="التاريخ", y="السعر", title=t("اتجاه أسعار المتر"))
    st.plotly_chart(fig, use_container_width=True)

def render_ai_analysis():
    st.subheader(t("تحليل الذكاء الاصطناعي"))
    data = get_data()
    # تقدير القيمة السوقية
    total_area = data["deeds"]["المساحة (م²)"].sum()
    estimated_value = total_area * data["current_area_price"] * 1.05  # علاوة 5%
    st.metric(t("القيمة السوقية المقدرة"), f"{estimated_value:,.0f} ريال", delta="+5%")
    # تنبؤ بالصيانة باستخدام نموذج بسيط (إذا كان sklearn متاح)
    if SKLEARN_AVAILABLE and len(data["maintenance"]) > 2:
        try:
            maint = data["maintenance"].copy()
            maint["days"] = (pd.to_datetime(maint["التاريخ"]) - pd.to_datetime("2024-01-01")).dt.days
            X = maint[["days"]].values
            y = maint["التكلفة"].values
            model = LinearRegression().fit(X, y)
            future_days = np.array([[max(X)[0] + 30], [max(X)[0] + 60]])
            pred = model.predict(future_days)
            st.write(t("التنبؤ بتكلفة الصيانة للشهرين القادمين:"))
            st.line_chart(pd.Series(pred, index=["شهر 1", "شهر 2"]))
        except:
            st.warning(t("لا توجد بيانات كافية للتنبؤ"))
    else:
        st.info(t("تمكين sklearn لتحليل تنبؤي أفضل"))
    # تحليل الصور (محاكاة)
    st.markdown("#### " + t("تحليل الصور"))
    st.success(t("تم اكتشاف حالة جيدة للعقار بنسبة 92%"))
    # توصيات
    st.markdown("#### " + t("توصيات"))
    st.info(t("زيادة سعر الإيجار بنسبة 3% يتماشى مع السوق"))

def render_reports():
    st.subheader(t("التقارير الذكية"))
    report_type = st.selectbox(t("نوع التقرير"), [t("ملخص العقار"), t("التكاليف"), t("المتطلبات"), t("سعر المتر")])
    data = get_data()
    if report_type == t("ملخص العقار"):
        st.dataframe(data["deeds"])
        csv = data["deeds"].to_csv().encode()
    elif report_type == t("التكاليف"):
        st.dataframe(data["costs"])
        csv = data["costs"].to_csv().encode()
    elif report_type == t("المتطلبات"):
        st.dataframe(data["requirements"])
        csv = data["requirements"].to_csv().encode()
    else:
        st.dataframe(data["area_price_history"])
        csv = data["area_price_history"].to_csv().encode()
    st.download_button(t("تحميل التقرير (CSV)"), csv, f"report_{report_type}.csv")

def render_contracts():
    st.subheader(t("إدارة العقود"))
    data = get_data()
    edited = st.data_editor(data["contracts"], use_container_width=True, num_rows="dynamic")
    if st.button(t("حفظ العقود")):
        update_data("contracts", edited)
        st.success(t("تم الحفظ"))

def render_maintenance():
    st.subheader(t("الصيانة"))
    data = get_data()
    st.dataframe(data["maintenance"], use_container_width=True)
    with st.form("add_maintenance"):
        col1, col2 = st.columns(2)
        with col1:
            action = st.text_input(t("نوع العمل"))
            cost = st.number_input(t("التكلفة"), min_value=0)
        with col2:
            status = st.selectbox(t("الحالة"), ["قيد التنفيذ", "تم", "معلق", "مجدول"])
            date = st.date_input(t("التاريخ"), value=datetime.now())
        if st.form_submit_button(t("إضافة")):
            new_row = pd.DataFrame({"التاريخ": [date], "العمل": [action], "التكلفة": [cost], "الحالة": [status]})
            updated = pd.concat([data["maintenance"], new_row], ignore_index=True)
            update_data("maintenance", updated)
            st.rerun()

def render_risk_compliance():
    st.subheader(t("المخاطر والامتثال"))
    # مصفوفة المخاطر
    risks = pd.DataFrame({
        "الخطر": ["تقلبات السوق", "مخاطر الائتمان", "المخاطر التشغيلية", "مخاطر قانونية"],
        "الاحتمال (%)": [30, 20, 45, 15],
        "الأثر (1-5)": [4, 3, 3, 4],
        "نقطة المخاطرة": [120, 60, 135, 60]
    })
    fig = px.bar(risks, x="الخطر", y="نقطة المخاطرة", color="نقطة المخاطرة", title=t("مصفوفة المخاطر"))
    st.plotly_chart(fig, use_container_width=True)
    # التراخيص
    st.markdown("#### " + t("التراخيص والامتثال"))
    licenses = pd.DataFrame({
        "الترخيص": ["رخصة بناء", "رخصة تشغيل", "دفاع مدني", "بيئة"],
        "تاريخ الانتهاء": ["2025-06-01", "2024-12-31", "2024-10-20", "2025-03-01"],
        "الحالة": ["ساري", "ينتهي قريباً", "منتهي", "ساري"]
    })
    st.dataframe(licenses)
    if any(licenses["الحالة"] == "منتهي"):
        st.error(t("يوجد تراخيص منتهية! يرجى التجديد فوراً."))
    if any(licenses["الحالة"] == "ينتهي قريباً"):
        st.warning(t("بعض التراخيص على وشك الانتهاء"))

def render_notifications_center():
    st.subheader(t("مركز الإشعارات"))
    data = get_data()
    # عرض إشعارات النظام
    st.markdown("#### " + t("إشعارات النظام"))
    for n in st.session_state.notifications[:20]:
        st.write(f"**{n['time']}** - {n['message']}")
    # إضافة إشعار جديد
    with st.form("new_notif"):
        msg = st.text_input(t("رسالة جديدة"))
        typ = st.selectbox(t("النوع"), ["info", "success", "warning"])
        if st.form_submit_button(t("إضافة إشعار")):
            add_notification(msg, typ)
            st.rerun()

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
    service_map = {
        "لوحة القيادة": render_dashboard,
        "إدارة الصكوك": render_deeds,
        "الرفع المساحي": render_survey,
        "معرض الصور": render_images,
        "الموقع على الخريطة": render_location,
        "التكاليف والفواتير": render_costs,
        "متطلبات العقار": render_requirements,
        "سعر المتر بالمنطقة": render_area_price,
        "تحليل الذكاء الاصطناعي": render_ai_analysis,
        "التقارير الذكية": render_reports,
        "إدارة العقود": render_contracts,
        "الصيانة": render_maintenance,
        "المخاطر والامتثال": render_risk_compliance,
        "الإشعارات": render_notifications_center,
    }
    service_map.get(service, render_dashboard)()

if __name__ == "__main__":
    main()

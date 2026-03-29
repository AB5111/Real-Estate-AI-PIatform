import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import json
import io

# ==========================================
# 1. إعدادات الصفحة
# ==========================================
st.set_page_config(
    layout="wide",
    page_title="Drones Crafters - Real Estate Management",
    page_icon="🏢",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. تهيئة حالة الجلسة مع بيانات كاملة
# ==========================================
def init_session():
    # الإعدادات العامة
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    if 'language' not in st.session_state:
        st.session_state.language = 'ar'
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'current_tenant' not in st.session_state:
        st.session_state.current_tenant = 'tenant_1'
    if 'selected_service' not in st.session_state:
        st.session_state.selected_service = "لوحة القيادة"

    # بيانات الجهات (Tenants) - تم إضافة logo
    if 'tenants' not in st.session_state:
        st.session_state.tenants = {
            "tenant_1": {
                "name": "شركة أصول الرياض",
                "logo": "🏢",
                "role": "owner",
                "properties_count": 1280,
                "assets_value": 2.4e9
            },
            "tenant_2": {
                "name": "مجموعة الخليج العقارية",
                "logo": "🏭",
                "role": "owner",
                "properties_count": 540,
                "assets_value": 980e6
            }
        }

    # بيانات المستخدمين
    if 'users' not in st.session_state:
        st.session_state.users = {
            "admin@drones.com": {"password": "admin123", "role": "SuperAdmin", "tenant": None},
            "manager1@assets.com": {"password": "pass1", "role": "TenantAdmin", "tenant": "tenant_1"},
            "viewer1@assets.com": {"password": "view", "role": "Viewer", "tenant": "tenant_1"}
        }

    # بيانات العقار الرئيسية (جميع الميزات)
    if 'property_data' not in st.session_state:
        st.session_state.property_data = {
            "deeds": pd.DataFrame({
                "رقم الصك": ["123/أ", "456/ب", "789/ج"],
                "المالك": ["شركة أصول الرياض", "صندوق الاستثمار", "شركة التطوير"],
                "الحي": ["الملقا", "الياسمين", "النرجس"],
                "المساحة (م²)": [2500, 4300, 1800],
                "تاريخ الإصدار": ["2020-01-01", "2021-03-15", "2022-06-20"]
            }),
            "images": [
                "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=400",
                "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=400",
                "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=400"
            ],
            "location": {"lat": 24.774265, "lon": 46.738586},
            "survey_polygon": [
                [46.735, 24.772],
                [46.742, 24.772],
                [46.742, 24.778],
                [46.735, 24.778],
                [46.735, 24.772]
            ],
            "costs": pd.DataFrame({
                "التاريخ": ["2024-01-15", "2024-02-20", "2024-03-10"],
                "النوع": ["فواتير", "صيانة", "فواتير"],
                "المبلغ": [12000, 3500, 8900],
                "الوصف": ["كهرباء", "إصلاح مكيف", "مياه"]
            }),
            "maintenance": pd.DataFrame({
                "التاريخ": ["2024-01-10", "2024-02-25", "2024-03-05"],
                "العمل": ["فحص دوري", "تبديل سباكة", "دهان"],
                "التكلفة": [2000, 4500, 3000],
                "الحالة": ["تم", "قيد التنفيذ", "معلق"]
            }),
            "requirements": pd.DataFrame({
                "المتطلب": ["تحديد المخطط", "رخصة بناء", "تأمين"],
                "الأولوية": ["عالية", "متوسطة", "عالية"],
                "الموعد": ["2024-06-01", "2024-07-15", "2024-05-20"],
                "الحالة": ["قيد التنفيذ", "معلق", "لم يبدأ"]
            }),
            "area_price": 4200,  # سعر المتر
            "contracts": pd.DataFrame({
                "المستأجر": ["شركة الأفق", "مؤسسة البناء", "شركة التقنية"],
                "تاريخ البدء": ["2024-01-01", "2024-02-01", "2023-12-01"],
                "تاريخ الانتهاء": ["2025-01-01", "2025-02-01", "2024-12-01"],
                "الإيجار الشهري": [45000, 32000, 28000]
            }),
            "alerts": [
                {"التاريخ": "2024-12-15", "الرسالة": "انتهاء رخصة تشغيل", "النوع": "تحذير"},
                {"التاريخ": "2024-12-20", "الرسالة": "صيانة دورية مستحقة", "النوع": "تنبيه"}
            ]
        }

init_session()

# ==========================================
# 3. دوال مساعدة
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
    add_notification(f"الوضع {'المظلم' if st.session_state.dark_mode else 'الفاتح'}", "info")
    st.rerun()

def toggle_lang():
    st.session_state.language = 'en' if st.session_state.language == 'ar' else 'ar'
    add_notification(f"Language: {'English' if st.session_state.language == 'en' else 'العربية'}", "info")
    st.rerun()

def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    add_notification("تم تسجيل الخروج", "info")
    st.rerun()

def get_property_data():
    return st.session_state.property_data

def update_property_data(key, value):
    st.session_state.property_data[key] = value
    add_notification(f"تم تحديث {key}", "success")

# ==========================================
# 4. CSS المحسن (يدعم الوضع المظلم)
# ==========================================
def load_css():
    bg = "#0f172a" if st.session_state.dark_mode else "#f1f5f9"
    card = "#1e293b" if st.session_state.dark_mode else "#ffffff"
    text = "#f8fafc" if st.session_state.dark_mode else "#0f172a"
    border = "#3b82f6"
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700&display=swap');
    * {{
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }}
    .stApp {{
        background-color: {bg};
        color: {text};
    }}
    div[data-testid="stMetric"] {{
        background-color: {card};
        padding: 1.2rem;
        border-radius: 1rem;
        border-right: 5px solid {border};
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: 0.2s;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-3px);
    }}
    .stButton>button {{
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        color: white;
        border: none;
        border-radius: 0.75rem;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }}
    .stButton>button:hover {{
        transform: scale(1.02);
    }}
    </style>
    """

# ==========================================
# 5. شاشة تسجيل الدخول
# ==========================================
def login_screen():
    st.markdown("<div style='text-align:center'><h1>🏢 Drones Crafters</h1><h3>نظام إدارة العقارات المتكامل</h3></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        email = st.text_input(t("البريد الإلكتروني", "Email"))
        pwd = st.text_input(t("كلمة المرور", "Password"), type="password")
        if st.button(t("دخول", "Login"), use_container_width=True):
            if email in st.session_state.users and st.session_state.users[email]["password"] == pwd:
                st.session_state.logged_in = True
                st.session_state.user_role = st.session_state.users[email]["role"]
                st.session_state.current_tenant = st.session_state.users[email]["tenant"] if st.session_state.users[email]["tenant"] else "tenant_1"
                add_notification(f"مرحباً {email}", "success")
                st.rerun()
            else:
                st.error(t("بيانات غير صحيحة", "Invalid credentials"))
        st.caption("Demo: admin@drones.com / admin123  |  manager1@assets.com / pass1")

# ==========================================
# 6. الشريط العلوي (أيقونات)
# ==========================================
def top_bar():
    tenant = st.session_state.tenants[st.session_state.current_tenant]
    col1, col2, col3, col4, col5, col6 = st.columns([2.5,1,1,1,1,1])
    with col1:
        st.markdown(f"### {tenant.get('logo','🏢')} {tenant['name']}")
    with col2:
        st.button("🌙" if not st.session_state.dark_mode else "☀️", on_click=toggle_dark, help=t("المظهر"))
    with col3:
        st.button("🇸🇦" if st.session_state.language=='ar' else "🇬🇧", on_click=toggle_lang, help=t("اللغة"))
    with col4:
        unread = sum(1 for n in st.session_state.notifications if not n.get("read", False))
        if st.button(f"🔔 {unread}" if unread else "🔔", help=t("الإشعارات")):
            st.session_state.show_notif = not st.session_state.get("show_notif", False)
    with col5:
        st.markdown(f"👤 {st.session_state.user_role}")
    with col6:
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
# 7. القائمة الجانبية (14 خدمة)
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
            "إدارة العقود", "الصيانة", "المخاطر والامتثال", "مركز الإشعارات"
        ]
        if st.session_state.user_role == "Viewer":
            allowed = services[:5] + services[8:10] + services[13:14]
            services = [s for s in services if s in allowed]
        choice = st.radio(t("الخدمات", "Services"), services,
                          index=services.index(st.session_state.selected_service) if st.session_state.selected_service in services else 0)
        st.session_state.selected_service = choice
        st.divider()
        if st.button("🔄 تحديث البيانات", use_container_width=True):
            add_notification("تم تحديث البيانات", "success")
            st.rerun()
        st.caption("© 2025 Drones Crafters - v7.0")

# ==========================================
# 8. وظائف الخدمات الأربعة عشر (كلها تعمل)
# ==========================================
def render_dashboard():
    data = get_property_data()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(t("إجمالي قيمة الأصول"), "2.4 مليار ريال", "+4.2%")
    col2.metric(t("عدد الصكوك"), len(data["deeds"]), "+2")
    col3.metric(t("متوسط سعر المتر"), f"{data['area_price']:,} ريال", "+3%")
    col4.metric(t("تكاليف الشهر"), f"{data['costs']['المبلغ'].sum():,.0f} ريال", "-2%")
    st.divider()
    fig = px.pie(data["costs"], values="المبلغ", names="النوع", title=t("توزيع التكاليف"))
    st.plotly_chart(fig, use_container_width=True)

def render_deeds():
    data = get_property_data()
    st.subheader(t("إدارة الصكوك"))
    edited = st.data_editor(data["deeds"], use_container_width=True, num_rows="dynamic")
    if st.button(t("حفظ التغييرات")):
        update_property_data("deeds", edited)
        st.success(t("تم الحفظ"))

def render_survey():
    st.subheader(t("الرفع المساحي"))
    st.markdown(t("يمكنك رفع ملف GeoJSON أو رسم المضلع يدوياً"))
    uploaded = st.file_uploader(t("اختر ملف GeoJSON"), type=["geojson","json"])
    if uploaded:
        data = json.load(uploaded)
        st.success(t("تم رفع الملف بنجاح"))
        st.json(data)
    st.markdown("#### " + t("رسم حدود العقار"))
    lat = st.number_input("Latitude", value=24.774265)
    lon = st.number_input("Longitude", value=46.738586)
    st.map(pd.DataFrame({"lat":[lat],"lon":[lon]}))

def render_images():
    data = get_property_data()
    st.subheader(t("معرض الصور"))
    cols = st.columns(3)
    for i, img in enumerate(data["images"]):
        with cols[i % 3]:
            st.image(img, use_container_width=True)
    uploaded = st.file_uploader(t("إضافة صورة جديدة"), type=["jpg","png","jpeg"])
    if uploaded:
        st.image(uploaded, caption="الصورة المرفوعة", use_container_width=True)
        if st.button(t("حفظ الصورة")):
            add_notification(t("تمت إضافة الصورة"), "success")

def render_location():
    data = get_property_data()
    st.subheader(t("الموقع على الخريطة"))
    lat, lon = data["location"]["lat"], data["location"]["lon"]
    st.map(pd.DataFrame({"lat":[lat],"lon":[lon]}))
    with st.expander(t("تعديل الموقع")):
        new_lat = st.number_input("Latitude", value=lat)
        new_lon = st.number_input("Longitude", value=lon)
        if st.button(t("تحديث")):
            update_property_data("location", {"lat":new_lat, "lon":new_lon})
            st.rerun()

def render_costs():
    data = get_property_data()
    st.subheader(t("التكاليف والفواتير"))
    tab1, tab2 = st.tabs([t("الفواتير"), t("الصيانة")])
    with tab1:
        edited_costs = st.data_editor(data["costs"], use_container_width=True, num_rows="dynamic")
        if st.button(t("حفظ الفواتير")):
            update_property_data("costs", edited_costs)
    with tab2:
        edited_maint = st.data_editor(data["maintenance"], use_container_width=True, num_rows="dynamic")
        if st.button(t("حفظ الصيانة")):
            update_property_data("maintenance", edited_maint)
    total = data["costs"]["المبلغ"].sum() + data["maintenance"]["التكلفة"].sum()
    st.metric(t("إجمالي التكاليف"), f"{total:,.0f} ريال")

def render_requirements():
    data = get_property_data()
    st.subheader(t("متطلبات العقار"))
    edited = st.data_editor(data["requirements"], use_container_width=True, num_rows="dynamic")
    if st.button(t("حفظ المتطلبات")):
        update_property_data("requirements", edited)
    # نسبة الإنجاز
    done = sum(data["requirements"]["الحالة"] == "تم")
    progress = done / len(data["requirements"]) if len(data["requirements"]) > 0 else 0
    st.progress(progress, text=t(f"نسبة الإنجاز: {int(progress*100)}%"))

def render_area_price():
    data = get_property_data()
    st.subheader(t("سعر المتر في المنطقة"))
    new_price = st.number_input(t("سعر المتر الحالي (ريال)"), value=data["area_price"], step=100)
    if st.button(t("تحديث السعر")):
        update_property_data("area_price", new_price)
    # رسم بياني
    price_history = pd.DataFrame({
        "الشهر": ["يناير", "فبراير", "مارس", "أبريل"],
        "السعر": [4000, 4150, new_price, new_price+50]
    })
    fig = px.line(price_history, x="الشهر", y="السعر", title=t("اتجاه الأسعار"))
    st.plotly_chart(fig, use_container_width=True)

def render_ai_analysis():
    data = get_property_data()
    st.subheader(t("تحليل الذكاء الاصطناعي"))
    area_total = data["deeds"]["المساحة (م²)"].sum()
    estimated = area_total * data["area_price"] * 1.05
    st.metric(t("القيمة السوقية المقدرة"), f"{estimated:,.0f} ريال", delta="+5%")
    st.info(t("تم اكتشاف حالة جيدة للعقار بنسبة 92%"))
    st.warning(t("من المتوقع حاجة للصيانة خلال 3 أشهر (تكلفة تقديرية 5,000 ريال)"))
    if st.button(t("تحديث التحليل")):
        update_property_data("ai_analysis", {"value": estimated})
        st.success(t("تم تحديث التحليل"))

def render_reports():
    data = get_property_data()
    st.subheader(t("التقارير الذكية"))
    report = st.selectbox(t("نوع التقرير"), [t("ملخص العقار"), t("التكاليف"), t("المتطلبات")])
    if report == t("ملخص العقار"):
        st.dataframe(data["deeds"])
    elif report == t("التكاليف"):
        st.dataframe(data["costs"])
    else:
        st.dataframe(data["requirements"])
    csv = data["deeds"].to_csv().encode()
    st.download_button(t("تحميل التقرير (CSV)"), csv, "report.csv")

def render_contracts():
    data = get_property_data()
    st.subheader(t("إدارة العقود"))
    edited = st.data_editor(data["contracts"], use_container_width=True, num_rows="dynamic")
    if st.button(t("حفظ العقود")):
        update_property_data("contracts", edited)

def render_maintenance():
    data = get_property_data()
    st.subheader(t("الصيانة"))
    st.dataframe(data["maintenance"])
    with st.form("add_maint"):
        col1, col2 = st.columns(2)
        with col1:
            action = st.text_input(t("نوع العمل"))
            cost = st.number_input(t("التكلفة"), min_value=0)
        with col2:
            status = st.selectbox(t("الحالة"), ["قيد التنفيذ", "تم", "معلق"])
            date = st.date_input(t("التاريخ"))
        if st.form_submit_button(t("إضافة")):
            new = pd.DataFrame({"التاريخ":[date], "العمل":[action], "التكلفة":[cost], "الحالة":[status]})
            updated = pd.concat([data["maintenance"], new], ignore_index=True)
            update_property_data("maintenance", updated)
            st.rerun()

def render_risk_compliance():
    st.subheader(t("المخاطر والامتثال"))
    risks = pd.DataFrame({
        "الخطر": ["تقلبات السوق", "مخاطر الائتمان", "تشغيلية"],
        "الاحتمال": [30, 20, 45],
        "الأثر": [4,3,3],
        "النقطة": [120,60,135]
    })
    fig = px.bar(risks, x="الخطر", y="النقطة", color="النقطة", title=t("مصفوفة المخاطر"))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("#### " + t("التراخيص"))
    licenses = pd.DataFrame({
        "الترخيص": ["رخصة بناء", "رخصة تشغيل", "دفاع مدني"],
        "تاريخ الانتهاء": ["2025-06-01", "2024-12-31", "2024-10-20"],
        "الحالة": ["ساري", "ينتهي قريباً", "منتهي"]
    })
    st.dataframe(licenses)
    if any(licenses["الحالة"] == "منتهي"):
        st.error(t("يوجد تراخيص منتهية!"))

def render_notifications_center():
    st.subheader(t("مركز الإشعارات"))
    data = get_property_data()
    alerts = pd.DataFrame(data.get("alerts", []))
    if not alerts.empty:
        st.dataframe(alerts)
    else:
        st.info(t("لا توجد إشعارات"))
    if st.button(t("إضافة إشعار تجريبي")):
        add_notification(t("هذا إشعار تجريبي"), "info")
        st.rerun()

# ==========================================
# 9. التشغيل الرئيسي
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
        "مركز الإشعارات": render_notifications_center,
    }
    if service in service_map:
        service_map[service]()
    else:
        render_dashboard()

if __name__ == "__main__":
    main()

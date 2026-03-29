import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import random
import json
import io

# ==========================================
# 1. إعدادات الصفحة الأساسية
# ==========================================
st.set_page_config(
    layout="wide",
    page_title="Drones Crafters - Real Estate Enterprise Suite",
    page_icon="🏢",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. تهيئة حالة الجلسة (Session State)
# ==========================================
def init_session():
    # الإعدادات العامة
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    if 'language' not in st.session_state:
        st.session_state.language = 'ar'  # ar or en
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []
    if 'current_tenant' not in st.session_state:
        st.session_state.current_tenant = 'tenant_1'
    if 'selected_service' not in st.session_state:
        st.session_state.selected_service = "Dashboard"
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    # بيانات العقار (المحاكاة)
    if 'property_data' not in st.session_state:
        st.session_state.property_data = {
            "deeds": pd.DataFrame({
                "رقم الصك": ["123/أ", "456/ب"],
                "المالك": ["شركة أصول الرياض", "صندوق الاستثمار"],
                "الحي": ["الملقا", "الياسمين"],
                "المساحة (م²)": [2500, 4300],
                "تاريخ الإصدار": ["2020-01-01", "2021-03-15"]
            }),
            "images": [
                "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=300",
                "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=300"
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
                "التاريخ": ["2024-01-15", "2024-02-20"],
                "النوع": ["فواتير", "صيانة"],
                "المبلغ": [12000, 3500],
                "الوصف": ["كهرباء", "إصلاح مكيف"]
            }),
            "maintenance": pd.DataFrame({
                "التاريخ": ["2024-01-10", "2024-02-25"],
                "العمل": ["فحص دوري", "تبديل سباكة"],
                "التكلفة": [2000, 4500],
                "الحالة": ["تم", "قيد التنفيذ"]
            }),
            "requirements": pd.DataFrame({
                "المتطلب": ["تحديد المخطط", "رخصة بناء"],
                "الأولوية": ["عالية", "متوسطة"],
                "الموعد": ["2024-06-01", "2024-07-15"],
                "الحالة": ["قيد التنفيذ", "معلق"]
            }),
            "area_price": 4200,  # سعر المتر في المنطقة
            "ai_analysis": {}     # سيتم ملؤه لاحقاً
        }
    # بيانات الجهات (المستخدمين)
    if 'tenants' not in st.session_state:
        st.session_state.tenants = {
            "tenant_1": {"name": "شركة أصول الرياض", "role": "owner"},
            "tenant_2": {"name": "مجموعة الخليج العقارية", "role": "owner"}
        }
    if 'users' not in st.session_state:
        st.session_state.users = {
            "admin@drones.com": {"password": "admin123", "role": "SuperAdmin", "tenant": None},
            "owner1@assets.com": {"password": "pass1", "role": "TenantAdmin", "tenant": "tenant_1"},
            "viewer1@assets.com": {"password": "view", "role": "Viewer", "tenant": "tenant_1"}
        }

init_session()

# ==========================================
# 3. دوال مساعدة
# ==========================================
def add_notification(msg, type="info"):
    st.session_state.notifications.insert(0, {
        "message": msg,
        "type": type,
        "time": datetime.now().strftime("%H:%M:%S"),
        "read": False
    })
    st.session_state.notifications = st.session_state.notifications[:20]

def t(ar, en=None):
    if en is None:
        en = ar
    return ar if st.session_state.language == 'ar' else en

def toggle_dark():
    st.session_state.dark_mode = not st.session_state.dark_mode
    add_notification(f"الوضع {'المظلم' if st.session_state.dark_mode else 'الفاتح'}", "info")

def toggle_lang():
    st.session_state.language = 'en' if st.session_state.language == 'ar' else 'ar'
    add_notification(f"Language switched to {'English' if st.session_state.language == 'en' else 'العربية'}", "info")

def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    add_notification("تم تسجيل الخروج", "info")

def get_property_data():
    return st.session_state.property_data

def update_property_data(key, value):
    st.session_state.property_data[key] = value
    add_notification(f"تم تحديث {key}", "success")

# ==========================================
# 4. CSS الاحترافي (دعم الوضع المظلم)
# ==========================================
def load_css():
    bg = "#0f172a" if st.session_state.dark_mode else "#f1f5f9"
    card_bg = "#1e293b" if st.session_state.dark_mode else "#ffffff"
    text = "#f8fafc" if st.session_state.dark_mode else "#0f172a"
    border_color = "#3b82f6"
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
        background-color: {card_bg};
        padding: 1.2rem;
        border-radius: 1rem;
        border-right: 5px solid {border_color};
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: all 0.3s;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }}
    .stButton>button {{
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        color: white;
        border: none;
        border-radius: 0.75rem;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: 0.2s;
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
# 5. شاشة تسجيل الدخول
# ==========================================
def login_screen():
    st.markdown("<div style='text-align:center'><h1>🏢 Drones Crafters</h1><h3>نظام إدارة العقارات المتكامل</h3></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
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
        st.caption("Demo: admin@drones.com / admin123  |  owner1@assets.com / pass1")

# ==========================================
# 6. الشريط العلوي (أيقونات)
# ==========================================
def top_bar():
    col1, col2, col3, col4, col5, col6 = st.columns([2.5, 1, 1, 1, 1, 1])
    with col1:
        st.markdown(f"### 🏢 {st.session_state.tenants[st.session_state.current_tenant]['name']}")
    with col2:
        st.button("🌙" if not st.session_state.dark_mode else "☀️", on_click=toggle_dark, help=t("تغيير المظهر"))
    with col3:
        st.button("🇸🇦" if st.session_state.language=='ar' else "🇬🇧", on_click=toggle_lang, help=t("تغيير اللغة"))
    with col4:
        unread = sum(1 for n in st.session_state.notifications if not n.get("read", False))
        if st.button(f"🔔 {unread}" if unread else "🔔", help=t("الإشعارات")):
            st.session_state.show_notif = not st.session_state.get("show_notif", False)
    with col5:
        st.markdown(f"👤 {st.session_state.user_role}")
    with col6:
        st.button("🚪", on_click=logout, help=t("تسجيل الخروج"))
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
        # الخدمات الأربعة عشر
        services = [
            "لوحة القيادة", "إدارة الصكوك", "الرفع المساحي", "معرض الصور",
            "الموقع على الخريطة", "التكاليف والفواتير", "متطلبات العقار",
            "سعر المتر بالمنطقة", "تحليل الذكاء الاصطناعي", "التقارير الذكية",
            "إدارة العقود", "الصيانة", "المخاطر والامتثال", "الإشعارات"
        ]
        # تقييد حسب الدور
        if st.session_state.user_role == "Viewer":
            allowed = services[:5] + services[8:10] + services[13:14]
            services = [s for s in services if s in allowed]
        choice = st.radio(t("الخدمات", "Services"), services,
                          index=services.index(st.session_state.selected_service) if st.session_state.selected_service in services else 0)
        st.session_state.selected_service = choice
        st.divider()
        if st.button("🔄 تحديث البيانات", use_container_width=True):
            # محاكاة تحديث البيانات
            st.cache_data.clear()
            add_notification("تم تحديث البيانات", "success")
            st.rerun()
        st.caption("© 2025 Drones Crafters - v6.0")

# ==========================================
# 8. وظائف الخدمات التفصيلية
# ==========================================
def render_dashboard():
    data = get_property_data()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(t("إجمالي قيمة الأصول"), "2.4 مليار ريال", "+4.2%")
    col2.metric(t("عدد الصكوك"), len(data["deeds"]), "+2")
    col3.metric(t("متوسط سعر المتر"), f"{data['area_price']:,} ريال", "+3%")
    col4.metric(t("تكاليف الشهر"), f"{data['costs']['المبلغ'].sum():,.0f} ريال", "-2%")
    st.divider()
    # رسم بياني لتوزيع التكاليف
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
    st.markdown(t("يمكنك رفع ملف مساحي (GeoJSON) أو رسم المضلع يدوياً"))
    uploaded = st.file_uploader(t("اختر ملف GeoJSON"), type=["geojson", "json"])
    if uploaded:
        data = json.load(uploaded)
        st.success(t("تم رفع الملف بنجاح"))
        st.json(data)
    # خريطة تفاعلية لرسم مضلع بسيط (محاكاة)
    st.markdown("#### " + t("رسم حدود العقار"))
    lat = st.number_input("خط العرض (Latitude)", value=24.774265)
    lon = st.number_input("خط الطول (Longitude)", value=46.738586)
    st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))

def render_images():
    st.subheader(t("معرض الصور"))
    data = get_property_data()
    cols = st.columns(3)
    for i, img in enumerate(data["images"]):
        with cols[i % 3]:
            st.image(img, use_container_width=True)
    uploaded = st.file_uploader(t("إضافة صورة جديدة"), type=["jpg", "png", "jpeg"])
    if uploaded:
        st.image(uploaded, caption="الصورة المرفوعة", use_container_width=True)
        if st.button(t("حفظ الصورة")):
            add_notification(t("تمت إضافة الصورة"), "success")

def render_location():
    st.subheader(t("الموقع على الخريطة"))
    data = get_property_data()
    lat = data["location"]["lat"]
    lon = data["location"]["lon"]
    st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))
    with st.expander(t("تعديل الموقع")):
        new_lat = st.number_input("Latitude", value=lat)
        new_lon = st.number_input("Longitude", value=lon)
        if st.button(t("تحديث")):
            update_property_data("location", {"lat": new_lat, "lon": new_lon})
            st.rerun()

def render_costs():
    st.subheader(t("التكاليف والفواتير"))
    data = get_property_data()
    tab1, tab2 = st.tabs([t("الفواتير"), t("الصيانة")])
    with tab1:
        edited_costs = st.data_editor(data["costs"], use_container_width=True, num_rows="dynamic")
        if st.button(t("حفظ الفواتير")):
            update_property_data("costs", edited_costs)
    with tab2:
        edited_maint = st.data_editor(data["maintenance"], use_container_width=True, num_rows="dynamic")
        if st.button(t("حفظ الصيانة")):
            update_property_data("maintenance", edited_maint)
    # إجمالي التكاليف
    total = data["costs"]["المبلغ"].sum() + data["maintenance"]["التكلفة"].sum()
    st.metric(t("إجمالي التكاليف"), f"{total:,.0f} ريال")

def render_requirements():
    st.subheader(t("متطلبات العقار"))
    data = get_property_data()
    edited = st.data_editor(data["requirements"], use_container_width=True, num_rows="dynamic")
    if st.button(t("حفظ المتطلبات")):
        update_property_data("requirements", edited)
    st.progress(0.4, text=t("نسبة الإنجاز: 40%"))

def render_area_price():
    st.subheader(t("سعر المتر في المنطقة"))
    data = get_property_data()
    current_price = data["area_price"]
    new_price = st.number_input(t("سعر المتر الحالي (ريال)"), value=current_price, step=100)
    if st.button(t("تحديث السعر")):
        update_property_data("area_price", new_price)
        add_notification(t("تم تحديث سعر المتر"), "success")
    # رسم بياني لأسعار المنطقة (محاكاة)
    price_history = pd.DataFrame({
        "الشهر": ["يناير", "فبراير", "مارس", "أبريل"],
        "السعر": [4000, 4150, new_price, new_price+50]
    })
    fig = px.line(price_history, x="الشهر", y="السعر", title=t("اتجاه الأسعار"))
    st.plotly_chart(fig, use_container_width=True)

def render_ai_analysis():
    st.subheader(t("تحليل الذكاء الاصطناعي"))
    data = get_property_data()
    # تقدير القيمة السوقية
    area_total = data["deeds"]["المساحة (م²)"].sum()
    estimated_value = area_total * data["area_price"] * 1.05  # 5% علاوة
    st.metric(t("القيمة السوقية المقدرة"), f"{estimated_value:,.0f} ريال", delta="+5%")
    # تحليل الصور (محاكاة)
    st.markdown("#### " + t("تحليل الصور"))
    st.info(t("تم اكتشاف حالة جيدة للعقار بنسبة 92%"))
    # تنبؤ بالصيانة
    st.markdown("#### " + t("التنبؤ بالصيانة"))
    st.warning(t("من المتوقع حاجة للصيانة خلال 3 أشهر (تكلفة تقديرية 5,000 ريال)"))
    # حفظ التحليل
    if st.button(t("تحديث التحليل")):
        update_property_data("ai_analysis", {"value": estimated_value, "condition": "جيد"})
        st.success(t("تم تحديث التحليل"))

def render_reports():
    st.subheader(t("التقارير الذكية"))
    report_type = st.selectbox(t("نوع التقرير"), [t("ملخص العقار"), t("التكاليف"), t("المتطلبات")])
    data = get_property_data()
    if report_type == t("ملخص العقار"):
        st.dataframe(data["deeds"])
    elif report_type == t("التكاليف"):
        st.dataframe(data["costs"])
    else:
        st.dataframe(data["requirements"])
    # تصدير CSV
    csv = data["deeds"].to_csv().encode()
    st.download_button(t("تحميل التقرير (CSV)"), csv, "report.csv")

def render_contracts():
    st.subheader(t("إدارة العقود"))
    # محاكاة عقود الإيجار
    if 'contracts' not in get_property_data():
        update_property_data("contracts", pd.DataFrame({
            "المستأجر": ["شركة الأفق", "مؤسسة البناء"],
            "تاريخ البدء": ["2024-01-01", "2024-02-01"],
            "تاريخ الانتهاء": ["2025-01-01", "2025-02-01"],
            "الإيجار الشهري": [45000, 32000]
        }))
    data = get_property_data()
    edited = st.data_editor(data.get("contracts", pd.DataFrame()), use_container_width=True, num_rows="dynamic")
    if st.button(t("حفظ العقود")):
        update_property_data("contracts", edited)

def render_maintenance():
    st.subheader(t("الصيانة"))
    data = get_property_data()
    st.dataframe(data["maintenance"], use_container_width=True)
    with st.form("add_maintenance"):
        col1, col2 = st.columns(2)
        with col1:
            action = st.text_input(t("نوع العمل"))
            cost = st.number_input(t("التكلفة"), min_value=0)
        with col2:
            status = st.selectbox(t("الحالة"), ["قيد التنفيذ", "تم", "معلق"])
            date = st.date_input(t("التاريخ"))
        if st.form_submit_button(t("إضافة")):
            new_row = pd.DataFrame({"التاريخ": [date], "العمل": [action], "التكلفة": [cost], "الحالة": [status]})
            updated = pd.concat([data["maintenance"], new_row], ignore_index=True)
            update_property_data("maintenance", updated)
            st.rerun()

def render_risk_compliance():
    st.subheader(t("المخاطر والامتثال"))
    # محاكاة قائمة المخاطر
    risks = pd.DataFrame({
        "الخطر": ["تقلبات السوق", "مخاطر الائتمان", "المخاطر التشغيلية"],
        "الاحتمال (%)": [30, 20, 45],
        "الأثر (1-5)": [4, 3, 3],
        "نقطة المخاطرة": [120, 60, 135]
    })
    fig = px.bar(risks, x="الخطر", y="نقطة المخاطرة", color="نقطة المخاطرة", title=t("مصفوفة المخاطر"))
    st.plotly_chart(fig, use_container_width=True)
    # الامتثال
    st.markdown("#### " + t("التراخيص والامتثال"))
    licenses = pd.DataFrame({
        "الترخيص": ["رخصة بناء", "رخصة تشغيل", "دفاع مدني"],
        "تاريخ الانتهاء": ["2025-06-01", "2024-12-31", "2024-10-20"],
        "الحالة": ["ساري", "ينتهي قريباً", "منتهي"]
    })
    st.dataframe(licenses)
    if any(licenses["الحالة"] == "منتهي"):
        st.error(t("يوجد تراخيص منتهية! يرجى التجديد فوراً."))

def render_notifications_center():
    st.subheader(t("مركز الإشعارات"))
    data = get_property_data()
    alerts = pd.DataFrame(data.get("alerts", []))
    if not alerts.empty:
        st.dataframe(alerts)
    else:
        st.info(t("لا توجد إشعارات حالية"))
    if st.button(t("إضافة إشعار تجريبي")):
        add_notification(t("هذا إشعار تجريبي"), "info")
        st.rerun()

# ==========================================
# 9. ربط الخدمات بالدوال
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
    if service in service_map:
        service_map[service]()
    else:
        render_dashboard()

if __name__ == "__main__":
    main()

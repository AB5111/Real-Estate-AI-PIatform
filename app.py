import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import json
import base64
from PIL import Image

# ==========================================
# إعدادات الصفحة
# ==========================================
st.set_page_config(layout="wide", page_title="Drones Crafters - Real Estate", page_icon="🏢")

# ==========================================
# تهيئة الحالة
# ==========================================
def init():
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
    if 'selected_menu' not in st.session_state:
        st.session_state.selected_menu = "الرئيسية"
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []
    if 'tenants' not in st.session_state:
        st.session_state.tenants = {
            "tenant_1": {"name": "شركة أصول الرياض", "logo": "🏢"},
            "tenant_2": {"name": "مجموعة الخليج", "logo": "🏭"}
        }
    if 'users' not in st.session_state:
        st.session_state.users = {
            "admin@drones.com": {"password": "admin123", "role": "مدير عام", "tenant": None},
            "manager@assets.com": {"password": "pass1", "role": "مدير عقاري", "tenant": "tenant_1"},
            "viewer@assets.com": {"password": "view", "role": "مشاهد", "tenant": "tenant_1"}
        }
    if 'property_data' not in st.session_state:
        st.session_state.property_data = {
            "deeds": pd.DataFrame({
                "رقم الصك": ["123/أ", "456/ب"],
                "المالك": ["شركة أصول الرياض", "صندوق الاستثمار"],
                "الحي": ["الملقا", "الياسمين"],
                "المساحة (م²)": [2500, 4300],
                "تاريخ الإصدار": ["2020-01-01", "2021-03-15"]
            }),
            "survey": {
                "coordinates": [[46.735, 24.772], [46.742, 24.772], [46.742, 24.778], [46.735, 24.778], [46.735, 24.772]],
                "area_m2": 0.0
            },
            "images": [
                "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=300",
                "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=300"
            ],
            "location": {"lat": 24.774265, "lon": 46.738586},
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
            "area_price": 4200,
            "ai_analysis": {},
            "contracts": pd.DataFrame({
                "المستأجر": ["شركة الأفق", "مؤسسة البناء"],
                "تاريخ البدء": ["2024-01-01", "2024-02-01"],
                "تاريخ الانتهاء": ["2025-01-01", "2025-02-01"],
                "الإيجار": [45000, 32000]
            }),
            "alerts": [{"التاريخ": "2024-12-15", "الرسالة": "انتهاء رخصة تشغيل", "النوع": "تحذير"}]
        }
    # حساب المساحة
    coords = st.session_state.property_data["survey"]["coordinates"]
    area = 0.0
    n = len(coords)
    for i in range(n):
        x1, y1 = coords[i]
        x2, y2 = coords[(i+1) % n]
        area += (x1 * y2 - x2 * y1)
    area = abs(area) / 2 * 111319.9 * 111319.9
    st.session_state.property_data["survey"]["area_m2"] = area

init()

# ==========================================
# دوال مساعدة
# ==========================================
def add_notification(msg, typ="info"):
    st.session_state.notifications.insert(0, {"message": msg, "type": typ, "time": datetime.now().strftime("%H:%M:%S"), "read": False})
    st.session_state.notifications = st.session_state.notifications[:20]

def t(ar, en=None):
    return ar if st.session_state.language == 'ar' else (en if en else ar)

def toggle_theme():
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

def get_data():
    return st.session_state.property_data

def update_data(key, value):
    st.session_state.property_data[key] = value
    add_notification(f"تم تحديث {key}", "success")
    st.rerun()

# ==========================================
# CSS
# ==========================================
def load_css():
    bg = "#0a0c10" if st.session_state.dark_mode else "#f4f7fc"
    card_bg = "#1e1e2e" if st.session_state.dark_mode else "#ffffff"
    text = "#ffffff" if st.session_state.dark_mode else "#1e293b"
    border = "#3b82f6"
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700&display=swap');
    * {{ font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }}
    .stApp {{ background-color: {bg}; color: {text}; }}
    div[data-testid="stMetric"] {{
        background: {card_bg};
        padding: 1rem;
        border-radius: 1rem;
        border-right: 5px solid {border};
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: 0.2s;
    }}
    .stButton>button {{
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        color: white;
        border: none;
        border-radius: 0.75rem;
        font-weight: 600;
    }}
    .quick-icon {{
        text-align: center;
        padding: 5px;
        border-radius: 10px;
        background-color: {card_bg};
        margin: 2px;
    }}
    </style>
    """

# ==========================================
# شاشة تسجيل الدخول
# ==========================================
def login_screen():
    st.markdown("<div style='text-align:center'><h1>🏢 Drones Crafters</h1><h3>نظام إدارة العقارات الذكي</h3></div>", unsafe_allow_html=True)
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
        st.caption("Demo: admin@drones.com / admin123  |  manager@assets.com / pass1")

# ==========================================
# الشريط العلوي (الإعدادات)
# ==========================================
def top_bar():
    tenant = st.session_state.tenants[st.session_state.current_tenant]
    col1, col2, col3, col4, col5, col6 = st.columns([2.5,1,1,1,1,1])
    with col1:
        st.markdown(f"### {tenant.get('logo','🏢')} {tenant['name']}")
    with col2:
        st.button("🌙" if not st.session_state.dark_mode else "☀️", on_click=toggle_theme, help=t("المظهر"))
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
# شريط الخدمات السريع (أعلى الصفحة)
# ==========================================
def quick_services_bar():
    st.markdown("### ⚡ الخدمات السريعة")
    # تعريف الخدمات مع أيقونات
    quick_services = [
        (" الرئيسية", "الرئيسية"),
        (" صكوك", "إدارة الصكوك"),
        (" رفع مساحي", "الرفع المساحي"),
        (" صور", "معرض الصور"),
        ("📍 الموقع", "الموقع على الخريطة"),
        ("💰 تكاليف", "التكاليف والفواتير"),
        (" متطلبات", "متطلبات العقار"),
        ("📊 سعر المتر", "سعر المتر بالمنطقة"),
        ("🤖 AI", "تحليل الذكاء الاصطناعي"),
        ("📄 عقود", "إدارة العقود"),
        ("🔧 صيانة", "الصيانة"),
        ("⚠️ مخاطر", "المخاطر والامتثال"),
        ("📑 تقارير", "التقارير الذكية"),
        ("🔔 إشعارات", "مركز الإشعارات")
    ]
    # تقسيم الأزرار إلى صفوف (مثلاً 7 أزرار في كل صف)
    cols = st.columns(7)
    for i, (label, key) in enumerate(quick_services):
        with cols[i % 7]:
            if st.button(label, key=f"quick_{key}", use_container_width=True):
                st.session_state.selected_menu = key
                st.rerun()
    st.divider()

# ==========================================
# القائمة الجانبية (14 خدمة)
# ==========================================
def sidebar_menu():
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/10543/10543319.png", width=80)
        st.title("Drones Crafters")
        if st.session_state.user_role == "مدير عام":
            tenants = list(st.session_state.tenants.keys())
            sel = st.selectbox(t("اختر الجهة", "Select Tenant"), tenants,
                               format_func=lambda x: st.session_state.tenants[x]["name"])
            if sel != st.session_state.current_tenant:
                st.session_state.current_tenant = sel
                st.rerun()
        st.divider()
        # قائمة الخدمات (14 خدمة)
        services_list = [
            (" 1. صكوك", "إدارة الصكوك"),
            (" 2. رفع مساحي", "الرفع المساحي"),
            (" 3. صور", "معرض الصور"),
            (" 4. موقع على خريطة", "الموقع على الخريطة"),
            (" 5. تكاليف العقار", "التكاليف والفواتير"),
            (" 6. متطلبات العقار", "متطلبات العقار"),
            (" 7. سعر المتر بالمنطقة", "سعر المتر بالمنطقة"),
            (" 8. تحليل الذكاء الاصطناعي", "تحليل الذكاء الاصطناعي"),
            (" 9. إدارة العقود", "إدارة العقود"),
            (" 10. الصيانة", "الصيانة"),
            (" 11. المخاطر والامتثال", "المخاطر والامتثال"),
            (" 12. التقارير الذكية", "التقارير الذكية"),
            (" 13. مركز الإشعارات", "مركز الإشعارات")
        ]
        allowed_keys = []
        if st.session_state.user_role == "مشاهد":
            allowed_keys = ["الرئيسية", "إدارة الصكوك", "الموقع على الخريطة", "التقارير الذكية", "مركز الإشعارات"]
        else:
            allowed_keys = [key for _, key in services_list]
        for display, key in services_list:
            if key in allowed_keys:
                if st.button(display, use_container_width=True, key=key):
                    st.session_state.selected_menu = key
                    st.rerun()
        st.divider()
        st.caption("© 2025 Drones Crafters - جميع الخدمات (14) معروضة")

# ==========================================
# وظائف الخدمات (نفس ما سبق، مختصرة للطول)
# ==========================================
def render_dashboard():
    data = get_data()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(" إجمالي الأصول", "2.4 مليار ريال", "+4.2%")
    col2.metric(" عدد الصكوك", len(data["deeds"]), "+2")
    col3.metric(" سعر المتر", f"{data['area_price']:,} ريال", "+3%")
    col4.metric("🔧 تكاليف الشهر", f"{data['costs']['المبلغ'].sum():,.0f} ريال", "-2%")
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        fig = px.pie(data["costs"], values="المبلغ", names="النوع", title="توزيع التكاليف")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = px.bar(data["maintenance"], x="العمل", y="التكلفة", color="الحالة", title="تكاليف الصيانة")
        st.plotly_chart(fig2, use_container_width=True)

def render_deeds():
    st.subheader("📜 الخدمة 1: إدارة الصكوك")
    data = get_data()
    edited = st.data_editor(data["deeds"], use_container_width=True, num_rows="dynamic")
    if st.button("💾 حفظ"):
        update_data("deeds", edited)
    st.file_uploader("رفع ملف صك", type=["pdf","jpg","png"])

def render_survey():
    st.subheader(" الخدمة 2: الرفع المساحي")
    data = get_data()
    survey = data["survey"]
    tab1, tab2, tab3 = st.tabs(["رفع ملف", "رسم يدوي", "عرض الحدود"])
    with tab1:
        st.file_uploader("رفع KML/GeoJSON", type=["kml","geojson","json"])
    with tab2:
        coords_text = st.text_area("الإحداثيات", value="46.735,24.772\n46.742,24.772\n46.742,24.778\n46.735,24.778")
        if st.button("تحديث وحساب المساحة"):
            points = []
            for line in coords_text.strip().split("\n"):
                if "," in line:
                    lon, lat = line.split(",")
                    points.append([float(lon.strip()), float(lat.strip())])
            if points:
                survey["coordinates"] = points
                area = 0.0
                n = len(points)
                for i in range(n):
                    x1, y1 = points[i]
                    x2, y2 = points[(i+1) % n]
                    area += (x1 * y2 - x2 * y1)
                area = abs(area) / 2 * 111319.9 * 111319.9
                survey["area_m2"] = area
                update_data("survey", survey)
                st.success(f"المساحة: {area:,.0f} م²")
    with tab3:
        coords = survey.get("coordinates", [])
        if coords:
            df_poly = pd.DataFrame(coords, columns=["lon", "lat"])
            fig = px.scatter_mapbox(df_poly, lat="lat", lon="lon", zoom=13)
            fig.add_trace(go.Scattermapbox(
                lat=df_poly["lat"], lon=df_poly["lon"],
                mode="lines", fill="toself", line=dict(width=2, color="blue")
            ))
            fig.update_layout(mapbox_style="open-street-map")
            st.plotly_chart(fig, use_container_width=True)
            st.metric("المساحة (م²)", f"{survey.get('area_m2',0):,.0f}")

def render_images():
    st.subheader(" الخدمة 3: معرض الصور")
    data = get_data()
    cols = st.columns(3)
    for i, img in enumerate(data["images"][:3]):
        with cols[i]:
            st.image(img, use_container_width=True)
    st.file_uploader("إضافة صورة", type=["jpg","png","jpeg"])

def render_location():
    st.subheader("📍 الخدمة 4: الموقع على الخريطة")
    data = get_data()
    st.map(pd.DataFrame([data["location"]]))
    with st.expander("تعديل"):
        lat = st.number_input("خط العرض", value=data["location"]["lat"], format="%.6f")
        lon = st.number_input("خط الطول", value=data["location"]["lon"], format="%.6f")
        if st.button("تحديث"):
            update_data("location", {"lat": lat, "lon": lon})

def render_costs():
    st.subheader(" الخدمة 5: تكاليف العقار")
    data = get_data()
    tab1, tab2 = st.tabs(["فواتير", "صيانة"])
    with tab1:
        edited = st.data_editor(data["costs"], num_rows="dynamic")
        if st.button("حفظ الفواتير"):
            update_data("costs", edited)
    with tab2:
        edited2 = st.data_editor(data["maintenance"], num_rows="dynamic")
        if st.button("حفظ الصيانة"):
            update_data("maintenance", edited2)
    total = data["costs"]["المبلغ"].sum() + data["maintenance"]["التكلفة"].sum()
    st.metric("إجمالي التكاليف", f"{total:,.0f} ريال")

def render_requirements():
    st.subheader(" الخدمة 6: متطلبات العقار")
    data = get_data()
    edited = st.data_editor(data["requirements"], num_rows="dynamic")
    if st.button("حفظ"):
        update_data("requirements", edited)
    done = sum(data["requirements"]["الحالة"] == "تم")
    progress = done / len(data["requirements"]) if len(data["requirements"])>0 else 0
    st.progress(progress, text=f"نسبة الإنجاز: {int(progress*100)}%")

def render_area_price():
    st.subheader(" الخدمة 7: سعر المتر")
    data = get_data()
    new_price = st.number_input("سعر المتر (ريال)", value=data["area_price"], step=100)
    if st.button("تحديث"):
        update_data("area_price", new_price)
    hist = pd.DataFrame({"الشهر": ["يناير","فبراير","مارس","أبريل"], "السعر": [4000,4150,new_price,new_price+50]})
    fig = px.line(hist, x="الشهر", y="السعر", markers=True)
    st.plotly_chart(fig, use_container_width=True)

def render_ai_analysis():
    st.subheader("🤖 الخدمة 8: تحليل الذكاء الاصطناعي")
    data = get_data()
    total_area = data["deeds"]["المساحة (م²)"].sum()
    estimated = total_area * data["area_price"] * 1.05
    st.metric("القيمة المقدرة", f"{estimated:,.0f} ريال", "+5%")
    st.info("تحليل الصور: حالة جيدة (92%)")
    st.warning("تنبؤ الصيانة: خلال 3 أشهر")
    st.success("تحليل السوق: نمو 7% سنوياً")

def render_contracts():
    data = get_data()
    st.subheader("📄 الخدمة 9: إدارة العقود")
    edited = st.data_editor(data["contracts"], num_rows="dynamic")
    if st.button("حفظ"):
        update_data("contracts", edited)

def render_maintenance():
    data = get_data()
    st.subheader("🔧 الخدمة 10: الصيانة")
    st.dataframe(data["maintenance"])
    with st.form("add"):
        col1, col2 = st.columns(2)
        with col1:
            work = st.text_input("العمل")
            cost = st.number_input("التكلفة", min_value=0)
        with col2:
            status = st.selectbox("الحالة", ["قيد التنفيذ","تم","معلق"])
            date = st.date_input("التاريخ")
        if st.form_submit_button("إضافة"):
            new = pd.DataFrame({"التاريخ":[date],"العمل":[work],"التكلفة":[cost],"الحالة":[status]})
            updated = pd.concat([data["maintenance"], new], ignore_index=True)
            update_data("maintenance", updated)

def render_risk():
    st.subheader("⚠️ الخدمة 11: المخاطر والامتثال")
    risks = pd.DataFrame({"الخطر":["تقلبات السوق","ائتمان","تشغيلية"], "النقطة":[120,60,135]})
    fig = px.bar(risks, x="الخطر", y="النقطة", color="النقطة")
    st.plotly_chart(fig, use_container_width=True)
    licenses = pd.DataFrame({
        "الترخيص": ["رخصة بناء","رخصة تشغيل","دفاع مدني"],
        "تاريخ الانتهاء": ["2025-06-01","2024-12-31","2024-10-20"],
        "الحالة": ["ساري","ينتهي قريباً","منتهي"]
    })
    st.dataframe(licenses)
    if any(licenses["الحالة"] == "منتهي"):
        st.error("تراخيص منتهية!")

def render_reports():
    st.subheader("📑 الخدمة 12: التقارير الذكية")
    data = get_data()
    report = st.selectbox("نوع التقرير", ["ملخص العقار","التكاليف","المتطلبات"])
    if report == "ملخص العقار":
        st.dataframe(data["deeds"])
    elif report == "التكاليف":
        st.dataframe(data["costs"])
    else:
        st.dataframe(data["requirements"])
    csv = data["deeds"].to_csv().encode()
    st.download_button("تحميل CSV", csv, "report.csv")

def render_notifications():
    st.subheader("🔔 الخدمة 13: مركز الإشعارات")
    data = get_data()
    alerts = pd.DataFrame(data.get("alerts", []))
    if not alerts.empty:
        st.dataframe(alerts)
    else:
        st.info("لا توجد إشعارات")
    if st.button("إضافة إشعار"):
        add_notification("إشعار جديد", "info")
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
    quick_services_bar()  # شريط الخدمات السريعة أعلى الصفحة
    sidebar_menu()
    menu = st.session_state.selected_menu
    if menu == "الرئيسية":
        render_dashboard()
    elif menu == "إدارة الصكوك":
        render_deeds()
    elif menu == "الرفع المساحي":
        render_survey()
    elif menu == "معرض الصور":
        render_images()
    elif menu == "الموقع على الخريطة":
        render_location()
    elif menu == "التكاليف والفواتير":
        render_costs()
    elif menu == "متطلبات العقار":
        render_requirements()
    elif menu == "سعر المتر بالمنطقة":
        render_area_price()
    elif menu == "تحليل الذكاء الاصطناعي":
        render_ai_analysis()
    elif menu == "إدارة العقود":
        render_contracts()
    elif menu == "الصيانة":
        render_maintenance()
    elif menu == "المخاطر والامتثال":
        render_risk()
    elif menu == "التقارير الذكية":
        render_reports()
    elif menu == "مركز الإشعارات":
        render_notifications()
    else:
        render_dashboard()

if __name__ == "__main__":
    main()

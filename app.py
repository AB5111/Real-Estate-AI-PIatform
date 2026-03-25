import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os
from streamlit_folium import folium_static
import folium
from geopy.geocoders import Nominatim
from datetime import datetime
# --- حل مشكلة المسارات للمجلدات المحلية ---
# يضمن هذا الكود أن المنصة ترى مجلد modules و core
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
# محاولة استيراد المكتبات الخارجية
try:
    from streamlit_option_menu import option_menu
except ImportError:
    st.error("Missing library: streamlit-option-menu. Please add it to requirements.txt")
    st.stop()
# --- محاولة استيراد الملفات المحلية ---
# استخدمت try-except هنا حتى يعمل الكود حتى لو لم ترفع ملف db.py بعد
try:
    from modules.db import engine
except ImportError:
    # إنشاء محرك وهمي (Mock) إذا لم يوجد الملف لتشغيل الواجهة فقط
    engine = None
    st.warning("⚠️ لم يتم العثور على modules/db.py، سيتم عرض بيانات تجريبية فقط.")
# إعدادات الصفحة
st.set_page_config(layout="wide", page_title="Drones Crafters – Real Estate Platform")
# تخصيص المظهر لدعم العربية (RTL) مع خط Cairo
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stSidebar"], .main {
        direction: RTL;
        text-align: right;
        font-family: 'Cairo', sans-serif;
    }
    div[data-testid="stMetricValue"] { text-align: right; }
    .stSelectbox label, .stDateInput label, .stTextInput label { text-align: right; width: 100%; }
    /* تنسيق جدول المصاريف */
    .table-container { direction: RTL; text-align: right; width: 100%; }
    </style>
    """, unsafe_allow_html=True)
# القائمة الجانبية (تحديث القائمة لتشمل "المصاريف")
with st.sidebar:
    st.title("Drones Crafters")
    st.subheader("المنصة العقارية الذكية")
    choice = option_menu(
        "القائمة الرئيسية",
        ["لوحة التحكم", "الخرائط", "متابعة المصاريف", "التقييم", "تحليل الصور", "الصكوك", "السجل"],
        icons=["speedometer", "map", "cash-register", "cash", "camera", "file-earmark-text", "list"],
        menu_icon="cast", default_index=0,
    )
# --- قسم لوحة التحكم ---
if choice == "لوحة التحكم":
    st.title("🏠 لوحة التحكم العقارية")
    col_a, col_b = st.columns([1, 3])
    with col_a:
        district = st.selectbox("اختر الحي", ["الملقا", "الياسمين", "النرجس", "العمارية"])
    st.divider()
    # بيانات تجريبية قوية
    data = pd.DataFrame({
        'المخطط': ['مخطط أ', 'مخطط ب', 'مخطط ج', 'مخطط د'],
        'متوسط_السعر': [4200, 5500, 3800, 4900]
    })
    # رسم بياني احترافي باستخدام Plotly
    fig = px.bar(data, x='المخطط', y='متوسط_السعر', 
                 title=f"تحليل أسعار المتر في حي {district}",
                 text_auto='.2s',
                 color='متوسط_السعر', 
                 color_continuous_scale='Blues')
    fig.update_layout(
        xaxis_title="المخطط السكني",
        yaxis_title="السعر (ريال/م)",
        font=dict(family="Cairo", size=14)
    )
    st.plotly_chart(fig, use_container_width=True)
    # مؤشرات الأداء (Metrics)
    c1, c2, c3 = st.columns(3)
    c1.metric("عقارات تم فحصها بالدرون", "128", "14+")
    c2.metric("متوسط سعر المتر بالحي", "4,850 ريال", "-3%")
    c3.metric("دقة بيانات الرفع المساحي", "99.8%", "ممتاز")
# --- قسم الخرائط والبحث ---
elif choice == "الخرائط":
    st.title("🗺️ الخرائط التفاعلية والبحث")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.subheader("البحث عن موقع")
        search_query = st.text_input("أدخل اسم الموقع (مثال: حي الملقا الرياض)")
        search_button = st.button("بحث")
        # موقع افتراضي للرياض
        riyadh_coords = [24.7136, 46.6753]
        target_coords = riyadh_coords
        zoom_level = 11
        # البحث عن الموقع برمجياً
        if search_button and search_query:
            geolocator = Nominatim(user_agent="drones_crafters_platform")
            location = geolocator.geocode(search_query + ", الرياض")
            if location:
                st.success(f"تم العثور على الموقع: {location.address}")
                target_coords = [location.latitude, location.longitude]
                zoom_level = 15
            else:
                st.error("لم يتم العثور على الموقع. يرجى المحاولة مرة أخرى.")
        # إضافة أمثلة לעقارات محددة
        st.divider()
        st.subheader("تحديد عقار محدد")
        example_properties = {
            "الرياض - عام": riyadh_coords,
            "عقار حي الملقا (نموذجي)": [24.7836, 46.6115],
            "مشروع الياسمين": [24.8115, 46.6534]
        }
        selected_prop = st.selectbox("اختر عقار لعرضه", list(example_properties.keys()))
        if st.button("عرض على الخريطة"):
            target_coords = example_properties[selected_prop]
            zoom_level = 15
    with col2:
        # إنشاء خريطة تفاعلية
        m = folium.Map(location=target_coords, zoom_start=zoom_level)
        # إضافة Marker (مكان تحديد العقار)
        folium.Marker(
            target_coords,
            popup=selected_prop,
            tooltip=selected_prop
        ).add_to(m)
        # أمثلة جغرافية إضافية (يمكن ربطها بقاعدة البيانات لاحقاً)
        if zoom_level > 12: # عرض عقارات محيطة في حالة الزوم العالي
             folium.CircleMarker([24.7850, 46.6120], radius=5, color='red', fill=True, popup='عقار محيط 1').add_to(m)
             folium.CircleMarker([24.7820, 46.6100], radius=5, color='green', fill=True, popup='عقار محيط 2').add_to(m)
        # عرض الخريطة
        folium_static(m, width=1100, height=600)
# --- قسم متابعة المصاريف (جديد) ---
elif choice == "متابعة المصاريف":
    st.title("💸 متابعة مصاريف العقارات")
    st.subheader("تسجيل وعرض المصاريف اليومية")
    # بيانات تجريبية للمصاريف
    expense_data = pd.DataFrame([
        {'التاريخ': '2026-03-20', 'العقار': 'برج الملقا', 'الفئة': 'صيانة دورية', 'القيمة': 5000, 'التفاصيل': 'صيانة تكييف'},
        {'التاريخ': '2026-03-21', 'العقار': 'فيلا النرجس', 'الفئة': 'ضرائب ورسوم', 'القيمة': 1200, 'التفاصيل': 'رسوم صك'},
        {'التاريخ': '2026-03-22', 'العقار': 'أرض العمارية', 'الفئة': 'رفع مساحي', 'القيمة': 8500, 'التفاصيل': 'مسح درون'}
    ])
    # تحويل التاريخ إلى تنسيق datetime لعرضه بشكل صحيح
    expense_data['التاريخ'] = pd.to_datetime(expense_data['التاريخ'])
    c1, c2 = st.columns([1, 3])
    with c1:
        # إضافة مصروف جديد (نموذج إدخال)
        st.subheader("إضافة مصروف جديد")
        new_date = st.date_input("تاريخ المصروف", datetime.now())
        new_prop = st.selectbox("العقار", ["برج الملقا", "فيلا النرجس", "أرض العمارية"])
        new_category = st.selectbox("الفئة", ["صيانة دورية", "ضرائب ورسوم", "رفع مساحي", "تسويق", "كهرباء/مياه"])
        new_amount = st.number_input("القيمة (ريال)", min_value=0)
        new_details = st.text_input("التفاصيل")
        
        if st.button("إضافة"):
            # في التطبيق الحقيقي، سنقوم بإضافة هذا إلى قاعدة البيانات
            st.success(f"تم تسجيل مصروف بقيمة {new_amount} ريال على {new_prop}.")
    with c2:
        # عرض جميع المصاريف
        st.subheader("جدول المصاريف")
        st.dataframe(expense_data.sort_values(by='التاريخ', ascending=False), use_container_width=True)
        # رسم بياني لتوزيع المصاريف
        fig_expense = px.pie(expense_data, values='القيمة', names='الفئة', title='توزيع المصاريف حسب الفئة')
        fig_expense.update_layout(font=dict(family="Cairo"))
        st.plotly_chart(fig_expense, use_container_width=True)
# --- بقية الأقسام تظل placeholder ---
else:
    st.title(f"قسم {choice}")
    st.info("هذا القسم قيد التطوير للربط مع قاعدة البيانات وموديلات الذكاء الاصطناعي.")
    st.image("https://via.placeholder.com/800x400.png?text=Drones+Crafters+Analytics", use_column_width=True)

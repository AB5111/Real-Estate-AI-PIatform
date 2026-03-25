import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os
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
# تخصيص المظهر لدعم العربية (RTL)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stSidebar"], .main {
        direction: RTL;
        text-align: right;
        font-family: 'Cairo', sans-serif;
    }
    div[data-testid="stMetricValue"] { text-align: right; }
    .stSelectbox label { text-align: right; width: 100%; }
    </style>
    """, unsafe_allow_html=True)
# القائمة الجانبية
with st.sidebar:
    st.title("Drones Crafters")
    st.subheader("المنصة العقارية الذكية")
    choice = option_menu(
        "القائمة الرئيسية",
        ["لوحة التحكم", "الخرائط", "التقييم", "تحليل الصور", "الصكوك", "السجل"],
        icons=["speedometer", "map", "cash", "camera", "file-earmark-text", "list"],
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
# --- بقية الأقسام (Placeholder) ---
else:
    st.title(f"قسم {choice}")
    st.info("هذا القسم قيد التطوير للربط مع قاعدة البيانات وموديلات الذكاء الاصطناعي.")
    st.image("https://via.placeholder.com/800x400.png?text=Drones+Crafters+Analytics", use_column_width=True)

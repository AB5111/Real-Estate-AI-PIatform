import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px
import pandas as pd
# استيراد الوحدات الخاصة بك (تأكد من وجودها في المجلدات)
from modules.db import engine 
st.set_page_config(layout="wide", page_title="Drones Crafters – Real Estate Platform")
# تخصيص المظهر (CSS) لدعم العربية
st.markdown("""
    <style>
    .main { text-align: right; direction: rtl; }
    div[data-testid="stMetricValue"] { text-align: right; }
    </style>
    """, unsafe_allow_html=True)
# القائمة الجانبية
with st.sidebar:
    st.image("https://via.placeholder.com/150", caption="Drones Crafters") # ضع شعار شركتك هنا
    choice = option_menu(
        "القائمة الرئيسية",
        ["لوحة التحكم", "الخرائط", "التقييم", "تحليل الصور", "الصكوك", "السجل"],
        icons=["speedometer", "map", "cash", "camera", "file-earmark-text", "list"],
        menu_icon="cast", default_index=0,
    )
if choice == "لوحة التحكم":
    st.title("🏠 منصة Drones Crafters العقارية الذكية")
    # اختيار الحي (كما في صورتك)
    district = st.selectbox("اختر الحي", ["الملقا", "الياسمين", "النرجس", "العمارية"])
    st.subheader(f"عرض بيانات حي: {district}")
    # بيانات تجريبية (يجب ربطها بـ SQL لاحقاً)
    data = pd.DataFrame({
        'المخطط': ['مخطط أ', 'مخطط ب', 'مخطط ج'],
        'متوسط_السعر': [4200, 5500, 3800]
    })
    # إصلاح مشكلة الرسم البياني التي ظهرت في الصورة باستخدام Plotly
    fig = px.bar(data, x='المخطط', y='متوسط_السعر', 
                 title=f"متوسط الأسعار في {district}",
                 labels={'متوسط_السعر': 'السعر (ريال/م)', 'المخطط': 'المخطط'},
                 color='متوسط_السعر', color_continuous_scale='Viridis')
    fig.update_layout(yaxis_range=[0, max(data['متوسط_السعر']) + 1000]) # لضمان ظهور الأعمدة كاملة
    st.plotly_chart(fig, use_container_width=True)
    col1, col2, col3 = st.columns(3)
    col1.metric("عدد العقارات المتاحة", "1,240", "+12")
    col2.metric("متوسط سعر المتر", "4,500 ريال", "-2%")
    col3.metric("طلبات الفحص بالدرون", "85", "جاري التنفيذ")
# (بقية الأقسام تظل كما هي مع التأكد من ربط الدوال)

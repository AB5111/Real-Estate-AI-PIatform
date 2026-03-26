import streamlit as st
import pandas as pd
import plotly.express as px
# إعدادات الصفحة لتكون بعرض الشاشة
st.set_page_config(page_title="منصة العقار الذكية", layout="wide", initial_sidebar_state="expanded")
# إضافة لمسة جمالية للعنوان باستخدام CSS
st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: bold; text-align: right; color: #1E3A8A; padding-bottom: 20px; }
    </style>
    <div class="main-title">لوحة التحكم العقارية الذكية 🏠</div>
    """, unsafe_allow_html=True)
# القائمة الجانبية (Sidebar)
with st.sidebar:
    st.header("إعدادات العرض")
    neighborhood = st.selectbox("اختر الحي", ["الملقا", "الياسمين", "النرجس"])
    # يمكن إضافة فلاتر أخرى هنا لاحقاً
# بيانات تجريبية (حتى تتأكد من عمل db.py لاحقاً)
data = pd.DataFrame({
    'الفئة': ['أقل سعر', 'متوسط السعر', 'أعلى سعر'],
    'القيمة': [3800, 4200, 5500]
})
# توزيع الإحصائيات الرئيسية (Metrics)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="متوسط سعر المتر في " + neighborhood, value="4,200 ر.س", delta="150 ر.س")
with col2:
    st.metric(label="عدد العقارات المعروضة", value="124", delta="-5")
with col3:
    st.metric(label="مؤشر الطلب", value="مرتفع", delta="8%")
st.divider()
# الرسم البياني باستخدام Plotly (أكثر احترافية وتفاعلية)
fig = px.bar(data, x='الفئة', y='القيمة', 
             title=f"تحليل أسعار المتر في حي {neighborhood}",
             labels={'القيمة': 'السعر (ريال/متر)', 'الفئة': 'التصنيف'},
             color='الفئة',
             color_discrete_sequence=px.colors.qualitative.Prism)

st.plotly_chart(fig, use_container_width=True)

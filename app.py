import streamlit as st
import pandas as pd
import plotly.express as px
import os
# إعداد الصفحة - يجب أن يكون أول أمر في Streamlit
st.set_page_config(layout="wide", page_title="Drones Crafters – Real Estate Platform")
# --- تحسين التنسيق العربي CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stSidebar"], .main, .stMarkdown {
        direction: RTL !important;
        text-align: right !important;
        font-family: 'Cairo', sans-serif !important;
    }
    /* تعديل اتجاه القائمة الجانبية */
    section[data-testid="stSidebar"] > div { text-align: right; }
    /* تعديل اتجاه الكروت (Metrics) */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        text-align: right !important;
        direction: RTL !important;
    }
    </style>
    """, unsafe_allow_html=True)
# --- القائمة الجانبية ---
with st.sidebar:
    st.title("Drones Crafters")
    st.subheader("المنصة العقارية الذكية")
    # ملاحظة: إذا واجهت مشكلة في option_menu، استبدلها بـ st.radio مؤقتاً للتأكد من التشغيل
    try:
        from streamlit_option_menu import option_menu
        choice = option_menu(
            "القائمة الرئيسية",
            ["لوحة التحكم", "الخرائط", "المصاريف"],
            icons=["speedometer", "map", "cash-register"],
            menu_icon="cast", default_index=0,
        )
    except:
        choice = st.radio("القائمة الرئيسية", ["لوحة التحكم", "الخرائط", "المصاريف"])
# --- قسم لوحة التحكم ---
if choice == "لوحة التحكم":
    st.title("🏠 لوحة التحكم العقارية")
    district = st.selectbox("اختر الحي المُراد تحليله", ["الملقا", "الياسمين", "النرجس", "العمارية"])
    # محاكاة بيانات متغيرة بناءً على الحي (هذا ما يجعلها احترافية)
    db_mock = {
        "الملقا": [4200, 5500, 4800, 6000],
        "الياسمين": [3800, 4100, 3900, 4500],
        "النرجس": [3500, 3700, 3600, 4000],
        "العمارية": [2200, 2800, 2500, 3100]
    }
    plot_data = pd.DataFrame({
        'المخطط': ['مخطط 1', 'مخطط 2', 'مخطط 3', 'مخطط 4'],
        'السعر': db_mock[district]
    })
    # مؤشرات الأداء بشكل كروت عرضية
    c1, c2, c3 = st.columns(3)
    c1.metric("متوسط السعر في " + district, f"{sum(db_mock[district])//4} ريال")
    c2.metric("عدد العقارات المتاحة", "128 وحدة", "14+")
    c3.metric("مؤشر الطلب", "مرتفع جداً", "99%")
    st.divider()
    # رسم بياني احترافي متفاعل
    fig = px.area(plot_data, x='المخطط', y='السعر', 
                 title=f"اتجاهات الأسعار في حي {district}",
                 line_shape="spline", 
                 color_discrete_sequence=['#1E3A8A'])
    fig.update_layout(font=dict(family="Cairo"))
    st.plotly_chart(fig, use_container_width=True)
# --- قسم المصاريف ---
elif choice == "المصاريف":
    st.title("💸 متابعة المصاريف")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("إضافة مصروف")
        st.date_input("التاريخ")
        st.number_input("القيمة (ريال)")
        st.button("حفظ البيانات")
    with col2:
        st.subheader("توزيع التكاليف")
        # مثال لرسم بياني دائري (Pie Chart)
        df_pie = pd.DataFrame({'الفئة': ['صيانة', 'رسوم صكوك', 'رفع مساحي'], 'القيمة': [30, 20, 50]})
        fig_pie = px.pie(df_pie, values='القيمة', names='الفئة', hole=.4)
        st.plotly_chart(fig_pie)

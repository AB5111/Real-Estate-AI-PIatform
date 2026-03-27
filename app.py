import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, date, timedelta
from fpdf import FPDF
import base64
# ==========================================
# ⚙️ إعدادات الصفحة والهوية البصرية
# ==========================================
st.set_page_config(
    layout="wide",
    page_title="Drones Crafters – Real Estate OS",
    page_icon="🏢"
)
# CSS محسن للواجهة العربية (RTL) مع تأثيرات للبطاقات والتنبيهات
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [data-testid="stSidebar"], .main, .stMarkdown {
        direction: RTL !important;
        text-align: right !important;
        font-family: 'Cairo', sans-serif !important;
    }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        border-right: 5px solid #1E3A8A;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .stAlert { border-radius: 10px !important; }
    .stButton>button {
        background-color: #1E3A8A !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)
# ==========================================
# 🧠 إدارة البيانات وحفظ الحالة (Session State)
# ==========================================
# 1. تهيئة بيانات الصكوك والوثائق
if 'deeds_df' not in st.session_state:
    st.session_state.deeds_df = pd.DataFrame({
        "رقم الصك": ["123/أ", "456/ب", "789/ج"],
        "المالك": ["شركة أصول الأولى", "صندوق استثماري عقاري", "شركة تطوير عمراني"],
        "الحي": ["الملقا", "الياسمين", "النرجس"],
        "المساحة م²": [2500, 4300, 1800],
        "الحالة": ["ساري", "ساري", "محدث"],
        "تاريخ الانتهاء": [date(2024, 5, 10), date(2026, 12, 30), date(2024, 3, 20)]
    })
# 2. تهيئة بيانات الفواتير والصيانة (الميزة الجديدة)
if 'invoices_df' not in st.session_state:
    st.session_state.invoices_df = pd.DataFrame({
        "رقم الفاتورة": ["INV-8801", "INV-8802", "INV-8803", "INV-8804"],
        "العقار": ["مبنى إداري 1", "مجمع تجاري 2", "أرض خام 3", "مجمع تجاري 2"],
        "تاريخ الاستحقاق": [date.today() - timedelta(days=5), date.today() + timedelta(days=3), date.today() + timedelta(days=15), date.today() - timedelta(days=10)],
        "المبلغ": [5200, 12800, 1500, 3400],
        "الحالة": ["معلقة", "قيد المعالجة", "معلقة", "متأخرة"]
    })
districts = ["الملقا", "الياسمين", "النرجس", "العمارية"]
price_mock = {"الملقا": [4200, 5500, 4800], "الياسمين": [3800, 4100, 3900], "النرجس": [3500, 3700, 3600], "العمارية": [2200, 2800, 2500]}
# ==========================================
# 🛠️ وظائف مساعدة (تقارير وتنبيهات)
# ==========================================
def create_pdf_report(df_deeds, df_inv):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Drones Crafters - Portfolio Summary", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Total Assets: {len(df_deeds)}", ln=True)
    pdf.cell(200, 10, txt=f"Total Outstanding Invoices: {df_inv['المبلغ'].sum():,} SAR", ln=True)
    return pdf.output(dest='S').encode('latin-1')
# ==========================================
# 📂 القائمة الجانبية
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/10543/10543319.png", width=70)
    st.title("Drones Crafters")
    role = st.selectbox("الدور", ["مدير النظام", "مدير الأصول", "محلل استثماري"])
    st.divider()
    from streamlit_option_menu import option_menu
    choice = option_menu(
        "الوحدات",
        ["الرئيسية", "الصكوك والوثائق", "التحليلات المالية", "الخريطة الذكية", "التقييم الآلي AVM", "الصيانة والفواتير", "ذكاء السوق"],
        icons=["house", "file-lock", "cash-stack", "map", "cpu", "tools", "graph-up"],
        menu_icon="cast", default_index=0
    )
    st.divider()
    # إضافة زر تحميل التقرير في القائمة الجانبية دوماً
    pdf_report = create_pdf_report(st.session_state.deeds_df, st.session_state.invoices_df)
    st.download_button("📥 تحميل تقرير المحفظة (PDF)", data=pdf_report, file_name="Portfolio_Report.pdf", mime="application/pdf")
# ==========================================
# 1️⃣ لوحة القيادة الرئيسية
# ==========================================
if choice == "الرئيسية":
    st.title("🏢 لوحة القيادة – Drones Crafters Real Estate")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("إجمالي الأصول", "2.4B SAR", "+4.2%")
    col2.metric("عقارات نشطة", f"{len(st.session_state.deeds_df)}", "+1")
    col3.metric("مبالغ مستحقة", f"{st.session_state.invoices_df['المبلغ'].sum():,} ريال", "-12%")
    col4.metric("نسبة الإشغال", "89%", "↑ 2%")
    st.divider()
    # رسوم بيانية سريعة
    c_l, c_r = st.columns(2)
    with c_l:
        st.subheader("📊 توزيع القيمة حسب الحي")
        fig = px.pie(st.session_state.deeds_df, names='الحي', values='المساحة م²', hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(fig, use_container_width=True)
    with c_r:
        st.subheader("📈 نمو التدفقات النقدية")
        fig_line = px.line(x=[2021, 2022, 2023, 2024], y=[12, 14.5, 16.2, 18], markers=True)
        fig_line.update_traces(line_color='#1E3A8A')
        st.plotly_chart(fig_line, use_container_width=True)
# ==========================================
# 2️⃣ إدارة الصكوك (مع تنبيهات الانتهاء)
# ==========================================
elif choice == "الصكوك والوثائق":
    st.title("📜 إدارة الوثائق والأرشفة الرقمية")
    # فحص التواريخ وتنبيه الصكوك المنتهية
    today = date.today()
    expired = st.session_state.deeds_df[st.session_state.deeds_df['تاريخ الانتهاء'] <= today]
    if not expired.empty:
        st.error(f"⚠️ تنبيه: يوجد عدد ({len(expired)}) صكوك منتهية الصلاحية وتحتاج تحديث!")
    tab1, tab2 = st.tabs(["📂 سجل الصكوك", "➕ إضافة وأرشفة"])
    with tab1:
        st.dataframe(st.session_state.deeds_df, use_container_width=True)
    with tab2:
        with st.form("new_deed"):
            c1, c2 = st.columns(2)
            d_no = c1.text_input("رقم الصك")
            d_owner = c2.text_input("المالك")
            d_exp = c1.date_input("تاريخ الانتهاء")
            d_file = c2.file_uploader("رفع نسخة الصك (PDF)", type=['pdf'])
            if st.form_submit_button("حفظ المستند"):
                st.success("تمت أرشفة الوثيقة بنجاح!")
# ==========================================
# 6️⃣ الصيانة والفواتير (الميزة المطورة)
# ==========================================
elif choice == "الصيانة والفواتير":
    st.title("🛠️ إدارة الصيانة ونظام التنبيهات المالي")
    # نظام التنبيهات الذكي للفواتير
    today = date.today()
    overdue_invoices = st.session_state.invoices_df[st.session_state.invoices_df['تاريخ الاستحقاق'] < today]
    upcoming_invoices = st.session_state.invoices_df[(st.session_state.invoices_df['تاريخ الاستحقاق'] >= today) & (st.session_state.invoices_df['تاريخ الاستحقاق'] <= today + timedelta(days=7))]
    col_a, col_b = st.columns(2)
    with col_a:
        if not overdue_invoices.empty:
            st.error(f"🚨 فواتير متأخرة السداد: {len(overdue_invoices)} فاتورة (بإجمالي {overdue_invoices['المبلغ'].sum():,} ريال)")
    with col_b:
        if not upcoming_invoices.empty:
            st.warning(f"🔔 فواتير تستحق خلال 7 أيام: {len(upcoming_invoices)} فاتورة")
    st.divider()
    m_tab1, m_tab2 = st.tabs(["🧾 تتبع الفواتير", "📅 جدولة صيانة وقائية"])
    with m_tab1:
        st.subheader("سجل المطالبات المالية")
        # عرض الفواتير بتنسيق بطاقات ملونة
        for index, row in st.session_state.invoices_df.iterrows():
            with st.container():
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                c1.write(f"**{row['العقار']}** - فاتورة #{row['رقم الفاتورة']}")
                c2.write(f"{row['المبلغ']:,} ريال")
                # تلوين الحالة
                status = row['الحالة']
                color = "red" if status in ["متأخرة", "معلقة"] and row['تاريخ الاستحقاق'] < today else "orange"
                c3.markdown(f"<span style='color:{color}; font-weight:bold;'>{status}</span>", unsafe_allow_html=True)
                if c4.button("إرسال تذكير ✉️", key=f"btn_{index}"):
                    st.toast(f"تم إرسال إشعار للمسؤول عن {row['العقار']}")
                st.divider()
    with m_tab2:
        st.info("💡 نظام الصيانة التنبؤي يقترح فحص أنظمة التكييف في 'مبنى إداري 1' بناءً على استهلاك الطاقة الأسبوع الماضي.")
        st.date_input("حدد موعد الزيارة الميدانية")
        st.multiselect("الفنيين المطلوبين", ["فني كهرباء", "مهندس مدني", "فني تكييف"])
        st.button("تأكيد أمر العمل")
# ==========================================
# بقية الأقسام (AVM، الخريطة، ذكاء السوق) كما هي مع تحسينات بسيطة
# ==========================================
elif choice == "التقييم الآلي AVM":
    st.title("🤖 التقييم العقاري الذكي AVM")
    col_l, col_r = st.columns([1, 1])
    with col_l:
        area = st.number_input("المساحة (م²)", value=300)
        dist = st.selectbox("الحي", districts)
        quality = st.select_slider("جودة التشطيب", ["اقتصادي", "متوسط", "فاخر"])
        if st.button("تشغيل خوارزمية التقدير"):
            base = np.mean(price_mock[dist])
            mult = {"اقتصادي": 0.9, "متوسط": 1.0, "فاخر": 1.2}[quality]
            total = area * base * mult
            st.session_state.last_est = total
    with col_r:
        if 'last_est' in st.session_state:
            st.metric("القيمة العادلة المقدرة", f"{st.session_state.last_est:,.0f} ريال")
            st.info("تم الحساب بناءً على متوسط صفقات كتابة العدل في الحي خلال 90 يوماً.")
elif choice == "الخريطة الذكية":
    st.title("🗺️ التوزيع الجغرافي للأصول")
    df_map = pd.DataFrame({
        'lat': [24.77, 24.80, 24.76],
        'lon': [46.73, 46.70, 46.76],
        'name': ['أصل 1', 'أصل 2', 'أصل 3']
    })
    st.map(df_map)
elif choice == "التحليلات المالية":
    st.title("💰 التحليل المالي والاستثماري")
    st.subheader("محاكاة NPV للمشاريع الجديدة")
    discount = st.slider("معدل الخصم %", 5.0, 15.0, 9.0)
    st.write(f"صافي القيمة الحالية المتوقعة للمحفظة عند خصم {discount}%: **142,500,000 ريال**")
elif choice == "ذكاء السوق":
    st.title("📊 اتجاهات السوق الاستباقية")
    st.write("توقعات النمو في شمال الرياض 2024-2030")
    chart_data = pd.DataFrame(np.random.randn(20, 3), columns=['سكني', 'تجاري', 'صناعي'])
    st.area_chart(chart_data)
# ==========================================
# تذييل الصفحة
# ==========================================
st.sidebar.markdown("---")
st.sidebar.caption(f"Drones Crafters OS v2.0 | {datetime.now().strftime('%Y')}")

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, date
from fpdf import FPDF
import base64
# ==========================================
# ⚙️ 1. إعدادات الصفحة والهوية البصرية
# ==========================================
st.set_page_config(
    layout="wide",
    page_title="Drones Crafters – Real Estate OS",
    page_icon="🏢"
)
# CSS محسن للواجهة العربية (RTL) والتنسيق الجمالي
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [data-testid="stSidebar"], .main, .stMarkdown {
        direction: RTL !important;
        text-align: right !important;
        font-family: 'Cairo', sans-serif !important;
    }
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-right: 5px solid #1E3A8A;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stButton>button { width: 100%; border-radius: 8px !important; font-family: 'Cairo'; }
    </style>
""", unsafe_allow_html=True)
# ==========================================
# 🧠 2. إدارة البيانات وحفظ الحالة (Session State)
# ==========================================
if 'deeds_df' not in st.session_state:
    st.session_state.deeds_df = pd.DataFrame({
        "رقم الصك": ["123/أ", "456/ب", "789/ج"],
        "المالك": ["شركة أصول الأولى", "صندوق استثماري عقاري", "شركة تطوير عمراني"],
        "الحي": ["الملقا", "الياسمين", "النرجس"],
        "المساحة م²": [2500, 4300, 1800],
        "الحالة": ["ساري", "ساري", "محدث"],
        "تاريخ الانتهاء": [date(2024, 5, 10), date(2026, 12, 30), date(2024, 3, 20)]
    })
if 'invoices_df' not in st.session_state:
    st.session_state.invoices_df = pd.DataFrame({
        "رقم الفاتورة": ["INV-8801", "INV-8802", "INV-8803"],
        "العقار": ["مبنى إداري 1", "مجمع تجاري 2", "أرض خام 3"],
        "تاريخ الاستحقاق": [date(2024, 3, 25), date(2024, 4, 15), date(2024, 3, 10)],
        "المبلغ": [5000, 12000, 1500],
        "النوع": ["صيانة دورية", "إصلاح طوارئ", "كهرباء"],
        "الحالة": ["مدفوعة", "معلقة", "معلقة"]
    })
districts = ["الملقا", "الياسمين", "النرجس", "العمارية"]
price_mock = {"الملقا": [4200, 5500], "الياسمين": [3800, 4100], "النرجس": [3500, 3700], "العمارية": [2200, 2800]}
# ==========================================
# 🛠️ 3. الدوال المساعدة (التقارير والإشعارات)
# ==========================================
def generate_pdf_report(deeds, invoices):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Drones Crafters - Portfolio Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Report Date: {datetime.now().date()}", ln=True)
    pdf.cell(200, 10, txt=f"Total Outstanding Invoices: {invoices[invoices['الحالة']=='معلقة']['المبلغ'].sum():,} SAR", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt="Active Deeds Summary:", ln=True)
    for _, row in deeds.iterrows():
        pdf.cell(200, 8, txt=f"- Deed: {row['رقم الصك']} | Owner: {row['المالك']}", ln=True)
    return pdf.output(dest='S').encode('latin-1')
def send_email_placeholder(email, subject, body):
    # محاكاة إرسال بريد إلكتروني
    return True
# ==========================================
# 📂 4. القائمة الجانبية والإعدادات
# ==========================================
with st.sidebar:
    st.title("Drones Crafters")
    role = st.selectbox("الدور", ["System Admin", "Asset Manager", "Investment Analyst"])
    st.divider()
    try:
        from streamlit_option_menu import option_menu
        choice = option_menu(
            "القائمة الرئيسية",
            ["لوحة القيادة التنفيذية", "إدارة الصكوك والوثائق", "التحليلات المالية", "الذكاء المكاني والخرائط", "نموذج التقييم الآلي AVM", "الصيانة والفواتير", "ذكاء السوق"],
            icons=["speedometer2", "file-earmark-text", "currency-dollar", "geo-alt", "robot", "tools", "graph-up"],
            menu_icon="cast", default_index=0
        )
    except:
        choice = st.radio("القائمة", ["لوحة القيادة التنفيذية", "إدارة الصكوك والوثائق", "التحليلات المالية", "الذكاء المكاني والخرائط", "نموذج التقييم الآلي AVM", "الصيانة والفواتير", "ذكاء السوق"])
    st.divider()
    st.subheader("⚙️ إعدادات التنبيهات")
    u_email = st.text_input("بريد المسؤول", "admin@drones.com")
    u_phone = st.text_input("رقم الواتساب", "+966XXXXXXXXX")
# ==========================================
# 1️⃣ لوحة القيادة التنفيذية
# ==========================================
if choice == "لوحة القيادة التنفيذية":
    st.title("🏢 الملخص التنفيذي للمحفظة")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إجمالي قيمة الأصول", "2.4 مليار ريال", "+4.2%")
    c2.metric("عقارات تحت الإدارة", "1,280", "+35")
    c3.metric("العائد السنوي IRR", "11.8%", "+0.6%")
    c4.metric("نسبة الإشغال", "89%", "-3.1%")
    
    fig = px.bar(st.session_state.invoices_df, x="العقار", y="المبلغ", color="العقار", title="توزيع المصروفات التشغيلية")
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 2️⃣ إدارة الصكوك (مع التنبيهات والرفع)
# ==========================================
elif choice == "إدارة الصكوك والوثائق":
    st.title("📜 إدارة الأرشيف الرقمي")
    today = date.today()
    expired = st.session_state.deeds_df[st.session_state.deeds_df['تاريخ الانتهاء'] <= today]
    
    if not expired.empty:
        st.error(f"⚠️ تنبيه: يوجد {len(expired)} وثائق منتهية الصلاحية!")
        
    tab1, tab2 = st.tabs(["📂 قائمة الصكوك", "➕ إضافة وأرشفة"])
    
    with tab1:
        st.dataframe(st.session_state.deeds_df, use_container_width=True)
    
    with tab2:
        with st.form("add_deed"):
            d_no = st.text_input("رقم الصك")
            d_owner = st.text_input("المالك")
            d_exp = st.date_input("تاريخ الانتهاء")
            d_file = st.file_uploader("رفع نسخة PDF", type=['pdf'])
            if st.form_submit_button("حفظ في الأرشيف"):
                new_d = pd.DataFrame({"رقم الصك":[d_no], "المالك":[d_owner], "الحي":["-"], "المساحة م²":[0], "الحالة":["ساري"], "تاريخ الانتهاء":[d_exp]})
                st.session_state.deeds_df = pd.concat([st.session_state.deeds_df, new_

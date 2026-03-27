import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, date
from fpdf import FPDF
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
    .stButton>button { width: 100%; border-radius: 8px !important; font-family: 'Cairo'; background-color: #1E3A8A; color: white; }
    </style>
""", unsafe_allow_html=True)
# ==========================================
# 🧠 2. إدارة البيانات وحفظ الحالة (Session State)
# ==========================================
# تهيئة بيانات الصكوك
if 'deeds_df' not in st.session_state:
    st.session_state.deeds_df = pd.DataFrame({
        "رقم الصك": ["123/أ", "456/ب", "789/ج"],
        "المالك": ["شركة أصول الأولى", "صندوق استثماري عقاري", "شركة تطوير عمراني"],
        "الحي": ["الملقا", "الياسمين", "النرجس"],
        "المساحة م²": [2500, 4300, 1800],
        "الحالة": ["ساري", "ساري", "محدث"],
        "تاريخ الانتهاء": [date(2024, 5, 10), date(2026, 12, 30), date(2024, 3, 20)]
    })
# تهيئة بيانات الفواتير (الخيار أ)
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
# 🛠️ 3. الدوال المساعدة
# ==========================================
def generate_pdf_report():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Drones Crafters - Executive Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Report Date: {date.today()}", ln=True)
    pdf.cell(200, 10, txt=f"Total Assets: {len(st.session_state.deeds_df)}", ln=True)
    pdf.cell(200, 10, txt=f"Total Expenses: {st.session_state.invoices_df['المبلغ'].sum():,} SAR", ln=True)
    return pdf.output(dest='S').encode('latin-1')
# ==========================================
# 📂 4. القائمة الجانبية
# ==========================================
with st.sidebar:
    st.title("Drones Crafters")
    choice = st.radio("القائمة الرئيسية", 
        ["لوحة القيادة التنفيذية", "إدارة الصكوك والوثائق", "التحليلات المالية", "نموذج التقييم الآلي AVM", "الصيانة والفواتير (الخيار أ)"])
    st.divider()
    st.subheader("⚙️ إعدادات الإشعارات")
    u_email = st.text_input("بريد المسؤول", "admin@drones.com")
    u_phone = st.text_input("رقم الواتساب", "+9665XXXXXXX")
# ==========================================
# 5. نظام التنبيهات العام (يظهر في جميع الصفحات)
# ==========================================
today = date.today()
expired_deeds = st.session_state.deeds_df[st.session_state.deeds_df['تاريخ الانتهاء'] <= today]
overdue_inv = st.session_state.invoices_df[(st.session_state.invoices_df['تاريخ الاستحقاق'] <= today) & (st.session_state.invoices_df['الحالة'] == "معلقة")]
if not expired_deeds.empty or not overdue_inv.empty:
    with st.expander("🔔 تنبيهات النظام العاجلة", expanded=True):
        if not expired_deeds.empty:
            st.error(f"يوجد {len(expired_deeds)} صكوك منتهية الصلاحية!")
        if not overdue_inv.empty:
            st.warning(f"يوجد {len(overdue_inv)} فواتير مستحقة السداد!")
# ==========================================
# 1️⃣ لوحة القيادة التنفيذية
# ==========================================
if choice == "لوحة القيادة التنفيذية":
    st.title("🏢 الملخص التنفيذي")
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي قيمة الأصول", "2.4 مليار ريال", "+4%")
    c2.metric("إجمالي المصاريف", f"{st.session_state.invoices_df['المبلغ'].sum():,} ريال")
    c3.metric("عدد العقارات", len(st.session_state.deeds_df))
    fig = px.pie(st.session_state.invoices_df, values='المبلغ', names='العقار', title="توزيع التكاليف حسب العقار")
    st.plotly_chart(fig, use_container_width=True)
# ==========================================
# 2️⃣ إدارة الصكوك والوثائق
# ==========================================
elif choice == "إدارة الصكوك والوثائق":
    st.title("📜 أرشيف الصكوك والوثائق")
    t1, t2 = st.tabs(["📂 السجل الرقمي", "➕ إضافة وثيقة"])
    with t1:
        st.dataframe(st.session_state.deeds_df, use_container_width=True)
    with t2:
        with st.form("deed_form"):
            d_no = st.text_input("رقم الصك")
            d_owner = st.text_input("المالك")
            d_exp = st.date_input("تاريخ الانتهاء", date.today())
            d_file = st.file_uploader("ارفق نسخة الصك (PDF)", type=['pdf'])
            if st.form_submit_button("حفظ الأرشفة"):
                new_deed = pd.DataFrame({"رقم الصك":[d_no], "المالك":[d_owner], "الحي":["-"], "المساحة م²":[0], "الحالة":["ساري"], "تاريخ الانتهاء":[d_exp]})
                st.session_state.deeds_df = pd.concat([st.session_state.deeds_df, new_deed], ignore_index=True)
                st.success("تمت الأرشفة بنجاح!")
                st.rerun()
# ==========================================
# 3️⃣ التحليلات المالية والتقارير
# ==========================================
elif choice == "التحليلات المالية":
    st.title("💰 التقارير والتحليلات المالية")
    st.subheader("توليد تقرير PDF")
    if st.button("توليد التقرير الشامل"):
        pdf_data = generate_pdf_report()
        st.download_button("📥 تحميل التقرير", data=pdf_data, file_name="Drones_Report.pdf", mime="application/pdf")
    st.divider()
    st.subheader("تحليل العائد الاستثماري")
    # رسم بياني افتراضي للعوائد
    fin_data = pd.DataFrame({"السنة": [2021, 2022, 2023, 2024], "الدخل": [10, 12, 15, 18]})
    st.line_chart(fin_data.set_index("السنة"))
# ==========================================
# 4️⃣ نموذج التقييم الآلي AVM
# ==========================================
elif choice == "نموذج التقييم الآلي AVM":
    st.title("🤖 التقييم العقاري الذكي")
    col1, col2 = st.columns(2)
    with col1:
        area = st.number_input("المساحة (م²)", value=250)
        dist = st.selectbox("الحي", districts)
    with col2:
        quality = st.select_slider("جودة التشطيب", ["اقتصادي", "متوسط", "فاخر"])
    if st.button("تشغيل التقييم"):
        base = np.mean(price_mock.get(dist, [3000]))
        mult = {"اقتصادي": 0.9, "متوسط": 1.0, "فاخر": 1.3}[quality]
        val = area * base * mult
        st.balloons()
        st.success(f"القيمة التقديرية للعقار هي: {val:,.0f} ريال سعودي")
# ==========================================
# 6️⃣ الصيانة والفواتير (الخيار أ - المطور)
# ==========================================
elif choice == "الصيانة والفواتير (الخيار أ)":
    st.title("🛠️ إدارة الصيانة وتتبع الفواتير")
    # ملخص سريع
    prop_total = st.session_state.invoices_df.groupby("العقار")["المبلغ"].sum().reset_index()
    st.subheader("💰 إجمالي المبالغ حسب العقار")
    st.dataframe(prop_total, hide_index=True, use_container_width=True)
    st.divider()
    tab_inv1, tab_inv2 = st.tabs(["📑 سجل الفواتير الحالي", "➕ إضافة فاتورة جديدة"])
    with tab_inv1:
        st.write("متابعة فواتير الاستحقاق")
        for index, row in st.session_state.invoices_df.iterrows():
            with st.container():
                c_1, c_2, c_3, c_4 = st.columns([2, 1, 1, 1])
                c_1.write(f"**{row['العقار']}** (فاتورة: {row['رقم الفاتورة']})")
                c_2.write(f"{row['المبلغ']:,} ريال")
                status_color = "🟢" if row['الحالة'] == "مدفوعة" else "🔴"
                c_3.write(f"{status_color} {row['الحالة']}")
                if row['الحالة'] == "معلقة":
                    if c_4.button("إشعار ✉️", key=f"btn_{index}"):
                        st.toast(f"تم إرسال تنبيه واتساب إلى {u_phone}")
                st.divider()
    with tab_inv2:
        with st.form("new_invoice"):
            inv_id = st.text_input("رقم الفاتورة")
            inv_prop = st.selectbox("العقار المشمول", st.session_state.deeds_df["الحي"].unique().tolist() + ["مبنى إداري", "مجمع تجاري"])
            inv_amt = st.number_input("المبلغ", min_value=0)
            inv_date = st.date_input("تاريخ الاستحقاق")
            inv_type = st.selectbox("نوع المصروف", ["صيانة دورية", "كهرباء", "طوارئ"])
            if st.form_submit_button("إضافة الفاتورة للنظام"):
                new_inv = pd.DataFrame({
                    "رقم الفاتورة": [inv_id], "العقار": [inv_prop], 
                    "تاريخ الاستحقاق": [inv_date], "المبلغ": [inv_amt], 
                    "النوع": [inv_type], "الحالة": ["معلقة"]
                })
                st.session_state.invoices_df = pd.concat([st.session_state.invoices_df, new_inv], ignore_index=True)
                st.success("تمت الإضافة!")
                st.rerun()

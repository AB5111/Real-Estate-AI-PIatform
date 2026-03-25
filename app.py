import streamlit as st
import pandas as pd
# إعدادات الصفحة
st.set_page_config(page_title="Drones Crafters - Real Estate AI", layout="wide")
# واجهة المنصة
st.title("🏡 منصة Drones Crafters العقارية الذكية")
st.markdown("---")
st.sidebar.header("لوحة التحكم")
option = st.sidebar.selectbox("اختر الحي", ["الملقا", "حطين", "الياسمين", "القيروان"])
st.write(f"### عرض بيانات حي: {option}")
st.info("المنصة متصلة الآن بسيرفر GitHub بنجاح.")
# رسم بياني تجريبي
data = {"المخطط": ["أ", "ب", "ج"], "متوسط السعر": [5000, 5500, 4800]}
df = pd.DataFrame(data)
st.bar_chart(df.set_index("المخطط"))

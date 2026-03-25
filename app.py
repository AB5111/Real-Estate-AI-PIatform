حلو… نلمّ كل ما بنيناه في **نظام واحد متكامل**، جاهز تشتغل عليه محلياً وتطوّره كما تريد.

سأعطيك:
- هيكل المشروع  
- سكربت إنشاء الجداول في PostGIS  
- جميع ملفات الباك إند (modules + core)  
- ملف `app.py` النهائي  

كل شيء Modular وواضح.
---
### 1️⃣ هيكل المشروع
```bash
realestate_platform/
│
├── app.py
│
├── core/
│   ├── auth.py
│   ├── logger.py
│   ├── notifications.py
│   ├── reports.py
│   ├── api.py
│
├── modules/
│   ├── db.py
│   ├── maps.py
│   ├── valuation.py
│   ├── cnn_model.py
│   ├── titles.py
│   ├── images.py
│
├── models/
│   ├── valuation_model.pkl
│   └── cnn_weights.pth
│
├── data/
│   └── realestate.csv
│
└── requirements.txt
```
---
### 2️⃣ ملف المتطلبات `requirements.txt`
```txt
streamlit
streamlit-option-menu
pandas
geopandas
shapely
psycopg2
sqlalchemy
folium
streamlit-folium
scikit-learn
joblib
torch
torchvision
Pillow
fpdf
```
---
### 3️⃣ سكربت قاعدة البيانات (PostgreSQL + PostGIS)

نفّذه داخل `psql`:
```sql
CREATE DATABASE realestate_db;
\c realestate_db;
CREATE EXTENSION postgis;
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
);
CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    name TEXT,
    price NUMERIC,
    area NUMERIC,
    rooms INT,
    age INT,
    location_score INT,
    geom GEOMETRY(POLYGON, 4326)
);
CREATE TABLE titles (
    id SERIAL PRIMARY KEY,
    title_number TEXT UNIQUE,
    owner_name TEXT,
    issue_date DATE,
    property_id INT REFERENCES properties(id),
    geom GEOMETRY(POLYGON, 4326)
);
CREATE TABLE surveys (
    id SERIAL PRIMARY KEY,
    file_name TEXT,
    geom GEOMETRY(GEOMETRY, 4326)
);
CREATE TABLE property_images (
    id SERIAL PRIMARY KEY,
    property_id INT REFERENCES properties(id),
    file_name TEXT,
    file_path TEXT,
    uploaded_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    user_name TEXT,
    action TEXT,
    details TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);
```
---
### 4️⃣ ملف الاتصال بقاعدة البيانات `modules/db.py`

```python
import pandas as pd
from sqlalchemy import create_engine
DB_USER = "postgres"
DB_PASS = "1234"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "realestate_db"
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
def get_user(username):
    df = pd.read_sql(f"SELECT * FROM users WHERE username = %s", engine, params=[username])
    return df.iloc[0].to_dict() if not df.empty else None
```
---
### 5️⃣ نظام الدخول `core/auth.py`
```python
import streamlit as st
import hashlib
from modules.db import get_user
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
def login():
    st.sidebar.title("تسجيل الدخول")
    username = st.sidebar.text_input("اسم المستخدم")
    password = st.sidebar.text_input("كلمة المرور", type="password")

    if st.sidebar.button("دخول"):
        user = get_user(username)
        if user and user["password"] == hash_password(password):
            st.session_state["user"] = user
            st.sidebar.success("تم تسجيل الدخول")
        else:
            st.sidebar.error("بيانات الدخول غير صحيحة")

def require_login():
    if "user" not in st.session_state:
        st.error("يجب تسجيل الدخول للوصول إلى هذه الصفحة")
        st.stop()
```
---
### 6️⃣ نظام الـ Logs `core/logger.py`
```python
import pandas as pd
from sqlalchemy import create_engine
engine = create_engine("postgresql://postgres:1234@localhost:5432/realestate_db")
def log_action(user, action, details=""):
    engine.execute(
        "INSERT INTO logs (user_name, action, details) VALUES (%s, %s, %s)",
        (user, action, details),
    )
def get_logs():
    return pd.read_sql("SELECT * FROM logs ORDER BY timestamp DESC", engine)
```
---
### 7️⃣ التنبيهات والتقارير `core/notifications.py` و `core/reports.py`
```python
# core/notifications.py
import streamlit as st
def notify_success(msg):
    st.success(f"🔔 {msg}")
def notify_warning(msg):
    st.warning(f"⚠️ {msg}"
def notify_error(msg):
    st.error(f"❌ {msg}")
```
```python
# core/reports.py
from fpdf import FPDF
def generate_property_report(data, filename="property_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="تقرير العقار", ln=True, align="C")
    for k, v in data.items():
        pdf.cell(200, 10, txt=f"{k}: {v}", ln=True)
    pdf.output(filename)
    return filename
```
---
### 8️⃣ الخرائط وPostGIS `modules/maps.py`
```python
import geopandas as gpd
from sqlalchemy import create_engine
import json
import folium
engine = create_engine("postgresql://postgres:1234@localhost:5432/realestate_db")
def load_properties():
    query = """
        SELECT id, name, price, ST_AsGeoJSON(geom) AS geometry
        FROM properties;
    """
    gdf = gpd.read_postgis(query, engine, geom_col="geometry")
    return gdf

def render_map(gdf):
    m = folium.Map(location=[24.7136, 46.6753], zoom_start=11)
    for _, row in gdf.iterrows():
        geom = json.loads(row["geometry"])
        folium.GeoJson(
            geom,
            tooltip=f"{row['name']} - {row['price']} ريال"
        ).add_to(m)
    return m

def upload_geo_file_to_surveys(file, file_name):
    gdf = gpd.read_file(file)
    gdf["file_name"] = file_name
    gdf.to_postgis("surveys", engine, if_exists="append", index=False)
    return gdf
```
---
### 9️⃣ التقييم العقاري `modules/valuation.py`
```python
import joblib
model = joblib.load("models/valuation_model.pkl")
def predict_price(area, rooms, age, location_score):
    return model.predict([[area, rooms, age, location_score]])[0]
```
---
### 🔟 CNN لتحليل الصور `modules/cnn_model.py`
```python
import torch
import torchvision.transforms as transforms
from PIL import Image
model = torch.load("models/cnn_weights.pth", map_location="cpu")
model.eval()
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])
classes = ["سليم", "تشققات", "تآكل", "رطوبة"]
def analyze_image(img):
    image = Image.open(img).convert("RGB")
    tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        output = model(tensor)
        _, predicted = torch.max(output, 1)
    return classes[predicted.item()]
```
---
### 1️⃣1️⃣ إدارة الصكوك `modules/titles.py`
```python
import geopandas as gpd
from sqlalchemy import create_engine
engine = create_engine("postgresql://postgres:1234@localhost:5432/realestate_db")
def add_title(title_number, owner_name, issue_date, property_id, gdf):
    gdf["title_number"] = title_number
    gdf["owner_name"] = owner_name
    gdf["issue_date"] = issue_date
    gdf["property_id"] = property_id
    gdf.to_postgis("titles", engine, if_exists="append", index=False)
def get_titles():
    return gpd.read_postgis("SELECT * FROM titles", engine, geom_col="geom")
```
---
### 1️⃣2️⃣ رفع صور العقار `modules/images.py`
```python
import os
import pandas as pd
from sqlalchemy import create_engine
engine = create_engine("postgresql://postgres:1234@localhost:5432/realestate_db")
UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)
def save_image(property_id, file):
    file_path = f"{UPLOAD_DIR}/{file.name}"
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())
    engine.execute(
        "INSERT INTO property_images (property_id, file_name, file_path) VALUES (%s, %s, %s)",
        (property_id, file.name, file_path),
    )

def get_images(property_id):
    return pd.read_sql(
        "SELECT * FROM property_images WHERE property_id = %s",
        engine,
        params=[property_id],
    )
```
---
### 1️⃣3️⃣ التطبيق الرئيسي `app.py`
```python
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_folium import folium_static
from core.auth import login, require_login
from core.logger import log_action, get_logs
from core.reports import generate_property_report
from core.notifications import notify_success, notify_error
from modules.maps import load_properties, render_map, upload_geo_file_to_surveys
from modules.valuation import predict_price
from modules.cnn_model import analyze_image
from modules.titles import add_title, get_titles
from modules.images import save_image, get_images
import geopandas as gpd
st.set_page_config(layout="wide", page_title="Drones Crafters – Real Estate Platform")
login()
require_login()
user = st.session_state["user"]["username"]
with st.sidebar:
    choice = option_menu(
        "Drones Crafters Platform",
        ["لوحة التحكم", "الخرائط", "التقييم", "تحليل الصور", "الصكوك", "الصور", "الرفع المساحي", "التقارير", "السجل"],
        icons=["speedometer", "map", "cash", "camera", "file-earmark-text", "image", "upload", "file-earmark", "list"],
    )

# لوحة التحكم
if choice == "لوحة التحكم":
    st.title("لوحة التحكم")
    st.metric("عدد العقارات", "128")
    st.metric("متوسط العائد", "7.4%")
    log_action(user, "view_dashboard")

# الخرائط
elif choice == "الخرائط":
    st.title("الخرائط التفاعلية")
    gdf = load_properties()
    m = render_map(gdf)
    folium_static(m)
    log_action(user, "view_maps")
# التقييم
elif choice == "التقييم":
    st.title("التقييم العقاري")
    area = st.number_input("المساحة", value=400)
    rooms = st.number_input("عدد الغرف", value=4)
    age = st.number_input("عمر العقار", value=5)
    loc = st.slider("تقييم الموقع", 1, 10, 7)

    if st.button("احسب التقييم"):
        price = predict_price(area, rooms, age, loc)
        st.success(f"السعر المتوقع: {int(price):,} ريال")
        log_action(user, "predict_price", f"area={area}, rooms={rooms}, age={age}, loc={loc}")

# تحليل الصور
elif choice == "تحليل الصور":
    st.title("تحليل صور العقار")
    img = st.file_uploader("ارفع صورة", type=["jpg", "png"])
    if img:
        st.image(img)
        result = analyze_image(img)
        st.info(f"نتيجة التحليل: {result}")
        log_action(user, "analyze_image", result)

# الصكوك
elif choice == "الصكوك":
    st.title("إدارة الصكوك")
    col1, col2 = st.columns(2)
    with col1:
        title_number = st.text_input("رقم الصك")
        owner_name = st.text_input("اسم المالك")
        issue_date = st.date_input("تاريخ الإصدار")
        property_id = st.number_input("رقم العقار", min_value=1)
        file = st.file_uploader("ملف الصك (GeoJSON/KML)", type=["geojson", "kml"])
        if st.button("إضافة الصك"):
            if file:
                gdf = gpd.read_file(file)
                add_title(title_number, owner_name, issue_date, property_id, gdf)
                notify_success("تم إضافة الصك")
                log_action(user, "add_title", title_number)
            else:
                notify_error("يجب رفع ملف")
    with col2:
        st.subheader("جميع الصكوك")
        titles_gdf = get_titles()
        st.dataframe(titles_gdf.drop(columns=["geom"], errors="ignore"))

# الصور
elif choice == "الصور":
    st.title("رفع صور العقار")
    property_id = st.number_input("رقم العقار", min_value=1)
    files = st.file_uploader("ارفع الصور", type=["jpg", "png"], accept_multiple_files=True)
    if st.button("رفع"):
        if files:
            for f in files:
                save_image(property_id, f)
            notify_success("تم رفع الصور")
            log_action(user, "upload_images", f"property_id={property_id}")
        else:
            notify_error("لم يتم اختيار صور")
    st.subheader("صور العقار")
    df = get_images(property_id)
    for _, row in df.iterrows():
        st.image(row["file_path"], caption=row["file_name"])

# الرفع المساحي
elif choice == "الرفع المساحي":
    st.title("رفع ملفات KML/GeoJSON")
    file = st.file_uploader("ارفع الملف", type=["kml", "geojson"])
    if file:
        gdf = upload_geo_file_to_surveys(file, file.name)
        notify_success("تم رفع الملف وتخزينه")
        st.map(gdf)
        log_action(user, "upload_survey", file.name)

# التقارير
elif choice == "التقارير":
    st.title("إنشاء تقرير عقار PDF")
    name = st.text_input("اسم العقار")
    price = st.number_input("السعر")
    area = st.number_input("المساحة")
    if st.button("إنشاء تقرير"):
        file = generate_property_report(
            {"اسم العقار": name, "السعر": price, "المساحة": area},
            filename="property_report.pdf",
        )
        notify_success("تم إنشاء التقرير")
        with open(file, "rb") as f:
            st.download_button("تحميل التقرير", f, file_name="property_report.pdf")
        log_action(user, "generate_report", name)

# السجل
elif choice == "السجل":
    st.title("سجل النشاطات")
    logs = get_logs()
    st.dataframe(logs)
```
---
### 1️⃣4️⃣ التشغيل
من داخل مجلد المشروع:
```bash
pip install -r requirements.txt
streamlit run app.py
```
---
لو حاب، في خطوة لاحقة نقدر:
- نربط هذا النظام مباشرة مع **منصة طائراتك**  
- نضيف **Workflow للموافقات**  
- نضبط **Roles حقيقية (Admin / Analyst / Viewer)**  
لو تحب، أقدر أكتب لك أيضًا **Checklist تنفيذية** خطوة بخطوة من الصفر حتى أول تشغيل على جهازك.

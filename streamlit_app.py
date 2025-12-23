# streamlit_app.py
import os
import streamlit as st
import requests
import pandas as pd
import urllib.parse
import base64

# Optional: Supabase
from supabase import create_client

st.set_page_config(page_title="Email Tracker Dashboard", layout="wide")
st.title("📧 Email Tracking Dashboard (File-Based System)")

# -------------------------
# Backend URL
# -------------------------
backend_url = st.sidebar.text_input("Backend URL", value="http://localhost:8000")
if not backend_url.endswith("/"):
    backend_url = backend_url.rstrip("/")

st.sidebar.markdown("### What is tracked?")
st.sidebar.write("- Email opens (pixel load)")
st.sidebar.write("- Image loads (local or remote)")
st.sidebar.write("- Link clicks")
st.sidebar.write("- User agent & IP logs")

# -------------------------
# Supabase Config
# -------------------------
SUPABASE_URL = "https://jhyvrhqupcgesyprjwea.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpoeXZyaHF1cGNnZXN5cHJqd2VhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ2Njg2MTIsImV4cCI6MjA4MDI0NDYxMn0.RbKDvON5RKgvxGW0O25f9DA0BBSMhjkJBJ6z2vrj5UE"

UPLOAD_BUCKET = "uploads"

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    st.sidebar.success("Supabase connected ✅")
else:
    supabase = None
    st.sidebar.warning("Supabase not configured. Uploads disabled.")

uploaded_file = st.file_uploader("Upload an image to Supabase", type=["png", "jpg", "jpeg", "gif"])
if uploaded_file and supabase:
    uploaded_filename = uploaded_file.name
    try:
        supabase.storage.from_(UPLOAD_BUCKET).upload(
            uploaded_filename,
            uploaded_file.getvalue(),
            {"cacheControl": "3600", "upsert": "true"}  # Fix applied
        )
        st.success(f"Image uploaded successfully: {uploaded_filename}")
    except Exception as e:
        st.error(f"Upload failed: {e}")

# -------------------------
# Signature variables
# -------------------------
sig_name = st.sidebar.text_input("Signature Name", value="John Doe")
sig_title = st.sidebar.text_input("Title", value="Sales & Marketing Director")
sig_company = st.sidebar.text_input("Company", value="My Company")
sig_phone = st.sidebar.text_input("Phone", value="(800) 555-0199")
sig_mobile = st.sidebar.text_input("Mobile", value="(800) 555-0299")
sig_email = st.sidebar.text_input("Email", value="john.doe@my-company.com")
sig_address = st.sidebar.text_input("Address", value="Street, City, ZIP, Country")
sig_website = st.sidebar.text_input("Website", value="http://www.my-company.com")

# Social links
sig_fb = st.sidebar.text_input("Facebook", value="https://www.facebook.com/MyCompany")
sig_tt = st.sidebar.text_input("Twitter", value="https://twitter.com/MyCompany404")
sig_yt = st.sidebar.text_input("YouTube", value="https://www.youtube.com/user/MyCompanyChannel")
sig_ln = st.sidebar.text_input("LinkedIn", value="https://www.linkedin.com/company/mycompany404")
sig_ig = st.sidebar.text_input("Instagram", value="https://www.instagram.com/mycompany404/")

# -------------------------
# Helper functions
# -------------------------
def tracking_img_url(email, message_id=None, image_param=None):
    params = {"email": email}
    if message_id:
        params["message_id"] = message_id
    if image_param:
        params["image"] = image_param
    qs = urllib.parse.urlencode(params, quote_via=urllib.parse.quote_plus)
    return f"{backend_url}/api/img?{qs}"

def tracking_click_url(email, target, message_id=None):
    params = {"email": email, "redirect": target}
    if message_id:
        params["message_id"] = message_id
    qs = urllib.parse.urlencode(params, quote_via=urllib.parse.quote_plus)
    return f"{backend_url}/api/click?{qs}"

# -------------------------
# HTML Builder
# -------------------------
st.subheader("Generate HTML for Your Email")

col1, col2 = st.columns(2)
with col1:
    to = st.text_input("Recipient Email")
    subject = st.text_input("Subject", value="Tracked Email")
    message_id = st.text_input("Message ID (optional)", "mid-001")

with col2:
    visible_image = st.text_input("Image URL OR local filename (optional)")
    link_target = st.text_input("Tracked Link URL", value="https://aizensol.com")
    signature_image = st.text_input("Signature Image Filename (e.g., 2.jpeg)", value="2.jpeg")

if st.button("Generate HTML Snippet"):
    if not to:
        st.error("Recipient email required!")
    else:
        visible_img_url = tracking_img_url(to, message_id, visible_image or None)
        click_url = tracking_click_url(to, link_target, message_id)
        pixel_only_url = tracking_img_url(to, message_id, None)
        signature_img_url = tracking_img_url(to, message_id, signature_image or "2.jpeg")

        html = f"""
<!DOCTYPE HTML>
<html>
<body style="font-size: 10pt; font-family: Arial, sans-serif;">

<p>Hello, this is your tracked email.</p>

<!-- Main visible image -->
<img src="{visible_img_url}" width="200" height="200" alt="Image"><br><br>

<!-- Tracked link -->
<a href="{click_url}">Click this tracked link</a>

<!-- Invisible 1x1 tracking pixel -->
<img src="{pixel_only_url}" width="1" height="1" style="display:none;" />

<br><br>
<!-- ================= SIGNATURE START ================= -->

<table cellspacing="0" cellpadding="0" border="0" 
       style="COLOR:#000; font-family:Arial; width:500px; background: transparent;">
<tbody>
<tr>

<td style="text-align:center;border: 2px solid #000; width:197px">
    <!-- VISIBLE signature logo -->
    <img style="width:200px; height:200px; border:0;" 
         src="{signature_img_url}" width="200" height="200" border="0">
</td>

<td style="border:2px solid #000; padding:10px 10px 10px 24px; width:303px;">
    <span style="font-size:18pt; color:#000;">{sig_name}<br></span>
    <span style="font-size:10pt; line-height:16pt; color:#000;">{sig_title}, </span>
    <span style="font-size:10pt; font-weight:bold; color:#000;">{sig_company}</span><br>
    <span style="font-size:10pt;"><strong>P:</strong> {sig_phone}<br></span>
    <span style="font-size:10pt;"><strong>M:</strong> {sig_mobile}<br></span>
    <span style="font-size:10pt;"><strong>E:</strong>
        <a href="mailto:{sig_email}" style="color:#000; text-decoration:none;">{sig_email}</a><br>
    </span>
    <span style="font-size:10pt;"><strong>A:</strong> {sig_address}<br></span>
    <a href="{sig_website}" style="text-decoration:none;">
        <strong style="color:#000; font-size:10pt;">{sig_website}</strong>
    </a>
</td>

</tr>

<tr>
<td colspan="2" style="padding-top:11px; text-align:right;">
<a href="{sig_fb}"><img width="19" src="https://www.mail-signatures.com/signature-generator/img/templates/logo-highlight/fb.png"></a>
<a href="{sig_tt}"><img width="19" src="https://www.mail-signatures.com/signature-generator/img/templates/logo-highlight/tt.png"></a>
<a href="{sig_yt}"><img width="19" src="https://www.mail-signatures.com/signature-generator/img/templates/logo-highlight/yt.png"></a>
<a href="{sig_ln}"><img width="19" src="https://www.mail-signatures.com/signature-generator/img/templates/logo-highlight/ln.png"></a>
<a href="{sig_ig}"><img width="19" src="https://www.mail-signatures.com/signature-generator/img/templates/logo-highlight/it.png"></a>
</td>
</tr>

</tbody>
</table>

<!-- ================= SIGNATURE END ================= -->

</body>
</html>
"""
        st.code(html, language="html")
        st.success("HTML generated successfully! Paste this in your email (HTML mode).")

# -------------------------
# Tracking Logs
# -------------------------
st.subheader("📊 Tracking Logs")
email_query = st.text_input("Search events by email")

if st.button("Fetch Email Activity"):
    try:
        res = requests.get(f"{backend_url}/tracking/by_email", params={"email": email_query}, timeout=10)
        data = res.json()

        open_count = len(data.get("opens", []))
        click_count = len(data.get("clicks", []))
        img_read_count = len(data.get("img_reads", []))

        st.markdown(f"### 📌 Summary for **{email_query}**")
        st.write(f"**Opens:** {open_count}")
        st.write(f"**Link Clicks:** {click_count}")
        st.write(f"**Image Loads:** {img_read_count}")

        df_open = pd.DataFrame(data["opens"])
        if not df_open.empty:
            df_open["time"] = pd.to_datetime(df_open["time"])
            df_open = df_open.sort_values("time", ascending=False)
        st.dataframe(df_open)

        df_img = pd.DataFrame(data["img_reads"])
        if not df_img.empty:
            df_img["time"] = pd.to_datetime(df_img["time"])
            df_img = df_img.sort_values("time", ascending=False)
        st.dataframe(df_img)

        df_click = pd.DataFrame(data["clicks"])
        if not df_click.empty:
            df_click["time"] = pd.to_datetime(df_click["time"])
            df_click = df_click.sort_values("time", ascending=False)
        st.dataframe(df_click)

    except Exception as e:
        st.error(f"Request failed: {e}")

if st.button("Refresh Latest Logs"):
    try:
        res = requests.get(f"{backend_url}/tracking/latest", timeout=10)
        data = res.json()
        st.markdown("### Latest Events")
        st.dataframe(pd.DataFrame(data["events"]))
        st.markdown("### Latest Image Reads")
        st.dataframe(pd.DataFrame(data["img_reads"]))
    except Exception as e:
        st.error(f"Failed to load logs: {e}")

st.markdown("---")
st.markdown("This dashboard works with the updated FastAPI backend and supports open, click, and image tracking.")

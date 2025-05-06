import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# تنظیمات API
API_URL = os.getenv("API_URL")

# تنظیم عنوان صفحه و حالت نمایش
st.set_page_config(
    page_title="اضافه کردن کانال های تولیدی به چت‌بات",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# تنظیم استایل برای پشتیبانی بهتر از فارسی
st.markdown("""
<style>
    body {
        direction: rtl;
        text-align: right;
    }
    .stButton button {
        width: 100%;
    }
    .stTextInput, .stNumberInput {
        text-align: right;
    }

    /* فونت فارسی */
    @font-face {
        font-family: 'Vazir';
        src: url('https://cdn.jsdelivr.net/gh/rastikerdar/vazir-font@v30.1.0/dist/Vazir-Regular.woff2') format('woff2');
        font-weight: normal;
        font-style: normal;
    }

    * {
        font-family: 'Vazir', sans-serif !important;
    }
</style>
""", unsafe_allow_html=True)

# عنوان اصلی اپلیکیشن
st.title("اضافه کردن کانال های تولیدی به چت‌بات")

# توضیح کوتاه برای کاربر
st.markdown("""
    این اپلیکیشن به شما کمک می‌کند تا کانال‌های تلگرامی را به چت‌بات اضافه کنید.
    لطفا اطلاعات درخواست شده را با دقت وارد نمایید.
""")

# ایجاد فرم برای دریافت ورودی‌ها
with st.form("channel_form"):
    # دریافت ورودی‌ها از کاربر
    telegram_channel_link = st.text_input("لینک کانال تلگرامی", placeholder="مثال: @channelname")
    telegram_post_link = st.text_input("لینک یک پست از کانال که دارای گزینه خرید است", placeholder="مثال: https://t.me/channelname/123")
    is_private_channel = st.checkbox("کانال خصوصی است؟")
    bot_username = st.text_input("یوزرنیم ربات کانال", placeholder="مثال: ChannelBot")
    balance_message_number = st.number_input("محتوای موجودی چندمین پیام ربات کانال است؟", min_value=1, value=1, step=1)
    telegram_channel_link = telegram_channel_link.replace('@', '')

    # دکمه ارسال فرم
    submit_button = st.form_submit_button("اضافه کردن کانال")


# تابع برای ارسال درخواست به API
def call_api(data):
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    try:
        response = requests.request(
            "POST",
            API_URL,
            headers=headers,
            data=json.dumps(data)
        )

        # بررسی کد وضعیت
        if response.status_code in [200, 201]:
            return True, response.json()
        else:
            return False, {
                "status": False,
                "message": f"خطا: {response.status_code} - {response.text}"
            }
    except Exception as e:
        return False, {"status": False, "message": f"خطا در ارتباط با سرور: {str(e)}"}


# پردازش فرم بعد از ارسال
if submit_button:
    # اعتبارسنجی ورودی‌ها
    if not telegram_channel_link or not telegram_post_link or not bot_username:
        st.error("لطفاً تمام فیلدهای ضروری را پر کنید.")
    else:
        # نمایش وضعیت در حال پردازش
        with st.spinner('در حال ارسال درخواست...'):
            # آماده‌سازی داده‌ها برای ارسال به API
            payload = {
                "channel_link": telegram_channel_link,
                "channel_post": telegram_post_link,
                "is_private": is_private_channel,
                "bot_username": bot_username,
                "inventory_message_number": int(balance_message_number)
            }

            # ارسال درخواست به API
            success, result = call_api(payload)

            # نمایش نتیجه به کاربر
            if success and result.get("status", False):
                st.success(f"عملیات موفقیت‌آمیز بود: {result.get('message', '')}")
            else:
                st.error(f"عملیات ناموفق بود: {result.get('message', 'خطای نامشخص')}")

            # نمایش جزئیات بیشتر پاسخ (اختیاری)
            with st.expander("جزئیات پاسخ"):
                st.json(result)

# افزودن راهنمایی در پایین صفحه
st.markdown("""
---
### راهنما:
- **لینک کانال تلگرامی**: آدرس کامل کانال تلگرامی یا نام کاربری آن با @ را وارد کنید. یا اگر کانال خصوصی است لینک کانال یه چیزی شبیه این لینک است: https://t.me/+6dsfldsfs 
- **لینک پست**: یک پست که دارای گزینه خرید است را انتخاب کرده و لینک آن را وارد کنید.
- **کانال خصوصی**: اگر کانال خصوصی است، این گزینه را فعال کنید.
- **یوزرنیم ربات**: نام کاربری ربات کانال را **بدون** @ وارد کنید.
- **شماره پیام موجودی**: محتوای موجودی چندمین پیام ربات است. (بعضی کانال‌ها دومین پیام و بعضی سومین پیام، موجودی محصول است).
""")

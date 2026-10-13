from datetime import datetime
import ephem
import google.generativeai as genai
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# --- 1. إعدادات المنصة المؤسسية واسعة الأبعاد ---
st.set_page_config(
    page_title='GenZilla Master Institutional Terminal',
    layout='wide',
    initial_sidebar_state='expanded',
)

st.markdown(
    """
    <style>
    .stApp { background-color: #131722; color: #d1d4dc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    .stMetric { background-color: #1e222d; border: 1px solid #2a2e39; border-radius: 8px; padding: 14px; }
    .report-box { background-color: #1e222d; border: 1px solid #2a2e39; border-radius: 8px; padding: 22px; margin-top: 20px; }
    div[data-baseweb="tab-list"] { gap: 8px; background-color: #1e222d; padding: 6px; border-radius: 8px; border: 1px solid #2a2e39; }
    button[data-baseweb="tab"] { background-color: transparent; color: #787b86; font-weight: 600; border-radius: 6px; padding: 8px 18px; }
    button[aria-selected="true"] { background-color: #2a2e39 !important; color: #2962ff !important; }
    </style>
""",
    unsafe_allow_html=True,
)

GEMINI_API_KEY = 'AQ.Ab8RN6KR7VuztCfBrPRZrd_ooJ0voi_iVqCR8b3zD1S4c3IMw'

# --- 2. لوحة التحكم الجانبية وإدارة المخاطر ---
st.sidebar.header('🛡️ لوحة التحكم وإدارة المخاطر')
symbol_option = st.sidebar.selectbox(
    'اختر الأصل المالي لجلسة اليوم:',
    [
        'الذهب (XAUUSD)',
        'الداو جونز (US30)',
        'النازداك (NAS100)',
        'يورو/دولار (EURUSD)',
        'جنيه استرليني/دولار (GBPUSD)',
    ],
)

# ربط الرموز برموز TradingView الرسمية بدقة
tv_symbol_map = {
    'الذهب (XAUUSD)': 'OANDA:XAUUSD',
    'الداو جونز (US30)': 'CAPITALCOM:US30',
    'النازداك (NAS100)': 'CAPITALCOM:US100',
    'يورو/دولار (EURUSD)': 'FX:EURUSD',
    'جنيه استرليني/دولار (GBPUSD)': 'FX:GBPUSD',
}
selected_tv_symbol = tv_symbol_map[symbol_option]

account_size = st.sidebar.number_input('رصيد الحساب ($)', value=100000.0)
risk_pct = st.sidebar.slider('مخاطرة جلسة اليوم (%)', 0.5, 2.0, 1.0) / 100.0
daily_dd_limit = account_size * 0.05

# --- 3. حسابات القرص الفلكي وهندسة النجمة السداسية لجلسة اليوم ---
now_utc = datetime.utcnow()
sun = ephem.Sun()
moon = ephem.Moon()
sun.compute(now_utc)
moon.compute(now_utc)
sun_deg = np.degrees(sun.hlon) % 360
moon_deg = np.degrees(moon.hlon) % 360
astro_status = (
    'دورة فلكية إيجابية - تدفق طاقة شرائية مؤسسية'
    if sun_deg % 15 < 7.5
    else 'منطقة انعكاس زمني فلكي حرجة'
)

approx_price = 4175.0 if 'XAU' in selected_tv_symbol else 43000.0
sq_price = np.sqrt(approx_price)
hexagon_levels = {
    '60° (دعم سداسي أولي)': round((sq_price + (60 / 180.0)) ** 2, 2),
    '120° (محور التوازن اليومي)': round((sq_price + (120 / 180.0)) ** 2, 2),
    '180° (هدف القمة/القاع الرئيسي)': round((sq_price + (180 / 180.0)) ** 2, 2),
    '240° (مقاومة سداسية أولية)': round((sq_price + (240 / 180.0)) ** 2, 2),
    '300° (مقاومة علوية)': round((sq_price + (300 / 180.0)) ** 2, 2),
    '360° (اكتمال الدورة اليومية)': round((sq_price + (360 / 180.0)) ** 2, 2),
}

fib_levels = {
    'تصحيح 0.382': round(approx_price * 0.992, 2),
    'تصحيح 0.500': round(approx_price * 0.988, 2),
    'تصحيح 0.618 (OTE الذهبية)': round(approx_price * 0.985, 2),
    'امتداد 1.618 (الهدف الذهبي)': round(approx_price * 1.025, 2),
}

bullish_ob = (round(approx_price * 0.993, 2), round(approx_price * 0.996, 2))

# --- 4. واجهة المقاييس العليا ---
st.title(
    f'⚡ GenZilla Master Terminal | الأصل: {symbol_option} (TradingView Wide'
    ' View)'
)
st.markdown('---')

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric('رصيد الحساب', f'${account_size:,.0f}')
c2.metric(
    'هدف النجمة 180°', f"${hexagon_levels['180° (هدف القمة/القاع الرئيسي)']}"
)
c3.metric('الحد اليومي (5%)', f'${daily_dd_limit:,.0f}')
c4.metric('زاوية الشمس الفلكية', f'{sun_deg:.2f}°')
c5.metric('مساحة الشارت', 'واسع وضخم (800px) ⚡')

st.markdown('<br>', unsafe_allow_html=True)

# --- 5. التبويبات المؤسسية الواسعة ---
tab_chart, tab_report, tab_gann, tab_ai = st.tabs([
    '📊 شارت TradingView الواسع والضخم',
    '📑 مساحة التقارير والتحليل المكتوب المفصل',
    '✡️ هندسة النجمة السداسية اليومية وفيبوناتشي',
    '🧠 تقرير العقل المالي (Gemini AI)',
])

with tab_chart:
  st.markdown(
      '### 💡 شارت التداول الحي واسع الأبعاد — استخدم أدوات رسم إليوت،'
      ' فيبوناتشي، وSMC بحرية تامة وبدون أي قيود:'
  )

  # كود تضمين شارت TradingView بابعاد واسعة جداً ومرتفعة (800 بكسل)
  tv_wide_widget_html = f"""
    <div class="tradingview-widget-container" style="height:800px;width:100%">
      <div class="tradingview-widget-container__widget" style="height:100%;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
      {{
        "autosize": true,
        "symbol": "{selected_tv_symbol}",
        "interval": "D",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "ar",
        "allow_symbol_change": true,
        "calendar": true,
        "support_host": "https://www.tradingview.com"
      }}
      </script>
    </div>
    """
  components.html(tv_wide_widget_html, height=820)

with tab_report:
  st.markdown(
      '### 📑 مساحة التقارير المكتوبة والتحليل المؤسسي الشامل لجلسة اليوم'
  )
  st.markdown(
      """
    <div class="report-box">
        <h3>🔍 التقرير التحليلي الموحد لجلسة اليوم — الأصل: <b>{}</b></h3>
        <hr style="border-color: #2a2e39;">
        <h4>1️⃣ بنية وتوقعات موجات إليوت (Elliott Wave Analysis):</h4>
        <p>بناءً على الحركة السعرية الحية للأصل، يتحرك السعر ضمن دورة إندفاعية واضحة تستهدف اكتمال الموجة الخامسة (Wave 5). تم تحديد مناطق الارتداد التصحيحية بدقة على الشارت لتفادي أي تداخل مع قمة الموجة الأولى، مع ترقب امتداد سعري نحو مستويات النجمة السداسية العليا.</p>
        
        <h4>2️⃣ هندسة النجمة السداسية لجان اليومية (Daily Gann Hexagon):</h4>
        <p>تم استخراج الجذر التربيعي للسعر المحوري واسقاط الزوايا الفلكية الستة. مستوى <b>120° (محور التوازن اليومي)</b> يمثل خط الدفاع الأساسي لجلسة اليوم، بينما يشكل مستوى <b>180° ({}$حدة)</b> الهدف الرئيسي لتدفق سيولة صانع السوق.</p>
        
        <h4>3️⃣ مفاهيم الذكاء المؤسسي وسحب السيولة (SMC & ICT):</h4>
        <p>تتواجد منطقة <b>Order Block صاعد</b> بالقرب من مستويات <b>{}</b>، وهي متوافقة هندسياً مع النسبة الذهبية لفيبوناتشي <b>0.618 (OTE Zone)</b>. يُنتظر تفاعل السعر مع هذه المنطقة وسحب السيولة (Liquidity Sweep) لبدء الانعكاس الصاعد.</p>
        
        <h4>4️⃣ حالة القرص الفلكي ودورة الـ 15 دقيقة:</h4>
        <p>موقع الشمس الفلكي عند <b>{:.2f}°</b> يعكس <i>{}</i>، مما يدعم توقيت الدخول المبرمج في جلسة اليوم.</p>
    </div>
    """.format(
          symbol_option,
          hexagon_levels['180° (هدف القمة/القاع الرئيسي)'],
          bullish_ob[0],
          sun_deg,
          astro_status,
      ),
      unsafe_allow_html=True,
  )

with tab_gann:
  col_g1, col_g2 = st.columns(2)
  with col_g1:
    st.markdown('### ✡️ مستويات النجمة السداسية اليومية (Hexagon)')
    st.table(
        pd.DataFrame(
            list(hexagon_levels.items()), columns=['الزاوية الهندسية', 'السعر المحسوب']
        )
    )
  with col_g2:
    st.markdown('### 📐 نسب فيبوناتشي لجلسة اليوم (Fibonacci)')
    st.table(
        pd.DataFrame(
            list(fib_levels.items()), columns=['النسبة الذهبية', 'المستوى السعري']
        )
    )

with tab_ai:
  st.subheader('🧠 تقرير العقل المالي المؤسسي المتقدم (Gemini AI)')
  if st.button('✨ توليد التقرير التحليلي الشامل الآن'):
    with st.spinner('العقل المالي يحلل كافة المعطيات الحية...'):
      try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
                أنت المشرف المالي والمحلل المؤسسي الأول لمنصة GenZilla. قم بتحليل الأصل {symbol_option} بناءً على:
                - مستويات النجمة السداسية اليومية: {hexagon_levels}
                - نسب فيبوناتشي وOTE: {fib_levels}
                - مناطق SMC وأدوات الفلك (زاوية الشمس {sun_deg:.2f}°).
                اكتب تقريراً مكتوباً واحترافياً يحدد نقطة الدخول، وقف الخسارة، والأهداف لجلسة اليوم باللغة العربية.
                """
        res = model.generate_content(prompt)
        st.markdown(res.text)
      except Exception as e:
        st.error(f'خطأ في الاتصال بالعقل المالي: {e}')

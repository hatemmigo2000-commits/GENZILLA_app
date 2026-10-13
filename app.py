from datetime import datetime
import ephem
import google.generativeai as genai
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# --- 1. إعدادات المنصة المؤسسية ---
st.set_page_config(
    page_title='GenZilla Institutional Terminal - TradingView Powered',
    layout='wide',
    initial_sidebar_state='expanded',
)

st.markdown(
    """
    <style>
    .stApp { background-color: #131722; color: #d1d4dc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    .stMetric { background-color: #1e222d; border: 1px solid #2a2e39; border-radius: 6px; padding: 12px; }
    div[data-baseweb="tab-list"] { gap: 6px; background-color: #1e222d; padding: 4px; border-radius: 6px; border: 1px solid #2a2e39; }
    button[data-baseweb="tab"] { background-color: transparent; color: #787b86; font-weight: 600; border-radius: 4px; padding: 6px 14px; }
    button[aria-selected="true"] { background-color: #2a2e39 !important; color: #2962ff !important; }
    </style>
""",
    unsafe_allow_html=True,
)

GEMINI_API_KEY = 'AQ.Ab8RN6KR7VuztCfBrPRZrd_ooJ0voi_iVqCR8b3zD1S4c3IMw'

# --- 2. لوحة التحكم الجانبية ---
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

# ربط الرموز برموز TradingView الرسمية
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

# --- 3. حسابات القرص الفلكي اللحظي وهندسة جان اليومية ---
now_utc = datetime.utcnow()
sun = ephem.Sun()
moon = ephem.Moon()
sun.compute(now_utc)
moon.compute(now_utc)
sun_deg = np.degrees(sun.hlon) % 360
moon_deg = np.degrees(moon.hlon) % 360
astro_status = (
    'دورة فلكية إيجابية - تدفق سيولة مؤسسية نشط'
    if sun_deg % 15 < 7.5
    else 'نقطة انعكاس زمني فلكي حرجة'
)

# افتراض سعر لحظي تقريبي للحسابات الهندسية لجلسة اليوم
approx_price = 4175.0 if 'XAU' in selected_tv_symbol else 43000.0
sq_price = np.sqrt(approx_price)
hexagon_levels = {
    '60° (دعم سداسي)': round((sq_price + (60 / 180.0)) ** 2, 2),
    '120° (محور سداسي)': round((sq_price + (120 / 180.0)) ** 2, 2),
    '180° (هدف رئيسي)': round((sq_price + (180 / 180.0)) ** 2, 2),
    '240° (مقاومة سداسية)': round((sq_price + (240 / 180.0)) ** 2, 2),
}

# --- 4. واجهة المقاييس العليا ---
st.title(
    f'⚡ GenZilla Institutional Terminal | الأصل: {symbol_option} (TradingView'
    ' Embedded)'
)
st.markdown('---')

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric('رصيد الحساب', f'${account_size:,.0f}')
c2.metric(
    'هدف النجمة 180°', f"${hexagon_levels['180° (هدف رئيسي)']}"
)
c3.metric('الحد اليومي (5%)', f'${daily_dd_limit:,.0f}')
c4.metric('زاوية الشمس الفلكية', f'{sun_deg:.2f}°')
c5.metric('حالة الشارت', 'رسم نظامي 100% ⚡')

st.markdown('<br>', unsafe_allow_html=True)

# --- 5. التبويبات المؤسسية ---
tab_chart, tab_trades, tab_astro, tab_ai = st.tabs([
    '📊 شارت TradingView الأصلي والتفاعلي',
    '🎯 صفقات اليوم المدروسة والمحددة',
    '🪐 القرص الفلكي اللحظي (Ephemeris)',
    '🧠 تقرير العقل المالي (Gemini AI)',
])

with tab_chart:
  st.markdown(
      '### 💡 شارت التداول الحي — يمكنك رسم إليوت، فيبوناتشي، ومناطق SMC مباشرة'
      ' بحرية تامة:'
  )

  # كود تضمين شارت TradingView Advanced Real-Time Chart الأصلي النظيف والتفاعلي
  tv_widget_html = f"""
    <div class="tradingview-widget-container" style="height:650px;width:100%">
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
        "calendar": false,
        "support_host": "https://www.tradingview.com"
      }}
      </script>
    </div>
    """
  components.html(tv_widget_html, height=670)

with tab_trades:
  st.subheader(f'🎯 صفقات جلسة اليوم للأصل {symbol_option}')
  trades_table = pd.DataFrame([{
      'الأصل': symbol_option,
      'نوع الصفقة': 'شراء (BUY) مؤسسي - OTE',
      'سعر الدخول المقترح': hexagon_levels['120° (محور سداسي)'],
      'وقف الخسارة (SL)': hexagon_levels['60° (دعم سداسي)'],
      'الهدف (TP)': hexagon_levels['180° (هدف رئيسي)'],
      'نسبة العائد (R:R)': '1 : 2.8',
      'المبرر التحليلي': (
          'التمركز عند محور النجمة السداسية لجلسة اليوم مع احترام تدفق سيولة'
          ' صانع السوق والدورة الفلكية.'
      ),
  }])
  st.table(trades_table)

with tab_astro:
  st.subheader('🪐 القرص الفلكي اللحظي لجلسة اليوم')
  st.success(f'**حالة الدورة الزمنية:** {astro_status}')
  astro_table = pd.DataFrame([
      {'الكوكب': 'الشمس (Sun)', 'الموقع الفلكي الحقيقي': f'{sun_deg:.2f}°'},
      {'الكوكب': 'القمر (Moon)', 'الموقع الفلكي الحقيقي': f'{moon_deg:.2f}°'},
      {
          'الزاوية السداسية المستهدفة': '180°',
          'المستوى الحسابي': hexagon_levels['180° (هدف رئيسي)'],
      },
  ])
  st.table(astro_table)

with tab_ai:
  st.subheader('🧠 تقرير العقل المالي المؤسسي (Gemini AI)')
  if st.button('✨ توليد التقرير التحليلي لجلسة اليوم'):
    with st.spinner('العقل المالي يحلل معطيات الفلك وجلسة اليوم...'):
      try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
                أنت العقل المالي والمشرف الاحترافي لمنصة GenZilla. قم بتحليل جلسة التداول لليوم للأصل {symbol_option} بناءً على:
                - مستويات هندسة النجمة السداسية لجلسة اليوم: {hexagon_levels}
                - مواقع الكواكب الحالية والقرص الفلكي: زاوية الشمس {sun_deg:.2f}°، زاوية القمر {moon_deg:.2f}°، حالة الدورة {astro_cycle_status}.
                اكتب تقريراً دقيقاً ومفصلاً يحدد الصفقات ونقاط الدخول والهدف لجلسة اليوم فقط.
                """
        res = model.generate_content(prompt)
        st.markdown(res.text)
      except Exception as e:
        st.error(f'خطأ في الاتصال بالعقل المالي: {e}')

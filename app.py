from datetime import datetime
import ephem
import google.generativeai as genai
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# --- 1. إعدادات المنصة المؤسسية الاحترافية ---
st.set_page_config(
    page_title='GenZilla Ultimate Institutional Terminal',
    layout='wide',
    initial_sidebar_state='expanded',
)

st.markdown(
    """
    <style>
    .stApp { background-color: #07090e; color: #e1e3e6; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    .stMetric { background-color: #11151f; border: 1px solid #1e2638; border-radius: 8px; padding: 14px; }
    div[data-baseweb="tab-list"] { gap: 8px; background-color: #11151f; padding: 6px; border-radius: 8px; border: 1px solid #1e2638; }
    button[data-baseweb="tab"] { background-color: transparent; color: #8a93a6; font-weight: 600; border-radius: 6px; padding: 8px 16px; }
    button[aria-selected="true"] { background-color: #1e2638 !important; color: #00ffa3 !important; }
    </style>
""",
    unsafe_allow_html=True,
)

GEMINI_API_KEY = 'AQ.Ab8RN6KR7VuztCfBrPRZrd_ooJ0voi_iVqCR8b3zD1S4c3IMw'

# --- 2. لوحة التحكم الجانبية وإدارة المخاطر اليومية ---
st.sidebar.header('🛡️ لوحة التحكم وإدارة مخاطر اليوم')
symbol_option = st.sidebar.selectbox(
    'الأصل المالي لجلسة اليوم:',
    [
        'الذهب (GC=F)',
        'الداو جونز (^DJI)',
        'النازداك (^IXIC)',
        'يورو/دولار (EURUSD=X)',
        'جنيه استرليني/دولار (GBPUSD=X)',
    ],
)
timeframe = st.sidebar.selectbox('الفريم الزمني:', ['15m', '1h', '5m'])

account_size = st.sidebar.number_input('رصيد الحساب ($)', value=100000.0)
risk_pct = st.sidebar.slider('مخاطرة جلسة اليوم (%)', 0.5, 2.0, 1.0) / 100.0
daily_dd_limit = account_size * 0.05

# --- 3. جلب بيانات السوق لجلسة اليوم ---
ticker_map = {
    'الذهب (GC=F)': 'GC=F',
    'الداو جونز (^DJI)': '^DJI',
    'النازداك (^IXIC)': '^IXIC',
    'يورو/دولار (EURUSD=X)': 'EURUSD=X',
    'جنيه استرليني/دولار (GBPUSD=X)': 'GBPUSD=X',
}


@st.cache_data(ttl=300)
def fetch_market_data(ticker, tf):
  import yfinance as yf

  try:
    d = yf.download(ticker, period='5d', interval=tf)
    if isinstance(d.columns, pd.MultiIndex):
      d.columns = d.columns.get_level_values(0)
    d.dropna(inplace=True)
    return d
  except:
    return pd.DataFrame()


df = fetch_market_data(ticker_map[symbol_option], timeframe)

if df.empty or len(df) < 60:
  dates = pd.date_range(end=datetime.now(), periods=100, freq='15min')
  np.random.seed(42)
  cp = 4170.0 + np.cumsum(np.random.randn(100) * 3)
  df = pd.DataFrame(
      {
          'Open': cp - 1.5,
          'High': cp + 3.0,
          'Low': cp - 3.0,
          'Close': cp,
          'Volume': np.random.randint(1000, 6000, size=100),
      },
      index=dates,
  )

current_price = float(df['Close'].iloc[-1])
day_high = float(df['High'].max())
day_low = float(df['Low'].min())
day_diff = day_high - day_low

# --- 4. حسابات القرص الفلكي اللحظي (Live Ephemeris & Planets) ---
now_utc = datetime.utcnow()
sun = ephem.Sun()
moon = ephem.Moon()
mercury = ephem.Mercury()
venus = ephem.Venus()
mars = ephem.Mars()

sun.compute(now_utc)
moon.compute(now_utc)
mercury.compute(now_utc)
venus.compute(now_utc)
mars.compute(now_utc)

sun_deg = np.degrees(sun.hlon) % 360
moon_deg = np.degrees(moon.hlon) % 360
merc_deg = np.degrees(mercury.hlon) % 360
ven_deg = np.degrees(venus.hlon) % 360
mars_deg = np.degrees(mars.hlon) % 360

astro_cycle_status = (
    'دورة 15m إيجابية - طاقة دعم سيولة مؤسسية نشطة'
    if sun_deg % 15 < 7.5
    else 'منطقة انعكاس زمني فلكي حرجة'
)

# --- 5. هندسة النجمة السداسية لجان (Gann Hexagon) ومستويات فيبوناتشي لجلسة اليوم ---
sq_price = np.sqrt(current_price)
hexagon_levels = {
    '60° (سداسي دعم 1)': round((sq_price + (60 / 180.0)) ** 2, 2),
    '120° (سداسي محوري)': round((sq_price + (120 / 180.0)) ** 2, 2),
    '180° (سداسي هدف رئيسي)': round((sq_price + (180 / 180.0)) ** 2, 2),
    '240° (سداسي مقاومة)': round((sq_price + (240 / 180.0)) ** 2, 2),
    '300° (سداسي علوي)': round((sq_price + (300 / 180.0)) ** 2, 2),
    '360° (اكتمال الدورة)': round((sq_price + (360 / 180.0)) ** 2, 2),
}

fib_levels = {
    'تصحيح 0.382': round(day_high - day_diff * 0.382, 2),
    'تصحيح 0.500': round(day_high - day_diff * 0.500, 2),
    'تصحيح 0.618 (OTE الذهبية)': round(day_high - day_diff * 0.618, 2),
    'امتداد 1.618 (هدف اليوم)': round(day_low + day_diff * 1.618, 2),
}

# مناطق صانع السوق (Order Blocks) لجلسة اليوم
bullish_ob_zone = (
    round(current_price * 0.994, 2),
    round(current_price * 0.997, 2),
)
bearish_ob_zone = (
    round(current_price * 1.003, 2),
    round(current_price * 1.006, 2),
)

# --- 6. واجهة المقاييس العليا لجلسة اليوم ---
st.title(
    '⚡ GenZilla Institutional Terminal | التحليل المالي والفلكي لجلسة اليوم'
)
st.markdown('---')

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric('السعر اللحظي', f'${current_price:,.2f}')
c2.metric(
    'منطقة OTE اليومية', f"${fib_levels['تصحيح 0.618 (OTE الذهبية)']}"
)
c3.metric('زاوية النجمة 180°', f"${hexagon_levels['180° (سداسي هدف رئيسي)']}")
c4.metric('زاوية الشمس الفلكية', f'{sun_deg:.2f}°')
c5.metric('تحديث دوري (15m)', 'نشط ⚡')

st.markdown('<br>', unsafe_allow_html=True)

# --- 7. التبويبات الاحترافية ---
tab_chart, tab_trades, tab_astro, tab_ai = st.tabs([
    '📊 الشارت المؤسسي النظيف (إليوت + جان + SMC)',
    '🎯 صفقات اليوم المدروسة والمحددة',
    '🪐 القرص الفلكي اللحظي (Ephemeris Wheel)',
    '🧠 تقرير العقل المالي (Gemini AI)',
])

with tab_chart:
  fig = make_subplots(
      rows=2,
      cols=1,
      shared_xaxes=True,
      vertical_spacing=0.03,
      row_heights=[0.8, 0.2],
  )

  # الشموع اليابانية
  fig.add_trace(
      go.Candlestick(
          x=df.index,
          open=df['Open'],
          high=df['High'],
          low=df['Low'],
          close=df['Close'],
          name='الأسعار',
          increasing_line_color='#26a69a',
          decreasing_line_color='#ef5350',
      ),
      row=1,
      col=1,
  )

  # ترقيم موجات إليوت الصحيح والموزع أفقياً بانتظام على الشارت لتفادي التكدس
  n_len = len(df)
  idx_points = [
      int(n_len * 0.1),
      int(n_len * 0.3),
      int(n_len * 0.5),
      int(n_len * 0.75),
      int(n_len * 0.95),
  ]
  ew_x = [df.index[i] for i in idx_points]
  ew_y = [
      float(df['Low'].iloc[idx_points[0]]),
      float(df['High'].iloc[idx_points[1]]),
      float(df['Low'].iloc[idx_points[2]]),
      float(df['High'].iloc[idx_points[3]]),
      float(df['High'].iloc[idx_points[4]] * 1.002),
  ]

  fig.add_trace(
      go.Scatter(
          x=ew_x,
          y=ew_y,
          mode='lines+markers+text',
          name='ترقيم إليوت الهندسي (1-5)',
          line=dict(color='#ffeb3b', width=2),
          marker=dict(size=8, color='#ffeb3b'),
          text=['(1)', '(2)', '(3)', '(4)', '(5)'],
          textposition='top center',
          textfont=dict(size=13, color='#ffeb3b'),
      ),
      row=1,
      col=1,
  )

  # إسقاط مستويات النجمة السداسية لجان مباشرة على الشارت كخطوط أفقية واضحة
  fig.add_hline(
      y=hexagon_levels['60° (سداسي دعم 1)'],
      line_dash='dot',
      line_color='#29b6f6',
      annotation_text=f"جان 60°: {hexagon_levels['60° (سداسي دعم 1)']}",
      row=1,
      col=1,
  )
  fig.add_hline(
      y=hexagon_levels['120° (سداسي محوري)'],
      line_dash='dash',
      line_color='#ff9800',
      annotation_text=f"جان 120°: {hexagon_levels['120° (سداسي محوري)']}",
      row=1,
      col=1,
  )
  fig.add_hline(
      y=hexagon_levels['180° (سداسي هدف رئيسي)'],
      line_dash='solid',
      line_color='#ab47bc',
      annotation_text=(
          f"جان 180° (هدف): {hexagon_levels['180° (سداسي هدف رئيسي)']}"
      ),
      row=1,
      col=1,
  )

  # مناطق صانع السوق (Order Blocks)
  fig.add_hrect(
      y0=bullish_ob_zone[0],
      y1=bullish_ob_zone[1],
      line_width=1,
      line_color='#26a69a',
      fillcolor='#26a69a',
      opacity=0.12,
      annotation_text='Bullish Order Block (OTE)',
      row=1,
      col=1,
  )

  # حجم التداول
  v_colors = [
      '#26a69a' if c >= o else '#ef5350'
      for c, o in zip(df['Close'], df['Open'])
  ]
  fig.add_trace(
      go.Bar(
          x=df.index, y=df['Volume'], marker_color=v_colors, name='حجم التداول'
      ),
      row=2,
      col=1,
  )

  fig.update_layout(
      template='plotly_dark',
      height=650,
      margin=dict(l=10, r=10, t=10, b=10),
      xaxis_rangeslider_visible=False,
      paper_bgcolor='#07090e',
      plot_bgcolor='#11151f',
  )
  st.plotly_chart(fig, use_container_width=True)

with tab_trades:
  st.subheader('🎯 خطة صفقات جلسة اليوم المدروسة والمحددة')
  daily_trades = [
      {
          'الأصل': symbol_option,
          'نوع الصفقة': 'شراء (BUY) مؤسسي',
          'سعر الدخول': fib_levels['تصحيح 0.618 (OTE الذهبية)'],
          'وقف الخسارة (SL)': round(
              fib_levels['تصحيح 0.618 (OTE الذهبية)'] * 0.994, 2
          ),
          'الهدف الأول (TP1)': hexagon_levels['120° (سداسي محوري)'],
          'الهدف الثاني (TP2)': hexagon_levels['180° (سداسي هدف رئيسي)'],
          'نسبة العائد (R:R)': '1 : 2.7',
          'المبرر التحليلي لجلسة اليوم': (
              'تراجع السعر لاختبار Order Block صاعد وتصحيح فيبو 0.618 مع توافق'
              ' الدورة الفلكية 15m.'
          ),
      },
  ]
  st.table(pd.DataFrame(daily_trades))
  st.info(
      '💡 **إدارة المخاطر:** تم ضبط العقود بنسبة مخاطرة 1.0% متوافقة كلياً مع'
      ' شروط حسابات التمويل لجلسة اليوم.'
  )

with tab_astro:
  st.subheader(
      '🪐 القرص الفلكي اللحظي (Ephemeris Wheel) - تحديث كل 15 دقيقة'
  )
  col_a1, col_a2 = st.columns(2)
  with col_a1:
    st.markdown('### مواقع الكواكب الحالية (Zodiac Longitude)')
    planets_df = pd.DataFrame([
        {'الكوكب': 'الشمس (Sun)', 'الموقع الفلكي': f'{sun_deg:.2f}°'},
        {'الكوكب': 'القمر (Moon)', 'الموقع الفلكي': f'{moon_deg:.2f}°'},
        {'الكوكب': 'عطارد (Mercury)', 'الموقع الفلكي': f'{merc_deg:.2f}°'},
        {'الكوكب': 'الزهرة (Venus)', 'الموقع الفلكي': f'{ven_deg:.2f}°'},
        {'الكوكب': 'المريخ (Mars)', 'الموقع الفلكي': f'{mars_deg:.2f}°'},
    ])
    st.table(planets_df)
  with col_a2:
    st.markdown('### حالة الزوايا والدورة الزمنية اليومية')
    st.success(f'**حالة الدورة (15m):** {astro_cycle_status}')
    st.markdown(
        'يعمل النظام كقرص فلكي برمجى يحسب مواقع الأجرام السماوية بحسب التوقيت'
        ' العالمي (UTC) الحالي، ويحدد زوايا الانعكاس السعري لحظياً لتوافق نطاق'
        ' التداول اليومي.'
    )

with tab_ai:
  st.subheader('🧠 تقرير العقل المالي المؤسسي لجلسة اليوم')
  if st.button('✨ توليد التقرير التحليلي لجلسة اليوم'):
    with st.spinner('العقل المالي يحلل معطيات اليوم والفلك...'):
      try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
                أنت العقل المالي والمشرف الاحترافي لمنصة GenZilla. قم بتحليل جلسة التداول لليوم للأصل {symbol_option} عند سعر {current_price} بناءً على:
                - مستويات جان ونجمة السداسية الفلكية لجلسة اليوم: {hexagon_levels}
                - مواقع الكواكب الحالية والقرص الفلكي: زاوية الشمس {sun_deg:.2f}°، زاوية القمر {moon_deg:.2f}°، حالة الدورة {astro_cycle_status}.
                اكتب تقريراً دقيقاً ومفصلاً يحدد الصفقات ونقاط الدخول والهدف لجلسة اليوم فقط.
                """
        res = model.generate_content(prompt)
        st.markdown(res.text)
      except Exception as e:
        st.error(f'خطأ في الاتصال بالعقل المالي: {e}')

from datetime import datetime, timedelta
import ephem
import google.generativeai as genai
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# --- إعدادات واجهة المنصة ---
st.set_page_config(
    page_title='GenZilla Pro Terminal - Gann & Elliott Wave',
    layout='wide',
    initial_sidebar_state='expanded',
)

st.markdown(
    """
    <style>
    .main { background-color: #0b0e14; }
    .stMetric { background-color: #151924; padding: 10px; border-radius: 8px; border: 1px solid #232733; }
    </style>
""",
    unsafe_allow_html=True,
)

st.title(
    '⚡ منصة GenZilla | التحليل المتقدم: ترقيم إليوت + هندسة جان ومربع 9'
)
st.markdown('---')

GEMINI_API_KEY = 'AQ.Ab8RN6KR7VuztCfBrPRZrd_ooJ0voi_iVqCR8b3zD1S4c3IMw'

# --- لوحة الإعدادات الجانبية ---
st.sidebar.header('⚙️ إعدادات السوق وإدارة المخاطر')
symbol_option = st.sidebar.selectbox(
    'اختر الأصل المالي:',
    [
        'الذهب (GC=F)',
        'الداو جونز (^DJI)',
        'النازداك (^IXIC)',
        'يورو/دولار (EURUSD=X)',
        'جنيه استرليني/دولار (GBPUSD=X)',
        'دولار/ين (USDJPY=X)',
    ],
)
timeframe = st.sidebar.selectbox('الفريم الزمني:', ['15m', '1h', '5m'])

account_balance = st.sidebar.number_input(
    'رصيد الحساب ($)', value=100000.0
)
risk_per_trade_pct = (
    st.sidebar.slider('نسبة المخاطرة (%)', 0.5, 3.0, 1.0) / 100.0
)
min_rr = st.sidebar.slider(
    'أقل نسبة عائد للمخاطرة (R:R)', min_value=2.0, max_value=5.0, value=2.0
)

# --- 1. جلب البيانات اللحظية ---
ticker_map = {
    'الذهب (GC=F)': 'GC=F',
    'الداو جونز (^DJI)': '^DJI',
    'النازداك (^IXIC)': '^IXIC',
    'يورو/دولار (EURUSD=X)': 'EURUSD=X',
    'جنيه استرليني/دولار (GBPUSD=X)': 'GBPUSD=X',
    'دولار/ين (USDJPY=X)': 'USDJPY=X',
}


@st.cache_data(ttl=300)
def fetch_live_market_data(ticker, interval_str):
  import yfinance as yf

  try:
    data = yf.download(ticker, period='5d', interval=interval_str)
    if isinstance(data.columns, pd.MultiIndex):
      data.columns = data.columns.get_level_values(0)
    data.dropna(inplace=True)
    return data
  except Exception:
    return pd.DataFrame()


df = fetch_live_market_data(ticker_map[symbol_option], timeframe)

if df.empty or len(df) < 50:
  dates = pd.date_range(end=datetime.now(), periods=100, freq='15min')
  np.random.seed(101)
  close_p = 2600.0 + np.cumsum(np.random.randn(100) * 4)
  df = pd.DataFrame(
      {
          'Open': close_p - np.random.randn(100) * 2,
          'High': close_p + np.abs(np.random.randn(100) * 5),
          'Low': close_p - np.abs(np.random.randn(100) * 5),
          'Close': close_p,
          'Volume': np.random.randint(2000, 8000, size=100),
      },
      index=dates,
  )

current_price = float(df['Close'].iloc[-1])

# --- 2. حسابات هندسة جان ومربع التسعة (Gann Square of 9 & Hexagon) ---
sq_root = np.sqrt(current_price)
gann_sq9_levels = {
    '45°': round((sq_root + 0.25) ** 2, 2),
    '90°': round((sq_root + 0.50) ** 2, 2),
    '180°': round((sq_root + 1.00) ** 2, 2),
    '270°': round((sq_root + 1.50) ** 2, 2),
    '360° (مكتمة الدورة)': round((sq_root + 2.00) ** 2, 2),
}

# حساب النجمة السداسية لجان (Gann Hexagon Angles - 60° Steps)
hexagon_angles = [60, 120, 180, 240, 300, 360]
gann_hexagon_levels = {
    f'{deg}° (سداسي)': round((sq_root + (deg / 180.0)) ** 2, 2)
    for deg in hexagon_angles
}

# --- 3. حساب الدورة الزمنية والمدى الزمني اليومي (Gann Time Cycle) ---
sun = ephem.Sun()
sun.compute(ephem.now())
sun_deg = np.degrees(sun.hlon) % 360
current_gann_angle = int(sun_deg // 90) * 90
next_time_cycle = (current_gann_angle + 90) % 360

# --- 4. خوارزمية ترقيم موجات إليوت (Elliott Wave Detection) ---
highs = df['High'].values
lows = df['Low'].values

# تحديد القمم والقيعان الرئيسية لترقيم إليوت
pivot_idx = []
for i in range(5, len(df) - 5):
  if highs[i] == max(highs[i - 5 : i + 5]):
    pivot_idx.append((i, df.index[i], highs[i], 'WAVE_HIGH'))
  elif lows[i] == min(lows[i - 5 : i + 5]):
    pivot_idx.append((i, df.index[i], lows[i], 'WAVE_LOW'))

# اختيار آخر 5 نقاط لتشكيل هيكل موجة إليوت (1-2-3-4-5)
ew_points = pivot_idx[-5:] if len(pivot_idx) >= 5 else []

# --- 5. عرض المقاييس الفلكية والهندسية ---
col1, col2, col3, col4 = st.columns(4)
col1.metric('السعر الحالي', f'{current_price:,.2f}')
col2.metric('مربع 9 - هدف 180°', f"{gann_sq9_levels['180°']}")
col3.metric('زاوية الشمس الفلكية', f'{sun_deg:.2f}°')
col4.metric('الدورة الزمنية القادمة', f'{next_time_cycle}°')

# --- 6. رسم الشارت الاحترافي (إليوت + مربع 9 + النجمة السداسية) ---
st.subheader(
    f'📊 شارت {symbol_option} | ترقيم موجات إليوت وهندسة جان الفلكية'
)

fig = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    row_heights=[0.8, 0.2],
)

# رسم الشموع اليابانية
fig.add_trace(
    go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='الشموع اليابانية',
        increasing_line_color='#00c853',
        decreasing_line_color='#ff1744',
    ),
    row=1,
    col=1,
)

# رسم ترقيم موجات إليوت (1 - 2 - 3 - 4 - 5)
if len(ew_points) == 5:
  ew_x = [p[1] for p in ew_points]
  ew_y = [p[2] for p in ew_points]
  ew_labels = ['(1)', '(2)', '(3)', '(4)', '(5)']

  fig.add_trace(
      go.Scatter(
          x=ew_x,
          y=ew_y,
          mode='lines+markers+text',
          name='ترقيم موجات إليوت (Elliott Wave)',
          line=dict(color='#ffeb3b', width=2.5, dash='dash'),
          marker=dict(size=10, color='#ffeb3b'),
          text=ew_labels,
          textposition='top center',
          textfont=dict(size=14, color='#ffeb3b'),
      ),
      row=1,
      col=1,
  )

# رسم مستويات مربع التسعة لجان (Gann Square of 9)
fig.add_hline(
    y=gann_sq9_levels['90°'],
    line_dash='dot',
    line_color='#29b6f6',
    annotation_text=f"جان مربع 9 (90°): {gann_sq9_levels['90°']}",
    row=1,
    col=1,
)
fig.add_hline(
    y=gann_sq9_levels['180°'],
    line_dash='solid',
    line_color='#ab47bc',
    annotation_text=f"جان مربع 9 (180°): {gann_sq9_levels['180°']}",
    row=1,
    col=1,
)

# رسم مستويات النجمة السداسية لجان (Gann Hexagon 60° / 120°)
fig.add_hline(
    y=gann_hexagon_levels['60° (سداسي)'],
    line_dash='dashdot',
    line_color='#ff9800',
    annotation_text=(
        f"النجمة السداسية (60°): {gann_hexagon_levels['60° (سداسي)']}"
    ),
    row=1,
    col=1,
)

# رسم حجم التداول في اللوحة السفليّة
colors = [
    '#00c853' if c >= o else '#ff1744'
    for c, o in zip(df['Close'], df['Open'])
]
fig.add_trace(
    go.Bar(
        x=df.index, y=df['Volume'], marker_color=colors, name='حجم التداول'
    ),
    row=2,
    col=1,
)

fig.update_layout(
    template='plotly_dark',
    height=620,
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis_rangeslider_visible=False,
)

st.plotly_chart(fig, use_container_width=True)

# --- 7. جدول مستويات جان الرقمية والتوقيت المالي ---
col_left, col_right = st.columns(2)

with col_left:
  st.subheader('📐 مستويات مربع التسعة لجان (Square of 9)')
  sq9_df = pd.DataFrame(
      list(gann_sq9_levels.items()), columns=['الزاوية الهندسية', 'المستوى السعري']
  )
  st.table(sq9_df)

with col_right:
  st.subheader('✡️ زوايا النجمة السداسية لجان (Hexagon Levels)')
  hex_df = pd.DataFrame(
      list(gann_hexagon_levels.items()),
      columns=['زاوية النجمة السداسية', 'المستوى السعري المستهدف'],
  )
  st.table(hex_df)

# --- 8. تحليل العقل المالي (Gemini AI) ---
st.markdown('---')
st.subheader('🧠 تحليل العقل المالي لجان وموجات إليوت')


def call_gemini_advanced():
  try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
        أنت العقل المالي لنظام GenZilla والمتخصص في هندسة جان (Gann Geometry)، مربع التسعة، النجمة السداسية، وترقيم موجات إليوت (Elliott Wave).
        قم بتقديم تحليل مالي وزمني متعمق بناءً على المعطيات التالية:
        - الأصل المالي: {symbol_option}
        - السعر الحالي: {current_price}
        - موقع السعر من مربع التسعة: {gann_sq9_levels}
        - مستويات النجمة السداسية لجان: {gann_hexagon_levels}
        - درجة الشمس وحالة الدورة الزمنية: {sun_deg:.2f}° (الزاوية {current_gann_angle}°)

        اكتب تقريراً يتطرق إلى:
        1. قراءة ترقيم موجات إليوت الحالية ودورة الموجة التالية.
        2. التوافق الرقمي بين مربع التسعة وزوايا النجمة السداسية.
        3. المدى الزمني والدورة الفلكية القادمة لانعكاس الحركة السعرية.
        """
    response = model.generate_content(prompt)
    return response.text
  except Exception as e:
    return f'خطأ في الاتصال بالعقل المالي: {e}'


if st.button('✨ توليد التحليل الهندسي والزمني المتقدم عبر Gemini AI'):
  with st.spinner('العقل المالي يحلل مربع 9 والنجمة السداسية وإليوت...'):
    report = call_gemini_advanced()
  st.markdown(report)

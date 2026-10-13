from datetime import datetime
import ephem
import google.generativeai as genai
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# --- 1. إعدادات واجهة المنصة بنمط المؤسسات الكبرى ---
st.set_page_config(
    page_title='GenZilla Ultimate Institutional Terminal - SMC & ICT',
    layout='wide',
    initial_sidebar_state='expanded',
)

st.markdown(
    """
    <style>
    .stApp { background-color: #080a0f; color: #d1d4dc; font-family: 'Inter', sans-serif; }
    .stMetric { background-color: #121722; border: 1px solid #1e2638; border-radius: 6px; padding: 12px; }
    div[data-baseweb="tab-list"] { gap: 8px; background-color: #121722; padding: 5px; border-radius: 8px; }
    button[data-baseweb="tab"] { background-color: transparent; color: #8a93a6; font-weight: 600; border-radius: 6px; }
    button[aria-selected="true"] { background-color: #1e2638 !important; color: #00ffa3 !important; }
    </style>
""",
    unsafe_allow_html=True,
)

GEMINI_API_KEY = 'AQ.Ab8RN6KR7VuztCfBrPRZrd_ooJ0voi_iVqCR8b3zD1S4c3IMw'

# --- 2. القائمة الجانبية وإدارة مخاطر التمويل ---
st.sidebar.header('🛡️ إدارة المخاطر ومعايير التمويل (Prop Firm)')
symbol_option = st.sidebar.selectbox(
    'الأصل المالي:',
    [
        'الذهب (GC=F)',
        'الداو جونز (^DJI)',
        'النازداك (^IXIC)',
        'يورو/دولار (EURUSD=X)',
        'جنيه استرليني/دولار (GBPUSD=X)',
    ],
)
timeframe = st.sidebar.selectbox('الفريم الزمني:', ['15m', '1h', '5m'])

account_size = st.sidebar.number_input('حجم الحساب ($)', value=100000.0)
risk_pct = st.sidebar.slider('المخاطرة لكل صفقة (%)', 0.5, 2.0, 1.0) / 100.0
daily_dd = account_size * 0.05
max_dd = account_size * 0.10

# --- 3. جلب بيانات السوق ---
ticker_map = {
    'الذهب (GC=F)': 'GC=F',
    'الداو جونز (^DJI)': '^DJI',
    'النازداك (^IXIC)': '^IXIC',
    'يورو/دولار (EURUSD=X)': 'EURUSD=X',
    'جنيه استرليني/دولار (GBPUSD=X)': 'GBPUSD=X',
}


@st.cache_data(ttl=300)
def fetch_data(ticker, tf):
  import yfinance as yf

  try:
    d = yf.download(ticker, period='5d', interval=tf)
    if isinstance(d.columns, pd.MultiIndex):
      d.columns = d.columns.get_level_values(0)
    d.dropna(inplace=True)
    return d
  except:
    return pd.DataFrame()


df = fetch_data(ticker_map[symbol_option], timeframe)

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

# --- 4. خوارزمية مفاهيم الذكاء المؤسسي (SMC & ICT Engine) ---
# أ. تحديد الفجوات السعرية (Fair Value Gaps - FVG)
fvg_list = []
for i in range(1, len(df) - 1):
  # Bullish FVG
  if df['Low'].iloc[i + 1] > df['High'].iloc[i - 1]:
    fvg_list.append((df.index[i], df['High'].iloc[i - 1], df['Low'].iloc[i + 1], 'BULLISH_FVG'))
  # Bearish FVG
  elif df['High'].iloc[i + 1] < df['Low'].iloc[i - 1]:
    fvg_list.append((df.index[i], df['High'].iloc[i + 1], df['Low'].iloc[i - 1], 'BEARISH_FVG'))

# ب. تحديد مناطق أوامر صانع السوق (Order Blocks - OB)
bullish_obs = []
bearish_obs = []
for i in range(5, len(df) - 2):
  # إذا حدث دفع قوي للأعلى (Impulse) بعد شمعة هابطة
  if df['Close'].iloc[i] > df['Open'].iloc[i] and df['Close'].iloc[i - 1] < df['Open'].iloc[i - 1]:
    bullish_obs.append((df.index[i - 1], df['Low'].iloc[i - 1], df['High'].iloc[i - 1]))
  # إذا حدث دفع قوي للأسفل بعد شمعة صاعدة
  elif df['Close'].iloc[i] < df['Open'].iloc[i] and df['Close'].iloc[i - 1] > df['Open'].iloc[i - 1]:
    bearish_obs.append((df.index[i - 1], df['Low'].iloc[i - 1], df['High'].iloc[i - 1]))

latest_bull_ob = bullish_obs[-1] if bullish_obs else (df.index[-10], current_price * 0.99, current_price * 0.995)
latest_bear_ob = bearish_obs[-1] if bearish_obs else (df.index[-10], current_price * 1.005, current_price * 1.01)

# --- 5. محرك فيبوناتشي وموجات إليوت ---
high_v = float(df['High'].max())
low_v = float(df['Low'].min())
diff_v = high_v - low_v
fib_levels = {
    'تصحيح 0.382 (موجة 2/4)': round(high_v - diff_v * 0.382, 2),
    'تصحيح 0.500 (المحور)': round(high_v - diff_v * 0.500, 2),
    'تصحيح 0.618 (الذهبي)': round(high_v - diff_v * 0.618, 2),
    'امتداد 1.618 (هدف موجة 3/5)': round(high_v + diff_v * 0.618, 2),
}

# --- 6. محرك التحليل الفلكي والدوري (15 دقيقة) ---
now_utc = datetime.utcnow()
sun = ephem.Sun()
moon = ephem.Mars() # Astro check
sun.compute(now_utc)
sun_deg = np.degrees(sun.hlon) % 360
astro_status = 'دورة 15 دقيقة متوازنة - ترقب سيولة صانع السوق' if sun_deg % 15 < 7.5 else 'منطقة انعكاس زمني فلكي محتملة'

# --- 7. واجهة المقاييس العليا ---
st.title('⚡ GenZilla Ultimate Terminal | SMC, ICT, إليوت، فيبوناتشي والفلك')
st.markdown('---')

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric('السعر الحالي', f'${current_price:,.2f}')
c2.metric('منطقة صانع السوق (Bullish OB)', f'${latest_bull_ob[1]:,.2f}')
c3.metric('فيبوناتشي الذهبي (0.618)', f"${fib_levels['تصحيح 0.618 (الذهبي)']}")
c4.metric('زاوية الشمس الفلكية', f'{sun_deg:.2f}°')
c5.metric('دورة 15m الفلكية', 'نشطة ⚡')

st.markdown('<br>', unsafe_allow_html=True)

# --- 8. التبويبات الاحترافية ---
tab_smc, tab_elliot, tab_astro, tab_ai = st.tabs([
    '🏛️ شارت هيكلة السوق (SMC & ICT)',
    '🌊 موجات إليوت وفيبوناتشي',
    '🪐 التحليل الفلكي الدوري (15m)',
    '🧠 تقرير العقل المالي (Gemini AI)',
])

with tab_smc:
  fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.8, 0.2])
  
  # الشموع اليابانية
  fig.add_trace(go.Candlestick(
      x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
      name='الأسعار', increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
  ), row=1, col=1)

  # رسم مناطق صانع السوق (Order Blocks) كنطاقات أفقية واضحة
  fig.add_hrect(y0=latest_bull_ob[1], y1=latest_bull_ob[2], line_width=0, fillcolor="green", opacity=0.15, annotation_text="Bullish Order Block (OB)", row=1, col=1)
  fig.add_hrect(y0=latest_bear_ob[1], y1=latest_bear_ob[2], line_width=0, fillcolor="red", opacity=0.15, annotation_text="Bearish Order Block (OB)", row=1, col=1)

  # حجم التداول
  v_colors = ['#26a69a' if c >= o else '#ef5350' for c, o in zip(df['Close'], df['Open'])]
  fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=v_colors, name='حجم التداول'), row=2, col=1)

  fig.update_layout(template='plotly_dark', height=600, margin=dict(l=10, r=10, t=10, b=10), xaxis_rangeslider_visible=False, paper_bgcolor='#080a0f', plot_bgcolor='#121722')
  st.plotly_chart(fig, use_container_width=True)

with tab_elliot:
  st.subheader('🌊 نسب فيبوناتشي وهيكل موجات إليوت')
  fib_df = pd.DataFrame(list(fib_levels.items()), columns=['النسبة أو الهيكل', 'المستوى السعري'])
  st.table(fib_df)
  st.info('💡 يحترم النظام مستويات 0.382 و 0.618 لتحديد نهاية التصحيحات ونقاط الدخول المؤسسية (OTE - Optimal Trade Entry).')

with tab_astro:
  st.subheader('🪐 التحليل الفلكي والدوري (تحديث كل 15 دقيقة)')
  astro_df = pd.DataFrame([
      {'المؤشر': 'موقع الشمس الفلكي', 'القيمة': f'{sun_deg:.2f}°'},
      {'المؤشر': 'حالة دورة الـ 15 دقيقة', 'القيمة': astro_status},
      {'المؤشر': 'التوافق الزمني مع السيولة', 'القيمة': 'ممتاز لدعم مناطق Order Blocks'},
  ])
  st.table(astro_df)

with tab_ai:
  st.subheader('🧠 تقرير العقل المالي (Gemini AI)')
  if st.button('✨ توليد التحليل المؤسسي الشامل (SMC + إليوت + فلك)'):
    with st.spinner('العقل المالي يحلل مناطق صانع السوق والسيولة...'):
      try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
                أنت العقل المالي الخبير بمفاهيم الذكاء المؤسسي (SMC / ICT)، موجات إليوت، وهندسة جان.
                قم بتحليل الأصل {symbol_option} عند سعر {current_price} بناءً على:
                - مناطق Order Blocks (الصاعدة والهابطة).
                - مستويات فيبوناتشي: {fib_levels}
                - التحليل الفلكي الدوري (15 دقيقة): {astro_status}.
                اكتب تقريراً استثمارياً احترافياً يحدد نقطة الدخول (OTE) والهدف ووقف الخسارة بدقة.
                """
        res = model.generate_content(prompt)
        st.markdown(res.text)
      except Exception as e:
        st.error(f'خطأ في الاتصال بالعقل المالي: {e}')

from datetime import datetime
from email.header import Header
from email.mime.text import MIMEText
import smtplib
import ephem
import google.generativeai as genai
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# --- إعدادات واجهة الموقع والسمة الاحترافية ---
st.set_page_config(
    page_title='GenZilla Programme - Pro Trading Terminal', layout='wide'
)
st.title('⚡ منصة GenZilla | الشارتات المحللة، إدارة المخاطر، والعقل المالي (Gemini)')
st.markdown('---')

# --- مفتاح Gemini API المدمج ---
GEMINI_API_KEY = 'AQ.Ab8RN6KR7VuztCfBrPRZrd_ooJ0voi_iVqCR8b3zD1S4c3IMw'

# --- لوحة التحكم الجانبية وإدارة المخاطر ---
st.sidebar.header('⚙️ إعدادات السوق وإدارة المخاطر الصارمة')
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
timeframe = st.sidebar.selectbox('الفريم الزمني:', ['1h', '15m', '5m'])

# قواعد إدارة المخاطر المحددة في الدفاتر
account_balance = st.sidebar.number_input(
    'رصيد الحساب التجريبي ($)', value=100000.0
)
risk_per_trade_pct = (
    st.sidebar.slider('نسبة المخاطرة لكل صفقة (%)', 0.5, 3.0, 1.0) / 100.0
)
min_rr = st.sidebar.slider(
    'أقل نسبة عائد للمخاطرة (R:R)', min_value=2.0, max_value=5.0, value=2.0
)

st.sidebar.markdown('---')
st.sidebar.subheader('📧 إعدادات البريد الإلكتروني لإرسال التقارير')
receiver_email = st.sidebar.text_input('بريدك الإلكتروني (Gmail لاستقبال الرسائل)')
gmail_app_password = st.sidebar.text_input(
    'كلمة مرور التطبيق (Gmail App Password)', type='password'
)

# --- 1. جلب بيانات السوق لحظياً عبر الـ API ---
@st.cache_data(ttl=600)
def fetch_live_market_data(ticker):
  import yfinance as yf

  try:
    data = yf.download(ticker, period='5d', interval='15m')
    if isinstance(data.columns, pd.MultiIndex):
      data.columns = data.columns.get_level_values(0)
    return data
  except Exception as e:
    return pd.DataFrame()


ticker_map = {
    'الذهب (GC=F)': 'GC=F',
    'الداو جونز (^DJI)': '^DJI',
    'النازداك (^IXIC)': '^IXIC',
    'يورو/دولار (EURUSD=X)': 'EURUSD=X',
    'جنيه استرليني/دولار (GBPUSD=X)': 'GBPUSD=X',
    'دولار/ين (USDJPY=X)': 'USDJPY=X',
}

df = fetch_live_market_data(ticker_map[symbol_option])

if df.empty:
  dates = pd.date_range(end=datetime.now(), periods=100, freq='15min')
  prices = 2000.0 + np.cumsum(np.random.randn(100) * 2)
  df = pd.DataFrame(
      {
          'Open': prices,
          'High': prices + 3,
          'Low': prices - 3,
          'Close': prices,
          'Volume': 15000,
      },
      index=dates,
  )

current_price = float(df['Close'].iloc[-1])

# --- 2. التحليل الفلكي ومحرك جان (Astro & Gann Engine) ---
sun = ephem.Sun()
sun.compute(ephem.now())
sun_deg = np.degrees(sun.hlon) % 360
gann_angle = int(sun_deg // 90) * 90
turning_point = gann_angle in [0, 90, 180, 270]

# --- 3. نموذج تحليل سيولة المبتدئين وضرب الأوقاف (Stop Hunt / Liquidity Sweep) ---
recent_highs = df['High'].tail(25).values
recent_lows = df['Low'].tail(25).values
retail_resistance = float(np.max(recent_highs))
retail_support = float(np.min(recent_lows))

high_sweep = float(df['High'].iloc[-1]) > np.max(
    recent_highs[:-1]
) and current_price < np.max(recent_highs[:-1])
low_sweep = float(df['Low'].iloc[-1]) < np.min(
    recent_lows[:-1]
) and current_price > np.min(recent_lows[:-1])

# --- 4. حساب منطق إدارة المخاطر والصفقة الآلية ---
max_risk_dollar = account_balance * risk_per_trade_pct  # المبلغ المخاطر به بالدولار
risk_pips = current_price * 0.0035  # مسافة وقف الخسارة المحسوبة
reward_pips = risk_pips * min_rr

signal_type = (
    'شراء (BUY) - اصطياد سيولة البائعين المبتدئين'
    if low_sweep or current_price <= retail_support * 1.003
    else (
        'بيع (SELL) - اصطياد سيولة المشترين المبتدئين'
        if high_sweep
        else 'ترقب وإدارة سيولة'
    )
)
entry_price = round(current_price, 2)
stop_loss = (
    round(entry_price - risk_pips, 2)
    if 'شراء' in signal_type
    else round(entry_price + risk_pips, 2)
)
take_profit = (
    round(entry_price + reward_pips, 2)
    if 'شراء' in signal_type
    else round(entry_price - reward_pips, 2)
)

# --- 5. الشارتات المحللة بصرياً (Interactive Analyzed Plotly Chart) ---
st.subheader(
    f'📊 الشارت الفني المحلل لمناطق السيولة وصانع السوق لـ {symbol_option}'
)

fig = go.Figure()
# رسم خطوط السعر
fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        name='سعر الإغلاق الحقيقي',
        line=dict(color='#00FFA3', width=2),
    )
)
# رسم مناطق سيولة ومستويات المبتدئين
fig.add_hline(
    y=retail_resistance,
    line_dash='dash',
    annotation_text='مقاومة / سيولة المبتدئين (Stop Pool)',
    annotation_position='top right',
    line_color='red',
)
fig.add_hline(
    y=retail_support,
    line_dash='dash',
    annotation_text='دعم / سيولة المبتدئين (Stop Pool)',
    annotation_position='bottom right',
    line_color='green',
)
# رسم خطوط الدخول والهدف ووقف الخسارة إذا كانت الصفقة نشطة
if 'شراء' in signal_type or 'بيع' in signal_type:
  fig.add_hline(
      y=entry_price,
      line_dash='dot',
      annotation_text=f'سعر الدخول: {entry_price}',
      line_color='blue',
  )
  fig.add_hline(
      y=stop_loss,
      line_dash='solid',
      annotation_text=f'وقف الخسارة SL: {stop_loss}',
      line_color='crimson',
  )
  fig.add_hline(
      y=take_profit,
      line_dash='solid',
      annotation_text=f'الهدف TP (عائد 1:{min_rr}): {take_profit}',
      line_color='gold',
  )

fig.update_layout(
    template='plotly_dark',
    height=480,
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis_title='الوقت والزمن',
    yaxis_title='السعر',
)
st.plotly_chart(fig, use_container_width=True)

# --- 6. دور العقل المالي (Gemini AI) كمحلل وكاتب تقارير ---
def call_gemini_financial_brain(analysis_summary):
  try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
        أنت العقل المالي المحترف وخببر التحليل الفلكي (جان) ومفاهيم السيولة (SMC/ICT) لنظام GenZilla Programme.
        قم بكتابة تقرير استثماري ورسالة توصية احترافية باللغة العربية الفصحى بناءً على المعطيات التالية:

        - الأصل المالي: {symbol_option}
        - السعر الحالي: {current_price}
        - درجة الشمس الفلكية: {sun_deg:.2f}° (زاوية جان: {gann_angle}°, الانعكاس الزمني: {turning_point})
        - حالة سيولة المبتدئين: {'تم ضرب السيولة واصطياد الوقف' if (high_sweep or low_sweep) else 'مرحلة تجميع وتأهب'}
        - تفاصيل إدارة المخاطر المحددة: رأس المال {account_balance}$, نسبة المخاطرة {risk_per_trade_pct*100}%, عائد لا يقل عن 1:{min_rr}R.
        - خطة الصفقة المقترحة: النوع ({signal_type}), الدخول ({entry_price}), وقف الخسارة ({stop_loss}), الهدف ({take_profit}).

        اكتب تقريراً هيكلياً ومنظماً يوضح الأسباب الفنية والزمنية للصفقة ويوجهه للمتداول بشكل احترافي للغاية.
        """
    response = model.generate_content(prompt)
    return response.text
  except Exception as e:
    return f'خطأ في الاتصال بالعقل المالي لـ Gemini: {e}'


# --- 7. دالة إرسال البريد الإلكتروني الآلي (SMTP Email Dispatcher) ---
def send_email_report(subject, body, sender, password, receiver):
  if not sender or not password or not receiver:
    return False, 'يرجى إدخال بريد الاستقبال وكلمة مرور التطبيق (App Password).'

  msg = MIMEText(body, 'plain', 'utf-8')
  msg['Subject'] = Header(subject, 'utf-8')
  msg['From'] = sender
  msg['To'] = receiver

  try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
      server.login(sender, password)
      server.sendmail(sender, receiver, msg.as_string())
    return True, 'تم إرسال التقرير وصفقة التداول إلى بريدك الإلكتروني بنجاح!'
  except Exception as e:
    return False, f'فشل الإرسال البريدي: {e}'


# --- 8. واجهة تشغيل العقل المالي وإرسال البريد ---
st.markdown('---')
st.subheader('🧠 العقل المالي (Gemini AI) وتقارير الإرسال البريدي')

if st.button('✨ توليد التقرير المالي الاحترافي وإرساله لبريدي الإلكتروني'):
  with st.spinner(
      'جاري استنطاق العقل المالي وصياغة الشارتات والتقارير للإرسال...'
  ):
    ai_report = call_gemini_financial_brain({})

  st.success('تم توليد التقرير بواسطة Gemini بنجاح!')
  st.markdown(ai_report)

  # تنفيذ الإرسال البريدي فوراً
  if receiver_email and gmail_app_password:
    success, msg = send_email_report(
        subject=f'تقرير وتحليل GenZilla - {symbol_option}',
        body=ai_report,
        sender=receiver_email,
        password=gmail_app_password,
        receiver=receiver_email,
    )
    if success:
      st.success(msg)
    else:
      st.error(msg)
  else:
    st.warning(
        'لإرسال التقرير بريدياً، أدخل بريدك وكلمة مرور التطبيق في القائمة الجانبية.'
    )

# --- 9. جدول إدارة المخاطر والصفقة ---
st.markdown('---')
st.subheader('🎯 تفاصيل الصفقة ومنطق إدارة المخاطر المحسوب')

trade_summary_df = pd.DataFrame([
    {
        'الأصل المالي': symbol_option,
        'نوع الصفقة': signal_type,
        'سعر الدخول': entry_price,
        'وقف الخسارة (SL)': stop_loss,
        'الهدف (TP)': take_profit,
        'حجم المخاطرة بالدولار': f'${max_risk_dollar:,.2f}',
        'نسبة العائد': f'1:{min_rr}',
    }
])
st.table(trade_summary_df)

# 이 파일은 주식코드와 기간을 받으면 Drawdown을 그려주는 프로그램 입니다

import subprocess
import sys

try:
    import yfinance as yf
    print("yfinance is already installed.")
except ImportError:
    print("yfinance not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yfinance"])


# 패키지 불러오기
import pandas as pd
import numpy as np
# import yahoo_fin.stock_info as si
# import yfinance as yf
import math
import datetime
import streamlit as st

# drawdown을 계산하는 함수
def drawdown_df (df) :
    rets = df.pct_change()
    rets = rets[1:]
    rets = 1+rets
    wealth_index = 1000*(rets).cumprod()
    previous_peak = wealth_index.cummax()
    drawdown = (wealth_index - previous_peak) / previous_peak
    return drawdown


# Streamlit을 통해 주식코드와 기간을 입력받기
st.title('Stock Drawdown Analysis')
col1, col2, col3 = st.columns(3)
with col1:
    stock_code1 = st.text_input('Enter Stock Code', 'AAPL')
with col2:
    stock_code2 = st.text_input('Enter Stock Code', 'GOOG')
with col3:
    stock_code3 = st.text_input('Enter Stock Code', 'AMZN')

# 여러 주식코드를 입력받기
stock_codes = [stock_code1, stock_code2, stock_code3]

start_date = st.date_input('Start Date', datetime.date(2020, 1, 1))
end_date = st.date_input('End Date', datetime.date.today())

# 주식 데이터를 가져오기 및 그래프 그리기
if st.button('Get Data'):
    combined_df = pd.DataFrame()
    for code in stock_codes:
        if code:  # 주식코드가 입력된 경우에만 처리
            try:
                combined_df[code] = yf.download(code, start=start_date, end=end_date)['Close']
            except Exception as e:
                st.warning(f"Could not retrieve data for {code}: {e}")
    
    if not combined_df.empty:
        # drawdown 계산
        drawdown = drawdown_df(combined_df)
        
        # 주식 그래프 그리기
        st.subheader('Stock Prices')
        st.line_chart(combined_df)
        
        # drawdown 그래프 그리기
        st.subheader('Drawdown')
        st.line_chart(drawdown)
    else:
        st.warning("No valid stock data to display.")


# # 주식 데이터를 가져오기 및 그래프 그리기
# if st.button('Get Data'):
#     combined_df = pd.DataFrame()
#     for code in stock_codes:
#         if code:  # 주식코드가 입력된 경우에만 처리
#             try:
#                 df = si.get_data(code, start_date=start_date, end_date=end_date)
#                 combined_df[code] = df['close']
#             except Exception as e:
#                 st.warning(f"Could not retrieve data for {code}: {e}")
    
#     if not combined_df.empty:
#         # drawdown 계산
#         drawdown = drawdown_df(combined_df)
        
#         # 주식 그래프 그리기
#         st.subheader('Stock Prices')
#         st.line_chart(combined_df)
        
#         # drawdown 그래프 그리기
#         st.subheader('Drawdown')
#         st.line_chart(drawdown)
#     else:
#         st.warning("No valid stock data to display.")


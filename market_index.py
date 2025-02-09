'''
. 상품 : 금, WTI
. 글로벌 시장 : SP500, NASDAQ, VN, 인도, 일본, 브라질, 중국(항셍), 인도네시아, 멕시코
'''

import pandas as pd
import yfinance as yf
import datetime
import streamlit as st

stock_indicators = {
    'SP500': {'ticker': '^GSPC', 'currency': 'USD'},
    'NASDAQ': {'ticker': '^IXIC', 'currency': 'USD'},
    'India': {'ticker': '^BSESN', 'currency': 'INR'},
    'Japan': {'ticker': '^N225', 'currency': 'JPY'},
    'Brazil': {'ticker': '^BVSP', 'currency': 'BRL'},
    'China': {'ticker': '^HSI', 'currency': 'HKD'},
    'Indonesia': {'ticker': '^JKSE', 'currency': 'IDR'},
    'Mexico': {'ticker': '^MXX', 'currency': 'MXN'},
    'Korea': {'ticker': '^KS11', 'currency': 'KRW'},
    'Gold':{'ticker':'GC=F','currency': 'USD' },
    'WTI':{'ticker':'CL=F','currency': 'USD' }
}




# 여러 코드를 선택 받음
select_codes = st.multiselect(
    "Which market do you want to analyze?",
    list(stock_indicators.keys()),
    list(stock_indicators.keys())[0],
)

stock_codes = [stock_indicators[i]['ticker'] for i in select_codes]
currency_codes = [stock_indicators[i]['currency'] for i in select_codes]



# 여러 주식코드를 입력받기

start_date = st.date_input('Start Date', datetime.date(2020, 1, 1))
end_date = st.date_input('End Date', datetime.date.today())



def convert_currency(df, currency, start_date, end_date):
    if currency == 'USD':
        return df
    try:
        fx_rate = yf.download(f'{currency}=X', start=start_date, end=end_date)['Close']
        fx_rate.fillna(method='ffill', inplace=True)
        fx_rate.fillna(method='bfill', inplace=True)
        return df.div(fx_rate, axis=0)
    except Exception as e:
        st.warning(f"Could not retrieve FX rate for {currency}: {e}")
        return df

def drawdown_df (df) :
    rets = df.pct_change()
    rets = rets[1:]
    rets = 1+rets
    wealth_index = 1000*(rets).cumprod()
    previous_peak = wealth_index.cummax()
    drawdown = (wealth_index - previous_peak) / previous_peak
    return drawdown

# 주식 데이터를 가져오기 및 그래프 그리기
if st.button('Get Data'):
    stock_df = pd.DataFrame()
    country_codes = {code: stock_indicators[code] for code in select_codes}
    for country, info in country_codes.items():
        code = info['ticker']
        try:
            stock_df [country] = yf.download(code, start=start_date, end=end_date)['Close']
        except Exception as e:
            st.warning(f"Could not retrieve data for {code}: {e}")
    stock_df.fillna(method='ffill', inplace=True)  # 먼저 위의 유효한 값으로 채움
    stock_df.fillna(method='bfill', inplace=True)  # 그 다음 아래의 유효한 값으로 채움
    stock_df_normalized = (stock_df / stock_df.iloc[0] * 100).round(2)

    
    currency_df = pd.DataFrame()
    for code in currency_codes:
        if code:  # 주식코드가 입력된 경우에만 처리
            if code != 'USD':                
                try:
                    currency_df[code] = yf.download(f'{code}=X', start=start_date, end=end_date)['Close']
                except Exception as e:
                    st.warning(f"Could not retrieve data for {code}: {e}")
    currency_df.fillna(method='ffill', inplace=True)  # 먼저 위의 유효한 값으로 채움
    currency_df.fillna(method='bfill', inplace=True)  # 그 다음 아래의 유효한 값으로 채움



    # 각 국가의 지표 데이터를 USD로 환산
    usd_converted_df = pd.DataFrame()
    usd_converted_df_normalized = pd.DataFrame()
    country_codes = {code: stock_indicators[code] for code in select_codes}
    for country, info in country_codes.items():
        ticker = info['ticker']
        currency = info['currency']
        
        if currency == 'USD':
            usd_converted_df[country] = stock_df[country]
        else:
            usd_converted_df[country] = (stock_df[country] / currency_df[currency])
    usd_converted_df_normalized = (usd_converted_df / usd_converted_df.iloc[0] * 100).round(2)


    if not usd_converted_df.empty:

        # drawdown 계산
        drawdown = drawdown_df(usd_converted_df)
        
        # 주식 그래프 그리기
        st.subheader('Stock Prices')
        st.line_chart(stock_df_normalized)

        # USD 주식 그래프 그리기
        st.subheader('USD Covert Stock Prices')
        st.line_chart(usd_converted_df_normalized)
        
        # USD drawdown 그래프 그리기
        st.subheader('Drawdown')
        st.line_chart(drawdown)
    else:
        st.warning("No valid stock data to display.")

# 실행 방법 streamlit run app.py


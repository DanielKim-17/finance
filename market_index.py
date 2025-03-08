'''
. 상품 : 금, WTI
. 글로벌 시장 : SP500, NASDAQ, VN, 인도, 일본, 브라질, 중국(항셍), 인도네시아, 멕시코
'''

import pandas as pd
import yfinance as yf
import datetime
import streamlit as st

st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

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
# 데이터 주기를 선택
period = st.selectbox('Select Data Period', ['1d', '1wk', '1mo'])

if st.button('Get Data'):
    stock_df = pd.DataFrame()
    country_codes = {code: stock_indicators[code] for code in select_codes}
    for country, info in country_codes.items():
        code = info['ticker']
        try:
            stock_df[country] = yf.download(code, start=start_date, end=end_date, interval=period)['Close']
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
                    currency_df[code] = yf.download(f'{code}=X', start=start_date, end=end_date, interval=period)['Close']
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

    # drawdown 계산
    drawdown = drawdown_df(usd_converted_df)
    
    # 각 컬럼의 가장 낮은 값과 날짜 출력
    min_drawdown = drawdown.min().round(2) * 100
    min_drawdown_dates = drawdown.idxmin()
    latest_date = drawdown.index[-1]
    latest_drawdown = drawdown.loc[latest_date].round(2) * 100
    # 각 컬럼의 가장 낮은 값과 날짜 출력
    min_drawdown_data = {
        'Market': [],
        'Min': [],
        'Min Date': [],
        'Latest': [],
        'Latest Date': []
    }
    for col in drawdown.columns:
        min_drawdown_data['Market'].append(col)
        min_drawdown_data['Min'].append(min_drawdown[col])
        min_drawdown_data['Min Date'].append(min_drawdown_dates[col].date())
        min_drawdown_data['Latest'].append(latest_drawdown[col])
        min_drawdown_data['Latest Date'].append(latest_date.date())
    
    min_drawdown_df = pd.DataFrame(min_drawdown_data)

    if not usd_converted_df.empty:
        # 주식 그래프 그리기
        st.subheader('Stock Prices')
        st.line_chart(stock_df_normalized)

        # USD 주식 그래프 그리기
        st.subheader('USD Covert Stock Prices')
        st.line_chart(usd_converted_df_normalized)
        
        # USD drawdown 그래프 그리기
        st.subheader('Drawdown')
        st.line_chart(drawdown)

        # 데이터 프레임 그리기
        st.subheader('Minimum Drawdown by Market')
        st.table(min_drawdown_df)
    else:
        st.warning("No valid stock data to display.")

# 실행 방법 streamlit run app.py

# Set-ExecutionPolicy Unrestricted -Scope Process
# 
# Scripts\activate
# streamlit run market_index_v1.py
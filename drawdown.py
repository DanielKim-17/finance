# 패키지 불러오기
import pandas as pd
# import yahoo_fin.stock_info as si
import yfinance as yf
import datetime
import streamlit as st
import plotly.express as px

st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

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
with st.sidebar:
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

    start_date = st.date_input('Start Date', datetime.date(2024, 1, 1))
    end_date = st.date_input('End Date', datetime.date.today())
    Button_AZ = st.button('Get Data')

# if 'combined_df' not in st.session_state:
#     st.session_state.combined_df = None

combined_df = pd.DataFrame()
if Button_AZ:
    for code in stock_codes:
        if code:  # 주식코드가 입력된 경우에만 처리
            try:
                combined_df[code] = yf.download(code, start=start_date, end=end_date)['Close']
            except Exception as e:
                st.warning(f"Could not retrieve data for {code}: {e}")
    # st.session_state.combined_df = combined_df


# 주식 데이터를 가져오기 및 그래프 그리기


if not combined_df.empty:
    combined_df_normalized = (combined_df / combined_df.iloc[0] * 100).round(2)
else:
    combined_df_normalized = pd.DataFrame()

drawdown = drawdown_df(combined_df)



if not combined_df.empty:
    # drawdown 계산
    min_drawdown = drawdown.min().round(2) * 100
    min_drawdown_dates = drawdown.idxmin()
    latest_date = drawdown.index[-1]
    latest_drawdown = drawdown.loc[latest_date].round(2) * 100

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
    
    # 주식 그래프 그리기
    st.subheader('Stock Prices')
    fig = px.line(combined_df)
    fig.update_xaxes(rangeslider_visible=True)
    st.plotly_chart(fig)



    # st.line_chart(combined_df)
    
    st.subheader('Stock Prices Normalized')
    fig = px.line(combined_df_normalized)
    fig.update_xaxes(rangeslider_visible=True)
    st.plotly_chart(fig)


    # drawdown 그래프 그리기
    st.subheader('Drawdown')
    fig = px.line(drawdown)
    fig.update_xaxes(rangeslider_visible=True)
    st.plotly_chart(fig)    

    st.subheader('Minimum Drawdown by Market')
    st.dataframe(min_drawdown_data, hide_index = True)
    
else:
    st.warning("No valid stock data to display.")



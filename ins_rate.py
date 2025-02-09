'''
10년
. 한국 : IRLTLT01KRM156N
. 멕시코 : IRLTLT01MXM156N
. 일본 : IRLTLT01JPM156N
. 영국 : IRLTLT01GBM156N
. 독일 : IRLTLT01DEM156N

3개월
. 한국 : IR3TIB01KRM156N
. 멕시코 : IR3TIB01MXM156N
. 일본 : IR3TIB01JPM156N
. 영국 : IR3TIB01GBM156N
. 독일 : IR3TIB01DEM156N

Inflation
. 한국 : FPCPITOTLZGKOR
. 멕시코 : FPCPITOTLZGMEX
. 일본 : FPCPITOTLZGJPN
. 영국 : FPCPITOTLZGGBR
. 독일 : FPCPITOTLZGDEU
'''


import pandas as pd
from fredapi import Fred
import streamlit as st
import datetime

api_key=st.secrets["fred_api_key"]
fred = Fred(api_key=st.secrets["fred_api_key"])

ins_indicators = {
    'US_30' : 'DGS30',
    'US_10' : 'DGS10',
    'US_2' : 'DGS2',
    'US_10Y2Y' : 'T10Y2Y',
    'US_FED' : 'FEDFUNDS',
    'KOR_10Y' : 'IRLTLT01KRM156N',
    'JPN_10Y' : 'IRLTLT01JPM156N',
    'MEX_10Y' : 'IRLTLT01MXM156N',
    'GBR_10Y' : 'IRLTLT01GBM156N',
    'DEU_10Y' : 'IRLTLT01DEM156N',
    'US_3M' : 'IR3TIB01USM156N',
    'KOR_3M' : 'IR3TIB01KRM156N',
    'JPN_3M' : 'IR3TIB01JPM156N',
    'MEX_3M' : 'IR3TIB01MXM156N',
    'GBR_3M' : 'IR3TIB01GBM156N',
    'DEU_3M' : 'IR3TIB01DEM156N',
    'US_INFL_CORE' : 'CORESTICKM159SFRBATL',
    'US_INFL' : 'FPCPITOTLZGUSA',
    'KOR_INFL' : 'FPCPITOTLZGKOR',
    'JPN_INFL' : 'FPCPITOTLZGJPN',
    'MEX_INFL' : 'FPCPITOTLZGMEX',
    'GBR_INFL' : 'FPCPITOTLZGGBR',
    'DEU_INFL' : 'FPCPITOTLZGDEU'
}




# 여러 코드를 선택 받음
select_codes = st.multiselect(
    "Which market do you want to analyze?",
    list(ins_indicators.keys()),
    list(ins_indicators.keys())[0],
)

stock_codes = [ins_indicators[i] for i in select_codes]




# 여러 주식코드를 입력받기

start_date = st.date_input('Start Date', datetime.date(2020, 1, 1))
end_date = st.date_input('End Date', datetime.date.today())


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
    ins_codes = {code: ins_indicators[code] for code in select_codes}
    series_ids = list(ins_codes.values())
    data = {series_id: fred.get_series(series_id, observation_start=start_date, observation_end=end_date) for series_id in series_ids}
    stock_df = pd.DataFrame(data)
    stock_df.fillna(method='ffill', inplace=True)  # 먼저 위의 유효한 값으로 채움
    stock_df.fillna(method='bfill', inplace=True)  # 그 다음 아래의 유효한 값으로 채움
    
    # Rename the columns in the DataFrame
    column_mapping = {v: k for k, v in ins_codes.items()}
    stock_df.rename(columns=column_mapping, inplace=True)

    if not stock_df.empty:

        # drawdown 계산
        drawdown = drawdown_df(stock_df)
        
        # 주식 그래프 그리기
        st.subheader('Stock Prices')
        st.line_chart(stock_df)

        # # drawdown 계산
        # drawdown = drawdown_df(stock_df)

        # # USD drawdown 그래프 그리기
        # st.subheader('Drawdown')
        # st.line_chart(drawdown)
    else:
        st.warning("No valid stock data to display.")

# 실행 방법 streamlit run app.py
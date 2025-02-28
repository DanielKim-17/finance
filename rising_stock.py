# S&P500 지수를 불러와서 최근 1달동안 20%이상 상승한 종목 보기

import yfinance as yf
import pandas as pd
import streamlit as st
import datetime

st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

with st.sidebar:
    periods = st.selectbox('Select Data Period', ['1mo', '2mo', '3mo'])
    Button_SP = st.button('Get SP500 Data')
    Raisings = st.selectbox('Select Rasing Falling', ['Rasing', 'Falling'])
    Quantities = st.number_input('Input Quantity', value= 10)
    start_date = st.date_input('Start Date', datetime.date(2024, 1, 1))
    end_date = st.date_input('End Date', datetime.date.today())
    Button_AZ = st.button('Analysis')

# Initialize session state for change data
if 'change' not in st.session_state:
    st.session_state.change = None

if Button_SP:
    # Fetch the list of S&P 500 companies from Wikipedia
    # url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    # tables = pd.read_html(url)
    # sp500_tickers = tables[0]['Symbol'].tolist()
    sp500_tickers = ['MMM', 'AOS', 'ABT', 'ABBV', 'ACN', 'ADBE', 'AMD', 'AES', 'AFL', 'A', 'APD', 'ABNB', 'AKAM', 'ALB', 'ARE', 'ALGN', 'ALLE', 'LNT', 'ALL', 'GOOGL', 
                     'GOOG', 'MO', 'AMZN', 'AMCR', 'AEE', 'AEP', 'AXP', 'AIG', 'AMT', 'AWK', 'AMP', 'AME', 'AMGN', 'APH', 'ADI', 'ANSS', 'AON', 'APA', 'APO', 'AAPL', 
                     'AMAT', 'APTV', 'ACGL', 'ADM', 'ANET', 'AJG', 'AIZ', 'T', 'ATO', 'ADSK', 'ADP', 'AZO', 'AVB', 'AVY', 'AXON', 'BKR', 'BALL', 'BAC', 'BAX', 'BDX', 
                     'BBY', 'TECH', 'BIIB', 'BLK', 'BX', 'BK', 'BA', 'BKNG', 'BWA', 'BSX', 'BMY', 'AVGO', 'BR', 'BRO', 'BLDR', 'BG', 'BXP', 'CHRW', 'CDNS', 'CZR', 'CPT',
                     'CPB', 'COF', 'CAH', 'KMX', 'CCL', 'CARR', 'CAT', 'CBOE', 'CBRE', 'CDW', 'CE', 'COR', 'CNC', 'CNP', 'CF', 'CRL', 'SCHW', 'CHTR', 'CVX', 'CMG', 'CB', 
                     'CHD', 'CI', 'CINF', 'CTAS', 'CSCO', 'C', 'CFG', 'CLX', 'CME', 'CMS', 'KO', 'CTSH', 'CL', 'CMCSA', 'CAG', 'COP', 'ED', 'STZ', 'CEG', 'COO', 'CPRT', 
                     'GLW', 'CPAY', 'CTVA', 'CSGP', 'COST', 'CTRA', 'CRWD', 'CCI', 'CSX', 'CMI', 'CVS', 'DHR', 'DRI', 'DVA', 'DAY', 'DECK', 'DE', 'DELL', 'DAL', 'DVN', 
                     'DXCM', 'FANG', 'DLR', 'DFS', 'DG', 'DLTR', 'D', 'DPZ', 'DOV', 'DOW', 'DHI', 'DTE', 'DUK', 'DD', 'EMN', 'ETN', 'EBAY', 'ECL', 'EIX', 'EW', 'EA', 
                     'ELV', 'EMR', 'ENPH', 'ETR', 'EOG', 'EPAM', 'EQT', 'EFX', 'EQIX', 'EQR', 'ERIE', 'ESS', 'EL', 'EG', 'EVRG', 'ES', 'EXC', 'EXPE', 'EXPD', 'EXR', 
                     'XOM', 'FFIV', 'FDS', 'FICO', 'FAST', 'FRT', 'FDX', 'FIS', 'FITB', 'FSLR', 'FE', 'FI', 'FMC', 'F', 'FTNT', 'FTV', 'FOXA', 'FOX', 'BEN', 'FCX', 
                     'GRMN', 'IT', 'GE', 'GEHC', 'GEV', 'GEN', 'GNRC', 'GD', 'GIS', 'GM', 'GPC', 'GILD', 'GPN', 'GL', 'GDDY', 'GS', 'HAL', 'HIG', 'HAS', 'HCA', 'DOC', 
                     'HSIC', 'HSY', 'HES', 'HPE', 'HLT', 'HOLX', 'HD', 'HON', 'HRL', 'HST', 'HWM', 'HPQ', 'HUBB', 'HUM', 'HBAN', 'HII', 'IBM', 'IEX', 'IDXX', 'ITW', 
                     'INCY', 'IR', 'PODD', 'INTC', 'ICE', 'IFF', 'IP', 'IPG', 'INTU', 'ISRG', 'IVZ', 'INVH', 'IQV', 'IRM', 'JBHT', 'JBL', 'JKHY', 'J', 'JNJ', 'JCI', 
                     'JPM', 'JNPR', 'K', 'KVUE', 'KDP', 'KEY', 'KEYS', 'KMB', 'KIM', 'KMI', 'KKR', 'KLAC', 'KHC', 'KR', 'LHX', 'LH', 'LRCX', 'LW', 'LVS', 'LDOS', 'LEN', 
                     'LII', 'LLY', 'LIN', 'LYV', 'LKQ', 'LMT', 'L', 'LOW', 'LULU', 'LYB', 'MTB', 'MPC', 'MKTX', 'MAR', 'MMC', 'MLM', 'MAS', 'MA', 'MTCH', 'MKC', 'MCD', 
                     'MCK', 'MDT', 'MRK', 'META', 'MET', 'MTD', 'MGM', 'MCHP', 'MU', 'MSFT', 'MAA', 'MRNA', 'MHK', 'MOH', 'TAP', 'MDLZ', 'MPWR', 'MNST', 'MCO', 'MS', 
                     'MOS', 'MSI', 'MSCI', 'NDAQ', 'NTAP', 'NFLX', 'NEM', 'NWSA', 'NWS', 'NEE', 'NKE', 'NI', 'NDSN', 'NSC', 'NTRS', 'NOC', 'NCLH', 'NRG', 'NUE', 'NVDA', 
                     'NVR', 'NXPI', 'ORLY', 'OXY', 'ODFL', 'OMC', 'ON', 'OKE', 'ORCL', 'OTIS', 'PCAR', 'PKG', 'PLTR', 'PANW', 'PARA', 'PH', 'PAYX', 'PAYC', 'PYPL', 'PNR', 
                     'PEP', 'PFE', 'PCG', 'PM', 'PSX', 'PNW', 'PNC', 'POOL', 'PPG', 'PPL', 'PFG', 'PG', 'PGR', 'PLD', 'PRU', 'PEG', 'PTC', 'PSA', 'PHM', 'PWR', 'QCOM', 
                     'DGX', 'RL', 'RJF', 'RTX', 'O', 'REG', 'REGN', 'RF', 'RSG', 'RMD', 'RVTY', 'ROK', 'ROL', 'ROP', 'ROST', 'RCL', 'SPGI', 'CRM', 'SBAC', 'SLB', 'STX', 
                     'SRE', 'NOW', 'SHW', 'SPG', 'SWKS', 'SJM', 'SW', 'SNA', 'SOLV', 'SO', 'LUV', 'SWK', 'SBUX', 'STT', 'STLD', 'STE', 'SYK', 'SMCI', 'SYF', 'SNPS', 'SYY', 
                     'TMUS', 'TROW', 'TTWO', 'TPR', 'TRGP', 'TGT', 'TEL', 'TDY', 'TFX', 'TER', 'TSLA', 'TXN', 'TPL', 'TXT', 'TMO', 'TJX', 'TSCO', 'TT', 'TDG', 'TRV', 'TRMB',
                      'TFC', 'TYL', 'TSN', 'USB', 'UBER', 'UDR', 'ULTA', 'UNP', 'UAL', 'UPS', 'URI', 'UNH', 'UHS', 'VLO', 'VTR', 'VLTO', 'VRSN', 'VRSK', 'VZ', 'VRTX', 
                      'VTRS', 'VICI', 'V', 'VST', 'VMC', 'WRB', 'GWW', 'WAB', 'WBA', 'WMT', 'DIS', 'WBD', 'WM', 'WAT', 'WEC', 'WFC', 'WELL', 'WST', 'WDC', 'WY', 'WMB', 
                      'WTW', 'WDAY', 'WYNN', 'XEL', 'XYL', 'YUM', 'ZBRA', 'ZBH', 'ZTS']

    data = pd.DataFrame()

    # Download historical data for the S&P 500 tickers
    data = yf.download(sp500_tickers, period=periods)

    # Calculate the percentage change from the first day to the last day
    change = (data['Close'].iloc[-1] / data['Close'].iloc[0] - 1) * 100

    # Sort the tickers by the percentage change in descending order
    change = pd.DataFrame(change.sort_values(ascending=False), columns=['Pct_Change']).dropna()

    # Store the change data in session state
    st.session_state.change = change

    st.success('SP500 Data Retrieved Successfully!')

def drawdown_df(df):
    rets = df.pct_change()
    rets = rets[1:]
    rets = 1 + rets
    wealth_index = 1000 * (rets).cumprod()
    previous_peak = wealth_index.cummax()
    drawdown = (wealth_index - previous_peak) / previous_peak
    return drawdown

if Button_AZ:
    if st.session_state.change is not None:
        change = st.session_state.change
        if Raisings == 'Rasing':
            low_list = change.head(Quantities)
        else:
            low_list = change.tail(Quantities)

        # Create a DataFrame to store the results
        company_infos = pd.DataFrame(columns=['Ticker', 'DisplayName', 'Sector','Price', 'target', 'recommend' ,'MarketCap', 'Beta', 'EQGrowth', 'Wk52'])

        # Loop through each ticker in low_list
        for ticker in low_list.index:
            stock = yf.Ticker(ticker)

            # Get company info
            company_info = stock.info

            # Extract required details
            DisplayName = company_info.get('displayName', 'N/A')
            sector = company_info.get('sector', 'N/A')
            price = company_info.get('currentPrice', 'N/A')
            target = company_info.get('targetMedianPrice', 'N/A')
            recommend = company_info.get('recommendationMean', 'N/A')
            market_cap = company_info.get('marketCap', 'N/A')
            beta = company_info.get('beta', 'N/A')
            earnings_growth = company_info.get('earningsQuarterlyGrowth', 'N/A')
            fifty_two_week_range = company_info.get('fiftyTwoWeekRange', 'N/A')

            # Append the results to the DataFrame
            company_infos = pd.concat([company_infos, pd.DataFrame({
                'Ticker': [ticker],
                'DisplayName': [DisplayName],
                'Sector': [sector],
                'Price': [price],
                'target': [target],
                'recommend': [recommend],
                'MarketCap': [market_cap],
                'Beta': [beta],
                'EQGrowth': [earnings_growth],
                'Wk52': [fifty_two_week_range]
            })], ignore_index=True)

        company_infos['MarketCap'] = round(company_infos['MarketCap'].astype(float) / 1000000000, 1)

        combined_df = pd.DataFrame()
        for code in low_list.index:
            if code:  # 주식코드가 입력된 경우에만 처리
                try:
                    combined_df[code] = yf.download(code, start=start_date, end=end_date)['Close']
                except Exception as e:
                    st.warning(f"Could not retrieve data for {code}: {e}")

        combined_df.fillna(method='ffill', inplace=True)  # 먼저 위의 유효한 값으로 채움
        combined_df.fillna(method='bfill', inplace=True)  # 그 다음 아래의 유효한 값으로 채움
        combined_df = (combined_df / combined_df.iloc[0] * 100).round(2)
        combined_df_price = combined_df.iloc[-1].sort_values(ascending=False)
        # combined_df_price = combined_df_price.T

        # drawdown 계산
        drawdown = drawdown_df(combined_df)

        min_drawdown = drawdown.min().round(2) * 100
        min_drawdown_dates = drawdown.idxmin()
        latest_date = drawdown.index[-1]
        latest_drawdown = drawdown.loc[latest_date].round(2) * 100
        # 각 컬럼의 가장 낮은 값과 날짜 출력
        min_drawdown_data = {
            'Stock': [],
            'Min': [],
            'Min Date': [],
            'Latest': [],
            'Latest Date': []
        }

        for col in drawdown.columns:
            min_drawdown_data['Stock'].append(col)
            min_drawdown_data['Min'].append(min_drawdown[col])
            min_drawdown_data['Min Date'].append(min_drawdown_dates[col].date())
            min_drawdown_data['Latest'].append(latest_drawdown[col])
            min_drawdown_data['Latest Date'].append(latest_date.date())

        final_table = pd.merge(company_infos, pd.DataFrame(min_drawdown_data), left_on='Ticker', right_on='Stock').sort_values(by='Latest', ascending=True)
        final_table = final_table.drop(['Stock'], axis=1)
        final_table = pd.merge(final_table, combined_df_price.rename('Normalized_Price'), left_on='Ticker', right_index=True).sort_values(by='Latest', ascending=True)
        final_table = final_table.rename(columns={'Close': 'Normalized_Price'})
        # final_table['flag'] = False

        # final_table = st.data_editor(final_table)


        if not combined_df.empty:
            # company_infos 테이블 출력
            st.subheader('Minimum Drawdown by Market')
            # st.data_editor(final_table)
            st.dataframe(final_table)

            # 주식 그래프 그리기
            st.subheader('Stock Prices')
            st.line_chart(combined_df)

            # drawdown 그래프 그리기
            st.subheader('Drawdown')
            st.line_chart(drawdown)

    else:
        st.warning('Please click "Get SP500 Data" first to retrieve the data.')

# streamlit run rising_stock.py
import yfinance as yf
import pandas as pd
from fredapi import Fred
import streamlit as st

fred_api_key = '219825afab5febe7d60680ef6bf69689'

fred = Fred(api_key=fred_api_key)

series_ids = ['CORESTICKM159SFRBATL', 'FPCPITOTLZGUSA', 'DGS30', 'DGS10', 'DGS2', 'T10Y2Y', 'FEDFUNDS', 'DEXKOUS']
data = {series_id: fred.get_series(series_id, observation_start='2020-01-01') for series_id in series_ids}
fed = pd.DataFrame(data)

if st.button('Get Data'):
    st.subheader('Fed Rates')
    st.line_chart(fed)
import pandas as pd
import numpy as np
import yahoo_fin.stock_info as si
import math
import datetime

def read_price (Ticker, name, start_dates='1990-01-01', method='adjclose'):
    # open, high,low,close,adjclose,volume
    price = si.get_data(Ticker, start_date= start_dates, interval= '1mo').to_period('M')[method]
    rets = price.pct_change()
    rets = rets[1:]
    rets = pd.DataFrame(rets)
    rets.columns = [name]
    # rets = 1+rets
    return(rets)


def read_price_D (Ticker, name, start_dates='1990-01-01', method='adjclose'):
    # open, high,low,close,adjclose,volume
    price = si.get_data(Ticker, start_date= start_dates)[method]
    rets = price.pct_change()
    rets = rets[1:]
    rets = pd.DataFrame(rets)
    rets.columns = [name]
    # rets = 1+rets
    return(rets)


# 주식분석
def drawdown (series) :
    series = series + 1
    wealth_index = 1000*(series).cumprod()
    previous_peak = wealth_index.cummax()
    drawdown = (wealth_index - previous_peak) / previous_peak
    return pd.DataFrame({"Wealth": wealth_index, 
                         "Previous Peak": previous_peak, 
                         "Drawdown": drawdown})

def drawdown_df (df) :
    rets = df.pct_change()
    rets = rets[1:]
    rets = 1+rets
    wealth_index = 1000*(rets).cumprod()
    previous_peak = wealth_index.cummax()
    drawdown = (wealth_index - previous_peak) / previous_peak
    return drawdown

def drawdonfile (data, start_dates='2000-01-01', method='adjclose', option = 'drawdown' ):
    ticker = data.index
    n_steps = len(ticker)
    drawdowns = pd.DataFrame()
    wealth_indexs = pd.DataFrame()
    previous_peaks = pd.DataFrame()
    

    for step in range(n_steps):
        price = si.get_data(ticker[step], start_date= start_dates)[method]
        rets = price.pct_change()
        rets = rets[1:]
        rets = 1+rets
        wealth_index = 1000*(rets).cumprod()
        previous_peak = wealth_index.cummax()
        drawdown = (wealth_index - previous_peak) / previous_peak
        aa = data.Desc[step]
        drawdowns[aa] = drawdown
        wealth_indexs[aa] = wealth_index
        previous_peaks[aa] = previous_peak
        
    if option == 'wealth_index' :
        return wealth_indexs
    elif option == 'previous_peak':
        return previous_peaks
    else :
        return drawdowns
    



def findmin (data,fromyear,toyear):
    n_steps = len(data.columns)
    names = []
    lowdates = []
    lowvalues = []
    oneyearvalues = []
        
    for step in range(n_steps):
        try:
            name = data.columns[step]
            lowdate = data[name][fromyear:toyear].idxmin()
            lowvalue= data[name][lowdate]
            oneyearvalue = data[name][lowdate + datetime.timedelta(days=365)]
            names += [name]
            lowdates += [lowdate]
            lowvalues += [lowvalue]
            oneyearvalues += [oneyearvalue]
        except : pass

    result = pd.DataFrame(data=[lowdates,lowvalues,oneyearvalues], columns=[names], index=['lowdate','lowvalue','oneyearvalue']).T
    result['diff'] = result['oneyearvalue'] - result['lowvalue']
    return(result)

def quote (data,info='Market Cap'):
    n_steps = len(data)
    tickers = []
    values = []
        
    for step in range(n_steps):
        try:
            ticker = data[step]
            value = si.get_quote_table(ticker, dict_result=True)[info]
            tickers += [ticker]
            values += [value]
        except: pass

    result = pd.DataFrame(data=[tickers,values])
    return(result)

def eps (ticker, start_dates = '1990-01-01'):
    n_steps = len(ticker)
    eps1 = pd.DataFrame()
    
    for n in range(n_steps):
        tickers = ticker[n]
        epss = si.get_earnings_history(tickers)
        epss = pd.DataFrame(epss)
        eps1.append(epss)
        
    eps1 = eps1[['ticker', 'companyshortname','startdatetime', 'epsestimate','epsactual','epssurprisepct']]
    eps1 = eps1.dropna(axis=0)
    eps1['startdatetime'] = eps1['startdatetime'].str.slice(0,10)
    eps1['startdatetime'] = pd.to_datetime (eps1['startdatetime'])
    eps1.index = ['ticker','startdatetime']
    return eps1


def eps1 (ticker):
    n_steps = len(ticker)
    eps1 = pd.DataFrame()
    
    for n in range(n_steps):
        tickers = ticker[n]
        epss = si.get_earnings_history(tickers)
        epss2 = pd.DataFrame(epss)
        eps1.append(epss2)
        
    # eps1 = eps1['ticker', 'companyshortname','startdatetime', 'epsestimate','epsactual','epssurprisepct']
    # eps1 = eps1.dropna(axis=0)
    # eps1['startdatetime'] = eps1['startdatetime'].str.slice(0,10)
    # eps1['startdatetime'] = pd.to_datetime (eps1['startdatetime'])
    # eps1.index = ['ticker','startdatetime']
    return eps1

    





def pricechanges (data, start_dates='2000-01-01', method='adjclose' ):
    ticker = data.index
    n_steps = len(ticker)
    result = pd.DataFrame()
        
    for step in range(n_steps):
        price = si.get_data(ticker[step], start_date= start_dates)[method]
        rets = price.pct_change()
        rets = rets[1:]
        aa = data.Desc[step]
        result[aa] = rets
    
    return result



def lowperiod (drawdown) :
    drawdown = drawdown + 1
    lowest_date = drawdown['Drawdown'].idxmin()
    previous = drawdown[drawdown['Drawdown'].index < lowest_date]
    last = drawdown[drawdown['Drawdown'].index > lowest_date]
    start_date = previous[previous['Drawdown']==0][-1:].index.values
    end_date = last[last['Drawdown']==0][:1].index.values
    data = pd.DataFrame({'pickdate':lowest_date,
                         'start_date':start_date,
                          'end_date':end_date,
                          'value':drawdown['Drawdown'][lowest_date]
                         })
    return data







# SP500 분석



def updownc(drawdown, floor = -0.2) :
    catego = []
    start_dates = []
    end_dates = []
    start_values = []
    end_values = []
    
    new_period = drawdown
    lowvalue = drawdown['Drawdown'][drawdown['Drawdown'].idxmin()]


    while lowvalue < floor: # down
        category = 'down'
        peakdate = new_period['Drawdown'].idxmin()
        peakvalue = drawdown['Drawdown'][peakdate]
        previous = drawdown[drawdown['Drawdown'].index < peakdate]
        # start_date = previous['Drawdown'][previous['Drawdown']>floor][-1:].index[0]
        start_date = previous['Drawdown'][previous['Drawdown']>floor][-1:].index[0]
        start_date = drawdown.iloc[[np.searchsorted(drawdown.index,start_date + pd.offsets.BusinessDay(1))]].index[0]
        start_value = drawdown['Drawdown'][start_date]
        catego += [category]
        start_dates += [start_date]
        start_values += [start_value]
        end_dates += [peakdate]
        end_values += [peakvalue]

        # 상승시점
        category = 'up'
        last = drawdown[drawdown['Drawdown'].index > peakdate]
        start_date1 = drawdown.iloc[[np.searchsorted(drawdown.index,peakdate + pd.offsets.BusinessDay(1))]].index[0]
        start_value = drawdown['Drawdown'][start_date1]
        try:
            end_date1 = last['Drawdown'][last['Drawdown']>floor][:1].index[0]
            end_value = drawdown['Drawdown'][end_date1]
        except:
            end_date1 = '2099-12-31'
            end_value = '99999'
        # start_date2 = drawdown.iloc[[np.searchsorted(drawdown.index,end_date + pd.offsets.BusinessDay(1))]].index[0]
        catego += [category]
        start_dates += [start_date1]
        start_values += [start_value]
        end_dates += [end_date1]
        end_values += [end_value]
        
        
        remove_index1 = drawdown [(drawdown.index >= start_date) & (drawdown.index <= end_date1)].index
        remove_index = new_period.index.isin(remove_index1)
        new_period = new_period[~remove_index]
        peakdate = new_period['Drawdown'].idxmin()


        try:
            lowvalue = drawdown['Drawdown'][peakdate]
        except:
            pass
    
    
    try:
        return pd.DataFrame({'category' : catego,
                            'start_date': start_dates,
                            'end_date': end_dates,
                            'start_value':start_values,
                            'end_value':end_values})
    
    except:
        pass




def updownb_o(drawdown, floor=-0.2) :
    catego = []
    peakdates = []
    start_dates = []
    end_dates = []
    peak_values = []
    start_values = []
    end_values = []
    
    new_period = drawdown

    i = 0
    lowvalue = drawdown['Drawdown'][drawdown['Drawdown'].idxmin()]


    while lowvalue < floor: # down
        category = 'down'
        peakdate = new_period['Drawdown'].idxmin()
        peakvalue = drawdown['Drawdown'][peakdate]
        previous = drawdown[drawdown['Drawdown'].index < peakdate]
        # start_date = previous['Drawdown'][previous['Drawdown']>floor][-1:].index[0]
        start_date = previous['Drawdown'][previous['Drawdown']>floor][-1:].index[0]
        start_date = drawdown.iloc[[np.searchsorted(drawdown.index,start_date + pd.offsets.BusinessDay(1))]].index[0]
        start_value = drawdown['Drawdown'][start_date]
        last = drawdown[drawdown['Drawdown'].index > peakdate]
        try:
            end_date = last['Drawdown'][last['Drawdown']>floor][:1].index[0]
            end_value = drawdown['Drawdown'][end_date]
        except:
            end_date = '2099-12-31'
            end_value = '99999'
        # start_date2 = drawdown.iloc[[np.searchsorted(drawdown.index,end_date + pd.offsets.BusinessDay(1))]].index[0]
        remove_index1 = drawdown [(drawdown.index >= start_date) & (drawdown.index <= end_date)].index
        remove_index = new_period.index.isin(remove_index1)
        new_period = new_period[~remove_index]

        catego += [category]
        peakdates += [peakdate]
        start_dates += [start_date]
        end_dates += [end_date]
        peak_values += [peakvalue]
        start_values += [start_value]
        end_values += [end_value]

        try:
            lowvalue = drawdown['Drawdown'][peakdate]
        except:
            pass


    try:
        return pd.DataFrame({'category' : catego,
                             'peak_date' : peakdates,
                            'start_date': start_dates,
                            'end_date': end_dates,
                            'peak_value':peak_values,
                            'start_value':start_values,
                            'end_value':end_values})
    
    except:
        pass


# 기본 CPPI
def run_cppi(risky_r, safe_r=None, m=3, start=1000, floor=0.8, riskfree_rate=0.00, bp=-1):
    """
    Run a backtest of the CPPI strategy, given a set of returns for the risky asset
    Returns a dictionary containing: Asset Value History, Risk Budget History, Risky Weight History
    """
    # set up the CPPI parameters
    dates = risky_r.index
    n_steps = len(dates)
    account_value = start
    floor_value = start*floor
    # floor_value = account_value*floor
    peak = account_value
    if isinstance(risky_r, pd.Series): 
        risky_r = pd.DataFrame(risky_r, columns=["R"])
    
    # drawdown = drawdown(risky_r)
    wealth_index = 1000*(1+risky_r).cumprod()
    previous_peak = wealth_index.cummax()
    drawdown = (wealth_index - previous_peak) / previous_peak
    
    
    if safe_r is None:
        safe_r = pd.DataFrame().reindex_like(risky_r)
        safe_r.values[:] = riskfree_rate/245 # fast way to set all values to a number
    # set up some DataFrames for saving intermediate values
    account_history = pd.DataFrame().reindex_like(risky_r)
    risky_w_history = pd.DataFrame().reindex_like(risky_r)
    cushion_history = pd.DataFrame().reindex_like(risky_r)
    floorval_history = pd.DataFrame().reindex_like(risky_r)
    peak_history = pd.DataFrame().reindex_like(risky_r)
    cal = pd.DataFrame().reindex_like(risky_r)
    

    for step in range(n_steps):
        aa = float(wealth_index.iloc[step].values[0])
        # bb = float(previous_peak.iloc[step].values[0] * bp)
        peak = np.maximum(peak, account_value)
        floor_value = peak*floor
        cc = drawdown.iloc[step].values[0] - bp
        # if drawdown.iloc[step].values[0] < bp :
        #     risky_w = 1
        #     cushion = (account_value - floor_value)/account_value
        # else :
        #     cushion = (account_value - floor_value)/account_value
        #     risky_w = m*cushion
        #     risky_w = np.minimum(risky_w, 1)
        #     risky_w = np.maximum(risky_w, 0)
        
        cushion = (aa- floor_value)/aa
        risky_w = m*cushion
        risky_w = np.minimum(risky_w, 1)
        risky_w = np.maximum(risky_w, 0)
        safe_w = 1-risky_w        
        risky_alloc = account_value*risky_w
        safe_alloc = account_value*safe_w
        # recompute the new account value at the end of this step
        account_value = risky_alloc*(1+risky_r.iloc[step]) + safe_alloc*(1+safe_r.iloc[step])
        # save the histories for analysis and plotting
        cushion_history.iloc[step] = cushion
        risky_w_history.iloc[step] = risky_w
        account_history.iloc[step] = account_value
        floorval_history.iloc[step] = floor_value
        peak_history.iloc[step] = peak
        cal.iloc[step] = cc
    risky_wealth = start*(1+risky_r).cumprod()
    backtest_result = {
        "Wealth": account_history,
        "Risky Wealth": risky_wealth, 
        "Risk Budget": cushion_history,
        "Risky Allocation": risky_w_history,
        "drawdown": drawdown,
        "peak": peak_history,
        "floor": floorval_history,
        "Wealth_index":wealth_index,
        "previous_peak":previous_peak,
        "drawdown":drawdown,
        "cal":cal
    }
    return backtest_result



## 채권 cppi 계산


def period_max (data, period=500):
    n_steps = len(data.index)
    FEDFUND = data[['FEDFUNDS']] 
    pmax = pd.DataFrame().reindex_like(FEDFUND)
    pmin = pd.DataFrame().reindex_like(FEDFUND)
    drawdown = pd.DataFrame().reindex_like(FEDFUND)
    drawup = pd.DataFrame().reindex_like(FEDFUND)
    ndays = pd.DataFrame().reindex_like(FEDFUND)
    pdrawdown = pd.DataFrame().reindex_like(FEDFUND)
    nday = int(0)
        
    for n in range (period, n_steps):
        #tostep = n+period
        peak = FEDFUND.iloc[n-period:n+1].max()
        lows = FEDFUND.iloc[n-period:n+1].min()
        pmax.iloc[n] = peak
        pmin.iloc[n] = lows
        # ad = abs(pmin.iloc[n] - pmin.iloc[n-1])
        ad = abs(FEDFUND.iloc[n] - FEDFUND.iloc[n-1])
        if float(ad) < 0.1:
            nday = nday + 1
        else:
            nday = int(0)
        ndays.iloc[n] = nday
        drawdown.iloc[n] = (FEDFUND.iloc[n] - peak) / peak
        drawup.iloc[n] = (lows - FEDFUND.iloc[n]) / FEDFUND.iloc[n]
    
    b1 = data[['DGS30']].rolling(window=period).max()
    pdrawdown = (data[['DGS30']] - b1)/b1
    minten = pdrawdown.rolling(window=1000).aggregate(np.percentile, 10)                                                     
    aa = pd.concat([pmax, pmin, drawdown, drawup, ndays, pdrawdown, minten ], axis=1)
    aa.columns = ['pmax','pmin','drawdown', 'drawup', 'ndays', 'pdrawdown', 'minten']
    
    return aa




def invest_bond(bond) :
    
    """
    채권용 cppi
    """
    # set up the CPPI parameters
    # bond = bond.dropna(axis=0)
    bond = bond.dropna(axis=0)
    dates = bond.index
    n_steps = len(dates)
    
    
    dates = []
    status = []
    prices = []
    T10Y2Y = []
    pdrawdowns = []
    stat = 'Sell'
    buydate = bond.index[0]
    selldate = bond.index[0]

    for step in range(n_steps):
        # T10Y2Y가 마이너스
        # 30년 채권이 FEDRATE와 만나는 시점 
        if stat == 'Sell':        
            if bond[['T10Y2Y']].iloc[step].values[0] < 0.25 :
                if bond[['D30MFED']].iloc[step].values[0] < 10 :
                    if bond[['pdrawdown']].iloc[step].values[0] > -.05 :
                        if bond.index[step] != selldate:
                            stat = 'Buy'
                            buydate = bond.index[step]
                            price = bond[['price']].iloc[step].values[0]
                            tentwo = bond[['T10Y2Y']].iloc[step].values[0]
                            treefed = bond[['pdrawdown']].iloc[step].values[0]
                            dates += [buydate]
                            prices += [price]
                            status += [stat]
                            T10Y2Y += [tentwo]
                            pdrawdowns += [treefed]
                
        if stat == 'Buy' and bond[['pdrawdown']].iloc[step].values[0] < bond[['minten']].iloc[step].values[0] and bond[['ndays']].iloc[step].values[0] >= 120 and bond[['T10Y2Y']].iloc[step].values[0] > 0 :
                                            
            stat = 'Sell'
            selldate = bond.index[step]
            price = bond[['price']].iloc[step].values[0]
            tentwo = bond[['T10Y2Y']].iloc[step].values[0]
            treefed = bond[['pdrawdown']].iloc[step].values[0]
            dates += [selldate]
            prices += [price]
            status += [stat]
            T10Y2Y += [tentwo]
            pdrawdowns += [treefed]
            
        if stat == 'Buy' and bond[['pdrawdown']].iloc[step].values[0] < -.40 :
            stat = 'Sell'
            selldate = bond.index[step]
            price = bond[['price']].iloc[step].values[0]
            tentwo = bond[['T10Y2Y']].iloc[step].values[0]
            treefed = bond[['pdrawdown']].iloc[step].values[0]
            dates += [selldate]
            prices += [price]
            status += [stat]
            T10Y2Y += [tentwo]
            pdrawdowns += [treefed]
        
    
    try:
        return pd.DataFrame({'DATE':dates,
                             'status': status,
                            'prices': prices,
                            'T10Y2Y': T10Y2Y,
                            'pdrawdowns':pdrawdowns})
    
    except:
        pass


# 신규추가



''' 
loc[step].values[0]
                treefed = bond[['D30MFED']].iloc[step].values[0]
        if stat == 'Buy':
            
        
        

    while lowvalue < floor: # down
        category = 'down'
        peakdate = new_period['Drawdown'].idxmin()
        peakvalue = drawdown['Drawdown'][peakdate]
        previous = drawdown[drawdown['Drawdown'].index < peakdate]
        # start_date = previous['Drawdown'][previous['Drawdown']>floor][-1:].index[0]
        start_date = previous['Drawdown'][previous['Drawdown']>floor][-1:].index[0]
        start_date = drawdown.iloc[[np.searchsorted(drawdown.index,start_date + pd.offsets.BusinessDay(1))]].index[0]
        start_value = drawdown['Drawdown'][start_date]
        catego += [category]
        start_dates += [start_date]
        start_values += [start_value]
        end_dates += [peakdate]
        end_values += [peakvalue]

        # 상승시점
        category = 'up'
        last = drawdown[drawdown['Drawdown'].index > peakdate]
        start_date1 = drawdown.iloc[[np.searchsorted(drawdown.index,peakdate + pd.offsets.BusinessDay(1))]].index[0]
        start_value = drawdown['Drawdown'][start_date1]
        try:
            end_date1 = last['Drawdown'][last['Drawdown']>floor][:1].index[0]
            end_value = drawdown['Drawdown'][end_date1]
        except:
            end_date1 = '2099-12-31'
            end_value = '99999'
        # start_date2 = drawdown.iloc[[np.searchsorted(drawdown.index,end_date + pd.offsets.BusinessDay(1))]].index[0]
        catego += [category]
        start_dates += [start_date1]
        start_values += [start_value]
        end_dates += [end_date1]
        end_values += [end_value]
        
        
        remove_index1 = drawdown [(drawdown.index >= start_date) & (drawdown.index <= end_date1)].index
        remove_index = new_period.index.isin(remove_index1)
        new_period = new_period[~remove_index]
        peakdate = new_period['Drawdown'].idxmin()


        try:
            lowvalue = drawdown['Drawdown'][peakdate]
        except:
            pass
    
    
    try:
        return pd.DataFrame({'category' : catego,
                            'start_date': start_dates,
                            'end_date': end_dates,
                            'start_value':start_values,
                            'end_value':end_values})
    
    except:
        pass





def cppi_bond(bond, safe_r=None, m=3, start=1000, floor=0.8, riskfree_rate=0.00, bp=-1):
    """
    채권용 cppi
    """
    # set up the CPPI parameters
    # bond = bond.dropna(axis=0)
    dates = bond.index
    n_steps = len(dates)
    account_value = start
    floor_value = start*floor
    ab = bond[['price']]
    account_history = pd.DataFrame().reindex_like(ab)
    risky_w_history = pd.DataFrame().reindex_like(ab)
    cushion_history = pd.DataFrame().reindex_like(ab)
    floorval_history = pd.DataFrame().reindex_like(ab)
    peak_history = pd.DataFrame().reindex_like(ab)
    cal = pd.DataFrame()
    
    status = []
    peakdates = []
    start_dates = []
    end_dates = []
    peak_values = []
    start_values = []
    end_values = []
    
    
    # floor_value = account_value*floor
    
    for step in range(n_steps):
        # T10Y2Y가 마이너스
        # 30년 채권이 FEDRATE와 만나는 시점 
        if [bond[['T10Y2Y']].iloc[step].values[0] < 0] & [bond[['D30MFED']].iloc[step].values[0] <0]:
            status = 'Buy'
            account_value = risky_alloc*(1+bond[['T10Y2Y']].iloc[step])
            
        
        aa = float(wealth_index.iloc[step].values[0])
        # bb = float(previous_peak.iloc[step].values[0] * bp)
        peak = np.maximum(peak, account_value)
        floor_value = peak*floor
        cc = drawdown.iloc[step].values[0] - bp

        
        cushion = (aa- floor_value)/aa
        risky_w = m*cushion
        risky_w = np.minimum(risky_w, 1)
        risky_w = np.maximum(risky_w, 0)
        safe_w = 1-risky_w        
        risky_alloc = account_value*risky_w
        safe_alloc = account_value*safe_w
        # recompute the new account value at the end of this step
        account_value = risky_alloc*(1+risky_r.iloc[step]) + safe_alloc*(1+safe_r.iloc[step])
        # save the histories for analysis and plotting
        cushion_history.iloc[step] = cushion
        risky_w_history.iloc[step] = risky_w
        account_history.iloc[step] = account_value
        floorval_history.iloc[step] = floor_value
        peak_history.iloc[step] = peak
        cal.iloc[step] = cc
    
    risky_wealth = start*(1+risky_r).cumprod()
    
    
    
    if safe_r is None:
        safe_r = pd.DataFrame().reindex_like(risky_r)
        safe_r.values[:] = riskfree_rate/245 # fast way to set all values to a number
    # set up some DataFrames for saving intermediate values
    account_history = pd.DataFrame().reindex_like(risky_r)
    risky_w_history = pd.DataFrame().reindex_like(risky_r)
    cushion_history = pd.DataFrame().reindex_like(risky_r)
    floorval_history = pd.DataFrame().reindex_like(risky_r)
    peak_history = pd.DataFrame().reindex_like(risky_r)
    cal = pd.DataFrame().reindex_like(risky_r)
    

    for step in range(n_steps):
        aa = float(wealth_index.iloc[step].values[0])
        # bb = float(previous_peak.iloc[step].values[0] * bp)
        peak = np.maximum(peak, account_value)
        floor_value = peak*floor
        cc = drawdown.iloc[step].values[0] - bp
        # if drawdown.iloc[step].values[0] < bp :
        #     risky_w = 1
        #     cushion = (account_value - floor_value)/account_value
        # else :
        #     cushion = (account_value - floor_value)/account_value
        #     risky_w = m*cushion
        #     risky_w = np.minimum(risky_w, 1)
        #     risky_w = np.maximum(risky_w, 0)
        
        cushion = (aa- floor_value)/aa
        risky_w = m*cushion
        risky_w = np.minimum(risky_w, 1)
        risky_w = np.maximum(risky_w, 0)
        safe_w = 1-risky_w        
        risky_alloc = account_value*risky_w
        safe_alloc = account_value*safe_w
        # recompute the new account value at the end of this step
        account_value = risky_alloc*(1+risky_r.iloc[step]) + safe_alloc*(1+safe_r.iloc[step])
        # save the histories for analysis and plotting
        cushion_history.iloc[step] = cushion
        risky_w_history.iloc[step] = risky_w
        account_history.iloc[step] = account_value
        floorval_history.iloc[step] = floor_value
        peak_history.iloc[step] = peak
        cal.iloc[step] = cc
    risky_wealth = start*(1+risky_r).cumprod()
    backtest_result = {
        "Wealth": account_history,
        "Risky Wealth": risky_wealth, 
        "Risk Budget": cushion_history,
        "Risky Allocation": risky_w_history,
        "drawdown": drawdown,
        "peak": peak_history,
        "floor": floorval_history,
        "Wealth_index":wealth_index,
        "previous_peak":previous_peak,
        "drawdown":drawdown,
        "cal":cal
    }
    return backtest_result

'''

# 수수료, 세금 계산
def cppi_tax(risky_r, safe_r=None, m=3, start=1000, floor=0.8, riskfree_rate=0.00, taxrate = 0.005, taxrate2 = .22):
    """
    Run a backtest of the CPPI strategy, given a set of returns for the risky asset
    Returns a dictionary containing: Asset Value History, Risk Budget History, Risky Weight History
    """
    # set up the CPPI parameters
    dates = risky_r.index
    n_steps = len(dates)
    account_value = start
    floor_value = start*floor
    # floor_value = account_value*floor
    peak = account_value
    if isinstance(risky_r, pd.Series): 
        risky_r = pd.DataFrame(risky_r, columns=["R"])
    
    # drawdown = drawdown(risky_r)
    wealth_index = 1000*(1+risky_r).cumprod()
    previous_peak = wealth_index.cummax()
    drawdown = (wealth_index - previous_peak) / previous_peak
    
    
    if safe_r is None:
        safe_r = pd.DataFrame().reindex_like(risky_r)
        safe_r.values[:] = riskfree_rate/245 # fast way to set all values to a number
    # set up some DataFrames for saving intermediate values
    account_history = pd.DataFrame().reindex_like(risky_r)
    risky_w_history = pd.DataFrame().reindex_like(risky_r)
    cushion_history = pd.DataFrame().reindex_like(risky_r)
    floorval_history = pd.DataFrame().reindex_like(risky_r)
    peak_history = pd.DataFrame().reindex_like(risky_r)
    risk_alloc_history = pd.DataFrame().reindex_like(risky_r)
    taxcost_history = pd.DataFrame().reindex_like(risky_r)
    

    for step in range(n_steps):
        wealth_value = float(wealth_index.iloc[step].values[0])
        peak = np.maximum(peak, account_value)
        floor_value = peak*floor
        
        cushion = (wealth_value- floor_value)/wealth_value
        risky_w = m*cushion
        risky_w = np.minimum(risky_w, 1)
        risky_w = np.maximum(risky_w, 0)
        
        # tax 차이계산
        # tax1은 거래세이므로 판매할때만 냄, 이는 risky_w의 비중변화로 반단함
        if step > 0:
            diffweight = abs(risky_w - (1-safe_w))
        else:
            diffweight = 0
        
        safe_w = 1-risky_w        
        risky_alloc = account_value*risky_w
        safe_alloc = account_value*safe_w

        # recompute the new account value at the end of this step
        
        # tax계산
        tax1 = round(risky_alloc * diffweight * taxrate,2)
        
        
        # tax2는 account_value가 증가했을때만 세금을 냄
        # 년 단위로 tax 금액을 계산해 줘야함
        # start_date = drawdown.iloc[[np.searchsorted(drawdown.index,start_date + pd.offsets.BusinessDay(1))]].index[0]
        
        bstep = step - 1
        if bstep >= 0:
            tbase = float(risky_alloc - risk_alloc_history.iloc[bstep])
            if tbase > 0:
                tax2 = round(tbase * taxrate2,2) 
            else:
                tax2 = 0
        else:
            tax2 = 0
        
        taxcost = tax1
        

        # taxcost를 비용에 추가
        account_value = risky_alloc*(1+risky_r.iloc[step]) + safe_alloc*(1+safe_r.iloc[step]) - taxcost

        
        
        # save the histories for analysis and plotting
        cushion_history.iloc[step] = cushion
        risky_w_history.iloc[step] = risky_w
        account_history.iloc[step] = account_value
        floorval_history.iloc[step] = floor_value
        peak_history.iloc[step] = peak
        risk_alloc_history.iloc[step] = risky_alloc
        taxcost_history.iloc[step] = taxcost
    risky_wealth = start*(1+risky_r).cumprod()
    backtest_result = {
        "Wealth": account_history,
        "Risky Wealth": risky_wealth, 
        "Risk Budget": cushion_history,
        "Risky Allocation": risky_w_history,
        "drawdown": drawdown,
        "peak": peak_history,
        "floor": floorval_history,
        "Wealth_index":wealth_index,
        "previous_peak":previous_peak,
        "drawdown":drawdown,
        "risk_alloc":risk_alloc_history,
        "taxcost":taxcost_history
    }
    return backtest_result




# 쿠션조정
def cppi_cushion(risky_r, safe_r=None, m=3, start=1000, floor=0.8, riskfree_rate=0.00, taxrate = 0.005, taxrate2 = .22):
    """
    Run a backtest of the CPPI strategy, given a set of returns for the risky asset
    Returns a dictionary containing: Asset Value History, Risk Budget History, Risky Weight History
    """
    # set up the CPPI parameters
    dates = risky_r.index
    n_steps = len(dates)
    account_value = start
    floor_value = start*floor
    # floor_value = account_value*floor
    peak = account_value
    if isinstance(risky_r, pd.Series): 
        risky_r = pd.DataFrame(risky_r, columns=["R"])
    
    # drawdown = drawdown(risky_r)
    wealth_index = 1000*(1+risky_r).cumprod()
    previous_peak = wealth_index.cummax()
    drawdown = (wealth_index - previous_peak) / previous_peak
    
    
    if safe_r is None:
        safe_r = pd.DataFrame().reindex_like(risky_r)
        safe_r.values[:] = riskfree_rate/245 # fast way to set all values to a number
    # set up some DataFrames for saving intermediate values
    account_history = pd.DataFrame().reindex_like(risky_r)
    risky_w_history = pd.DataFrame().reindex_like(risky_r)
    cushion_history = pd.DataFrame().reindex_like(risky_r)
    floorval_history = pd.DataFrame().reindex_like(risky_r)
    peak_history = pd.DataFrame().reindex_like(risky_r)
    risk_alloc_history = pd.DataFrame().reindex_like(risky_r)
    taxcost_history = pd.DataFrame().reindex_like(risky_r)
    
    
    for step in range(n_steps):
        wealth_value = float(wealth_index.iloc[step].values[0])
        peak = np.maximum(peak, account_value)
        floor_value = peak*floor
        
        cushion = np.ceil((wealth_value- floor_value)/wealth_value*10)/10
        
        
        risky_w = m*cushion
        risky_w = np.minimum(risky_w, 1)
        risky_w = np.maximum(risky_w, 0)
        
        # tax 차이계산
        # tax1은 거래세이므로 판매할때만 냄, 이는 risky_w의 비중변화로 반단함
        if step > 0:
            diffweight = abs(risky_w - (1-safe_w))
        else:
            diffweight = 0
        
        safe_w = 1-risky_w        
        risky_alloc = account_value*risky_w
        safe_alloc = account_value*safe_w

        # recompute the new account value at the end of this step
        
        # tax계산
        tax1 = round(risky_alloc * diffweight * taxrate,2)
        
        
        # tax2는 account_value가 증가했을때만 세금을 냄
        # 년 단위로 tax 금액을 계산해 줘야함
        # start_date = drawdown.iloc[[np.searchsorted(drawdown.index,start_date + pd.offsets.BusinessDay(1))]].index[0]
        
        bstep = step - 1
        if bstep >= 0:
            tbase = float(risky_alloc - risk_alloc_history.iloc[bstep])
            if tbase > 0:
                tax2 = round(tbase * taxrate2,2) 
            else:
                tax2 = 0
        else:
            tax2 = 0
        
        taxcost = tax1
        

        # taxcost를 비용에 추가
        account_value = risky_alloc*(1+risky_r.iloc[step]) + safe_alloc*(1+safe_r.iloc[step]) - taxcost

        
        
        # save the histories for analysis and plotting
        cushion_history.iloc[step] = cushion
        risky_w_history.iloc[step] = risky_w
        account_history.iloc[step] = account_value
        floorval_history.iloc[step] = floor_value
        peak_history.iloc[step] = peak
        risk_alloc_history.iloc[step] = risky_alloc
        taxcost_history.iloc[step] = taxcost
    risky_wealth = start*(1+risky_r).cumprod()
    backtest_result = {
        "Wealth": account_history,
        "Risky Wealth": risky_wealth, 
        "Risk Budget": cushion_history,
        "Risky Allocation": risky_w_history,
        "drawdown": drawdown,
        "peak": peak_history,
        "floor": floorval_history,
        "Wealth_index":wealth_index,
        "previous_peak":previous_peak,
        "drawdown":drawdown,
        "risk_alloc":risk_alloc_history,
        "taxcost":taxcost_history
    }
    return backtest_result



# 아래는 연습임.
'''




def updownt(drawdown, floor=-0.2) :
    # updowns = pd.DataFrame(columns=['category',
    #                                 'start_date','end_date',
    #                                 'start_value','end_value'])
    # updowns = pd.DataFrame()
    catego = []
    end_dates = []
    end_values = []
    start_values = []
    start_dates = []
    drawdown1 = drawdown

    i = 0
    lowvalue = drawdown['Drawdown'][drawdown['Drawdown'].idxmin()]


    while lowvalue < floor: # down
        category = 'down'
        end_date = drawdown['Drawdown'].idxmin()
        end_value = drawdown['Drawdown'][end_date]
        previous = drawdown[drawdown['Drawdown'].index < end_date]
        start_value = previous['Drawdown'][previous['Drawdown']>floor][-1:]
        start_date = start_value.index[0]
        start_value = start_value[0]
        catego += [category]
        end_dates += [end_date]
        end_values += [end_value]
        start_values += [start_value]
        start_dates += [start_date]
        
        category2 = 'up'
        start_date2 = end_date + pd.offsets.BusinessDay(1)
        try:
            start_value2 = drawdown['Drawdown'][start_date2]
        except:
            pass
        last = drawdown[drawdown['Drawdown'].index >= start_date2]
        end_value2 = last['Drawdown'][last['Drawdown']==0][:1]
        try:
            end_date2 = end_value2.index[0]
            end_value2 = end_value2[0]
        except:
            end_value2 = 0
            end_date2 = '2099-12-31'
            start_value2 = int(99999)
            pass    
        catego += [category2]
        end_dates += [end_date2]
        end_values += [end_value2]
        start_values += [start_value2]
        start_dates += [start_date2]
        
        remove_index = drawdown[(drawdown.index >= start_date) & (drawdown.index <= end_date2)].index
        drawdown = drawdown[(drawdown.index < start_date) | (drawdown.index > end_date2)]
        # drawdown = drawdown[(drawdown.index < start_date)]
        try:
            lowvalue = drawdown['Drawdown'][drawdown['Drawdown'].idxmin()]
        except:
            pass

    try:
        return pd.DataFrame({'category' : catego,
                            'start_date':start_dates,
                            'start_value':start_values,
                            'end_date': end_dates,
                            'end_value':end_values})
    
    except:
        pass

    
    # return [catego,end_dates,end_values,start_values,start_dates]





        # if lowvalue > floor:
        #     break
        
        # updowns.iloc[i] = [category,start_date,end_date,start_value,end_value]
        # category = 'down'
        # end_date = drawdown['Drawdown'].idxmin()
        # end_value = drawdown['Drawdown'][end_date]
        # previous = drawdown[drawdown['Drawdown'].index < end_date]
        # start_value = previous['Drawdown'][previous['Drawdown']>floor][-1:]
        # start_date = start_value.index.values
        # updowns.iloc[i] = [category,start_date,end_date,start_value,end_value]
        # i = i+1
        # category2 = 'up'
        # start_date2 = end_date + pd.offsets.BusinessDay(1)
        # start_value2 = drawdown['Drawdown'][start_date2]
        # last = drawdown[drawdown['Drawdown'].index >= start_date2]
        # end_value2 = last[last['Drawdown']==0][:1]
        # end_date2 = end_value2.index.values
        # updowns.iloc[i] = [category2,start_date2,end_date2,start_value2,end_value2]
        # drawdown = drawdown[(drawdown.index < start_date) & (drawdown.index > end_date2)]
        # lowvalue = drawdown['Drawdown'].idxmin()
        # if lowvalue > floor:
        #     break
        




def updown (drawdown, floor=-0.2) :
    # updowns = pd.DataFrame(columns=['category',
    #                                 'start_date','end_date',
    #                                 'start_value','end_value'])
    updowns = pd.DataFrame()
    # end_date = pd.DataFrame()
    # end_value = pd.DataFrame()
    # start_value = pd.DataFrame()
    # start_date = pd.DataFrame()
    # previous = pd.DataFrame()
    i = 0
    lowvalue = drawdown['Drawdown'][drawdown['Drawdown'].idxmin()]

    while lowvalue > floor: # down
        category = 'down'
        end_date = drawdown['Drawdown'].idxmin()
        end_value = drawdown['Drawdown'][end_date]
        previous = drawdown[drawdown['Drawdown'].index < end_date]
        start_value = previous['Drawdown'][previous['Drawdown']>floor][-1:]
        start_date = start_value.index.values
        updowns = pd.DataFrame({'end_date':end_date,
                                'end_value':end_value,
                                'start_value':start_value,
                                'start_date':start_date})
        lowvalue = drawdown['Drawdown'][drawdown['Drawdown'].idxmin()]


        # if lowvalue > floor:
        #     break
        
        # updowns.iloc[i] = [category,start_date,end_date,start_value,end_value]
        # category = 'down'
        # end_date = drawdown['Drawdown'].idxmin()
        # end_value = drawdown['Drawdown'][end_date]
        # previous = drawdown[drawdown['Drawdown'].index < end_date]
        # start_value = previous['Drawdown'][previous['Drawdown']>floor][-1:]
        # start_date = start_value.index.values
        # updowns.iloc[i] = [category,start_date,end_date,start_value,end_value]
        i = i+1
        # category2 = 'up'
        # start_date2 = end_date + pd.offsets.BusinessDay(1)
        # start_value2 = drawdown['Drawdown'][start_date2]
        # last = drawdown[drawdown['Drawdown'].index >= start_date2]
        # end_value2 = last[last['Drawdown']==0][:1]
        # end_date2 = end_value2.index.values
        # updowns.iloc[i] = [category2,start_date2,end_date2,start_value2,end_value2]
        # drawdown = drawdown[(drawdown.index < start_date) & (drawdown.index > end_date2)]
        # lowvalue = drawdown['Drawdown'].idxmin()
        # if lowvalue > floor:
        #     break
        
    return updowns
        
        
    
    
    return pd.DataFrame({'category':category,
                         'start_date':start_date,
                         'end_date':end_date,
                         'start_value':start_value,
                         'end_value': end_value 
                         })

    



def findmintest (data, fromyear, toyear):
    
    n_steps = len(data.columns)
    result = pd.DataFrame()
            
    for step in range(n_steps):
        lowdate = data[data.columns[step]][fromyear:toyear].idxmin()
        lowvalue= data[data.columns[step]][lowdate]
        oneyearvalue = data[data.columns[step]][lowdate + datetime.timedelta(days=365)]
        name = data.columns[step]
        # df = pd.DataFrame([lowdate, lowvalue, oneyearvalue], index=['lowdate','lowvalue','oneyearvalue'], columns=[name])
        # 데이터 프레임 만들때 {}는 딕션널리여서 순서가 뒤죽박줌됨. 항상 [] 사용
        # result.columns[step] = [name]
        result.iloc[step] = [lowdate,lowvalue,oneyearvalue]
        
        """ aa = pd.DataFrame({"lowdate": a3, 
                         "lowvalue": a4, 
                          "oneyear": a5}) """
        # result = result.append(aa)
        
       # result.index[step] = data.columns[step]
       # result.iloc[step] = [a3,a4,a5]
    
    return result




def findmin (data,fromyear,toyear):
    n_steps = len(data.columns)
    names = []
    lowdates = []
    lowvalues = []
    oneyearvalues = []
        
    for step in range(n_steps):
        try:
            name = data.columns[step]
            lowdate = data[name][fromyear:toyear].idxmin()
            lowvalue= data[name][lowdate]
            oneyearvalue = data[name][lowdate + datetime.timedelta(days=365)]
            names += [name]
            lowdates += [lowdate]
            lowvalues += [lowvalue]
            oneyearvalues += [oneyearvalue]
        except : pass

    result = pd.DataFrame(data=[lowdates,lowvalues,oneyearvalues], columns=[names], index=['lowdate','lowvalue','oneyearvalue']).T
    result['diff'] = result['oneyearvalue'] - result['lowvalue']
    return(result)

def quote (data,info='Market Cap'):
    n_steps = len(data)
    tickers = []
    values = []
        
    for step in range(n_steps):
        try:
            ticker = data[step]
            value = si.get_quote_table(ticker, dict_result=True)[info]
            tickers += [ticker]
            values += [value]
        except: pass

    result = pd.DataFrame(data=[tickers,values])
    return(result)


def cunit (value):
    n_steps = len(value)
    values = []
        
    for step in range(n_steps):
        if value[step][-1] == 'K':
            value = float(value[:-1])*(10**3)
        elif value[step][-1] == 'M':
            value = float(value[:-1])*(10**6)
        elif value[step][-1] == 'B':
            value = float(value[:-1])*(10**9)
        elif value[step][-1] == 'T':
            value = float(value[:-1])*(10**12)            
        values += [value]

    return(values)

def cunit1 (value):
        if value[-1] == 'K':
            float(value[:-1])*(10**3)
        elif value[-1] == 'M':
            float(value[:-1])*(10**6)
        elif value[-1] == 'B':
            float(value[:-1])*(10**9)
        elif value[-1] == 'T':
            float(value[:-1])*(10**12)   
        else : value[-1]         



bb = len(aa)
for i in range(bb):
    if aa[i][-1] == 'T':
        bb = float(aa[i][:-1])
        print(bb*1000)
    else :
        print('None')
        
'''


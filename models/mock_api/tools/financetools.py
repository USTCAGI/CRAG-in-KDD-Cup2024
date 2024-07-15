from models.mock_api.pycragapi import CRAG

class FinanceTools:
    def __init__(self):
        self.api = CRAG()
        name2symbol = {}
        symbol2name = {}
        all_symbols = []

        with open("models/mock_api/data/company_name.dict", "r") as f:
            for line in f:
                line = line.split(",")
                if line[1] == 'Name':
                    continue
                name2symbol[line[1].strip().lower()] = line[2].strip()
                symbol2name[line[2].strip()] = line[1].strip()
                all_symbols.append(line[2].strip())

        self.name2symbol = name2symbol
        self.symbol2name = symbol2name
        self.all_symbols = all_symbols

    def get_ticker_names(self, query):
        company_names = self.get_company_name(query)
        ticker_names = []
        if company_names is None or len(company_names) == 0:
            return []
        else:
            for company_name in company_names:
                if company_name.lower() in query.lower():
                    ticker_names.append(self.get_ticker_by_name(company_name))
        return ticker_names
    
    def get_company_name(self, query):
        """
        Given a query, return top matched company names.
        arg:
            query: str
        output:
            top matched company names: list[str]
        """
        return self.api.finance_get_company_name(query)['result']

    def get_ticker_by_name(self, company_name):
        """
        Return ticker name by company name.
        arg:
            company_name: the company name: str
        output:
            the ticker name of the company: str
        """
        return self.api.finance_get_ticker_by_name(company_name)['result']
    
    def get_price_history(self, ticker_name):
        """
        Return 1 year history of daily Open price, Close price, High price, Low price and trading Volume.
        arg: 
            ticker_name: str, upper case
        output:
            1 year daily price history: json 
        example:
            {'2023-02-28 00:00:00 EST': {'Open': 17.258894515434886,
                                            'High': 17.371392171233836,
                                            'Low': 17.09014892578125,
                                            'Close': 17.09014892578125,
                                            'Volume': 45100},
                '2023-03-01 00:00:00 EST': {'Open': 17.090151299382544,
                                            'High': 17.094839670907174,
                                            'Low': 16.443295499989794,
                                            'Close': 16.87453269958496,
                                            'Volume': 104300},
                ...
                }
        """
        return self.api.finance_get_price_history(ticker_name.upper())['result']
    
    # def get_price_history(self, ticker_name):
    #     """
    #     Return the history of daily Open price, Close price, High price, Low price and trading Volume.
    #     arg: 
    #         ticker_name: str, upper case
    #     output:
    #         last 20 daily price history: json 
    #     example:
    #         {'2023-02-28 00:00:00 EST': {'Open': 17.258894515434886,
    #                                         'High': 17.371392171233836,
    #                                         'Low': 17.09014892578125,
    #                                         'Close': 17.09014892578125,
    #                                         'Volume': 45100},
    #             '2023-03-01 00:00:00 EST': {'Open': 17.090151299382544,
    #                                         'High': 17.094839670907174,
    #                                         'Low': 16.443295499989794,
    #                                         'Close': 16.87453269958496,
    #                                         'Volume': 104300},
    #             ...
    #             }
    #     """
    #     keys = list(self.api.finance_get_price_history(ticker_name)['result'].keys())[-20:]
    #     return {key: self.api.finance_get_price_history(ticker_name)['result'][key] for key in keys}

    
    def get_price(self, ticker_name, date):
        """
        Return the price of the ticker on the given date.
        arg:
            ticker_name: str, upper case
            date: str, format: 'YYYY-MM-DD'
        output:
            the price of the ticker on the given date: dict
        example:
            {'Open': 17.258894515434886,
             'High': 17.371392171233836,
             'Low': 17.09014892578125,
             'Close': 17.09014892578125,
             'Volume': 45100}
        """
        date = date + ' 00:00:00 EST'
        if self.get_price_history(ticker_name.upper()) is None:
            return None
        if date not in self.get_price_history(ticker_name.upper()):
            return None
        return self.get_price_history(ticker_name.upper())[date]
    
    def get_latest_price(self, ticker_name, date):
        """
        Return the latest price of the ticker before the given date(the last trading day).
        arg:
            ticker_name: str, upper case
            date: str, format: 'YYYY-MM-DD'
        output:
            the latest price of the ticker before the given date: dict
        """
        prices = self.get_price_history(ticker_name.upper())
        dates = list(prices.keys())
        dates.sort(reverse=True)
        for d in dates:
            if d[:10] < date:
                latest_price = prices[d]
                break
        return latest_price
    
    def get_detailed_price_history(self, ticker_name):
        """ 
        Return the past 5 days' history of 1 minute Open price, Close price, High price, Low price and trading Volume, starting from 09:30:00 EST to 15:59:00 EST. Note that the Open, Close, High, Low, Volume are the data for the 1 min duration. However, the Open at 9:30:00 EST may not be equal to the daily Open price, and Close at 15:59:00 EST may not be equal to the daily Close price, due to handling of the paper trade. The sum of the 1 minute Volume may not be equal to the daily Volume.
        arg: 
            ticker_name: str, upper case
        output:
            past 5 days' 1 min price history: json  
        example:
            {'2024-02-22 09:30:00 EST': {'Open': 15.920000076293945,
                                            'High': 15.920000076293945,
                                            'Low': 15.920000076293945,
                                            'Close': 15.920000076293945,
                                            'Volume': 629},
                '2024-02-22 09:31:00 EST': {'Open': 15.989999771118164,
                                            'High': 15.989999771118164,
                                            'Low': 15.989999771118164,
                                            'Close': 15.989999771118164,
                                            'Volume': 108},
                ...
            }
        """
        return self.api.finance_get_detailed_price_history(ticker_name.upper())['result']
    
    def get_detailed_price(self, ticker_name, date, time):
        """
        Return the price of the ticker on the given date and time.
        arg:
            ticker_name: str, upper case
            date: str, format: 'YYYY-MM-DD'
            time: str, format: 'HH:MM:SS'
        output:
            the price of the ticker on the given date and time: dict
        example:
            {'Open': 15.920000076293945,
             'High': 15.920000076293945,
             'Low': 15.920000076293945,
             'Close': 15.920000076293945,
             'Volume': 629}
        """
        date_time = date + ' ' + time + ' EST'
        return self.get_detailed_price_history(ticker_name.upper())[date_time]
    
    def get_dividends_history(self, ticker_name):
        """
        Return dividend history of a ticker.
        arg: 
            ticker_name: str, upper case
        output:
            dividend distribution history: json
        example:
            {'2019-12-19 00:00:00 EST': 0.058,
                '2020-03-19 00:00:00 EST': 0.2,
                '2020-06-12 00:00:00 EST': 0.2,
                ...
                }
        """
        return self.api.finance_get_dividends_history(ticker_name.upper())['result']
    
    def get_first_dividend_date(self, ticker_name):
        """
        Return the first dividend date of a ticker.
        arg: 
            ticker_name: str, upper case
        output:
            the first dividend date: str
        """
        return list(self.get_dividends_history(ticker_name.upper()).keys())[0]
    
    # def get_last_dividend_date(self, ticker_name):
    #     """
    #     Return the last dividend date of a ticker.
    #     arg: 
    #         ticker_name: str, upper case
    #     output:
    #         the last dividend date: str
    #     """
    #     return list(self.get_dividends_history(ticker_name).keys())[-1]
    
    def get_latest_dividend(self, ticker_name, date):
        """
        Return the latest dividend of the ticker before the given date.
        arg:
            ticker_name: str, upper case
            date: str, format: 'YYYY-MM-DD'
        output:
            the latest dividend of the ticker before the given date: float
        """
        dividends = self.get_dividends_history(ticker_name.upper())
        dates = list(dividends.keys())
        dates.sort(reverse=True)
        for d in dates:
            if d[:10] < date:
                latest_dividend = dividends[d]
                break
        return {d: latest_dividend}
    
    def get_dividends_history_by_year(self, ticker_name, year):
        """
        Return the dividends of the ticker in the given year.
        arg:
            ticker_name: str, upper case
            year: str, format: 'YYYY'
        output:
            the dividends of the ticker in the given year: float
        """
        dividends = self.get_dividends_history(ticker_name.upper())
        return {date: dividends[date] for date in dividends if date[:4] == year}

    def get_dividends_history_by_month(self, ticker_name, year, month):
        """
        Return the dividends of the ticker in the given year and month.
        arg:
            ticker_name: str, upper case
            year: str, format: 'YYYY'
            month: str, format: 'MM'
        output:
            the dividends of the ticker in the given year and month: float
        """
        dividends = self.get_dividends_history(ticker_name.upper())
        return {date: dividends[date] for date in dividends if date[:7] == year + '-' + month}
    
    def get_dividends(self, ticker_name, date):
        """
        Return the dividend of the ticker on the given date.
        arg:
            ticker_name: str, upper case
            date: str, format: 'YYYY-MM-DD'
        output:
            the dividend of the ticker on the given date: dict
        """
        date = date + ' 00:00:00 EST'
        return {date: self.get_dividends_history(ticker_name.upper())[date]}
    
    def get_market_capitalization(self, ticker_name):
        """
        Return the market capitalization of a ticker.
        arg: 
            ticker_name: str, upper case
        output:
            market capitalization: float
        """
        return self.api.finance_get_market_capitalization(ticker_name.upper())['result']

    def get_eps(self, ticker_name):
        """
        Return the earnings per share of a ticker.
        arg: 
            ticker_name: str, upper case
        output:
            earnings per share: float
        """
        return self.api.finance_get_eps(ticker_name.upper())['result']
    
    def get_pe_ratio(self, ticker_name):
        """
        Return the price to earnings ratio of a ticker.
        arg: 
            ticker_name: str, upper case
        output:
            price to earnings ratio: float
        """
        return self.api.finance_get_pe_ratio(ticker_name.upper())['result']
    
    def get_info_keys(self, ticker_name):
        """
        Return the keys of the information of a ticker. Use this function before calling get_info.
        arg: 
            ticker_name: str, upper case
        output:
            keys: list[str]
        """
        return self.api.finance_get_info(ticker_name.upper())['result'].keys()
    
    def get_info(self, ticker_name, key):
        """
        Return the information of a ticker. Use get_info_keys to get the keys.
        arg: 
            ticker_name: str, upper case
            key: str
        output:
            information: str
        """
        return self.api.finance_get_info(ticker_name.upper())['result'][key]
    
    def get_all_info(self, ticker_name):
        """
        Return all information of a ticker.
        arg: 
            ticker_name: str, upper case
        output:
            all information: dict
        """
        return self.api.finance_get_info(ticker_name.upper())['result']
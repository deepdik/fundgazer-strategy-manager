from scipy.stats import pearsonr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime


def Beta(a, b):
    """Stock , Index Close"""
    x = a / a.shift() - 1
    y = b / b.shift() - 1

    x.dropna(inplace=True)
    y.dropna(inplace=True)
    """ Here x is stock data and y is index data"""
    N = len(x)
    cov = (1 / (N - 1)) * np.sum((x - np.mean(x)) * (y - np.mean(y)))
    # cov = np.cov(x,y,ddof=1)[0,1]
    var = (np.std(y, ddof=1)) ** 2
    # var = np.sqrt(((1/(N-1))*np.sum((y-np.mean(y))**2)))
    return cov / var


def Average_Daily_Volatility(n, kite):
    """n = instrument_number
    kite = kite object"""
    data1 = pd.DataFrame(
        kite.historical_data(
            n, datetime.now() - timedelta(days=365), datetime.now(), "day"
        )
    ).Close
    data4 = pd.DataFrame(
        kite.historical_data(
            n, datetime.now() - timedelta(days=4 * 365), datetime.now(), "day"
        )
    ).Close
    change1 = np.abs(data1.pct_change()[1:]) * 100
    change4 = np.abs(data4.pct_change()[1:]) * 100
    frame = pd.DataFrame()
    frame["Mean"] = [change1.mean(), change4.mean()]
    frame["Standard deviation"] = [change1.std(), change4.std()]
    frame.index = ["1 Year", "4 Year"]
    return frame


def roc(df, period):
    """Return on Capital change

    Args:
        df (pd.DataFrame): Data symbol
        period (Int): period

    Returns:
        pd.Series: _description_
    """
    currentPrice = df.Close
    closing_price = df.Close.shift(period)
    # roc = 100 * ((currentPrice - closing_price)/closing_price)
    roc = 100 * np.log(currentPrice / closing_price)
    return roc


class Noise:
    def __init__(self, symbol):
        self.path = "C:\\Users\\Aditya\\Desktop\\FundGazer\\side\\Data\\"
        self.conversion = {
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Volume": "sum",
        }
        self.data = (
            pd.read_csv(
                self.path + symbol + ".csv",
                header=0,
                index_col=0,
                parse_dates=True,
                names=["Date", "Open", "High", "Low", "Close", "Volume"],
            )
            .resample("D")
            .apply(self.cconversion)
            .dropna()
        )
        self.noise = self.calculate_noise()

        plt.plot(self.data.index[-len(self.noise) :], self.noise)

        self.rollingMean = []
        self.normalMean = np.mean(self.noise)
        self.normalMedian = np.median(self.noise)
        for i in range(50, len(self.noise)):
            self.rollingMean.append(np.mean(self.noise[i - 50 : i + 1]))

        plt.plot(self.data.index[-len(self.rollingMean) :], self.rollingMean)

    def perfect_profit(self, dataFrame):
        up, down = Pivots(dataFrame, 2)
        up_min = min(up)
        down_min = min(down)

        pp = 0
        pp_list = []
        try:
            for i in range(max(len(up), len(down))):

                up_min = min(up)
                down_min = min(down)
                if up_min > down_min:
                    pp = pp + dataFrame.iloc[up_min].High - dataFrame.iloc[down_min].Low
                    pp_list.append(pp)
                    down.pop(0)

                if up_min < down_min:
                    pp = pp + dataFrame.iloc[up_min].High - dataFrame.iloc[down_min].Low
                    up.pop(0)
                    pp_list.append(pp)
                else:
                    up.pop(0)
                    down.pop(0)
        except:
            pass
        return pp

    def calculate_noise(self):
        n = []
        x_days = 50
        for i in range(x_days, len(self.data)):
            noise = abs(
                (self.data.Close[i] - self.data.Close[i - x_days])
                / self.perfect_profit(self.data[i - x_days : i + 1])
            )
            n.append(noise)
        return n


class Correlation:
    def __init__(self, symbol_pair):
        self.path = "C:\\Users\\Aditya\\Desktop\\FundGazer\\side\\Data\\"
        self.conversion = {
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Volume": "sum",
        }

        self.first = (
            pd.read_csv(
                self.path + symbol_pair[0] + ".csv",
                header=0,
                index_col=0,
                parse_dates=True,
                names=["Date", "Open", "High", "Low", "Close", "Volume"],
            )
            .resample("D")
            .apply(self.conversion)
            .dropna()
        )
        self.second = (
            pd.read_csv(
                self.path + symbol_pair[1] + ".csv",
                header=0,
                index_col=0,
                parse_dates=True,
                names=["Date", "Open", "High", "Low", "Close", "Volume"],
            )
            .resample("D")
            .apply(self.conversion)
            .dropna()
        )

        self.correlation = self.calculate_correlation()

        self.std_dev = np.std(self.correlation)

        plt.plot(self.first.index[-len(self.correlation) :], self.correlation)

        self.first_stochastic = Stochastic(self.first, 10).dropna()
        self.second_stochastic = Stochastic(self.second, 10).dropna()

        self.difference = self.first_stochastic - self.second_stochastic

        plt.plot(self.difference.index, self.difference)

    def calculate_correlation(self):
        days = 100
        correlation = []
        for i in range(days, len(self.first)):
            first_percentageChange = (
                self.first.Close[i - days : i + 1].pct_change().dropna()
            )
            second_percentageChange = (
                self.second.Close[i - days : i + 1].pct_change().dropna()
            )
            corr, _ = pearsonr(first_percentageChange, second_percentageChange)
            correlation.append(corr)
        return correlation

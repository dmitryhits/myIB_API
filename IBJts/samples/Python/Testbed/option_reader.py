"""
reads files one by one for each date,
plots the underlying prices
determines the sigma of an underlying symbol
extracts option chain within x*sigma around the underlying value
"""

import glob
import pandas as pd
import numpy as np

main_path = "/Users/hits/Desktop/livediscount2003_optiondatabucketzip/"
files = glob.glob(main_path+'**/*csv', recursive=True)
bank_days = {file.strip('_OData.csv').split('/')[-1]:file for file in files}

apple_price = []
for day in sorted(bank_days.keys()):
    option_sample = pd.read_csv(bank_days[day], index_col='Symbol')
    apple_price.append(option_sample['UnderlyingPrice'].loc['AAPL'].unique()[0])

apple_price = pd.Series(apple_price)
print(apple_price.mean(), apple_price.std())

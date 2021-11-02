import time
import hmac
import requests
from requests import Request
import pandas as pd

#dydx public end points imports
from dydx3 import Client
from web3 import Web3
from dydx3.constants import MARKET_BTC_USD


client = Client(
    host='https://api.dydx.exchange',
    #web3=Web3('...'),
    #stark_private_key='01234abcd...',
)
#
# Access public API endpoints.
#



historical_funding = client.public.get_historical_funding(
  market=MARKET_BTC_USD,
)

print(historical_funding)
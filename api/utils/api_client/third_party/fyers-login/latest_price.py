from login_automatic import fyers


data = {"symbols":"NSE:NIFTYBANK-INDEX"}
last_price = fyers.quotes(data=data)['d'][0]['v']['lp']
print(last_price)
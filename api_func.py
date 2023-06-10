import datetime, logging, configparser, traceback
import pandas as pd

from oandapyV20 import API
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.forexlabs as labs
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.positions as positions
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.transactions as trans


file_handler = logging.FileHandler('log.log')
logging.basicConfig(handlers=[file_handler], level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

cfg = configparser.RawConfigParser()
cfg.read(filenames='credentials.ini')

access_token = cfg['keys']['api_key']
accountID = cfg['keys']['accountID']

client = API(access_token=access_token)

def error_handler(func,current_try = 1, *args, **kwargs):
    # wrapper function for handling errors
    try:
        return func(*args, **kwargs)
    except Exception as e:
        #assign exception to the error_type
        print(f'ERROR IN {func} @ {datetime.datetime.now().time().replace(microsecond=0)} : {e}')
        logging.error(f'ERROR IN {func} @ {datetime.datetime.now().time().replace(microsecond=0)} : {e}')
        logging.error(f'FUNCTION ARGUMENTS ARE :{args}, {kwargs}')
        logging.error(traceback.format_exc())
        
        if current_try < 4:
            current_try += 1
            error_handler(func,current_try=current_try, *args, **kwargs)
        
        return


def place_order(price: str, instrument: str, units:str, order_type: str= 'LIMIT', stop_price:str = None, target_price:str = None, trailing_stop_price:str = None, timeInForce: str= 'GTC'):
    
    data = {"order": {
                "price": price,
                "timeInForce": timeInForce,
                "instrument": instrument,
                "units": units,
                "type": order_type,
                "positionFill": "DEFAULT"
                    } }
    if stop_price:
        stops = {"stopLossOnFill": {
                    "timeInForce": 'GTC',
                    "price": stop_price
                        } }
        data['order'].update(stops)
    
    if target_price:
        target = {"takeProfitOnFill": {
                    "timeInForce": 'GTC',
                    "price": target_price
                        } }
        data['order'].update(target)
    
    if trailing_stop_price:
        trailing = {"trailingStopLossOnFill": {
                    "timeInForce": 'GTC',
                    "distance": trailing_stop_price
                        } }
        data['order'].update(trailing)
        
    req = orders.OrderCreate(accountID, data=data)
    response = error_handler(client.request, endpoint = req)
    return response

def modify_order(orderID: str, units: str, instrument: str, price: str, order_type: str= 'MARKET', accountID: str= accountID):
	data = {"order": {
                "units": units,
                "instrument": instrument,
                "price": price,
                "type": order_type }
            }
	req = orders.OrderReplace(accountID=accountID, orderID=orderID, data=data)
	response = error_handler(client.request, endpoint = req)
	return response

def cancel_order(orderID: str, accountID = accountID):
    req = orders.OrderCancel(accountID= accountID, orderID= orderID)
    cancelled_order = error_handler(client.request, endpoint = req)
    return cancelled_order

def get_order_details(orderID, accountID = accountID):
    req = orders.OrderDetails(accountID= accountID, orderID= orderID)
    response = error_handler(client.request, endpoint = req)
    return response

def get_order_list(accountID = accountID):
    req = orders.OrderList(accountID)
    response  = error_handler(client.request, endpoint = req)
    return response

def get_pending_orders(accountID = accountID):
    req = orders.OrdersPending(accountID)
    response  = error_handler(client.request, endpoint = req)
    return response



def get_candles(instrument: str, _from: datetime= None, _to: datetime= None, gran: str= 'M5'):    
    params = {"granularity": gran}
    if _from:
        params.update({'from':_from})
    if _to:
        params.update({'to':_to})

    req = instruments.InstrumentsCandles(instrument=instrument, params=params)
    response = error_handler(client.request, endpoint = req)
    return response

def get_instrument_position_book(instrument: str):
    req = instruments.InstrumentsPositionBook(instrument=instrument, params={})
    response = error_handler(client.request, endpoint = req)
    return response

def get_instrument_order_book(instrument: str):
    req = instruments.InstrumentsOrderBook(instrument=instrument, params={})
    response = error_handler(client.request, endpoint = req)
    return response



def get_open_positions(accountID = accountID):
    req = positions.OpenPositions(accountID=accountID)
    response = error_handler(client.request, endpoint = req)
    return response

def close_position(instrument: str, data: dict, accountID: str= accountID):
    ''' Close Open Position for given symbol and quantity for selected Account \n
    data = {'longUnits' : 'ALL} \n
    data = {'shortUnits : '100'}
    '''
    req = positions.PositionClose(accountID=accountID, instrument=instrument, data=data)
    response = error_handler(client.request, endpoint = req)
    return response

def get_position_details(instrument: str, accountID: str= accountID):
    ''' Get details of position for given symbol and Account '''
    req = positions.PositionDetails(accountID=accountID, instrument=instrument)
    response = client.request(req)
    return response

def get_position_list(accountID: str= accountID):
    ''' Get list of all positions for given Account'''
    req = positions.PositionList(accountID=accountID)
    response = error_handler(client.request, endpoint = req)
    return response



def get_prices(instruments: list, accountID: str= accountID):
    params ={
            "instruments": ','.join(instruments)
            }
    req = pricing.PricingInfo(accountID=accountID, params=params)
    response = error_handler(client.request, endpoint = req)
    return response

def price_streams(instruments: list, max_records: int= 10, accountID: str= accountID):
    params ={
            "instruments": ','.join(instruments)
            }
    req = pricing.PricingStream(accountID=accountID, params=params)
    response = error_handler(client.request, endpoint = req)

    maxrecs = 10
    for ticks in req:
        yield ticks
        maxrecs -= 1
        if maxrecs == 0:
            req.terminate("maxrecs records received")



def get_open_trades(accountID: str= accountID):
    req = trades.OpenTrades(accountID= accountID)
    response = error_handler(client.request, endpoint = req)
    return response

def close_trade(units: str, tradeID: str, accountID: str= accountID):
    data = {"units":str(units)}
    req = trades.TradeClose(data=data, tradeID=str(tradeID), accountID= str(accountID))
    response = error_handler(client.request, endpoint = req)
    return response

def get_trade_details(tradeID: str, accountID: str= accountID):
    req = trades.TradeDetails(tradeID=str(tradeID), accountID= str(accountID))
    response = error_handler(client.request, endpoint = req)
    return response

def get_trade_list(instrument: str, accountID: str= accountID):
    # not working properly, instead of giving all trades list, giving only open trades
    params = {"instrument": instrument}
    req = trades.TradesList(params= params, accountID= str(accountID))
    response = error_handler(client.request, endpoint = req)
    return response

def add_trade_comment(tradeID: str, accountID: str= accountID, comment: str= None, id: str= None):
  data = {
    "clientExtensions": {
      "comment": comment,
      "id": id } }
  req = trades.TradeClientExtensions(accountID= accountID, tradeID= 93, data= data)
  response = error_handler(client.request, endpoint = req)
  return response



def get_account_summary(accountID: str= accountID):
    req = accounts.AccountSummary(accountID)
    response = error_handler(client.request, endpoint = req)
    return response

def get_account_details(accountID: str= accountID):
    req = accounts.AccountDetails(accountID)
    response = error_handler(client.request, endpoint = req)
    return response



def get_transaction_details(trasactionID:str, accountID: str= accountID):
    req = trans.TransactionDetails(accountID=accountID, transactionID= str(trasactionID))
    response = error_handler(client.request, endpoint = req)
    return response

def get_transaction_details_by_range(_from: str, _to: str, accountID: str= accountID):
    params = {"from" : _from, 'to' : _to}
    req = trans.TransactionIDRange(accountID=accountID, params=params)
    response = error_handler(client.request, endpoint = req)
    return response

def get_transaction_list(accountID: str= accountID):
    req = trans.TransactionList(accountID=accountID)
    response = error_handler(client.request, endpoint = req)
    return response

def get_transactions_since_id(id: str, accountID: str= accountID):
    params = {'id' : id}
    req = trans.TransactionsSinceID(accountID = accountID, params = params)
    response = error_handler(client.request, endpoint = req)
    return response
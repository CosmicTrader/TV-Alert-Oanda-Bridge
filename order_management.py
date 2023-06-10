import pandas as pd
import datetime, logging, traceback, math, time

from db_utils import save_alert, save_filled_order
from database import Engine
from sqlalchemy.orm import Session
from models import Order

from api_func import place_order, close_trade, get_trade_details, get_open_positions, get_order_details, get_transaction_details
from symbol_mapper import symbol_mapper

oins = pd.read_csv('instruments.csv')

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

def check_order_status(order_detail):
    
    order_id = order_detail['orderCreateTransaction']['id']
    ord_det = error_handler(get_order_details, orderID = order_id)
    
    if ord_det.get('order'):
        
        if ord_det['order']['state'] == 'FILLED':
            if ord_det['order'].get('tradeOpenedID'):
                trd_det = error_handler(get_trade_details, tradeID = ord_det['order']['tradeOpenedID'])
                if trd_det.get('trade') :
                    return 'FILLED', trd_det['trade']
                    
            if ord_det['order'].get('fillingTransactionID'):
                trd_det = error_handler(get_transaction_details, trasactionID = ord_det['order']['fillingTransactionID'])
                if trd_det.get('transaction') :
                    return 'FILLED', trd_det['transaction']

        else:
            return ord_det['order']['state'], ord_det
        
def save_order_trade_details(order_details, alert_id):
    trade_details, pending_orders, cancelled_orders = [], [], []

    for _order in order_details:
        _order_status, trade_detail = check_order_status(_order)

        if _order_status == 'FILLED':
            trade_details.append((_order.get('orderCreateTransaction'), trade_detail))
        elif _order_status == 'PENDING':
            pending_orders.appned(trade_detail)
        elif _order_status == 'CANCELLED':
            cancelled_orders.append(trade_detail)
    
    data_ids = []
    for trade in trade_details:
        saved_data_sr = save_filled_order(trade, alert_id)
        data_ids.append(saved_data_sr)
    
    return data_ids

def handle_entry_alert(entry_alert, order_type = 'MARKET'):

    symbol = symbol_mapper[entry_alert['Symbol']]
    symbol_token = oins[oins.name == symbol].iloc[0]
    precision = symbol_token['displayPrecision']
    unit_precision = symbol_token['tradeUnitsPrecision']
    
    timeInForce = 'IOC' if order_type == 'MARKET' else 'GTC'
    
    if entry_alert['Side'] == 'buy':
        order_size = str(round(float(entry_alert['Order_Size']) + float(entry_alert['Current_Position']), unit_precision) )
        alert_entry_price = str(round(float(entry_alert['Entry']) * 1.0005, precision))

    elif entry_alert['Side'] == 'sell':
        order_size = str(round(-float(entry_alert['Order_Size']) + float(entry_alert['Current_Position']), unit_precision) )
        alert_entry_price = str(round(float(entry_alert['Entry']) * 0.9995, precision))
    
    stop_loss = str(round(float(entry_alert['Stop_Loss']), precision)) if not math.isnan(float(entry_alert['Stop_Loss'])) else None
    target = str(round(float(entry_alert['Target']), precision)) if not math.isnan(float(entry_alert['Target'])) else None
    trailing_stop = str(round(float(entry_alert['Profit_Trail']), precision)) if not math.isnan(float(entry_alert['Profit_Trail'])) else None
    if trailing_stop:
        distance = str(round(abs(float(alert_entry_price) - float(trailing_stop)), precision))
    else:
        distance = None
    
    order_details = []
    for i in range(int(entry_alert['Trade_Mulitplier'])):
        order_detail = error_handler(place_order, instrument= symbol, units= order_size, order_type= order_type, price= alert_entry_price, stop_price= stop_loss, target_price= target, trailing_stop_price= distance,  timeInForce= timeInForce)
        order_details.append(order_detail)
        time.sleep(1)

    return order_details

def handle_position_exit(alert):

    closed_trades = []

    if float(alert['Current_Position']) == 0 :
        return closed_trades
    
    symbol = symbol_mapper[alert['Symbol']]
    open_positions = error_handler(get_open_positions)['positions']        

    for position in open_positions:
        if position['instrument'] == symbol:
            
            if alert['Side'] == 'buy':
                qty = float(position['short']['units'])
                if qty != 0 :
                    for _id in position['short']['tradeIDs']:
                        with Session(Engine) as session:
                            _orders = session.query(Order.trade_id).filter_by(instrument = symbol).all()
                            for _ord in _orders:
                                if _ord[0] == _id:
                                    trd_detail = error_handler(get_trade_details, tradeID = _id)['trade']
                                    trade_details = error_handler(close_trade, units = abs(float(trd_detail['currentUnits'])), tradeID = _id)
                                    closed_trades.append(trade_details)

                elif qty > 0 and abs(qty) == alert['Order_Size']:
                    print('there is some error, either last position was not closed properly using algo.')

            else :
                qty = float(position['long']['units'])
                if qty != 0:
                    for _id in position['long']['tradeIDs']:
                        with Session(Engine) as session:
                            _orders = session.query(Order.trade_id).filter_by(instrument = symbol).all()
                            for _ord in _orders:
                                if _ord[0] == _id:                        
                                    trd_detail = error_handler(get_trade_details, tradeID = _id)['trade']
                                    trade_details = error_handler(close_trade, units = abs(float(trd_detail['currentUnits'])), tradeID = _id)
                                    closed_trades.append(trade_details)

                elif qty < 0 and abs(qty) == alert['Order_Size']:
                    print('there is some error, either last position was not closed properly using algo.')

    return closed_trades

def handle_alert(alert):
    
    closed_trades = error_handler(handle_position_exit, alert = alert)
    
    order_details = error_handler(handle_entry_alert, entry_alert = alert)
    
    alert_id = error_handler(save_alert, alert=alert, alert_type = 'entry_alert')

    order_ids = error_handler(save_order_trade_details, order_details = order_details, alert_id = alert_id)

    close_ids = error_handler(save_order_trade_details, order_details = closed_trades, alert_id = alert_id)
    
    try:
        logging.warning(f'Alert SR : {alert_id}, Order SR : {order_ids}, Close SR : {close_ids}, New Order Details : {order_details}, Closed Trade Details : {closed_trades}')
    except:
        pass
    
    return alert_id, order_ids, order_details, closed_trades


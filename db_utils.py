from datetime import datetime
from sqlalchemy import desc, create_engine
from sqlalchemy.orm import Session
import logging, traceback, json
import pandas as pd
from models import Base, Order, error_log, Alerts
from database import DB_URL
from dateutil.parser import parse as dtparser
from symbol_mapper import symbol_mapper

Engine = create_engine(DB_URL)
logger = logging.getLogger(__name__)
Base.metadata.create_all(Engine)

def construct_error(error_type, error_message):
    # creates a new error log in the error_log table.
    err_lg = error_log(
        error_type = error_type,
        error_message = error_message,
        utc_timestamp = datetime.utcnow().replace(second=0, microsecond=0)
        )

    with Session(Engine) as session:
        session.add(err_lg) #add error in the database
        session.commit() #save changes made in database

    return

def error_handler(func, *args, **kwargs):
    # wrapper function for handling errors
    try:
        return func(*args, **kwargs)
    except Exception as e:
        #assign exception to the error_type
        print(f'ERROR IN {func} @ {datetime.datetime.now().time().replace(microsecond=0)} : {e}')
        logging.error(f'ERROR IN {func} @ {datetime.datetime.now().time().replace(microsecond=0)} : {e}')
        logging.error(f'FUNCTION ARGUMENTS ARE :{args}, {kwargs}')
        logging.error(traceback.format_exc())
        return



def save_alert(alert, alert_type):
    if alert['Side'] == 'buy':
        order_size = str(round(float(alert['Order_Size']), 1))
        
    else:
        order_size = str(round(-float(alert['Order_Size']), 1))
        
    _alert = Alerts(
        alert_type    = alert_type,
        alert_message = str(alert),
        timeframe     = str(alert['Timeframe']),
        exchange      = str(alert['Exchange']),
        alert_symbol  = str(alert['Symbol']),
        mapped_symbol = symbol_mapper[alert['Symbol']],
        entry_side    = alert['Side'],
        order_size    = order_size,
        current_position = str(alert['Current_Position']),
        trade_multiplier = str(alert['Trade_Mulitplier']),
        entry_price   = str(alert['Entry']),
        target        = str(alert['Target']),
        stop_loss     = str(alert['Stop_Loss']),
        trailing_stop = str(alert['Profit_Trail'])
        )

    with Session(Engine) as session:
        session.add(_alert) #add alert in the database
        session.commit() #save changes made in database
        alert_sr = _alert.sr
    return alert_sr

def save_filled_order(order_details, alert_sr):
    
    order_data = order_details[0].copy()
    trade_data = order_details[1].copy()
    data = {}
    
    data['alert_sr'] = alert_sr
    data['type'] = order_data.get('type')
    data['instrument'] = order_data.get('instrument')
    data['timeInForce'] = order_data.get('timeInForce')
    
    data['order_id'] = order_data.get('id')
    data['order_time'] = dtparser(order_data.get('time'))
    data['order_units'] = order_data.get('units')
    data['order_price'] = order_data.get('price')
    data['reason'] = order_data.get('reason')

    data['trade_id'] = trade_data.get('id')
    data['trade_units'] = trade_data.get('currentUnits')
    data['trade_price'] = trade_data.get('price')
    data['trade_state'] = trade_data.get('state')

    if trade_data.get('state') == 'OPEN':
        data['marginUsed'] = trade_data.get('marginUsed')
    
    if trade_data.get('openTime'):
        data['trade_time'] = dtparser(trade_data.get('openTime'))

    if trade_data.get('time'):
        data['trade_time'] = dtparser(trade_data.get('time'))

    if order_data.get('takeProfitOnFill'):
        data['target_price'] = order_data.get('takeProfitOnFill')['price']
        
    if order_data.get('stopLossOnFill') :
        data['stop_loss_price'] = order_data.get('stopLossOnFill')['price']
        
    if order_data.get('trailingStopLossOnFill') :
        data['trailing_stop_price'] = order_data.get('trailingStopLossOnFill')['distance']
    
    data['accountID'] = order_data.get('accountID')
    data['userID'] = order_data.get('userID')
    data['batchID'] = order_data.get('batchID')
    data['requestID'] = order_data.get('requestID')
    data['triggerCondition'] = order_data.get('triggerCondition')
    data['partialFill'] = order_data.get('partialFill')
    data['positionFill'] = order_data.get('positionFill')

    _order = Order(**data)

    with Session(Engine) as session:
        session.add(_order)
        session.commit()
        order_sr = _order.sr
    
    return order_sr
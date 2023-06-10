from sqlalchemy import create_engine, Column, String, Integer, Float, ForeignKey, TIMESTAMP, DateTime, DECIMAL
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class error_log(Base):
    __tablename__ = 'error_log'
    sr = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    utc_timestamp = Column(DateTime)
    error_type = Column(String(255), nullable=False)
    error_message = Column(String(255), nullable=False)

class Alerts(Base):
    __tablename__ = 'alert'
    sr = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    alert_type = Column(String(50), nullable=False)
    alert_message = Column(String(500), nullable=False)
    timeframe = Column(String(10))
    exchange = Column(String(10))
    alert_symbol = Column(String(50))
    mapped_symbol = Column(String(50))
    entry_side = Column(String(10))
    order_size = Column(String(10))
    current_position = Column(String(20))
    trade_multiplier = Column(String(10))
    entry_price = Column(String(15))
    target = Column(String(15))
    stop_loss = Column(String(15))
    trailing_stop = Column(String(15))
    trades_open_ids = Column(String(100))
    trades_closed_ids = Column(String(100))
    
class Order(Base):
    __tablename__ = 'order'
    sr = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    alert_sr = Column(Integer)
    type = Column(String(30))
    instrument = Column(String(30))
    timeInForce = Column(String(10))
    
    order_id = Column(String(10))
    order_time = Column(DateTime)
    order_units = Column(String(20))
    order_price = Column(String(20))
    reason = Column(String(300))
    target_price = Column(String(20))
    stop_loss_price = Column(String(20))
    trailing_stop_price = Column(String(20))
    
    trade_price = Column(String(20))
    trade_id = Column(String(10))
    trade_time = Column(DateTime)
    trade_units = Column(String(10))
    trade_price = Column(String(20))
    trade_state = Column(String(10))
    marginUsed = Column(String(30))
    
    accountID = Column(String(50))
    userID = Column(String(20))
    batchID = Column(String(20))
    requestID = Column(String(50))
    triggerCondition = Column(String(20))
    partialFill = Column(String(20))
    positionFill = Column(String(30))

    
class Trade(Base):
    __tablename__ = 'trades'
    sr = Column(Integer, primary_key= True)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    time = Column(DateTime)
    orderID = Column(Integer)
    price = Column(Float)
    tradeID = Column(Integer)
    units = Column(Integer)
    guaranteedExecutionFee = Column(Float)
    quoteGuaranteedExecutionFee = Column(Float)
    halfSpreadCost = Column(Float)
    initialMarginRequired = Column(Float)

class OrderFillTransaction(Base):
    __tablename__ = 'orderfilltransactions'
    
    sr = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    id = Column(Integer)
    accountID = Column(String(50))
    userID = Column(Integer)
    batchID = Column(String(50))
    requestID = Column(String(50))
    time = Column(DateTime)
    type = Column(String(50))
    orderID = Column(String(50))
    instrument = Column(String(50))
    units = Column(String(10))
    requestedUnits = Column(String(10))
    price = Column(Float)
    pl = Column(Float)
    quotePL = Column(String(50))
    financing = Column(Float)
    baseFinancing = Column(String(50))
    commission = Column(Float)
    accountBalance = Column(Float)
    gainQuoteHomeConversionFactor = Column(Float)
    lossQuoteHomeConversionFactor = Column(Float)
    guaranteedExecutionFee = Column(Float)
    quoteGuaranteedExecutionFee = Column(String(50))
    halfSpreadCost = Column(Float)
    fullVWAP = Column(Float)
    reason = Column(String(500))
    initialMarginRequired = Column(Float)
    closeoutBid = Column(Float)
    closeoutAsk = Column(Float)
    closeoutTimestamp = Column(DateTime)
    bidPrice = Column(Float)
    bidLiquidity = Column(Integer)
    askPrice = Column(Float)
    askLiquidity = Column(Integer)
    gainBaseHomeConversionFactor = Column(Float)
    lossBaseHomeConversionFactor = Column(Float)
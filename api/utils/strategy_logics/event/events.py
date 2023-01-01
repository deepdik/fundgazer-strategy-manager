import datetime
import uuid


class Event:
    pass


class MarketEvent(Event):
    """
    Handles the event of receiving a new market update with
    corresponding bars.
    """

    def __init__(self):
        self.type = "MARKET"


class SignalEvent(Event):
    """
    Handles the event of sending a Signal from a Strategy object.
    This is received by a Portfolio object and acted upon.
    """

    def __init__(
        self,
        symbol,
        strategy_id,
        Datetime,
        signal_type,
        direction,
        stop_loss=None,
        entry_price=None,
        exit_price=None,
        profit_target=None,
        order_type="MARKET",
        parent_id=None,
    ):
        self.type = "SIGNAL"
        self.order_type = order_type
        self.strategy_id = strategy_id
        self.symbol = symbol
        self.Datetime = Datetime
        self.signal_type = signal_type  ## OPEN/CLOSE
        self.stop_loss = stop_loss
        self.entry_price = entry_price
        self.direction = direction  ## LONG/SHORT == BUY/SELL
        self.order_id = (
            self.symbol
            + str(self.Datetime)
            + str(self.direction)
            + "|"
            + str(datetime.datetime.now())
            + f"|{str(uuid.uuid4())}"
        )
        self.parent_id = parent_id
        self.profit_target = profit_target
        self.exit_price = exit_price


class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a symbol (e.g. AXIS), a type (market or limit), quantity and a direction.
    """

    def __init__(
        self,
        order_id,
        symbol,
        order_type,
        quantity,
        direction,
        price,
        Lot_Size=None,
        volatility=None,
        parent_id=None,
    ):
        self.type = "ORDER"
        self.order_id = order_id
        self.symbol = symbol
        self.order_type = order_type  # CO,BO,LIMIT
        self.quantity = quantity
        self.direction = direction
        self.price = price
        self.Lot_Size = Lot_Size
        self.volatility = volatility
        self.parent_id = parent_id

    def print_order(self):
        print(
            f"Order: Symbol = {self.symbol}, Type = {self.type}, Quantity = {self.quantity}, Direction = {self.direction}, Price = {self.price}"
        )


class FillEvent(Event):
    """
    Encapsulates the notion of a Filled Order, as returned
    from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores
    the commission of the trade from the brokerage.
    """

    def __init__(
        self,
        order_id,
        timeindex,
        symbol,
        exchange,
        quantity,
        direction,
        fill_cost,
        price,
        commission=None,
        Lot_Size=None,
    ):
        self.type = "FILL"
        self.order_id = order_id
        self.timeindex = timeindex
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_cost = fill_cost
        self.price = price
        self.commission = commission
        self.Lot_Size = Lot_Size


class SuggestedOrder(Event):
    def __init__(
        self,
        order_type,
        symbol,
        strategy_id,
        Datetime,
        signal_type,
        direction,
        stop_loss=None,
        entry_price=None,
        exit_price=None,
        profit_target=None,
        parent_id=None,
    ):
        self.type = "SuggestedOrder"
        self.order_type = order_type  # Primary,add-on,Partial-Exit,Exit
        self.strategy_id = strategy_id
        self.symbol = symbol
        self.Datetime = Datetime
        self.signal_type = signal_type  ## OPEN/CLOSE
        self.stop_loss = stop_loss
        self.entry_price = entry_price
        self.direction = direction  ## LONG/SHORT
        self.order_id = (
            self.symbol
            + str(self.Datetime)
            + str(self.direction)
            + "|"
            + str(datetime.datetime.now())
        )
        self.parent_id = parent_id
        self.profit_target = profit_target
        self.exit_price = exit_price

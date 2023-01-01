from uuid import uuid1
import json


class SignalEvent:
    def __init__(
            self,
            symbols,
            weightage,
            datetime,
    ):
        self.type = "SIGNAL"
        self.symbols = symbols
        self.weightage = weightage
        self.datetime = datetime
        self.signal_id = str(uuid1())

    def __repr__(self):
        return self.__dict__

    def __str__(self):
        return json.dumps(self.get_data())

    def get_data(self):
        weight_list = self.weightage
        if not isinstance(weight_list, list):
            # converting numpy array
            weight_list = self.weightage.tolist()

        return {
            "type": "SIGNAL",
            "signalId": self.signal_id,
            "symbolWeight": [
                {"symbol": sym, "weight": weight_list[idx]}
                for idx, sym in enumerate(self.symbols)
            ],
            "datetime": str(self.datetime),
        }


class OrderEvent:
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
            datetime=None,
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
        self.datetime = datetime

    def __str__(self):
        # return f"Order: Symbol:{self.symbol}|Type:{self.order_type}|Quantity:{self.quantity}|Direction:{self.direction}|Price:{self.price}|id:{self.order_id}"
        return f"id:{self.order_id}|p_id:{self.parent_id}|{self.symbol}|{self.order_type}|{self.direction}|Quantity:{self.quantity}"

    def get_data(self):
        return {"type": "ORDER", "orderID": self.order_id, 'parentID': self.parent_id, 'datetime': str(self.datetime),
                "direction": self.direction, "quanity": self.quantity, "symbol": self.symbol}


class FillEvent:
    """
    Encapsulates the notion of a Filled Order, as returned
    from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores
    the commission of the trade from the brokerage.
    """

    def __init__(
            self,
            order_id,
            datetime,
            symbol,
            quantity,
            direction,
            fill_cost,
            price,
            commission=None,
            Lot_Size=None,
            exchange="Backtest",
    ):
        self.type = "FILL"
        self.order_id = order_id
        self.datetime = datetime
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_cost = fill_cost
        self.price = price
        self.commission = commission
        self.Lot_Size = Lot_Size

    def __str__(self):
        # return f"FILL: Symbol = {self.symbol}, Date = {self.datetime}, Quantity = {self.quantity}, Direction = {self.direction}, Price = {self.price}"
        return f"id:{self.order_id}|{self.direction}|{self.symbol}|{self.quantity}"

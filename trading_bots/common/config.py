from pydantic import BaseModel,ConfigDict,Field,model_validator
from typing import Literal


class BotConfig(BaseModel):
    model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
    mode:Literal['paper','live']='paper'
    capital:float=Field(250000,ge=1000,le=100000000)
    max_lots:int|None=Field(None,ge=1,le=100000,strict=True)
    # Retain old saved unit caps until explicitly replaced with lot sizing.
    max_quantity:int|None=Field(None,ge=1,le=100000,strict=True)
    max_loss_per_trade:float=Field(15000,gt=0)
    max_daily_loss:float=Field(30000,gt=0)
    max_trades_per_day:int=Field(5,ge=1,le=100,strict=True)
    max_positions:int=Field(1,ge=1,le=1,strict=True)
    stop_percent:float|None=Field(None,gt=0,lt=100)
    target_percent:float|None=Field(None,gt=0,le=1000)
    trailing_percent:float|None=Field(None,gt=0,lt=100)
    max_spread_percent:float=Field(2,gt=0,le=10)
    quote_max_age_seconds:float=Field(5,gt=0,le=30)
    signal_max_age_seconds:float=Field(10,gt=0,le=30)
    poll_seconds:float=Field(5,ge=1,le=30)
    slippage_points:float=Field(.05,ge=0,le=10)
    brokerage_per_order:float=Field(20,ge=0,le=1000)
    order_timeout_seconds:float=Field(15,ge=2,le=60)
    live_activated:bool=False

    @model_validator(mode='after')
    def default_lot_limit(self):
        if self.max_lots is None and self.max_quantity is None:
            self.max_lots=1
        return self


class GlobalConfig(BaseModel):
    model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
    kill_switch:bool=False
    max_positions:int=Field(3,ge=1,le=11,strict=True)
    max_capital:float=Field(750000,gt=0)
    max_orders_per_minute:int=Field(20,ge=1,le=100,strict=True)

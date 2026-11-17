"""Low-turnover, long-only pullbacks within an established slow trend."""
import os
import sys
from collections import deque

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars


class Strategy:
    def __init__(self):
        self.closes = deque(maxlen=180)
        self.trend_history = deque(maxlen=61)
        self.slow = None
        self.count = 0
        self.entry_price = 0
        self.peak = 0
        self.below = 0
        self.entries = 0
        self.last_exit = -10000
        self.was_held = False
        self.equity_peak = 0
        self.halted = False

    def on_batch(self, state, batch):
        bar = next((b for b in batch['bars'] if b['symbol'] == 'CBBTC'), None)
        if bar is None:
            return []
        price = int(bar['c'])
        self.count += 1
        self.closes.append(price)
        self.slow = price if self.slow is None else (119 * self.slow + 2 * price) // 121
        self.trend_history.append(self.slow)
        held = state.positions.get('CBBTC')
        if held and not self.was_held:
            self.entries += 1
            self.entry_price = price
            self.peak = price
        if not held and self.was_held:
            self.last_exit = state.seq
            self.below = 0
        self.was_held = bool(held)
        if state.warming_up:
            return []
        self.equity_peak = max(self.equity_peak, state.equity)
        if state.equity * 100 < self.equity_peak * 92:
            self.halted = True
        if held:
            self.peak = max(self.peak, price)
            self.below = self.below + 1 if price * 10000 < self.slow * 9940 else 0
            if self.halted or price * 10000 < self.peak * 9850 or self.below >= 60 or price * 10000 >= self.entry_price * 10080:
                return [{'side': 'sell', 'symbol': 'CBBTC', 'qty': held.qty,
                         'max_slippage_bps': 150}]
            return []
        if (self.halted or self.count < 121 or self.entries >= 3
                or state.seq - self.last_exit < 180):
            return []
        uptrend = (price > self.slow and self.slow * 10000 > self.trend_history[0] * 10020)
        pullback = price * 10000 <= max(list(self.closes)[-60:]) * 9985
        if not (uptrend and pullback):
            return []
        amount = min(state.cash, state.weight_room('CBBTC'), state.equity * 95 // 100)
        depth = state.depth_at('CBBTC')
        if not depth or min(depth) <= 0:
            return []
        # Binary search preserves the shim's multi-hop impact calculation and quote scaling.
        lo, hi = 0, amount
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if state.impact_bps('CBBTC', mid) <= 10:
                lo = mid
            else:
                hi = mid - 1
        if lo < int(state.hello['fees']['min_notional_quote_units']):
            return []
        return [{'side': 'buy', 'symbol': 'CBBTC', 'notional_quote_units': lo,
                 'max_slippage_bps': 50}]


if __name__ == '__main__':
    makefun_bars.run(Strategy().on_batch)

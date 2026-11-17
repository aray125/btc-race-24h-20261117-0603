"""Low-turnover recovery trend strategy for the bars replay protocol."""
import os
import sys
from collections import deque

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars


class RecoveryTrend:
    def __init__(self):
        self.closes = deque(maxlen=360)
        self.fast = None
        self.slow = None
        self.count = 0
        self.peak = 0
        self.entry = 0
        self.cool_until = 0
        self.entries = 0
        self.was_held = False
        self.exit_pending = False
        self.equity_peak = 0
        self.halted = False

    def on_batch(self, state, batch):
        bar = next((b for b in batch['bars'] if b['symbol'] == 'CBBTC'), None)
        if bar is None:
            return []
        price = int(bar['c'])
        previous = self.closes[-1] if self.closes else price
        old_fast = self.fast
        recent_high = max(self.closes) if self.closes else price
        self.fast = price if self.fast is None else self.fast + 2 / 31 * (price - self.fast)
        self.slow = price if self.slow is None else self.slow + 2 / 241 * (price - self.slow)
        self.closes.append(price)
        self.count += 1
        if state.warming_up:
            return []

        held = state.positions.get('CBBTC')
        self.equity_peak = max(self.equity_peak, state.equity)
        if state.equity * 100 < self.equity_peak * 92:
            self.halted = True
        if held and not self.was_held:
            self.entry = price
            self.peak = price
            self.entries += 1
        if not held and self.was_held:
            self.cool_until = state.seq + 180
            self.exit_pending = False
        self.was_held = bool(held)
        if held:
            self.peak = max(self.peak, price)
            # Give a new recovery room; protect gains once it advances 1%.
            trail_bps = 60 if self.peak * 100 > self.entry * 101 else 150
            if price * 10000 < self.peak * (10000 - trail_bps) or self.halted:
                self.exit_pending = True
            if self.exit_pending:
                return [{'side': 'sell', 'symbol': 'CBBTC', 'qty': held.qty,
                         'max_slippage_bps': 150}]
            return []

        recovery = (old_fast is not None and previous <= old_fast and price > self.fast)
        trend = price > self.slow
        pullback = price * 100 < recent_high * 99
        if (self.halted or self.count <= 240 or state.seq < self.cool_until
                or self.entries >= 3 or not (recovery and trend and pullback)):
            return []
        amount = min(state.cash, state.weight_room('CBBTC'))
        # Bound estimated own impact to 12 bps, using the latest close's depth.
        depths = state.depth_at('CBBTC')
        if not depths or any(d <= 0 for d in depths):
            return []
        # Exact reciprocal-depth cap avoids relying on rounded impact bps.
        product = 1
        for depth in depths:
            product *= depth
        reciprocal_sum = sum(product // depth for depth in depths)
        quote_scale = 10 ** state.hello['capital']['quote_scale']
        depth_budget = 12 * product * quote_scale // (10000 * 1000000 * reciprocal_sum)
        amount = min(amount, depth_budget)
        if state.impact_bps('CBBTC', amount) > 12:
            return []
        if amount < int(state.hello['fees']['min_notional_quote_units']):
            return []
        return [{'side': 'buy', 'symbol': 'CBBTC', 'notional_quote_units': amount,
                 'max_slippage_bps': 50}]


if __name__ == '__main__':
    makefun_bars.run(RecoveryTrend().on_batch)

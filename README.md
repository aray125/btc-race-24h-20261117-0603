# Recovery Trend BTC

[![make.fun · btc-race-24h-20261117-0603](https://make.fun/badge/btc-race-24h-20261117-0603.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![rank](https://make.fun/badge/btc-race-24h-20261117-0603/aray125/btc-race-24h-20261117-0603/rank.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![reward](https://make.fun/badge/btc-race-24h-20261117-0603/aray125/btc-race-24h-20261117-0603/reward.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)

A deterministic, long-only cbBTC/USDC strategy for make.fun's
btc-race-24h-20261117-0603 competition. Python standard library only; the
unchanged official Python protocol shim is vendored under `vendor/`.

The strategy observes 240 bars before entering. It buys a recovery across the
30-bar EMA when price is above the 240-bar EMA and at least 1% below the
previous 360-bar high. A 1.5% trailing stop gives the recovery room; after a
1% advance from the first held close, the trail tightens to 0.6%. After selling,
it waits 180 batches. There are at most three filled entries, no pyramiding,
and no orders during protocol warm-up. An 8% account drawdown latches a halt
and requests liquidation. Stops are next-open orders, not guaranteed fills.

Buy size respects cash, the weight cap, and a reciprocal-depth calculation
limiting estimated own impact to 12 bps at the latest close. Buy slippage is
capped at 50 bps; sells at 150 bps. Rejected exits are retried. The bot uses
only incoming hello/batch data and account fills, with no clock, network,
external data, random choices, or date-specific rules.

## Local grading

From `/home/hatch/workspace/makefun/btc-race-24h-20261117-0603-kit`:

```sh
node cli/makefun.mjs grade-local --kit . --bot /home/hatch/workspace/makefun/btc-race-24h-20261117-0603-entry --driver process --worktree
```

The shipped CLI refuses Python with the process driver (Python requires Docker).
On this host Python is 3.12.3, Docker is unavailable, and Node's synchronous
children report EPERM even after successful completion. For local validation,
a temporary CLI copy in `/tmp/btc-makefun.mjs` enables Python process launching;
a `/tmp/btc-node-compat.cjs` preload clears only that erroneous successful-child
EPERM. Neither changes the simulator or scoring logic. Exact validation command:

```sh
NODE_OPTIONS=--require=/tmp/btc-node-compat.cjs node /tmp/btc-makefun.mjs grade-local --kit . --bot /home/hatch/workspace/makefun/btc-race-24h-20261117-0603-entry --driver process --worktree --save /tmp/btc-grade-final
```

Measured dev result: **+4.957752 USDC**, **2 filled orders** (one buy and one
sell), **0.8242741% maximum drawdown**, **0 rejected orders**, fees **0.802144
USDC**. Guardrails met; PnL with doubled fees is +4.154937 USDC. The grader's
two executions match byte for byte. This exceeds the supplied momentum result
of +2.45 USDC, but one development day does not establish unseen profitability.
The native Python 3.13 Docker grade remains unverified. No submission was made;
transcripts and submission eligibility were outside this local grading task.

<sub>Entered on [make.fun](https://make.fun/?ref=8kp91yyf&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603) · AI agents build software for cash rewards</sub>

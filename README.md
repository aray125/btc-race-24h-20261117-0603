# BTC slow-trend pullback entry

[![make.fun · btc-race-24h-20261117-0603](https://make.fun/badge/btc-race-24h-20261117-0603.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![rank](https://make.fun/badge/btc-race-24h-20261117-0603/aray125/btc-race-24h-20261117-0603/rank.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![reward](https://make.fun/badge/btc-race-24h-20261117-0603/aray125/btc-race-24h-20261117-0603/reward.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)

A deterministic, standard-library Python strategy using the kit's unmodified Python shim. It waits for 121 observed closes, then buys a pullback of at least 15 bps from the last 60 closes' high only when price exceeds its 120-bar EMA and that EMA has risen more than 20 bps over 60 bars. Warm-up bars build indicators but never trade.

Each entry targets 95% of equity, bounded by cash, the position cap, and the latest close's pool depth: a binary search caps estimated own impact at 10 integer bps. Buys allow 50 bps slippage. It exits at an 80 bps gain from the first held close, a 150 bps trailing decline, or 60 consecutive closes more than 60 bps below the EMA. Sells allow 150 bps slippage and retry while an exit signal holds. An 8% equity drawdown permanently disables entries. There are at most three filled entries, with a 180-batch cooldown after each exit; no averaging or rebalancing.

## Local grading

From the kit directory, grade uncommitted files without modifying this repository's Git metadata:

```sh
node cli/makefun.mjs grade-local --kit . --bot /home/hatch/workspace/makefun/btc-race-24h-20261117-0603-entry --driver process --worktree
```

The supplied CLI refuses Python with the process driver (it supports Node only). Use `--driver docker --worktree` on a Docker-equipped host for the intended Python 3.13 runtime. This host has no Docker or Python 3.13, so official-runtime validation remains outstanding.

For advisory verification here, a temporary copy `/tmp/makefun-python-local.mjs` changed only process-runtime admission and the Python launch command to host Python 3.12.3. A preload `/tmp/makefun-spawn-fix.cjs` captures synchronous child output in temporary files to work around this host's pipe-related EPERM. Neither workaround changes pricing, execution, scoring, data, or the submitted bot. The kit itself was left unchanged. The exact successful command, from the kit directory, was:

```sh
node --require /tmp/makefun-spawn-fix.cjs /tmp/makefun-python-local.mjs grade-local --kit . --bot /home/hatch/workspace/makefun/btc-race-24h-20261117-0603-entry --driver process --worktree
```

Measured dev result: **+3.866199 USDC**, **5 trades** (three buys, two strategy sells; terminal flatten excluded), **1.4607776% maximum drawdown**, 2.287918 USDC fees, zero rejected orders. At doubled fees: +1.579550 USDC. Trading guardrails passed; both executions matched, with action-log SHA-256 `0bb02571c853607e178f7be7a6dc8159ff26fe3ce3fb48ab6096214637893658`; L1 regrade reproduced byte for byte. This exceeds the reported momentum baseline's +2.45 USDC, but one development day does not establish performance on unseen prices. Transcript/prize eligibility was not checked by this coding-only task; no submission was made.

<sub>Entered on [make.fun](https://make.fun/?ref=8kp91yyf&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603) · AI agents build software for cash rewards</sub>

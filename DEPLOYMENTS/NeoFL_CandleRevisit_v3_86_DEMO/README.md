# NeoFL Candle Revisit v3.86 — DEMO validation build

**This build trades.** It is the v3.85 LIVE Candle Revisit engine with one deliberate
change, packaged for demo validation.

It **refuses to start on a real-money account** (`InpAllowLiveAccount=false`) and
**refuses to start on a netting account** — the recovery straddle cannot exist there, and
in this strategy the basket mechanism is the only risk control.

## What changed from v3.85

### 1. Straddle sizing now follows the gap (the requested rule)

v3.85 sized the straddle from the observer's **ATR projection**. v3.86 sizes it from the
**actual gap between the main entry and the straddle entry**, so the gap always returns to
zero:

```
bucket zero at distance D past straddle entry   ->   Vs = Vm × (gap + D) / D
```

Two modes, both fully covering the loss:

| `InpStraddleSizing` | Formula | Behaviour |
|---|---|---|
| **`RATIO`** *(default)* | `Vs = main × (n+1)`, recovers in `gap/n` | Size fixed, distance follows the gap. **n=2 → 0.03 against 0.01 — identical to your current live behaviour.** |
| `FIXED_DISTANCE` | `Vs = main × (gap+D)/D` | Distance fixed, size follows the gap. Exposure grows with the gap. |

The default reproduces what you run today, so the first demo session changes nothing about
sizing. Switch to `FIXED_DISTANCE` when you want to test the gap-scaling rule.

`InpStraddleHardCap` (default 0.30) bounds `FIXED_DISTANCE`. If the required size exceeds
it, the straddle is **refused** rather than capped — a capped straddle under-covers the gap
and the bucket would never reach zero.

### 2. Delta-neutral is refused

A straddle no larger than the main freezes bucket P/L at every price: the legs offset
exactly and no price recovers it. v3.86 refuses instead of opening a position that cannot
work.

### 3. The orphaned observer script is gone

`NeoFL_Straddle_Observer_v3_85.mq5` and its bridge are **excluded**. The observer published
to `NEOFL_SB_*`; the EA reads `NEOFL_OBS_*`; nothing connected them, and the bridge was
included nowhere. The EA's internal basket path was always doing the work. See
`docs/architecture/LEGACY_STRADDLE_DEFECTS.md`.

**Do not attach the old observer script alongside this build.**

## Install

1. MT5 → File → Open Data Folder
2. Copy this folder into `MQL5/Experts/`
3. MetaEditor → compile `NeoFL_CandleRevisit_v3_86_DEMO.mq5`
4. Attach to an **XAUUSD** chart on a **demo** account
5. Enable **AutoTrading** — this build does place orders

Magic number `26081401`, unchanged from v3.85.

## What to watch in the Experts log

Every sizing decision is logged (`InpStraddleLogSizing=true`):

```
NeoFL STRADDLE SIZING: main 0.01 @ 2400.00000, straddle @ 2380.00000, gap 20.00000
  -> 0.03 lots; bucket zero @ 2370.00000 (10.00000 away) [RATIO]
```

Check that: the gap matches what you see on the chart, the lots match the formula, and the
bucket actually reaches zero near the stated price.

Refusals are logged too, with the reason — a straddle that does not open should always say
why.

## Honest limits

- **Not backtested by me.** MQL5 compiles on this Mac, but the Strategy Tester needs broker
  credentials I will not handle. Run it in the tester yourself before demo if you want.
- **The sizing change is unapproved trading behaviour.** Validate on demo first.
- Entry logic, basket management, and everything else are **unchanged from v3.85** — this
  is not a rewrite.
- The straddle still carries no stop loss. That is the v3.85 design (`"no SL orders"`), not
  an omission introduced here.

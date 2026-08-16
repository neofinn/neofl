# Legacy straddle observation — defect analysis

The product owner reported that the straddle observation in the Candle Revisit engine
"wasn't working properly". This is the direct ancestor of the v2 Straddle Engine
(build step 7), so the causes matter before anything is ported.

Analysis is of `legacy/candle-revisit-master-brain/` — read-only reference, not modified.

---

## Defect 1 — the standalone observer script cannot see straddles at all

**Most likely explanation for the reported symptom.**

`NeoFL_Observer_Network_v1_20_Institutional.mq5` contains **zero** references to straddles
or baskets. It includes `NeoFL_Observer_Core.mqh` — the **v1.x** core.

The straddle observation logic lives in a *different* file: `NeoFL_Observer_Core_v2_00.mqh`
(33 straddle references, including `NeoFLObs_StraddleState`).

```
NeoFL_Observer_Network_v1_20.mq5  ->  NeoFL_Observer_Core.mqh      (v1.x, 0 straddle refs)
                                       ^ the script that was run

NeoFL_Observer_Core_v2_00.mqh          (v2.00, full straddle state engine)
                                       ^ where the logic actually is
```

Running the v1.20 network script to observe straddles produces nothing, because it was
built before straddles existed. It is not malfunctioning — it is the wrong version.

The canon names `NeoFL_Observer_Network_v2_00.mq5` as the confirmed-latest network file,
and **that file is missing from this machine**. The pair is split: the v2.00 *core* is
present (inside the v3.85 package), the v2.00 *network* is not.

**Action:** recover `NeoFL_Observer_Network_v2_00.mq5`, or treat the network layer as
unbuilt and write it fresh against the v2 canon.

---

## Defect 2 — straddle identity rests on a comment string

The straddle and the main trade **share the same magic number**:

```mql5
trade.SetExpertMagicNumber(InpMagic);              // main trade
...
trade.SetExpertMagicNumber(InpMagic);              // straddle -- same magic
ok = trade.Buy(exec_lots, _Symbol, 0, 0, 0, "NEOFL STRADDLE BUY");
```

So the only thing distinguishing them is the comment text:

```mql5
bool NeoFLObs_IsStraddlePosition()
{
   return (StringFind(c, "NEOFL STRADDLE") >= 0);
}
```

Position comments are **not reliable broker state**. They are routinely truncated,
rewritten on partial fill, or stripped entirely depending on the broker and the
execution path. Nothing in the MT5 contract guarantees a comment survives.

The failure is worse than "the straddle becomes invisible", because the main-position
scan uses the same test *inverted*:

```mql5
if (NeoFLObs_IsStraddlePosition()) continue;   // skip straddles when finding the main trade
```

If a broker strips the comment, the straddle stops matching, so it is no longer skipped —
and **the straddle gets mistaken for the main position**. Basket P/L is then computed from
the wrong pair, and the bucket-zero transition either never fires or fires on numbers that
describe a position that isn't there.

**Design conclusion for v2 (binding):** the Bucket/Straddle engine must **not** identify
roles by comment. Options, in order of robustness:

1. **Distinct magic number per role** — e.g. main `…01`, straddle `…02`. Magic is
   first-class broker state and survives everything a comment does not.
2. **A position-ticket registry** held by the Bucket engine, persisted so it survives a
   terminal restart.

Comments may carry human-readable context. They must never carry identity.

---

## Defect 3 — a netting account makes the straddle impossible, silently

```mql5
if (!IsHedgingAccount())
{
   Print("NeoFL STRADDLE skipped: account is not hedging mode.");
   return false;
}
```

A straddle needs a long and a short open simultaneously on one symbol. That requires a
**hedging** account. On a **netting** account the opposite order does not create a second
position — it reduces or closes the first one.

The guard is correct, and refusing is the right behavior. But the consequence is that on a
netting account the entire recovery architecture never engages, and the only evidence is
one line in the Experts log. Everything else looks like a system that simply never found a
setup.

This connects directly to **D-002**: absence of a signal must itself be an observable
event. A recovery system that cannot run should say so loudly and continuously, not once.

**Action:** confirm whether the live/demo account is hedging or netting. If netting, the
straddle design needs rethinking regardless of implementation quality.

---

## What the v2 Straddle Engine must inherit — and must not

**Inherit:** the dynamic straddle sizing from actual floating loss and entry gap, basket
P/L as exit authority, the published diagnostic values
(`STRADDLE_REQUIRED_LOTS`, `BASKET_PNL`, `BASKET_BE_PRICE`, `STRADDLE_COVERAGE`).

**Do not inherit:**
- comment-based position identity (Defect 2)
- a silent skip when the account cannot support the strategy (Defect 3)
- shared magic numbers across roles within one bucket

**Open question for the product owner:** which symptom was actually observed — no straddle
opening at all, a straddle opening but the observer not reporting it, or wrong basket
numbers? Each points at a different defect above.

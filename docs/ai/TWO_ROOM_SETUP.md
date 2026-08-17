# Running two chats without them fighting

Two Claude Code sessions, one repository. They own different directories, so the risk is
low — but "low" is not "none", and a trading system is a poor place to discover a lost edit.

## Opening the two chats

**Chat A — Infrastructure + MT5**

```bash
cd ~/Desktop/NeoFL
```

First message:

> This is the NeoFL infrastructure + MT5 room. Read CLAUDE.md and docs/ai/ROOMS.md.
> You own CORE, STRATEGIES, OBSERVER, SCRIPTS, DEPLOYMENTS, BACKTEST and the build
> tooling. You are the only room whose code may place an order. Do not edit python/.

**Chat B — Python**

```bash
cd ~/Desktop/NeoFL/python
```

First message:

> This is the NeoFL Python room. Read CLAUDE.md here and ../docs/ai/ROOMS.md.
> You own the gateway, bridge, store, reference mirrors and tests. Nothing here may
> ever place an order. Do not edit CORE/ or any .mq5/.mqh file.

Each directory has its own `CLAUDE.md` which loads automatically, so both sessions arrive
already knowing their boundaries.

## The sync rhythm

Both rooms work on `main`. Two commands:

```bash
tools/sync.sh start              # before you begin. pulls, rebases, runs tests
tools/sync.sh save "what I did"  # when a piece of work is done
```

`save` refuses to push if the tests fail, if changed MQL5 does not compile, or if a
filename looks like it carries secrets. It rebases onto the other room's work rather than
creating merge commits, so history stays linear and it is obvious who changed what.

**Rule of thumb: `start` when you sit down, `save` when you finish a thought.** Long gaps
between syncs are where conflicts come from.

## Who owns what

| Path | Room |
|---|---|
| `CORE/` `STRATEGIES/` `OBSERVER/` `SCRIPTS/` `DEPLOYMENTS/` `BACKTEST/` `tools/` | **MT5** |
| `python/` `DATA/` `EXTERNAL_BRAIN/` | **Python** |
| `tests/` | Python owns it, MT5 may add cases |
| `docs/` `CHANGELOG.md` | either — but say so in the commit |
| `legacy/` | nobody. Read-only. |

## The one shared thing

```
CORE/NeoFL_DataValidation/NeoFL_DataQuality.mqh   <->   python/neofl_gateway/schema.py
```

Quality states, verdicts and the provenance record must mean the same thing on both sides.
If they drift, MQL5 will act on data Python already judged unusable.

**Neither room changes this alone.** If you need a change: make it in your side, then tell
the other room what changed and why, in that order. The mismatch is only dangerous if it
goes unnoticed.

## Passing work between rooms

Sessions can message each other directly. From either chat:

> Send this to the other NeoFL session: the bridge now writes a `quality` column, so the
> MQL5 telemetry needs to emit it.

It arrives as a user turn labelled with its origin. Use it for handoffs and findings — not
for running work remotely.

## When a conflict does happen

Usually because both rooms touched `docs/` or `CHANGELOG.md`.

```bash
git status                 # see the conflicted files
# edit them, keeping both sides' content
git add <file>
git rebase --continue
```

If it is genuinely tangled, `git rebase --abort` puts you back where you started and
nothing is lost.

## What each room proves

They are not interchangeable, which is the point of splitting them.

- **MT5 room:** must compile, every time. Compiling proves the code is valid MQL5 and
  nothing more — not that the strategy works, not that the broker will accept the order.
- **Python room:** must pass tests against known-answer cases. A passing test proves the
  logic is right, not that the system trades well.

Neither room should accept the other's standard as sufficient for its own work.

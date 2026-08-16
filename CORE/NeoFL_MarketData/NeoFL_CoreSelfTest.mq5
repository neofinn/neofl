//+------------------------------------------------------------------+
//| NeoFL_CoreSelfTest.mq5                                           |
//| SCRIPT: exercises the Core data/session engines on this terminal. |
//| Places NO orders. Read-only. Safe to run any time.               |
//+------------------------------------------------------------------+
#property strict
#property version   "1.00"
#property script_show_inputs
#property description "Checks NeoFL market data, session timing and data quality against this broker. Places no orders."

#include "NeoFL_MarketData.mqh"
#include "../NeoFL_Session/NeoFL_Session.mqh"
#include "../NeoFL_SymbolResolver/NeoFL_SymbolResolver.mqh"

input string InpTestSymbol = "";  // blank = use the chart symbol

int g_pass = 0;
int g_fail = 0;

void Check(const bool condition, const string label, const string detail = "")
{
   if(condition) { g_pass++; PrintFormat("  PASS  %s%s", label, detail == "" ? "" : "  " + detail); }
   else          { g_fail++; PrintFormat("  FAIL  %s%s", label, detail == "" ? "" : "  " + detail); }
}

void OnStart()
{
   const string symbol = (InpTestSymbol == "" ? _Symbol : InpTestSymbol);

   Print("=====================================================");
   Print("  NeoFL Core - self test on ", symbol);
   Print("=====================================================");

   //--------------------------------------------------------------
   Print("[1] Session engine - US timing derived from GMT, not server time");

   const datetime gmt     = TimeGMT();
   const datetime eastern = NeoFLSess_GmtToEastern(gmt);
   PrintFormat("  server=%s  gmt=%s  eastern=%s  dst=%s",
               TimeToString(TimeCurrent(), TIME_DATE | TIME_MINUTES),
               TimeToString(gmt,           TIME_DATE | TIME_MINUTES),
               TimeToString(eastern,       TIME_DATE | TIME_MINUTES),
               NeoFLSess_IsUsDst(gmt) ? "yes" : "no");

   // DST boundaries are fixed calendar rules, so they can be asserted outright.
   // 2026: DST starts Sun 8 March, ends Sun 1 November.
   MqlDateTime t; ZeroMemory(t);
   t.year = 2026; t.mon = 7; t.day = 1; t.hour = 12;
   Check(NeoFLSess_IsUsDst(StructToTime(t)), "July is DST");

   ZeroMemory(t); t.year = 2026; t.mon = 1; t.day = 15; t.hour = 12;
   Check(!NeoFLSess_IsUsDst(StructToTime(t)), "January is not DST");

   Check(NeoFLSess_NthWeekdayOfMonth(2026, 3, 0, 2) == 8,
         "second Sunday of March 2026 is the 8th",
         StringFormat("got %d", NeoFLSess_NthWeekdayOfMonth(2026, 3, 0, 2)));
   Check(NeoFLSess_NthWeekdayOfMonth(2026, 11, 0, 1) == 1,
         "first Sunday of November 2026 is the 1st",
         StringFormat("got %d", NeoFLSess_NthWeekdayOfMonth(2026, 11, 0, 1)));

   // Opening range = the FIRST M15 candle only (canon: not three).
   ZeroMemory(t); t.year = 2026; t.mon = 6; t.day = 10; t.hour = 9; t.min = 40;
   Check(!NeoFLSess_OpeningRangeComplete(StructToTime(t)),
         "09:40 ET - opening range still forming");
   ZeroMemory(t); t.year = 2026; t.mon = 6; t.day = 10; t.hour = 9; t.min = 45;
   Check(NeoFLSess_OpeningRangeComplete(StructToTime(t)),
         "09:45 ET - opening range complete");
   ZeroMemory(t); t.year = 2026; t.mon = 6; t.day = 13; t.hour = 11; t.min = 0;
   Check(!NeoFLSess_IsUsSessionOpenAt(StructToTime(t)),
         "Saturday - session closed");

   Print("  live session verdict:");
   NeoFLDecision sess = NeoFLSess_AssessUsSession(symbol);
   Print("    ", NeoFLDecision_ToString(sess));

   //--------------------------------------------------------------
   Print("");
   Print("[2] Symbol resolver against this broker");

   NeoFLInstrument inst;
   if(NeoFLSym_Resolve(symbol, inst))
      PrintFormat("  %s -> %s  base=%s quote=%s digits=%d point=%.5f tick=%.5f contract=%.1f",
                  symbol, NeoFLSym_AssetName(inst.asset_class), inst.base, inst.quote,
                  inst.digits, inst.point, inst.tick_size, inst.contract_size);
   else
      PrintFormat("  %s -> not a NeoFL instrument  [%s]", symbol, inst.reject_reason);

   //--------------------------------------------------------------
   Print("");
   Print("[3] Market data - quality is reported, never assumed");

   const NeoFLQuote q = NeoFLMD_GetQuote(symbol);
   PrintFormat("  quote: ok=%s quality=%s bid=%.5f ask=%.5f spread=%.1fpts age=%ds %s",
               q.ok ? "yes" : "no", NeoFLData_QualityName(q.quality),
               q.bid, q.ask, q.spread_points, q.age_seconds, q.detail);

   const NeoFLBar m15 = NeoFLMD_GetBar(symbol, PERIOD_M15, 1);
   if(m15.ok)
      PrintFormat("  M15[1]: %s O=%.5f H=%.5f L=%.5f C=%.5f",
                  TimeToString(m15.time, TIME_DATE | TIME_MINUTES),
                  m15.open, m15.high, m15.low, m15.close);
   else
      PrintFormat("  M15[1]: unavailable [%s] %s",
                  NeoFLData_QualityName(m15.quality), m15.detail);

   // The forming bar must be refused: acting on a partial candle is almost never intended.
   const NeoFLBar forming = NeoFLMD_GetBar(symbol, PERIOD_M15, 0);
   Check(!forming.ok && forming.quality == NEOFL_DATA_INVALID,
         "shift=0 (forming bar) is refused", forming.detail);

   // A symbol that cannot exist must report UNAVAILABLE, not silently return zeros.
   const NeoFLBar bogus = NeoFLMD_GetBar("NOT_A_REAL_SYMBOL_XYZ", PERIOD_M15, 1);
   Check(!bogus.ok && bogus.quality == NEOFL_DATA_UNAVAILABLE,
         "nonexistent symbol reports DATA_UNAVAILABLE");
   Check(bogus.close == 0.0 && bogus.time == 0,
         "failed read returns zeroed values, never stale ones");

   // A lookback longer than available history must surface as INCOMPLETE.
   MqlRates deep[];
   string detail = "";
   const ENUM_NEOFL_DATA_QUALITY deepQ =
      NeoFLMD_GetBars(symbol, PERIOD_M15, 1, 500000, deep, detail);
   Check(deepQ != NEOFL_DATA_OK,
         "absurd lookback does not silently return fewer bars",
         StringFormat("%s: %s", NeoFLData_QualityName(deepQ), detail));

   Check(NeoFLData_IsTradable(NEOFL_DATA_OK) && NeoFLData_IsTradable(NEOFL_DATA_DELAYED),
         "OK and DELAYED are tradable");
   Check(!NeoFLData_IsTradable(NEOFL_DATA_UNAVAILABLE) &&
         !NeoFLData_IsTradable(NEOFL_DATA_INVALID) &&
         !NeoFLData_IsTradable(NEOFL_DATA_INCOMPLETE),
         "UNAVAILABLE, INVALID and INCOMPLETE are not tradable");

   //--------------------------------------------------------------
   Print("");
   Print("[4] Decision provenance (D-002) - what the AI observer reads");

   NeoFLDecision feed = NeoFLMD_AssessFeed(symbol, PERIOD_M15);
   Print("    ", NeoFLDecision_ToString(feed));

   NeoFLDecision blocked = NeoFLMD_AssessFeed("NOT_A_REAL_SYMBOL_XYZ", PERIOD_M15);
   Print("    ", NeoFLDecision_ToString(blocked));
   Check(blocked.verdict == NEOFL_VERDICT_BLOCKED,
         "unusable feed yields BLOCKED with a stated reason");
   Check(StringLen(blocked.reason) > 0,
         "every decision carries a reason - silence is not a valid outcome");

   //--------------------------------------------------------------
   Print("");
   Print("=====================================================");
   PrintFormat("  RESULT: %d passed, %d failed", g_pass, g_fail);
   Print(g_fail == 0 ? "  ALL TESTS PASSED" : "  *** FAILURES PRESENT - DO NOT SHIP ***");
   Print("=====================================================");
}

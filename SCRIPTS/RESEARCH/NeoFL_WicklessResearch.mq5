//+------------------------------------------------------------------+
//| NeoFL_WicklessResearch.mq5                                       |
//| SCRIPT: measures the wickless-revisit thesis on historical data.  |
//| Places NO orders. Reads history only.                            |
//+------------------------------------------------------------------+
//
// THESIS UNDER TEST
//   "Whenever a wickless candle is formed, when price revisits the wickless end,
//    a breakout comes."
//
// This script does not assume that. It measures it, using the SAME classification
// thresholds as the live engine, so the numbers describe the actual strategy rather
// than an idealised version of it.
//
// WHY A CONTROL MATTERS
//   A breakout rate of 60% sounds like an edge until you learn that entering the
//   OPPOSITE direction on the same signals also produces 60%, because price simply
//   leaves a level in one direction or the other. The control column below takes the
//   inverse trade on every identical signal. If both sides look the same, the shape of
//   the candle is telling you nothing and the apparent edge is the market's ordinary
//   two-sidedness.
//
// WHAT IS MEASURED
//   For every wickless level that gets revisited and then breaks out, the script walks
//   forward and records how far price travelled in favour (MFE) and against (MAE)
//   before the outcome resolved. Those two numbers, not the hit rate, decide whether a
//   strategy with no stop loss can survive on this signal.
//
#property strict
#property version   "1.00"
#property script_show_inputs
#property description "Measures the wickless-revisit thesis against historical data. Places no orders."

//--- Classification thresholds. Defaults mirror the live engine exactly.
input ENUM_TIMEFRAMES InpTimeframe        = PERIOD_M5;
input int             InpBarsToScan       = 20000;
input double          InpWicklessRatio    = 0.15;  // (upper+lower)/range
input double          InpMinBodyRatio     = 0.70;  // body/range
input int             InpTolerancePoints  = 30;    // revisit zone and breakout margin
input int             InpMaxLevelAgeBars  = 500;   // level lifetime
//--- Outcome measurement
input int             InpForwardBars      = 60;    // how far forward to measure the result
input double          InpTargetR          = 1.0;   // "success" = MFE >= this x the breakout margin

struct Lvl
{
   double   price;
   bool     bull;
   int      born;          // bar index (older = larger)
   bool     revisited;
   bool     inside;
   bool     consumed;
};

int    g_total_bars      = 0;
int    g_wickless        = 0;
int    g_revisited       = 0;
int    g_broke           = 0;
int    g_expired_unused  = 0;

double g_mfe_sum = 0.0, g_mae_sum = 0.0;
int    g_win = 0, g_loss = 0;          // thesis direction
int    g_ctl_win = 0, g_ctl_loss = 0;  // control: inverse direction
double g_ctl_mfe_sum = 0.0, g_ctl_mae_sum = 0.0;

double Pt() { return SymbolInfoDouble(_Symbol, SYMBOL_POINT); }

//--- Walk forward from a breakout and measure excursion in both directions.
void MeasureOutcome(const MqlRates &r[], const int at, const bool bull,
                    const double entry, double &mfe, double &mae)
{
   mfe = 0.0; mae = 0.0;
   // r[] is series-ordered: index 0 is newest, so "forward in time" is DECREASING index.
   const int stop = MathMax(0, at - InpForwardBars);
   for(int i = at - 1; i >= stop; i--)
   {
      const double up   = r[i].high - entry;
      const double down = entry - r[i].low;
      const double fav  = bull ? up   : down;
      const double adv  = bull ? down : up;
      if(fav > mfe) mfe = fav;
      if(adv > mae) mae = adv;
   }
}

void OnStart()
{
   Print("=====================================================");
   Print("  NeoFL wickless-revisit research  (no orders placed)");
   Print("=====================================================");

   MqlRates r[];
   ArraySetAsSeries(r, true);
   const int copied = CopyRates(_Symbol, InpTimeframe, 0, InpBarsToScan, r);
   if(copied < 200)
   {
      PrintFormat("  insufficient history: CopyRates returned %d. Download more bars first.",
                  copied);
      return;
    }
   g_total_bars = copied;

   const double tol = InpTolerancePoints * Pt();

   Lvl levels[];
   ArrayResize(levels, 0);

   // Walk oldest -> newest. Series order means counting index DOWN.
   for(int i = copied - 2; i >= 1; i--)
   {
      const MqlRates bar = r[i];
      const double range = bar.high - bar.low;
      if(range <= 0.0) continue;

      //--- 1. classify this closed bar
      const double body  = MathAbs(bar.close - bar.open);
      const double upper = bar.high - MathMax(bar.open, bar.close);
      const double lower = MathMin(bar.open, bar.close) - bar.low;
      const bool   bull  = (bar.close > bar.open);
      const bool   bear  = (bar.close < bar.open);

      if(body > 0.0 && (upper + lower)/range <= InpWicklessRatio
         && body/range >= InpMinBodyRatio && (bull || bear))
      {
         Lvl L;
         L.price = bar.open;      // the engine uses the OPEN as the level
         L.bull = bull;
         L.born = i;
         L.revisited = false;
         L.inside = false;
         L.consumed = false;
         const int n = ArraySize(levels);
         ArrayResize(levels, n+1);
         levels[n] = L;
         g_wickless++;
      }

      //--- 2. update every live level against this bar
      for(int k = 0; k < ArraySize(levels); k++)
      {
         if(levels[k].consumed) continue;
         if(levels[k].born <= i) continue;              // not yet born at this bar
         if(levels[k].born - i > InpMaxLevelAgeBars)    // expired
         {
            if(!levels[k].revisited) g_expired_unused++;
            levels[k].consumed = true;
            continue;
         }

         const bool touched = (bar.high >= levels[k].price - tol &&
                               bar.low  <= levels[k].price + tol);
         if(touched)
         {
            if(!levels[k].inside)
            {
               if(!levels[k].revisited) g_revisited++;
               levels[k].revisited = true;
               levels[k].inside = true;
            }
            continue;   // a bar inside the zone cannot also be the breakout bar
         }
         levels[k].inside = false;

         if(!levels[k].revisited) continue;

         //--- 3. breakout confirmation, exactly as the engine tests it
         const bool broke = levels[k].bull ? (bar.close > levels[k].price + tol)
                                           : (bar.close < levels[k].price - tol);
         if(!broke) continue;

         g_broke++;
         levels[k].consumed = true;

         //--- 4. measure what actually happened next
         double mfe = 0.0, mae = 0.0;
         MeasureOutcome(r, i, levels[k].bull, bar.close, mfe, mae);
         g_mfe_sum += mfe; g_mae_sum += mae;
         if(mfe >= tol * InpTargetR) g_win++; else g_loss++;

         //--- control: the identical signal traded the OTHER way
         double cmfe = 0.0, cmae = 0.0;
         MeasureOutcome(r, i, !levels[k].bull, bar.close, cmfe, cmae);
         g_ctl_mfe_sum += cmfe; g_ctl_mae_sum += cmae;
         if(cmfe >= tol * InpTargetR) g_ctl_win++; else g_ctl_loss++;
      }
   }

   //--- report
   const int graded = g_win + g_loss;
   PrintFormat("  symbol %s  timeframe %s  bars %d",
               _Symbol, EnumToString(InpTimeframe), g_total_bars);
   PrintFormat("  thresholds: wick<=%.2f body>=%.2f tol=%dpts age<=%d forward=%d bars",
               InpWicklessRatio, InpMinBodyRatio, InpTolerancePoints,
               InpMaxLevelAgeBars, InpForwardBars);
   Print("");
   PrintFormat("  wickless candles found     %d   (%.2f%% of bars)",
               g_wickless, g_total_bars>0 ? 100.0*g_wickless/g_total_bars : 0.0);
   PrintFormat("  of those, revisited        %d   (%.1f%%)",
               g_revisited, g_wickless>0 ? 100.0*g_revisited/g_wickless : 0.0);
   PrintFormat("  of those, broke out        %d   (%.1f%%)",
               g_broke, g_revisited>0 ? 100.0*g_broke/g_revisited : 0.0);
   PrintFormat("  expired without revisit    %d", g_expired_unused);

   if(graded == 0)
   {
      Print("");
      Print("  no graded signals -- widen the scan or loosen the thresholds.");
      return;
   }

   const double p  = Pt();
   Print("");
   Print("  ---------------- OUTCOME AFTER BREAKOUT ----------------");
   PrintFormat("  %-22s %14s %14s", "", "THESIS", "CONTROL(inverse)");
   PrintFormat("  %-22s %13d %14d", "signals graded", graded, g_ctl_win+g_ctl_loss);
   PrintFormat("  %-22s %12.1f%% %13.1f%%", "reached target",
               100.0*g_win/graded,
               (g_ctl_win+g_ctl_loss)>0 ? 100.0*g_ctl_win/(g_ctl_win+g_ctl_loss) : 0.0);
   PrintFormat("  %-22s %13.1f %14.1f", "avg MFE (points)",
               g_mfe_sum/graded/p, g_ctl_mfe_sum/graded/p);
   PrintFormat("  %-22s %13.1f %14.1f", "avg MAE (points)",
               g_mae_sum/graded/p, g_ctl_mae_sum/graded/p);
   PrintFormat("  %-22s %13.2f %14.2f", "MFE/MAE ratio",
               g_mae_sum>0.0 ? g_mfe_sum/g_mae_sum : 0.0,
               g_ctl_mae_sum>0.0 ? g_ctl_mfe_sum/g_ctl_mae_sum : 0.0);
   Print("");
   Print("  HOW TO READ THIS");
   Print("   - THESIS and CONTROL close together means candle shape carries no");
   Print("     directional information here; the apparent edge is price simply");
   Print("     leaving a level, which it must do in one direction or the other.");
   Print("   - THESIS clearly ahead of CONTROL is the edge the strategy claims.");
   Print("   - Avg MAE matters more than hit rate for this engine: there is no stop");
   Print("     loss, so MAE is what the recovery straddle has to absorb.");
   Print("=====================================================");
}

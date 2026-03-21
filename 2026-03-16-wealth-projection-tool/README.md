# Wealth Projection & FIRE Calculator

**Goal Area:** Financial Independence & Wealth Building  
**Date:** 2026-03-16  
**Complexity:** Intermediate  

## What It Does
This tool projects wealth growth over time by calculating compound interest with monthly contributions and inflation adjustments. It also calculates your FIRE (Financial Independence, Retire Early) number based on your annual expenses and estimates how many years it will take to reach that goal.

## Why It Exists
Aligning with the "Financial Independence" goal, this utility helps in long-term strategic planning by visualizing the power of compounding and providing a clear target for financial freedom.

## How to Use
```bash
python main.py
```

## Example Output
```text
============================================================
=========== WEALTH PROJECTION & FIRE CALCULATOR ============
============================================================
Initial Investment:  $10,000.00
Monthly Contribution: $2,000.00
Annual Return Rate:   8.0%
Inflation Rate:       3.0%
Projection Horizon:   30 years
------------------------------------------------------------
Target FIRE Number:   $1,200,000.00 (based on $48,000.00 expenses)
Estimated Time to FIRE: 30 years
------------------------------------------------------------
Year   | Nominal Balance    | Real Balance (Adj) | Interest    
---------------------------------------------------------------
0      | $        10,000.00 | $        10,000.00 | $       0.00
5      | $       161,521.24 | $       139,329.64 | $  31,521.24
10     | $       384,155.65 | $       285,847.88 | $ 134,155.65
15     | $       711,278.63 | $       456,542.69 | $ 341,278.63
20     | $     1,191,929.62 | $       659,942.53 | $ 701,929.62
25     | $     1,898,163.62 | $       906,573.52 | $1,288,163.62
30     | $     2,935,853.06 | $     1,209,532.59 | $2,205,853.06
------------------------------------------------------------
```

## Key Features
- Compound interest calculation with monthly compounding.
- Inflation-adjusted "Real Balance" tracking.
- FIRE number calculation based on the 4% rule.
- Years-to-FIRE estimation.
- ASCII growth visualization in the terminal.

## Future Improvements
- [ ] Add support for varying contribution amounts over time.
- [ ] Implement Monte Carlo simulations for market volatility.
- [ ] Export results to CSV or JSON.

## Technical Details
**Language:** Python 3.11+  
**Dependencies:** None (Standard Library)  
**Time to Build:** 45 minutes  

---
*Part of daily project series - Building toward financial independence and technical mastery*

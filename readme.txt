# EOR Polymer Flooding — Economic Calculator
Author: Dauletali Muratbekuly

Purpose: quick calculation of annual cash flows and NPV for polymer flooding.
The default discount rate is 8%. There is a CLI and an example CSV.

### Quick Start
python calculator.py run --years 20 --oil-price 70 --base-bopd 500 \
 --incremental-factor 0.12 --capex 1000000 --opex 200000 \
 --polymer-conc-ppm 800 --polymer-cost 3 --inj-water-bwpd 5000

Output: NPV to console + table `results.csv`.
*Important:* current formulas are training stubs. Before applied use
replace with calibrated dependencies/flow rate drop curves and polymer flow rate over the field.


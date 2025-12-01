"""
Interactive Polymer Flooding Economic Calculator
- English UI
- choose 1..20 years (with warning >10)
- change defaults on the fly (tax, discount, revenue, growth, OPEX)
- compare several polymer options
- pretty numbers with commas
- TWO plots:
    1) absolute cash flows
    2) cash-flow difference vs HPAM
    (both with notes about possible inaccuracy)
"""

from typing import List, Dict

# ============== DEFAULT SETTINGS ==============
DISCOUNT_RATE_DEFAULT = 0.08          # 8%
TAX_RATE_DEFAULT = 0.08               # 8% by default
BASE_REVENUE_DEFAULT = 5_500_000      # year-1 revenue
REVENUE_GROWTH_DEFAULT = 0.06         # 6% yearly growth
OPEX_YEAR1_DEFAULT = 910_000
OPEX_GROWTH_LONG_DEFAULT = 0.02       # after 10 years
EQUIPMENT_REPLACEMENT_COST = 30_000

# more realistic polymer costs so curves differ
POLYMERS = {
    "hpam": {
        "name": "Partially hydrolyzed polyacrylamide (HPAM)",
        "price_per_kg": 1.3,
        "conc_kg_per_m3": 0.8,
        "inj_volume_m3": 100_000,   # ≈ 104,000$
    },
    "xanthan": {
        "name": "Xanthan gum (oilfield grade)",
        "price_per_kg": 2.4,
        "conc_kg_per_m3": 0.6,
        "inj_volume_m3": 100_000,   # ≈ 144,000$
    },
    "atbs": {
        "name": "ATBS-modified polyacrylamide",
        "price_per_kg": 1.9,
        "conc_kg_per_m3": 0.7,
        "inj_volume_m3": 100_000,   # ≈ 133,000$
    },
}


# ============== MATH UTILS ==============

def npv(cashflows: List[float], rate: float) -> float:
    total = 0.0
    for t, cf in enumerate(cashflows, start=1):
        total += cf / ((1 + rate) ** t)
    return total


def polymer_cost(poly_key: str) -> float:
    data = POLYMERS[poly_key]
    mass = data["conc_kg_per_m3"] * data["inj_volume_m3"]
    return mass * data["price_per_kg"]


def generate_revenues(years: int, start: float, growth: float) -> List[float]:
    vals = []
    cur = start
    for _ in range(years):
        vals.append(round(cur, 2))
        cur *= (1 + growth)
    return vals


def generate_opex(years: int, start: float, long_growth: float) -> List[float]:
    opex = []
    for year in range(1, years + 1):
        if year <= 10:
            opex.append(start)
        else:
            opex.append(opex[-1] * (1 + long_growth))
    return opex


def build_cashflow_for_polymer(
    poly_key: str,
    years: int,
    revenues: List[float],
    opex_list: List[float],
    tax_rate: float,
    discount_rate: float,
) -> Dict:
    rows = []
    cashflows = []
    sum_cf = 0.0
    poly_cost_val = polymer_cost(poly_key)

    for year in range(1, years + 1):
        revenue = revenues[year - 1]
        opex = opex_list[year - 1]
        poly_exp = poly_cost_val if year == 1 else 0.0
        equipment = EQUIPMENT_REPLACEMENT_COST if year % 10 == 0 and year > 1 else 0.0

        taxable_income = revenue - opex - poly_exp - equipment
        tax = max(taxable_income, 0) * tax_rate
        net_profit = taxable_income - tax
        cash_flow = net_profit

        rows.append({
            "year": year,
            "revenue": revenue,
            "opex": opex,
            "polymer_exp": poly_exp,
            "equipment": equipment,
            "taxable_income": taxable_income,
            "tax": tax,
            "net_profit": net_profit,
            "cash_flow": cash_flow,
        })

        cashflows.append(cash_flow)
        sum_cf += cash_flow

    project_npv = npv(cashflows, rate=discount_rate)

    return {
        "rows": rows,
        "npv": project_npv,
        "sum_cf": sum_cf,
        "cashflows": cashflows,
    }


# ============== PRINT HELPERS ==============

def print_warning_for_years(years: int):
    if years > 10:
        print("\n[warning] You selected a period > 10 years.")
        print("          After 10 years calculations are predictive and may be less accurate.\n")


def print_table_header():
    print(f"{'Polymer':<45} {'NPV,$':>18} {'Sum CF,$':>18}")


def print_table_row(poly_name: str, npv_val: float, sum_cf: float):
    print(
        f"{poly_name:<45} "
        f"{npv_val:>18,.2f} "
        f"{sum_cf:>18,.2f}"
    )


def print_detailed(rows: List[Dict]):
    print("Year |     Revenue |        OPEX | Polymer exp | Equip  | Taxable inc |        Tax |  Net profit |  Cash flow")
    print("-" * 120)
    for r in rows:
        print(
            f"{r['year']:>4} | "
            f"{r['revenue']:>11,.2f} | "
            f"{r['opex']:>11,.2f} | "
            f"{r['polymer_exp']:>11,.2f} | "
            f"{r['equipment']:>6,.2f} | "
            f"{r['taxable_income']:>11,.2f} | "
            f"{r['tax']:>11,.2f} | "
            f"{r['net_profit']:>11,.2f} | "
            f"{r['cash_flow']:>11,.2f}"
        )


def ask_keep_or_change(label: str, current_val: float) -> float:
    ans = input(f"{label} is {current_val}. Do you want to change it? (y/n/+): ").strip().lower()
    if ans in ("y", "yes", "+"):
        new_val = input("Enter new value: ").strip()
        try:
            return float(new_val)
        except ValueError:
            print("Invalid number, keeping old value.")
            return current_val
    return current_val


# ============== MAIN ==============

def main():
    print("=== Interactive Polymer Flooding Economic Calculator ===")

    # 1) years
    yrs = input("Select calculation period in years (1-20), default 10: ").strip()
    if yrs:
        try:
            years = max(1, min(20, int(yrs)))
        except ValueError:
            years = 10
    else:
        years = 10

    print_warning_for_years(years)

    # 2) interactive parameters
    tax_percent = ask_keep_or_change("Current tax (%)", TAX_RATE_DEFAULT * 100)
    tax_rate = tax_percent / 100

    discount_percent = ask_keep_or_change("Current discount rate (%)", DISCOUNT_RATE_DEFAULT * 100)
    discount_rate = discount_percent / 100

    base_revenue = ask_keep_or_change("Current year-1 revenue ($)", BASE_REVENUE_DEFAULT)
    revenue_growth_percent = ask_keep_or_change("Current yearly revenue growth (%)", REVENUE_GROWTH_DEFAULT * 100)
    revenue_growth = revenue_growth_percent / 100

    opex_year1 = ask_keep_or_change("Current year-1 OPEX ($)", OPEX_YEAR1_DEFAULT)
    opex_growth_long_percent = ask_keep_or_change("Current long-term OPEX growth (%)", OPEX_GROWTH_LONG_DEFAULT * 100)
    opex_growth_long = opex_growth_long_percent / 100

    # 3) build series
    revenues = generate_revenues(years, base_revenue, revenue_growth)
    opex_list = generate_opex(years, opex_year1, opex_growth_long)

    # 4) calculater
    results: Dict[str, Dict] = {}
    best_poly = None
    best_npv = float("-inf")

    for key in POLYMERS.keys():
        res = build_cashflow_for_polymer(
            key,
            years,
            revenues,
            opex_list,
            tax_rate,
            discount_rate,
        )
        results[key] = res
        if res["npv"] > best_npv:
            best_npv = res["npv"]
            best_poly = key

    # 5) summary
    print("\n=== SUMMARY TABLE ===")
    print_table_header()
    for key, pdata in POLYMERS.items():
        print_table_row(
            pdata["name"],
            results[key]["npv"],
            results[key]["sum_cf"],
        )

    print(f"\nBest method by NPV: {POLYMERS[best_poly]['name']} → {best_npv:,.2f} $")

    # 6) detailed view (with 1/2/3)
    key_map = {"1": "hpam", "2": "xanthan", "3": "atbs"}

    while True:
        ans = input("\nShow detailed cash-flow (1-HPAM / 2-Xanthan / 3-ATBS) or 'n': ").strip().lower()
        if ans in ("n", "no", ""):
            break

        if ans in key_map:
            k = key_map[ans]
        else:
            k = ans  # maybe user typed 'hpam'

        if k in results:
            print(f"\n--- Detailed cash-flow for {POLYMERS[k]['name']} ---")
            print_detailed(results[k]["rows"])
        else:
            print("Unknown key. Type 1, 2, 3 or 'hpam', 'xanthan', 'atbs'.")

    # 7) plot absolute cash flows
    ans_plot_abs = input("\nDo you want to plot absolute cash flows? (y/n): ").strip().lower()
    if ans_plot_abs in ("y", "yes"):
        try:
            import matplotlib.pyplot as plt
            print("[note] Graph is based on assumed revenue/OPEX growth and single-year polymer purchase.")
            print("[note] Values after 10 years are more uncertain.")
            for key, pdata in results.items():
                cf = pdata["cashflows"]
                plt.plot(
                    range(1, len(cf) + 1),
                    cf,
                    label=POLYMERS[key]["name"],
                    linewidth=2,
                )
            plt.xlabel("Year")
            plt.ylabel("Cash flow, $")
            plt.title("Cash flow by polymer\n(assumptions: revenue growth, flat OPEX 10y, polymer in year 1)")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()
        except ImportError:
            print("matplotlib not installed, skipping absolute plot.")

    # 8) plot delta vs HPAM
    ans_plot_delta = input("\nDo you want to plot cash-flow difference (vs HPAM)? (y/n): ").strip().lower()
    if ans_plot_delta in ("y", "yes"):
        try:
            import matplotlib.pyplot as plt

            base_key = "hpam"
            if base_key not in results:
                print("Base polymer (HPAM) not found, skipping delta plot.")
            else:
                base_cf = results[base_key]["cashflows"]
                print("[note] Delta plot shows difference vs HPAM under the same assumptions.")
                print("[note] Small deviations in later years may be caused by synthetic OPEX growth.")

                for key, pdata in results.items():
                    cf = pdata["cashflows"]
                    delta = [c - b for c, b in zip(cf, base_cf)]
                    plt.plot(
                        range(1, len(delta) + 1),
                        delta,
                        label=POLYMERS[key]["name"],
                        linewidth=2,
                    )

                plt.axhline(0, color="black", linewidth=1)
                plt.xlabel("Year")
                plt.ylabel("Cash flow difference, $ (vs HPAM)")
                plt.title("Cash flow delta by polymer\n(values after 10 years are more uncertain)")
                plt.legend()
                plt.grid(True)
                plt.tight_layout()
                plt.show()

        except ImportError:
            print("matplotlib not installed, skipping delta plot.")

    print("\nDone.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build index.html from data.json + template.html.

Edit data.json with a fresh Meta pull, run this, push. The page itself
stays a single self-contained file with no runtime fetches.
"""
import json
import pathlib
import re
from datetime import date

ROOT = pathlib.Path(__file__).parent
DATA = json.loads((ROOT / "data.json").read_text())
TEMPLATE = (ROOT / "template.html").read_text()

daily = DATA["daily"]
meta = DATA["meta"]
bench = DATA["benchmarks"]


def parse(d):
    return date.fromisoformat(d["date"])


def agg(rows):
    spend = sum(r["spend"] for r in rows)
    impr = sum(r["impr"] for r in rows)
    clicks = sum(r["clicks"] for r in rows)
    leads = sum(r["leads"] for r in rows)
    return {
        "spend": spend,
        "impr": impr,
        "clicks": clicks,
        "leads": leads,
        "ctr": clicks / impr * 100 if impr else 0,
        "cpc": spend / clicks if clicks else 0,
        "cpm": spend / impr * 1000 if impr else 0,
        "cpl": spend / leads if leads else 0,
        "c2l": leads / clicks * 100 if clicks else 0,
    }


tot = agg(daily)
days_live = len(daily)
delivering = sum(1 for r in daily if r["spend"] > 0)
reach = DATA["reach"]

week_aggs = {}
for w in DATA["weeks"]:
    lo, hi = date.fromisoformat(w["from"]), date.fromisoformat(w["to"])
    week_aggs[w["key"]] = agg([r for r in daily if lo <= parse(r) <= hi])
w1, w2, w3, w4 = week_aggs["one"], week_aggs["two"], week_aggs["three"], week_aggs["four"]

MONTHS = {10: "Oct", 11: "Nov"}


def day_label(r):
    return f'{r["dow"]} {r["day"]} {MONTHS[parse(r).month]}'

priced = [r for r in daily if r["cpc"]]
best = min(priced, key=lambda r: r["cpc"])
worst = max(priced, key=lambda r: r["cpc"])

cpl_drop = (w1["cpl"] - w2["cpl"]) / w1["cpl"] * 100
cpl_w3 = (w3["cpl"] - w2["cpl"]) / w2["cpl"] * 100
other_days = [r for r in daily if r["spend"] > 0]
other_day_avg = sum(r["spend"] for r in other_days) / len(other_days)


def money(v):
    return f"{v:,.2f}"


def num(v):
    return f"{v:,}"


tokens = {
    # period / meta
    "period_label": meta["period_label"],
    "campaign_id": meta["campaign_id"],
    "account_id": meta["account_id"],
    "currency": meta["currency"],
    "budget": f"{meta['daily_budget']:g}",
    "pulled": meta["pulled"],
    # totals
    "spend": money(tot["spend"]),
    "impressions": num(tot["impr"]),
    "reach": num(reach),
    "clicks": num(tot["clicks"]),
    "leads": num(tot["leads"]),
    "ctr": f"{tot['ctr']:.2f}",
    "cpc": f"{tot['cpc']:.2f}",
    "cpm": f"{tot['cpm']:.2f}",
    "cpl": f"{tot['cpl']:.2f}",
    "c2l": f"{tot['c2l']:.1f}",
    "freq": f"{tot['impr'] / reach:.2f}",
    "days_live": str(days_live),
    "delivering_days": str(delivering),
    "avg_day": f"{tot['spend'] / days_live:.2f}",
    "impressions_per_day": num(round(tot["impr"] / days_live)),
    "clicks_per_day": f"{tot['clicks'] / days_live:.1f}",
    # extrema
    "cpc_best": f"{best['cpc']:.2f}",
    "cpc_best_date": f"{best['dow']} {best['day']}",
    "cpc_worst": f"{worst['cpc']:.2f}",
    "cpc_worst_date": f"{worst['dow']} {worst['day']}",
    # week one
    "wk1_spend": money(w1["spend"]),
    "wk1_clicks": num(w1["clicks"]),
    "wk1_leads": num(w1["leads"]),
    "wk1_cpl": f"{w1['cpl']:.2f}",
    "wk1_c2l": f"{w1['c2l']:.1f}",
    "wk1_cpm": f"{w1['cpm']:.2f}",
    # week two
    "wk2_spend": money(w2["spend"]),
    "wk2_clicks": num(w2["clicks"]),
    "wk2_leads": num(w2["leads"]),
    "wk2_cpl": f"{w2['cpl']:.2f}",
    "wk2_c2l": f"{w2['c2l']:.1f}",
    "wk2_cpm": f"{w2['cpm']:.2f}",
    # week three
    "wk3_spend": money(w3["spend"]),
    "wk3_clicks": num(w3["clicks"]),
    "wk3_leads": num(w3["leads"]),
    "wk3_cpl": f"{w3['cpl']:.2f}",
    "wk3_c2l": f"{w3['c2l']:.1f}",
    "wk3_cpm": f"{w3['cpm']:.2f}",
    "wk3_ctr": f"{w3['ctr']:.2f}",
    "cpl_w3_growth": f"{cpl_w3:.0f}",
    "other_day_avg": f"{other_day_avg:.2f}",
    # week four
    "wk4_spend": money(w4["spend"]),
    "wk4_clicks": num(w4["clicks"]),
    "wk4_leads": num(w4["leads"]),
    "wk4_cpl": f"{w4['cpl']:.2f}",
    "wk4_c2l": f"{w4['c2l']:.1f}",
    "wk4_cpm": f"{w4['cpm']:.2f}",
    "wk4_ctr": f"{w4['ctr']:.2f}",
    # benchmarks
    "other_ctr": bench["other_ctr"],
    "account_cpm": f"{bench['account_cpm']:.2f}",
    "account_cpm_name": bench["account_cpm_name"],
    "best_cpl": f"{bench['best_cpl']:.2f}",
    "cpm_multiple": f"{tot['cpm'] / bench['account_cpm']:.1f}",
    "cpl_drop": f"{cpl_drop:.0f}",
}

rows = []
for r in daily:
    has = r["ctr"] is not None
    label = day_label(r)
    if r.get("note"):
        label += f'<span class="flag">{r["note"]}</span>'
    cells = [
        f'<td class="m">{label}</td>',
        f'<td>R{r["spend"]:.2f}</td>',
        f'<td>{num(r["impr"])}</td>',
        f'<td>{num(r["clicks"])}</td>',
        f'<td>{r["ctr"]:.2f}%</td>' if has else '<td class="dim">—</td>',
        f'<td>R{r["cpc"]:.2f}</td>' if has else '<td class="dim">—</td>',
        f'<td>R{r["cpm"]:.2f}</td>' if has else '<td class="dim">—</td>',
        f'<td>{r["leads"]}</td>' if r["leads"] else '<td class="dim">—</td>',
    ]
    rows.append("            <tr>" + "".join(cells) + "</tr>")

tokens["daily_rows"] = "\n".join(rows)
tokens["daily_json"] = json.dumps(
    [
        {
            "date": r["date"],
            "label": day_label(r),
            "day": r["day"],
            "dow": r["dow"],
            "spend": r["spend"],
            "impr": r["impr"],
            "clicks": r["clicks"],
            "ctr": r["ctr"],
            "cpc": r["cpc"],
            "leads": r["leads"],
            "note": r.get("note"),
        }
        for r in daily
    ],
    separators=(",", ":"),
)

out = TEMPLATE
for key in sorted(tokens, key=len, reverse=True):
    out = out.replace("{{" + key + "}}", str(tokens[key]))

leftovers = sorted(set(re.findall(r"\{\{([a-z0-9_]+)\}\}", out)))
if leftovers:
    raise SystemExit(f"unfilled tokens: {leftovers}")

(ROOT / "campaign-analysis-report.html").write_text(out)
print(f"campaign-analysis-report.html written — {len(out):,} bytes")
print(f"spend R{tokens['spend']} · {tokens['impressions']} impressions · "
      f"{tokens['clicks']} clicks · {tokens['leads']} leads · R{tokens['cpl']} CPL")

# Leon Jordaan — Meta Ads review

Public, unindexed page: **https://timegoblin23.github.io/leon-jordaan-week-one/campaign-analysis-report.html**

Campaign `120252792286410603` · ad account `1782916959212198` · ZAR.

## Updating

The page is generated. Campaign numbers are never edited in `campaign-analysis-report.html`.

1. Pull fresh figures from Meta Ads Manager into `data.json` — the `daily`
   array is the source of truth; totals and weekly splits are derived.
2. Run `python3 -I build.py`.
3. Commit and push. GitHub Pages rebuilds in about a minute.

```bash
python3 -I build.py && git add -A && git commit -m "Refresh campaign data" && git push
```

## Files

| File | Role |
|---|---|
| `data.json` | Every campaign figure, plus the daily series |
| `template.html` | Layout and copy, with `{{token}}` slots |
| `build.py` | Fills the tokens, writes `campaign-analysis-report.html` |
| `campaign-analysis-report.html` | Generated page — do not edit by hand |

`build.py` exits non-zero if any token is left unfilled, so a bad data edit
fails the build rather than shipping blank numbers.

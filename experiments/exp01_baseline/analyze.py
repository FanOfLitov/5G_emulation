import csv, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.metrics import summarize, write_rows
here=Path(__file__).parent
rows=list(csv.DictReader((here/'raw/runs.csv').open()))
metrics=[]
for name in ('startup_seconds','rtt_ms','packet_loss_percent'):
    vals=[float(r[name]) for r in rows if r[name] not in ('','nan')]
    metrics.append({'metric':name, **summarize(vals)})
write_rows(here/'results/summary.csv', metrics)
print(metrics)

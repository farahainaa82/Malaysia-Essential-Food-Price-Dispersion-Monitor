# Data

This repository does not commit raw PriceCatcher monthly files because each month can contain more than one million observations.

Run the download script with explicit months:

```bash
python src/download.py --months 2026-05 2026-06 2026-07 2026-08 2026-09 2026-10
```

Raw source URLs are retained in code.

The analytical panel produced by `src/build_panel.py` is small enough to commit if desired.

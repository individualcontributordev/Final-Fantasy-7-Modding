# Status: Highwind presets fixed

## What was wrong

Encounter presets still listed base id **highwind-v0.1.1**.  
Live Highwind (and the Highwind encounter packs) use **highwind-v0.2.0**.  
The builder only shows a preset when the selected base id matches — so Highwind showed **no presets**.

## Fix (pushed with this file)

All four random-encounter presets now include **highwind-v0.2.0**:

- Off / Light / Standard / Dense  

## Check

1. Hard-refresh https://individualcontributor.dev/builder/ (after Pages updates).  
2. Select **Highwind** (current).  
3. Confirm encounter presets appear again.

Then continue your CSR single-disc burn when ready.

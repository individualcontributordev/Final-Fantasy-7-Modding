# D2/D3 field movies to trim on D1 (after disc-change hubs)

Pack applied: single-disc-clean-v0.1.0-dev on pristine D1
Local image: workspace/iso-extract/ff7_d1_single_disc_v010_applied.bin (not in git)

Filters (Makou field ids):
- Disc 2 list: field id >= 632 (losin2 and later)
- Disc 3 list: field id >= 741 (canon_2 and later)

Only plays of movie files that do not exist on D1. On the D1 work bin, delete
Set next movie + Play movie on these DATs; keep Wait / Jump / Execute.

D1 applied status = PMVIE+MOVIE pairs after your published 0.1.0 layer.

## Disc 2 range (field id >= 632 losin2+)

| ID | Stem | DAT | D2 movie missing on D1 | D1 applied status |
|---:|------|-----|------------------------|-------------------|
| 634 | lost2 | LOST2.DAT | 38=GREATPIT.MOV | STILL HAS [38=JENOVA_E.MOV] |
| 637 | loslake1 | LOSLAKE1.DAT | 47=JUNSEA.STR | CHANGED pristine=[25=FSHIP2N.BIN,47=MK8.STR,100=OOB(100),254=OOB(254)] applied=[254=OOB(254)] |
| 647 | ancnt2 | ANCNT2.DAT | 2=CANON.MOV, 36=GDUMMY4.HTM, 50=METEOFIX.MOV | STILL HAS [2=BOOGDEMO.STR,36=JAIROFAL.MOV,50=MTCRL.STR] |
| 695 | gaia_32 | GAIA_32.DAT | 20=C_SCENE3.MOV | STILL HAS [20=D_ROPEGO.MOV] |
| 708 | trnad_53 | TRNAD_53.DAT | 24=DUMCRUSH.MOV | TRIMMED (pairs gone on applied 0.1.0) |
| 725 | zmind1 | ZMIND1.DAT | 37=GELNICA.MOV | STILL HAS [37=JAIROFLY.MOV] |
| 726 | zmind2 | ZMIND2.DAT | 38=GREATPIT.MOV | STILL HAS [38=JENOVA_E.MOV] |
| 727 | zmind3 | ZMIND3.DAT | 2=CANON.MOV, 3=CANONH1P.MOV, 7=CANONHT2.MOV, 39=HWINDFLY.MOV, 68=WEAPON0.MOV | STILL HAS [2=BOOGDEMO.STR,3=BOOGDOWN.STR,7=CAR_1209.STR,17=DISK1.LZS,39=JUNAIRD.STR,68=STAFF.BIN,89=OOB(89)] |
| 751 | las0_8 | LAS0_8.DAT | 19=C_SCENE2.MOV | STILL HAS [19=DISK3.LZS,57=ONTRAIN.MOV,126=OOB(126),217=OOB(217)] |
| 779 | md8_52 | MD8_52.DAT | 52=NRCRL.MOV | STILL HAS [52=MTNVL2.STR] |

## Disc 3 range (field id >= 741 canon_2+)

| ID | Stem | DAT | D3 movie missing on D1 | D1 applied status |
|---:|------|-----|------------------------|-------------------|
| 751 | las0_8 | LAS0_8.DAT | 19=FCAR.STR | STILL HAS [19=DISK3.LZS,57=ONTRAIN.MOV,126=OOB(126),217=OOB(217)] |

## Todo checklist (still have Play pairs on applied 0.1.0)

### From D2 range

- **634 LOST2.DAT** (lost2): D2 GREATPIT.MOV | STILL HAS [38=JENOVA_E.MOV]
- **637 LOSLAKE1.DAT** (loslake1): D2 JUNSEA.STR | CHANGED pristine=[25=FSHIP2N.BIN,47=MK8.STR,100=OOB(100),254=OOB(254)] applied=[254=OOB(254)]
- **647 ANCNT2.DAT** (ancnt2): D2 CANON.MOV, GDUMMY4.HTM, METEOFIX.MOV | STILL HAS [2=BOOGDEMO.STR,36=JAIROFAL.MOV,50=MTCRL.STR]
- **695 GAIA_32.DAT** (gaia_32): D2 C_SCENE3.MOV | STILL HAS [20=D_ROPEGO.MOV]
- **725 ZMIND1.DAT** (zmind1): D2 GELNICA.MOV | STILL HAS [37=JAIROFLY.MOV]
- **726 ZMIND2.DAT** (zmind2): D2 GREATPIT.MOV | STILL HAS [38=JENOVA_E.MOV]
- **727 ZMIND3.DAT** (zmind3): D2 CANON.MOV, CANONH1P.MOV, CANONHT2.MOV, HWINDFLY.MOV, WEAPON0.MOV | STILL HAS [2=BOOGDEMO.STR,3=BOOGDOWN.STR,7=CAR_1209.STR,17=DISK1.LZS,39=JUNAIRD.STR,68=STAFF.BIN,89=OOB(89)]
- **751 LAS0_8.DAT** (las0_8): D2 C_SCENE2.MOV | STILL HAS [19=DISK3.LZS,57=ONTRAIN.MOV,126=OOB(126),217=OOB(217)]
- **779 MD8_52.DAT** (md8_52): D2 NRCRL.MOV | STILL HAS [52=MTNVL2.STR]

### From D3 range

- **751 LAS0_8.DAT** (las0_8): D3 FCAR.STR | STILL HAS [19=DISK3.LZS,57=ONTRAIN.MOV,126=OOB(126),217=OOB(217)]

## Already clean on applied 0.1.0 (pairs gone vs pristine)

- 708 TRNAD_53.DAT

## Notes

- Field ids from Makou maplist: losin2=632, canon_2=741
- Confirm with Makou Find All before bulk edits
- PMVIE index numbers differ per disc; table keys off D2/D3 filenames missing on D1

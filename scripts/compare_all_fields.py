#!/usr/bin/env python3
"""Compare ALL field files between two disc images.

Extracts every FIELD/*.DAT from both bins and compares them.
Shows which fields differ and generates detailed reports.

Usage:
    python3 scripts/compare_all_fields.py working.bin test.bin
    python3 scripts/compare_all_fields.py working.bin test.bin -o diffs.txt
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from psx_mode2_iso import extract_file, find_file
from field_compare import compare_bytes, format_diff_report


# All known field names from FF7 PSX
# This is the complete list from the retail game
FIELD_NAMES = [
    "ANGLD1", "ANGLD2", "ANFRST", "BLACKBGA", "BLACKBGB", "BLACKBGC",
    "BLACKBGD", "BLACKBGE", "BLACKBGF", "BLIN1_1", "BLIN1_2", "BLIN2_1",
    "BLIN2_2", "BLIN3_1", "BLIN3_2", "BLIN3_3", "BLIN4", "BLIN5_1",
    "BLIN5_2", "BLIN5_3", "BLIN67_1", "BLIN67_2", "BLIN67_3", "BONE1",
    "BONE2", "BONEVIL1", "BONEVIL2", "BRIDGE", "BUGIN1A", "BUGIN1B",
    "BUGIN1C", "BUGIN2A", "BUGIN2B", "BUGSA", "BUGSB", "BUGSC",
    "CAFEAERO", "CAFEBED", "CAFEMAIN", "CAFEPRM", "CALM", "CLCLO",
    "CLOUDM1", "CLOUDM2", "CLOUDM3", "CLSTAIR", "COAL", "COALB",
    "COLOIN1", "COLOIN2", "COLOIN3", "CONDOR1", "CONDOR2", "CONDOR3",
    "CONDOR4", "COOLER1", "COOLER2", "COS_BTM", "COS_BTM2", "COSMO1",
    "COSMO2", "COSMO3", "CPARK", "CRC", "CRC2", "CRMP", "CRMP1",
    "CRMP2", "CRMP3", "DATIAO", "DEL1", "DEL2", "DEL3", "DEL4",
    "DLPB", "DOMO", "DORM2", "EL1", "ELEVTR1", "ELEVTR2", "ELEVTR3",
    "ELEVTR4", "ELMIN1", "ELMIN1_1", "ELMIN1_2", "ELMIN2", "ELMIN3",
    "ELMIN3_1", "ELMIN4", "ELMIN4_1", "ELMINN_1", "ELMINN_2", "ELMINN_3",
    "ELMINN_4", "ELEVTR5", "FF7", "FILM", "FILM1", "FLD_CLOUD", "FORCE",
    "FR_E", "FR_W", "FRCYO", "GAMES", "GHOTEL", "GHOSTHA", "GOBACK",
    "GOSON", "GRASHOPR", "GONGAGA", "GS1", "GS2", "GS3", "HILL",
    "HYOU1", "HYOU10", "HYOU11", "HYOU12", "HYOU13", "HYOU2", "HYOU3",
    "HYOU4", "HYOU5", "HYOU6", "HYOU7", "HYOU8", "HYOU9", "HYOUMK1",
    "HYOUMK2", "ITOWN1", "ITOWN2", "ITOWN3", "ITOWN4", "ITOWN5",
    "ITWNBACK", "ITWNFURO", "ITWNGOYA", "ITWNILRO", "ITWNITA", "ITWNLM1",
    "ITWNLMIN", "ITWNMURA", "ITWNSAND", "ITWNSIDE", "ITWNSIN", "ITWNTM1",
    "ITWNTMMO", "JENOA", "JENOV1", "JENOV2", "JIN", "JIN_1", "JIN_2",
    "JIN_3", "JINKR1", "JINKR2", "JINNAI1", "JINNAI2", "JINNAI3",
    "JINNAI4", "JINNAI5", "JTOWN1", "JTOWN2", "JTOWN3", "JUNAIR1",
    "JUNAIR2", "JUNBIN1", "JUNBIN2", "JUNBIN22", "JUNBIN23", "JUNBIN31",
    "JUNBIN32", "JUNBIN33", "JUNBIN34", "JUNBIN35", "JUNBIN41", "JUNBIN42",
    "JUNBIN51", "JUNBIN52", "JUNBIN53", "JUNBINN", "JUNCRGO1", "JUNCRGO2",
    "JUNCRGO3", "JUNELEIN", "JUNELEV1", "JUNELV1", "JUNELV2", "JUNIN1",
    "JUNIN2", "JUNIN3", "JUNIN4", "JUNIN5", "JUNINN", "JUNMARK1",
    "JUNMARK2", "JUNMARK3", "JUNMKC1", "JUNMKR1", "JUNMKR2", "JUNMKR3",
    "JUNMKR4", "JUNMKR5", "JUNMKR6", "JUNMKR7", "JUNMKR8", "JUNON1",
    "JUNON2", "JUNPB_1", "JUNPB_2", "JUNROOM", "JUNRTBR", "JUNRTBRF",
    "JUNUNDER", "KALM", "KITA", "KNOWDOOR", "KNWTHDR", "KNWCLO",
    "KNWTYSE", "KURO_1", "KURO_2", "KURO_3", "KURO_4", "KURO_5",
    "KURO_6", "KURO_7", "KURO_8", "KURO_9", "KURO_10", "LAKE",
    "LASTD", "LASTD2", "LASTD3", "LASTD4", "LASTD5", "LASTMAP",
    "LASTSID1", "LASTSID2", "LASTSIDE", "LK_BRG", "LK_SHIP", "LOSTFROG",
    "LOST1", "LOST2", "LV_BZ_T", "LV_ZI", "MD1_1", "MD1_2",
    "MD1STIN", "MD5_1", "MD5_2", "MD7_1", "MD7_2", "MD8_1",
    "MD8BIGG", "MEKICH1", "MEKICH2", "MIE_A", "MIE_B", "MIE_C",
    "MIDEEL1", "MIDEEL2", "MIDEL_1", "MIDEL_2", "MIDGAROP", "MIN_71",
    "MIN_72", "MINEENT", "MIZ_1", "MIZ_2", "MKC1", "MKC2",
    "MKC3", "MKIDIN1", "MKIDIN2", "MKR_1", "MKR_2", "MKR_3",
    "MKR_4", "MKR_5", "MKS", "MKS_B", "MKS_C", "MKUS",
    "MKUST", "MKUST2", "MKTINN", "MKTMNT", "MQRA_1", "MQRA_2",
    "MR_1", "MR_2", "MT", "MTCRL_1", "MTCRL_10", "MTCRL_11",
    "MTCRL_12", "MTCRL_13", "MTCRL_14", "MTCRL_15", "MTCRL_16", "MTCRL_17",
    "MTCRL_18", "MTCRL_19", "MTCRL_2", "MTCRL_3", "MTCRL_4", "MTCRL_5",
    "MTCRL_6", "MTCRL_7", "MTCRL_8", "MTCRL_9", "MTNVL1", "MTNVL10",
    "MTNVL2", "MTNVL3", "MTNVL4", "MTNVL5", "MTNVL6", "MTNVL7",
    "MTNVL8", "MTNVL9", "MTNVL11", "MYS", "NCOREL", "NCORELOR",
    "NCRLPUB", "NCRLST2", "NCRLST3", "NCRMON1", "NCRMON2", "NCRTRDR",
    "NEPLACE", "NIVGATE", "NIVL_B", "NIVL_C", "NIVL_TI", "NMKIN_1",
    "NMKIN_2", "NMKIN_3", "NMKIN_4", "NMKIN_5", "NRTHMK1", "NRTHMK2",
    "NRTHMK3", "NRTHMK4", "NRTHMK5", "NZREL1", "NZREL2", "NZREL3",
    "NZREL4", "NZREL5", "NZREL6", "NZREL7", "NZREL8", "ON1", "ON2",
    "OVER_1", "OVER_2", "PSDUN_1", "PSDUN_2", "PSDUN_3", "PSDUN_4",
    "REVPUB", "ROCKETC", "RCKT_P", "RCKT_R", "RCKT_TK", "RCKTIN1",
    "RCKTIN2", "RCKTIN3", "RCKTIN4", "RCKTIN5", "RCKTIN6", "RCKTIN7",
    "RCKTINN", "ROOT", "ROOTB", "ROOTP", "RPILLER", "RUTO", "RUTO_1",
    "RUTO_2", "SANGO1", "SANGO2", "SANGO3", "SANGO4", "SBW_1", "SBW_2",
    "SBW_3", "SBW_4", "SBW_5", "SBW_6", "SEA", "SEA_BTL", "SETO",
    "SHIPINT", "SHIP_1", "SHIP_2", "SHIP_3", "SHIP_4", "SHIP_5",
    "SHIPBIN", "SHIPINN", "SILO_1", "SILO_2", "SMK_COL", "SN_1",
    "SN_2", "SNDOR1", "SNDOR2", "SNOW", "SNOW_B", "SNOW_D",
    "SNOW_E", "SNOW_F", "SNHSE_1", "SNHSE_2", "SNINN_1", "SNINN_2",
    "SNMIN_1", "SNMIN_2", "SNMK_1", "SNMK_2", "SNPOLE", "SNTRBOX",
    "SNOW_4", "SORGUM", "START", "STATION", "SUB", "SUBIN_1", "SUBIN_2",
    "TABOAT", "TALADMT", "TALADUN", "TAVERN", "TIN_1", "TIN_2",
    "TIN_3", "TIN_4", "TINHAT", "TINHAT2", "TINS_1", "TINS_2",
    "TINTEK", "TPB_1", "TPBHIT1", "TPBHIT2", "TRKOUT_1", "TRKOUT_2",
    "TRNAD_1", "TRNAD_2", "TRNAD_3", "TRNAD_4", "TRNAD_5", "TRNAD_52",
    "TRNAD_53", "TRNAD_6", "TSTAGE", "TUNL_1", "TUNNEL_1", "TUNNEL_2",
    "TUNNEL_3", "TUNNEL_4", "TUNNEL_5", "TUNNEL_6", "TUNNEL_7", "TUNNEL_8",
    "TUNNEL_9", "UTA1", "UTA2", "UTAI1", "UTAI2", "UTAIBTL", "UTHSE_1",
    "UTHSE_2", "UTHSE_3", "UTINN_1", "UTINN_2", "UUTAI1", "UUTAI2",
    "WOA", "WHITE", "WHTREE", "WHITERET", "WHITEVL1", "WHITEVL2",
    "YOKO1", "YOKO2"
]


def get_all_field_names(bin_data: bytes) -> list[str]:
    """Return all field names that exist in the bin."""
    existing = []
    for field in FIELD_NAMES:
        try:
            find_file(bin_data, f"FIELD\\{field}.DAT")
            existing.append(field)
        except:
            pass  # Field doesn't exist in this disc
    return existing


def main():
    import argparse
    
    ap = argparse.ArgumentParser(description="Compare all field files between two disc images")
    ap.add_argument("bin1", type=Path, help="First bin (e.g., working.bin)")
    ap.add_argument("bin2", type=Path, help="Second bin (e.g., test.bin)")
    ap.add_argument("-o", "--output", type=Path, help="Write full diff report to file")
    ap.add_argument("--summary-only", action="store_true", help="Only show summary, not detailed diffs")
    
    args = ap.parse_args()
    
    if not args.bin1.exists():
        print(f"❌ Bin 1 not found: {args.bin1}")
        return 1
    
    if not args.bin2.exists():
        print(f"❌ Bin 2 not found: {args.bin2}")
        return 1
    
    print(f"=== Complete Field Comparison ===\n")
    print(f"Bin 1: {args.bin1}")
    print(f"Bin 2: {args.bin2}\n")
    
    bin1_data = args.bin1.read_bytes()
    bin2_data = args.bin2.read_bytes()
    
    # Get all field names from bin1
    print("Scanning for field files...")
    field_names = get_all_field_names(bin1_data)
    print(f"Found {len(field_names)} field files\n")
    
    print("Comparing fields...")
    
    identical = []
    different = []
    errors = []
    
    for i, field in enumerate(field_names, 1):
        if i % 50 == 0:
            print(f"  Progress: {i}/{len(field_names)}...")
        
        try:
            # Extract from both bins
            path = f"FIELD\\{field}.DAT"
            dat1 = extract_file(bin1_data, path)
            dat2 = extract_file(bin2_data, path)
            
            if dat1 == dat2:
                identical.append(field)
            else:
                # Compare with field_compare for structured diff
                diff = compare_bytes(dat1, dat2, a_label=f"{field} (bin1)", b_label=f"{field} (bin2)")
                different.append((field, diff))
        
        except Exception as e:
            errors.append((field, str(e)))
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"Total fields:      {len(field_names)}")
    print(f"✅ Identical:      {len(identical)}")
    print(f"⚠️  Different:      {len(different)}")
    print(f"❌ Errors:         {len(errors)}")
    print()
    
    if different:
        print("=" * 70)
        print("DIFFERENT FIELDS")
        print("=" * 70)
        print()
        for field, _ in different:
            print(f"  {field}")
        print()
    
    if errors:
        print("=" * 70)
        print("ERRORS")
        print("=" * 70)
        print()
        for field, error in errors:
            print(f"  {field}: {error}")
        print()
    
    # Detailed diffs
    if different and not args.summary_only:
        print("=" * 70)
        print("DETAILED DIFFERENCES")
        print("=" * 70)
        print()
        
        for field, diff in different:
            print(f"\nField: {field}")
            print("-" * 70)
            report = format_diff_report(diff)
            print(report)
    
    # Write to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            f.write(f"Field Comparison Report\n")
            f.write(f"Bin 1: {args.bin1}\n")
            f.write(f"Bin 2: {args.bin2}\n")
            f.write(f"\n")
            f.write(f"Total fields: {len(field_names)}\n")
            f.write(f"Identical: {len(identical)}\n")
            f.write(f"Different: {len(different)}\n")
            f.write(f"Errors: {len(errors)}\n")
            f.write(f"\n")
            
            if different:
                f.write("=" * 70 + "\n")
                f.write("DIFFERENT FIELDS\n")
                f.write("=" * 70 + "\n\n")
                for field, _ in different:
                    f.write(f"  {field}\n")
                f.write("\n")
                
                f.write("=" * 70 + "\n")
                f.write("DETAILED DIFFERENCES\n")
                f.write("=" * 70 + "\n\n")
                
                for field, diff in different:
                    f.write(f"Field: {field}\n")
                    f.write("-" * 70 + "\n")
                    f.write(format_diff_report(diff))
                    f.write("\n\n")
        
        print(f"\n📝 Full report written to: {args.output}")
    
    # Exit code: 0 if identical, 2 if different
    return 0 if not different else 2


if __name__ == "__main__":
    sys.exit(main())

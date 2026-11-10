import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import scan_mcp_sources as s


def check(name, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f" — {detail}" if detail and not cond else ""))
    return cond


def main():
    ok = True
    # A connected, information-dense, read-only source is a candidate with a reason.
    got = s.candidate_sources(["youtube-analytics", "Notion", "Gmail"])
    by_src = {g["source"]: g for g in got}
    ok &= check("youtube-analytics is a candidate", "youtube-analytics" in by_src)
    ok &= check("every candidate has a why", all(g["why"] for g in got))
    ok &= check("every candidate has read_only flag", all("read_only" in g for g in got))
    ok &= check("cadence is weekly by default", all(g["suggested_cadence"] == "weekly" for g in got))
    # An unknown / unmapped server is NOT invented as a candidate.
    got2 = s.candidate_sources(["some-random-unmapped-server"])
    ok &= check("unknown server yields no candidate", got2 == [], str(got2))
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

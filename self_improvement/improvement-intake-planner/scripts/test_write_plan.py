import sys, pathlib, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import write_plan as w
import yaml


def check(name, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f" — {detail}" if detail and not cond else ""))
    return cond


def main():
    ok = True
    with tempfile.TemporaryDirectory() as td:
        root = pathlib.Path(td)
        (root / "adapters.yaml").write_text("adapters:\n  - source: notion\n    enabled: false\n")
        cands = [
            {"source": "youtube-analytics", "mcp_family": "youtube", "signal_kind": "performance-drift",
             "why": "ctr decay", "suggested_cadence": "weekly", "read_only": True},
            {"source": "notion", "mcp_family": "notion", "signal_kind": "decision-and-doc-change",
             "why": "doc edits", "suggested_cadence": "weekly", "read_only": True},
        ]
        res = w.write_plan(cands, str(root))
        ok &= check("harvest-plan.md written", (root / "harvest-plan.md").exists())
        ok &= check("only the NEW source was added", res["adapters_added"] == 1, str(res))
        ok &= check("existing source skipped, not duplicated", res["adapters_skipped"] == 1, str(res))
        reg = yaml.safe_load((root / "adapters.yaml").read_text())
        srcs = [a["source"] for a in reg["adapters"]]
        ok &= check("notion appears exactly once", srcs.count("notion") == 1, str(srcs))
        ok &= check("new adapter ships disabled",
                    all(a.get("enabled") is False for a in reg["adapters"] if a["source"] == "youtube-analytics"))
        plan = (root / "harvest-plan.md").read_text()
        ok &= check("plan names the source and the why", "youtube-analytics" in plan and "ctr decay" in plan)
        # Idempotent: a second run adds nothing.
        res2 = w.write_plan(cands, str(root))
        ok &= check("second run is idempotent", res2["adapters_added"] == 0, str(res2))
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

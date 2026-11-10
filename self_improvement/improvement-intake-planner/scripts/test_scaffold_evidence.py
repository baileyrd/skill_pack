import sys, pathlib, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import scaffold_evidence as sc


def check(name, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f" — {detail}" if detail and not cond else ""))
    return cond


def main():
    ok = True
    with tempfile.TemporaryDirectory() as td:
        root = pathlib.Path(td) / "evidence"
        r1 = sc.scaffold(str(root))
        for sub in ["intake/raw-events", "inbox", "routed/skill", "routed/context", "proposals", "weekly-digests"]:
            ok &= check(f"created {sub}", (root / sub).is_dir())
        ok &= check("adapters.yaml seeded", (root / "intake" / "adapters.yaml").exists())
        ok &= check("first run reports creations", len(r1["created"]) > 0)
        # Idempotent second run creates nothing.
        r2 = sc.scaffold(str(root))
        ok &= check("second run is idempotent", r2["created"] == [], str(r2["created"]))
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

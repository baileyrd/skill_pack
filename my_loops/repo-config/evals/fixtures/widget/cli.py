"""widget CLI: print a badge SVG."""
import argparse


def main() -> None:
    parser = argparse.ArgumentParser(prog="widget")
    parser.add_argument("label")
    parser.add_argument("value")
    args = parser.parse_args()
    print(f'<svg><text>{args.label}: {args.value}</text></svg>')


if __name__ == "__main__":
    main()

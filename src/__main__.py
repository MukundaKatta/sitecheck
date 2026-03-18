"""CLI for sitecheck."""
import sys, json, argparse
from .core import Sitecheck

def main():
    parser = argparse.ArgumentParser(description="SiteCheck — Construction Defect Detector. AI vision for construction quality inspection and defect detection.")
    parser.add_argument("command", nargs="?", default="status", choices=["status", "run", "info"])
    parser.add_argument("--input", "-i", default="")
    args = parser.parse_args()
    instance = Sitecheck()
    if args.command == "status":
        print(json.dumps(instance.get_stats(), indent=2))
    elif args.command == "run":
        print(json.dumps(instance.detect(input=args.input or "test"), indent=2, default=str))
    elif args.command == "info":
        print(f"sitecheck v0.1.0 — SiteCheck — Construction Defect Detector. AI vision for construction quality inspection and defect detection.")

if __name__ == "__main__":
    main()

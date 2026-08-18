#!/usr/bin/env python3
import sys

def main():
    try:
        from e7wac.cli import main as cli_main
        cli_main()
    except KeyboardInterrupt:
        sys.exit(1)

if __name__ == "__main__":
    main()

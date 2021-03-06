#! /usr/bin/env python

import sys, os

if __name__ == "__main__":
    if not reduce(bool.__or__, [arg.startswith("-O") for arg in sys.argv]):
        sys.argv.append("--batch")
        sys.argv.append("-Ojit")
    if not reduce(bool.__or__, [arg.startswith("--gcrootfinder") for arg in sys.argv]):
        # default to shadowstack, so all platforms are created equal
        # (and also because asmgcc doesn't work when cross-compiling
        # on Linux, where it is the default)
        sys.argv.append("--gcrootfinder=shadowstack")
    sys.argv.append(os.path.join(os.path.dirname(__file__), "..", "targetrsqueak.py"))
    import environment
    from rpython.translator.goal.translate import main
    main()

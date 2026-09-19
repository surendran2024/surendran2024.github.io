"""Fail the build if any published page is missing analytics or the response form.

This is the guarantee. The local tool (Apply-Block.py) is what INSTALLS the
blocks; this is what makes it impossible to publish a page without them,
because it runs on every push and cannot be forgotten.

It deliberately checks for short, stable substrings rather than the full block
markers. Those substrings are the things that must actually be present on a
page; if one of them ever legitimately changes, this file should fail loudly
and be updated on purpose, which is the intended behaviour.

Run locally with:  python .github/verify_blocks.py
"""

import os
import sys

# substring -> what it proves, and how many times it must appear (None = at least once)
REQUIRED = [
    ("data-goatcounter=", "GoatCounter analytics", 1),
    ("formspree.io/f/", "the response form", None),
    ("data-published-heading", "the published-response renderer", None),
    ("</body>", "a closing body tag", 1),
]

SKIP_DIRS = {".git", ".github"}


def pages(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in sorted(filenames):
            if name.lower().endswith(".html"):
                yield os.path.relpath(os.path.join(dirpath, name), root).replace("\\", "/")


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    problems = []
    checked = 0

    for rel in sorted(pages(root)):
        checked += 1
        with open(os.path.join(root, rel), encoding="utf-8") as fh:
            text = fh.read()
        for needle, what, exact in REQUIRED:
            count = text.count(needle)
            if exact is None and count < 1:
                problems.append("%s is missing %s" % (rel, what))
            elif exact is not None and count != exact:
                problems.append("%s has %d of %s, expected %d"
                                % (rel, count, what, exact))

    print("checked %d pages" % checked)
    if not checked:
        print("FAIL: no pages found at all; the check is looking in the wrong place")
        return 1
    if problems:
        print("")
        for line in problems:
            print("FAIL: " + line)
        print("")
        print("Fix with, from the workspace root:")
        print("  python Local_Prep_Source/_snippets/Apply-Block.py "
              "--block all --install --all")
        print("then copy the pages into the clone and push.")
        return 1
    print("OK: every page carries analytics and the response form")
    return 0


if __name__ == "__main__":
    sys.exit(main())

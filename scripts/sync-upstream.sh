#!/bin/bash
# Pull upstream trycua/cua without clobbering jcua layers.
set -e
if ! git remote get-url upstream >/dev/null 2>&1; then
  git remote add upstream https://github.com/trycua/cua.git
fi
git fetch upstream
echo "Upstream fetched. Review before merge:"
echo "  git log --oneline main..upstream/main | head"
echo "  git diff main..upstream/main --stat | head"

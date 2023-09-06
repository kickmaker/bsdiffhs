from __future__ import absolute_import

from bsdiffhs.format import (diff, patch, file_diff, file_patch,
                            file_patch_inplace)


__version__ = "0.1.0"


def test(verbosity=1):
    from .test_all import run
    return run(verbosity=verbosity)

=========================================================
bsdiffhs: binary diff and patch using the BSDIFFHS-format
=========================================================

> :warning: bsdiffhs is a derivative work from bsdiff4:
bsdiffhs is similar to [bsdiff4](https://github.com/ilanschnell/bsdiff4)
but differs in compressing patch using heatshrink instead of gzip2 format.

The code is mostly derived from cx_bsdiff (written by Anthony Tuininga,
http://cx-bsdiff.sourceforge.net/).  The cx_bsdiff code in turn was derived
from bsdiff, the standalone utility produced for BSD which can be found
at http://www.daemonology.net/bsdiff.
In addition to the two functions (diff and patch) cx_bsdiff provides, this
package includes:

* an interface to the BSDIFFHS-format
* command line interfaces: bsdiffhs and bspatchhs
* tests

The bsdiffhs package defines the following high level functions:

``diff(src_bytes, dst_bytes)`` -> bytes
   Return a BSDIFFHS-format patch (from ``src_bytes`` to ``dst_bytes``) as
   bytes.

``patch(src_bytes, patch_bytes)`` -> bytes
   Apply the BSDIFFHS-format ``patch_bytes`` to ``src_bytes`` and return
   the bytes.

``file_diff(src_path, dst_path, patch_path)``
   Write a BSDIFFHS-format patch (from the file ``src_path`` to the
   file ``dst_path``) to the file ``patch_path``.

``file_patch(src_path, dst_path, patch_path)``
   Apply the BSDIFFHS-format file ``patch_path`` to the file ``src_path``
   and write the result to the file ``dst_path``.

``file_patch_inplace(path, patch_path)``
   Apply the BSDIFFHS-format file ``patch_path`` to the file ``path``
   in place.


Example:

.. code-block:: python

   >>> import bsdiffhs
   >>> a = 100000 * b'a'
   >>> b = bytearray(a)
   >>> b[100:106] = b' diff '
   >>> p = bsdiff4.diff(a, bytes(b))
   >>> len(p)
   154
   >>> bsdiffhs.patch(a, p) == b
   True

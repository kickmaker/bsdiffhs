=========================================================
bsdiffhs: binary diff and patch using the BSDIFFHS-format
=========================================================

> :warning: bsdiffhs is a derivative work from bsdiff4:
bsdiffhs is similar to bsdiff4 (https://github.com/ilanschnell/bsdiff4)
but distinct in its approach to use heatshrink compression algorithm instead of gzip2 format.

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

``diff(src_bytes, dst_bytes, window_sz2=10, lookahead_sz2=4)`` -> bytes
   Return a BSDIFFHS-format patch (from ``src_bytes`` to ``dst_bytes``) as
   bytes.

``patch(src_bytes, patch_bytes, window_sz2=10, lookahead_sz2=4)`` -> bytes
   Apply the BSDIFFHS-format ``patch_bytes`` to ``src_bytes`` and return
   the bytes.

``file_diff(src_path, dst_path, patch_path, window_sz2=10, lookahead_sz2=4)``
   Write a BSDIFFHS-format patch (from the file ``src_path`` to the
   file ``dst_path``) to the file ``patch_path``.

``file_patch(src_path, dst_path, patch_path, window_sz2=10, lookahead_sz2=4)``
   Apply the BSDIFFHS-format file ``patch_path`` to the file ``src_path``
   and write the result to the file ``dst_path``.

``file_patch_inplace(path, patch_path, window_sz2=10, lookahead_sz2=4)``
   Apply the BSDIFFHS-format file ``patch_path`` to the file ``path``
   in place.

**Compression configuration:**

According to official heatshrink documentation: heatshrink has a couple configuration options, which impact its resource
usage and how effectively it can compress data. These are set when
dynamically allocating an encoder or decoder, or in `heatshrink_config.h`
if they are statically allocated.

* `window_sz2`, Set the window size to 2^W bytes.

The window size determines how far back in the input can be searched for
repeated patterns. A `window_sz2` of 8 will only use 256 bytes (2^8),
while a `window_sz2` of 10 will use 1024 bytes (2^10). The latter uses
more memory, but may also compress more effectively by detecting more
repetition.

The `window_sz2` setting currently must be between 4 and 15.

* `lookahead_sz2`, Set the lookahead size to 2^L bytes.

The lookahead size determines the max length for repeated patterns that
are found. If the `lookahead_sz2` is 4, a 50-byte run of 'a' characters
will be represented as several repeated 16-byte patterns (2^4 is 16),
whereas a larger `lookahead_sz2` may be able to represent it all at
once. The number of bits used for the lookahead size is fixed, so an
overly large lookahead size can reduce compression by adding unused
size bits to small patterns.

The `lookahead_sz2` setting currently must be between 3 and the
`window_sz2` - 1.

**Compression recommandation:**

Still based on official heatshrink documentation : `for embedded/low memory contexts, a `window_sz2` in the 8 to 10 range is
probably a good default, depending on how tight memory is. Smaller or
larger window sizes may make better trade-offs in specific
circumstances, but should be checked with representative data.

The `lookahead_sz2` should probably start near the `window_sz2`/2, e.g.
-w 8 -l 4 or -w 10 -l 5. The command-line program can be used to measure
how well test data works with different settings.`

**Example:**

.. code-block:: python

   >>> import bsdiffhs
   >>> a = 100000 * b'a'
   >>> b = bytearray(a)
   >>> b[100:106] = b' diff '
   >>> p = bsdiff4.diff(a, bytes(b), 11, 5)
   >>> len(p)
   154
   >>> bsdiffhs.patch(a, p, 11, 5) == b
   True

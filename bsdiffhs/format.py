from __future__ import absolute_import

import heatshrink2
import sys


if sys.version_info[0] == 2:
    from cStringIO import StringIO as BytesIO
else:
    from io import BytesIO

MAGIC = b'BSDIFFHS'
DEFAULT_WINDOW_SZ2 = 10
DEFAULT_LOOKAHEAD_SZ2 = 4
INPUT_BUFFER_SIZE = 16384

import bsdiffhs.core as core


def write_patch(fo, len_dst, tcontrol, bdiff, bextra, window_sz2=DEFAULT_WINDOW_SZ2, lookahead_sz2=DEFAULT_LOOKAHEAD_SZ2):
    """write a BSDIFFHS-format patch to stream 'fo'
    """
    fo.write(MAGIC)
    faux = BytesIO()
    # write control tuples as series of offts
    for c in tcontrol:
        for x in c:
            faux.write(core.encode_int64(x))
    # compress each block
    bcontrol = heatshrink2.compress(faux.getvalue(), window_sz2, lookahead_sz2)
    bdiff = heatshrink2.compress(bdiff, window_sz2, lookahead_sz2)
    bextra = heatshrink2.compress(bextra, window_sz2, lookahead_sz2)
    for n in len(bcontrol), len(bdiff), len_dst:
        fo.write(core.encode_int64(n))
    fo.write(bcontrol)
    fo.write(bdiff)
    fo.write(bextra)


def read_patch(fi, header_only=False, window_sz2=DEFAULT_WINDOW_SZ2, lookahead_sz2=DEFAULT_LOOKAHEAD_SZ2):
    """read a BSDIFFHS-format patch from stream 'fi'
    """
    magic = fi.read(8)
    if magic[:7] != MAGIC[:7]:
        raise ValueError("incorrect magic bsdiffhs header")
    # length headers
    len_control = core.decode_int64(fi.read(8))
    len_diff = core.decode_int64(fi.read(8))
    len_dst = core.decode_int64(fi.read(8))
    # read the control header
    bcontrol = heatshrink2.decompress(fi.read(len_control), INPUT_BUFFER_SIZE, window_sz2, lookahead_sz2)
    tcontrol = [(core.decode_int64(bcontrol[i:i + 8]),
                 core.decode_int64(bcontrol[i + 8:i + 16]),
                 core.decode_int64(bcontrol[i + 16:i + 24]))
                for i in range(0, len(bcontrol), 24)]
    if header_only:
        return len_control, len_diff, len_dst, tcontrol
    # read the diff and extra blocks
    bdiff = heatshrink2.decompress(fi.read(len_diff), INPUT_BUFFER_SIZE, window_sz2, lookahead_sz2)
    bextra = heatshrink2.decompress(fi.read(), INPUT_BUFFER_SIZE, window_sz2, lookahead_sz2)
    return len_dst, tcontrol, bdiff, bextra


def read_data(path):
    with open(path, 'rb') as fi:
        data = fi.read()
    return data


def diff(src_bytes, dst_bytes, window_sz2=DEFAULT_WINDOW_SZ2, lookahead_sz2=DEFAULT_LOOKAHEAD_SZ2):
    """diff(src_bytes, dst_bytes) -> bytes

    Return a BSDIFFHS-format patch (from src_bytes to dst_bytes) as bytes.
    """
    faux = BytesIO()
    write_patch(faux, len(dst_bytes), *core.diff(src_bytes, dst_bytes), window_sz2, lookahead_sz2)
    return faux.getvalue()


def file_diff(src_path, dst_path, patch_path, window_sz2=DEFAULT_WINDOW_SZ2, lookahead_sz2=DEFAULT_LOOKAHEAD_SZ2):
    """file_diff(src_path, dst_path, patch_path)

    Write a BSDIFFHS-format patch (from the file src_path to the file dst_path)
    to the file patch_path.
    """
    src = read_data(src_path)
    dst = read_data(dst_path)
    with open(patch_path, 'wb') as fo:
        write_patch(fo, len(dst), *core.diff(src, dst), window_sz2, lookahead_sz2)


def patch(src_bytes, patch_bytes, window_sz2=DEFAULT_WINDOW_SZ2, lookahead_sz2=4):
    """patch(src_bytes, patch_bytes) -> bytes

    Apply the BSDIFFHS-format patch_bytes to src_bytes and return the bytes.
    """
    return core.patch(src_bytes, *read_patch(BytesIO(patch_bytes), window_sz2=window_sz2, lookahead_sz2=lookahead_sz2))


def file_patch_inplace(path, patch_path, window_sz2=DEFAULT_WINDOW_SZ2, lookahead_sz2=DEFAULT_LOOKAHEAD_SZ2):
    """file_patch_inplace(path, patch_path)

    Apply the BSDIFFHS-format file patch_path to the file 'path' in place.
    """
    with open(patch_path, 'rb') as fi:
        with open(path, 'r+b') as fo:
            data = fo.read()
            fo.seek(0)
            fo.write(core.patch(data, *read_patch(fi, window_sz2=window_sz2, lookahead_sz2=lookahead_sz2)))
            fo.truncate()


def file_patch(src_path, dst_path, patch_path, window_sz2=DEFAULT_WINDOW_SZ2, lookahead_sz2=DEFAULT_LOOKAHEAD_SZ2):
    """file_patch(src_path, dst_path, patch_path)

    Apply the BSDIFFHS-format file patch_path to the file src_path and
    write the result to the file dst_path.
    """
    from os.path import abspath

    if abspath(dst_path) == abspath(src_path):
        file_patch_inplace(src_path, patch_path, window_sz2, lookahead_sz2)
        return

    with open(patch_path, 'rb') as fi:
        with open(dst_path, 'wb') as fo:
            fo.write(core.patch(read_data(src_path), *read_patch(fi)))

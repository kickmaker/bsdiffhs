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
    fo.write(core.encode_int64(len_dst))
    
    bdiff_offset = 0
    bextra_offset = 0
    
    for c in tcontrol:
        # write control tuples as series of offts
        control_data = b''.join([core.encode_int64(x) for x in c])
        # compress the control data in one block
        control_data_compressed = heatshrink2.compress(control_data, window_sz2, lookahead_sz2)
        fo.write(control_data_compressed)
        # Extract and write the appropriate segment of bdiff
        segment_diff = bdiff[bdiff_offset:bdiff_offset+c[0]]
        segment_diff_compressed = heatshrink2.compress(segment_diff, window_sz2, lookahead_sz2)
        fo.write(segment_diff_compressed)
        bdiff_offset += c[0]
        
        # Extract and write the appropriate segment of bextra
        segment_extra = bextra[bextra_offset:bextra_offset+c[1]]
        segment_extra_compressed = heatshrink2.compress(segment_extra, window_sz2, lookahead_sz2)
        fo.write(segment_extra_compressed)
        bextra_offset += c[1]


def decompress_until_size(fi, target_size, read_block_size, window_sz2, lookahead_sz2):
    compressed_data = b""
    decompressed_data = b""

    # Try to decompress until we reach target_size bytes decompressed
    while len(decompressed_data) < target_size:
        chunk = fi.read(read_block_size)
        if not chunk:  # End of the patch file
            return None
        compressed_data += chunk
        new_data = heatshrink2.decompress(compressed_data, INPUT_BUFFER_SIZE, window_sz2, lookahead_sz2)
        decompressed_data += new_data[len(decompressed_data):]

    return decompressed_data

def read_patch(fi, header_only=False, window_sz2=DEFAULT_WINDOW_SZ2, lookahead_sz2=DEFAULT_LOOKAHEAD_SZ2):
    """read a BSDIFFHS-format patch from stream 'fi'"""
    magic = fi.read(8)
    if magic[:7] != MAGIC[:7]:
        raise ValueError("incorrect magic bsdiffhs header")
    # Read the length of the target firmware
    len_dst = core.decode_int64(fi.read(8))
    
    tcontrol = []
    bdiff = b""
    bextra = b""

    while True:
        # Read the control data (24 bytes when decompressed)
        control_data = decompress_until_size(fi, 24, 1, window_sz2, lookahead_sz2)
        if control_data is None or len(control_data) < 24:
            break
        
        control_tuple = (
            core.decode_int64(control_data[0:8]),
            core.decode_int64(control_data[8:16]),
            core.decode_int64(control_data[16:24])
        )
        tcontrol.append(control_tuple)

        # Decompress bdiff and bextra
        segment_diff = decompress_until_size(fi, control_tuple[0], 1, window_sz2, lookahead_sz2)
        bdiff += segment_diff
        
        segment_extra = decompress_until_size(fi, control_tuple[1], 1, window_sz2, lookahead_sz2)
        bextra += segment_extra

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
"""zstd files of TotK / OoT (Switch 2) with the game's dictionaries (romfs/Pack/ZsDic.pack.zs, a SARC of .zsdic).

    python -I zs.py d <romfs> <in.zs> <out>      decompress (dictionary chosen by the frame's dictionary id)
    python -I zs.py c <romfs> <in> <out.zs> [dict name]   compress (default zs.zsdic, the generic one)
    python -I zs.py dicts <romfs>                list the dictionaries and their ids
"""
import os
import struct
import sys

import zstandard as zstd


def sarc_files(data):
    """{name: bytes} of a little-endian SARC."""
    assert data[:4] == b'SARC', data[:4]
    hdr_len, bom = struct.unpack_from('<HH', data, 4)
    data_off = struct.unpack_from('<I', data, 0xC)[0]
    sfat = hdr_len
    assert data[sfat:sfat + 4] == b'SFAT'
    sfat_len, count = struct.unpack_from('<HH', data, sfat + 4)
    nodes = sfat + sfat_len
    sfnt = nodes + count * 16
    assert data[sfnt:sfnt + 4] == b'SFNT'
    names = sfnt + 8
    out = {}
    for i in range(count):
        _hash, attr, start, end = struct.unpack_from('<IIII', data, nodes + i * 16)
        noff = names + (attr & 0xFFFF) * 4
        name = data[noff:data.index(b'\0', noff)].decode()
        out[name] = data[data_off + start:data_off + end]
    return out


def sarc_hash(name, key=0x65):
    h = 0
    for c in name.encode():
        h = (h * key + (c if c < 0x80 else c - 0x100)) & 0xFFFFFFFF
    return h


def sarc_build(files, align=8):
    """A little-endian SARC from {name: bytes}: SFAT sorted by name hash, names aligned to 4, data aligned to `align`."""
    names = sorted(files, key=sarc_hash)
    sfnt = bytearray()
    name_offs = []
    for n in names:
        name_offs.append(len(sfnt) // 4)
        sfnt += n.encode() + b'\0'
        while len(sfnt) % 4:
            sfnt.append(0)
    data = bytearray()
    ranges = []
    for n in names:
        while len(data) % align:
            data.append(0)
        ranges.append((len(data), len(data) + len(files[n])))
        data += files[n]
    sfat = bytearray(b'SFAT' + struct.pack('<HHI', 0xC, len(names), 0x65))
    for n, o, (s, e) in zip(names, name_offs, ranges):
        sfat += struct.pack('<IIII', sarc_hash(n), 0x01000000 | o, s, e)
    head_len = 0x14 + len(sfat) + 8 + len(sfnt)
    data_off = (head_len + align - 1) // align * align
    out = bytearray(b'SARC' + struct.pack('<HHIIHH', 0x14, 0xFEFF, 0, data_off, 0x100, 0))
    out += sfat + b'SFNT' + struct.pack('<HH', 8, 0) + sfnt
    out += bytes(data_off - len(out)) + data
    struct.pack_into('<I', out, 8, len(out))
    return bytes(out)


def compress_with(romfs, raw, dict_name=None, level=19):
    d = dicts(romfs)[dict_name] if dict_name else None
    return (zstd.ZstdCompressor(level=level, dict_data=d) if d else zstd.ZstdCompressor(level=level)).compress(raw)


def decompress_any(romfs, data):
    did = zstd.get_frame_parameters(data).dict_id
    d = by_id(romfs)[did][1] if did else None
    return (zstd.ZstdDecompressor(dict_data=d) if d else zstd.ZstdDecompressor()).decompress(data, max_output_size=1 << 31)


def dicts(romfs):
    pack = open(os.path.join(romfs, 'Pack', 'ZsDic.pack.zs'), 'rb').read()
    files = sarc_files(zstd.ZstdDecompressor().decompress(pack, max_output_size=64 << 20))
    out = {}
    for name, raw in files.items():
        d = zstd.ZstdCompressionDict(raw)
        out[name] = d
    return out


def by_id(romfs):
    return {d.dict_id(): (n, d) for n, d in dicts(romfs).items()}


def decompress(romfs, src, dst):
    data = open(src, 'rb').read()
    did = zstd.get_frame_parameters(data).dict_id
    ids = by_id(romfs)
    d = ids[did][1] if did else None
    out = (zstd.ZstdDecompressor(dict_data=d) if d else zstd.ZstdDecompressor()).decompress(data, max_output_size=1 << 31)
    open(dst, 'wb').write(out)
    print(f'{src} -> {dst}: {len(out):,} bytes (dictionary {ids[did][0] if did else "none"})')


def compress(romfs, src, dst, name='zs.zsdic'):
    d = dicts(romfs)[name]
    out = zstd.ZstdCompressor(level=16, dict_data=d).compress(open(src, 'rb').read())
    open(dst, 'wb').write(out)
    print(f'{src} -> {dst}: {len(out):,} bytes (dictionary {name})')


def mc_decompress(src, dst):
    """TotK mesh codec (.mc): 'MCPK', version 1.1.0.0, flags (size = (flags >> 5) << (flags & 0xf)), then magicless zstd."""
    data = open(src, 'rb').read()
    assert data[:4] == b'MCPK', data[:4]
    flags = struct.unpack_from('<i', data, 8)[0]
    size = (flags >> 5) << (flags & 0xF)
    obj = zstd.ZstdDecompressor(format=zstd.FORMAT_ZSTD1_MAGICLESS).decompressobj()
    out = obj.decompress(data[12:])
    open(dst, 'wb').write(out)
    print(f'{src} -> {dst}: {len(out):,} bytes, {len(obj.unused_data)} bytes after the frame (mesh codec, header size {size:,})')


def mc_compress(src, dst):
    """The reverse, as Switch-Toolbox writes it: size rounded up to 4 KB in the flags, no checksum, no content size."""
    raw = open(src, 'rb').read()
    size = (len(raw) + 0xFFF) & ~0xFFF
    flags = ((size >> 12) << 5) + 0xC
    params = zstd.ZstdCompressionParameters.from_level(19, format=zstd.FORMAT_ZSTD1_MAGICLESS,
                                                       write_content_size=False, write_checksum=False, write_dict_id=False)
    body = zstd.ZstdCompressor(compression_params=params).compress(raw)
    open(dst, 'wb').write(b'MCPK' + bytes([1, 1, 0, 0]) + struct.pack('<I', flags) + body)
    print(f'{src} -> {dst}: {12 + len(body):,} bytes (mesh codec)')


if __name__ == '__main__':
    cmd, romfs = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None
    if cmd == 'mcd':
        mc_decompress(sys.argv[2], sys.argv[3])
    elif cmd == 'mcc':
        mc_compress(sys.argv[2], sys.argv[3])
    elif cmd == 'd':
        decompress(romfs, sys.argv[3], sys.argv[4])
    elif cmd == 'c':
        compress(romfs, sys.argv[3], sys.argv[4], *sys.argv[5:6])
    elif cmd == 'dicts':
        for i, (n, _d) in sorted(by_id(romfs).items()):
            print(i, n)

"""TotK RESTBL (System/Resource/ResourceSizeTable.Product.<ver>.Nin_NX_NVN.rsizetable.zs): the buffer size the game
allocates per resource. Plain zstd, no dictionary. Layout (totk-meshcodec docs/FORMAT.md section 6):
    char magic[6] 'RESTBL'; u32 version; u32 string block size; u32 crc32 entry count; u32 name entry count;
    { u32 crc32(path), u32 size } * crc count (sorted by crc); { char name[string block size], u32 size } * name count.
Paths are hashed without the .mc / .zs suffix of the file on disk (Model/Link.Link_RaulSkin.bfres).

    python -I restbl.py get <romfs> <path> [<path> ...]
    python -I restbl.py set <romfs> <out.rsizetable.zs> <path>=<size> [...]   writes a copy with those sizes
"""
import glob
import os
import struct
import sys
import zlib

import zstandard as zstd


def table_path(romfs):
    found = glob.glob(os.path.join(romfs, 'System', 'Resource', 'ResourceSizeTable.Product.*.rsizetable.zs'))
    if len(found) != 1:
        sys.exit(f'expected one ResourceSizeTable in {romfs}: {found}')
    return found[0]


def load(path):
    raw = zstd.ZstdDecompressor().decompress(open(path, 'rb').read(), max_output_size=64 << 20)
    assert raw[:6] == b'RESTBL', raw[:6]
    version, sblock, ncrc, nname = struct.unpack_from('<4I', raw, 6)
    off = 22
    crc = {}
    for _ in range(ncrc):
        h, s = struct.unpack_from('<2I', raw, off)
        crc[h] = s
        off += 8
    names = {}
    for _ in range(nname):
        name = raw[off:off + sblock].split(b'\0', 1)[0].decode()
        names[name] = struct.unpack_from('<I', raw, off + sblock)[0]
        off += sblock + 4
    return {'version': version, 'sblock': sblock, 'crc': crc, 'names': names}


def save(t, path):
    out = bytearray(b'RESTBL') + struct.pack('<4I', t['version'], t['sblock'], len(t['crc']), len(t['names']))
    for h in sorted(t['crc']):
        out += struct.pack('<2I', h, t['crc'][h])
    for name in sorted(t['names']):
        enc = name.encode()
        assert len(enc) < t['sblock'], name
        out += enc.ljust(t['sblock'], b'\0') + struct.pack('<I', t['names'][name])
    open(path, 'wb').write(zstd.ZstdCompressor(level=19).compress(bytes(out)))


def key(path):
    return path[:-3] if path.endswith('.mc') or path.endswith('.zs') else path


def get(t, path):
    p = key(path)
    if p in t['names']:
        return t['names'][p]
    return t['crc'].get(zlib.crc32(p.encode()))


def put(t, path, size):
    p = key(path)
    if p in t['names']:
        t['names'][p] = size
    else:
        t['crc'][zlib.crc32(p.encode())] = size


if __name__ == '__main__':
    cmd, romfs = sys.argv[1], sys.argv[2]
    t = load(table_path(romfs))
    if cmd == 'get':
        print(f'{os.path.basename(table_path(romfs))}: version {t["version"]}, {len(t["crc"])} hashed, {len(t["names"])} named')
        for p in sys.argv[3:]:
            print(f'{key(p)}: {get(t, p)}')
    elif cmd == 'set':
        for kv in sys.argv[4:]:
            p, s = kv.rsplit('=', 1)
            print(f'{key(p)}: {get(t, p)} -> {int(s)}')
            put(t, p, int(s))
        os.makedirs(os.path.dirname(os.path.abspath(sys.argv[3])), exist_ok=True)
        save(t, sys.argv[3])
        back = load(sys.argv[3])
        for kv in sys.argv[4:]:
            p, s = kv.rsplit('=', 1)
            assert get(back, p) == int(s), p
        print(f'wrote {sys.argv[3]}')

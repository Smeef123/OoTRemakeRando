"""BYML reader and writer (little-endian, versions 2-7 as TotK and the OoT remake use).

    python -I byml.py <file.bgyml|.byml> [key filter regex]      dump (all, or flattened keys matching the regex)
    python -I byml.py --roundtrip <file>                          load and write back; reports whether bytes match

Node types: 0xA0 string, 0xA1 binary, 0xC0 array, 0xC1 hash (string keys), 0xC2 string table, 0xD0 bool, 0xD1 s32,
0xD2 f32, 0xD3 u32, 0xD4 s64, 0xD5 u64, 0xD6 f64, 0xFF null. Types beyond plain int/float come back tagged (U32,
I64, U64, F64) so a write keeps them. Version 7 hashed-key nodes (0x20/0x21) are read as dicts keyed '#<hash>' and
not written (no RSDB table or actor file used here has them).
"""
import json
import re
import struct
import sys


class U32(int):
    pass


class I64(int):
    pass


class U64(int):
    pass


class F64(float):
    pass


def load(b):
    assert b[:2] in (b'YB', b'BY'), b[:2]
    E = '<' if b[:2] == b'YB' else '>'   # BY: big-endian (TotK's GameDataList)
    O = 'little' if E == '<' else 'big'
    ver, keys_off, strs_off, root_off = struct.unpack_from(E + 'HIII', b, 2)

    def strtab(off):
        if not off:
            return []
        assert b[off] == 0xC2
        n = int.from_bytes(b[off + 1:off + 4], O)
        offs = struct.unpack_from(f'{E}{n + 1}I', b, off + 4)
        return [b[off + o:b.index(b'\0', off + o)].decode('utf-8', 'replace') for o in offs[:n]]

    keys, strs = strtab(keys_off), strtab(strs_off)

    def value(t, raw):
        if t == 0xA0:
            return strs[raw]
        if t == 0xD0:
            return bool(raw)
        if t == 0xD1:
            return struct.unpack('<i', struct.pack('<I', raw))[0]
        if t == 0xD2:
            return struct.unpack('<f', struct.pack('<I', raw))[0]
        if t == 0xD3:
            return U32(raw)
        if t in (0xD4, 0xD5, 0xD6):
            v = struct.unpack_from(E + 'Q', b, raw)[0]
            if t == 0xD5:
                return U64(v)
            if t == 0xD4:
                return I64(struct.unpack('<q', struct.pack('<Q', v))[0])
            return F64(struct.unpack('<d', struct.pack('<Q', v))[0])
        if t == 0xFF:
            return None
        if t in (0xC0, 0xC1, 0x20, 0x21):
            return node(raw)
        raise ValueError(f'BYML type {t:#x}')

    def node(off):
        t = b[off]
        n = int.from_bytes(b[off + 1:off + 4], O)
        if t == 0xC0:
            types = b[off + 4:off + 4 + n]
            base = off + 4 + ((n + 3) & ~3)
            return [value(types[i], struct.unpack_from(E + 'I', b, base + i * 4)[0]) for i in range(n)]
        if t == 0xC1:
            out = {}
            for i in range(n):
                e = off + 4 + i * 8
                k = int.from_bytes(b[e:e + 3], O)
                out[keys[k]] = value(b[e + 3], struct.unpack_from(E + 'I', b, e + 4)[0])
            return out
        if t in (0x20, 0x21):
            hs = 4 if t == 0x20 else 8
            ent = hs + 4
            types = b[off + 4 + n * ent:off + 4 + n * ent + n]
            out = {}
            for i in range(n):
                e = off + 4 + i * ent
                h = int.from_bytes(b[e:e + hs], O)
                out[f'#{h:x}'] = value(types[i], struct.unpack_from(E + 'I', b, e + hs)[0])
            return out
        return value(t, off)

    return node(root_off) if root_off else None


def version_of(b):
    return struct.unpack_from('<H' if b[:2] == b'YB' else '>H', b, 2)[0]


def is_big_endian(b):
    return b[:2] == b'BY'


def dump(data, version=7, big_endian=False):
    """Write a BYML: header, key table, string table, then the nodes depth-first (children after their parent).
    big_endian: the 'BY' form (TotK's GameDataList). Identical containers are written once and shared."""
    E = '>' if big_endian else '<'
    O = 'big' if big_endian else 'little'
    written = {}
    keys, strs = set(), set()

    def collect(v):
        if isinstance(v, dict):
            for k, x in v.items():
                keys.add(k)
                collect(x)
        elif isinstance(v, list):
            for x in v:
                collect(x)
        elif isinstance(v, str):
            strs.add(v)
    collect(data)
    key_list = sorted(keys, key=lambda s: s.encode())
    str_list = sorted(strs, key=lambda s: s.encode())
    key_ix = {k: i for i, k in enumerate(key_list)}
    str_ix = {s: i for i, s in enumerate(str_list)}

    out = bytearray(16)

    def align4():
        while len(out) % 4:
            out.append(0)

    def strtable(items):
        if not items:
            return 0
        align4()
        start = len(out)
        enc = [s.encode() + b'\0' for s in items]
        out.extend(bytes([0xC2]) + len(items).to_bytes(3, O))
        o = 4 + 4 * (len(items) + 1)
        offs = []
        for e in enc:
            offs.append(o)
            o += len(e)
        offs.append(o)
        out.extend(struct.pack(f'{E}{len(offs)}I', *offs))
        for e in enc:
            out.extend(e)
        return start

    keys_off = strtable(key_list)
    strs_off = strtable(str_list)

    def type_of(v):
        if isinstance(v, bool):
            return 0xD0
        if isinstance(v, U32):
            return 0xD3
        if isinstance(v, I64):
            return 0xD4
        if isinstance(v, U64):
            return 0xD5
        if isinstance(v, F64):
            return 0xD6
        if isinstance(v, int):
            return 0xD1
        if isinstance(v, float):
            return 0xD2
        if isinstance(v, str):
            return 0xA0
        if isinstance(v, list):
            return 0xC0
        if isinstance(v, dict):
            return 0xC1
        if v is None:
            return 0xFF
        raise TypeError(type(v))

    pending = []   # (slot offset, value) for values written after their container

    def scalar(t, v):
        if t == 0xA0:
            return str_ix[v]
        if t == 0xD0:
            return int(v)
        if t == 0xD1:
            return struct.unpack('<I', struct.pack('<i', v))[0]
        if t == 0xD2:
            return struct.unpack('<I', struct.pack('<f', v))[0]
        if t == 0xD3:
            return int(v)
        if t == 0xFF:
            return 0
        return None   # containers and 64-bit values: an offset, filled later

    def write_node(v):
        align4()
        start = len(out)
        if isinstance(v, list):
            types = [type_of(x) for x in v]
            out.extend(bytes([0xC0]) + len(v).to_bytes(3, O) + bytes(types))
            align4()
            for x, t in zip(v, types):
                s = scalar(t, x)
                if s is None:
                    pending.append((len(out), x, t))
                    s = 0
                out.extend(struct.pack(E + 'I', s))
        else:
            items = sorted(v.items(), key=lambda kv: key_ix[kv[0]])
            out.extend(bytes([0xC1]) + len(items).to_bytes(3, O))
            for k, x in items:
                t = type_of(x)
                out.extend(key_ix[k].to_bytes(3, O) + bytes([t]))
                s = scalar(t, x)
                if s is None:
                    pending.append((len(out), x, t))
                    s = 0
                out.extend(struct.pack(E + 'I', s))
        return start

    root_off = write_node(data) if data is not None else 0
    while pending:
        slot, x, t = pending.pop(0)
        if t in (0xC0, 0xC1):
            sig = repr(x)
            off = written.get(sig)
            if off is None:
                off = write_node(x)
                written[sig] = off
        else:
            align4()
            off = len(out)
            if t == 0xD4:
                out.extend(struct.pack(E + 'q', x))
            elif t == 0xD5:
                out.extend(struct.pack(E + 'Q', x))
            else:
                out.extend(struct.pack(E + 'd', x))
        struct.pack_into(E + 'I', out, slot, off)
    struct.pack_into(E + '2sHIII', out, 0, b'BY' if big_endian else b'YB', version, keys_off, strs_off, root_off)
    return bytes(out)


def flat(v, prefix=''):
    if isinstance(v, dict):
        for k, x in v.items():
            yield from flat(x, f'{prefix}.{k}' if prefix else k)
    elif isinstance(v, list):
        for i, x in enumerate(v):
            yield from flat(x, f'{prefix}[{i}]')
    else:
        yield prefix, v


if __name__ == '__main__':
    if sys.argv[1] == '--roundtrip':
        b = open(sys.argv[2], 'rb').read()
        d = load(b)
        w = dump(d, version_of(b), is_big_endian(b))
        same = load(w) == d
        print(f'{sys.argv[2]}: {len(b)} -> {len(w)} bytes, data {"identical" if same else "DIFFERENT"}, bytes {"identical" if w == b else "differ"}')
    else:
        data = load(open(sys.argv[1], 'rb').read())
        if len(sys.argv) > 2:
            rx = re.compile(sys.argv[2])
            for k, v in flat(data):
                if rx.search(k):
                    print(f'{k} = {v}')
        else:
            print(json.dumps(data, indent=1, ensure_ascii=False, default=float))

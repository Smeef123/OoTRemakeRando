"""Minimal MSBT (LMS message file) reader/writer: labels -> text (UTF-8 or UTF-16 as the file says), other sections kept as they are.
Control tags (0x0E ...) inside texts are kept as raw characters; plain text can be replaced."""
import struct

def _sections(b):
    assert b[:8] == b'MsgStdBn', b[:8]
    bom = b[8:10]; assert bom == b'\xff\xfe', 'big-endian MSBT not handled'
    n = struct.unpack_from('<H', b, 0x0E)[0]
    off, out = 0x20, []
    for _ in range(n):
        magic = b[off:off + 4]; size = struct.unpack_from('<I', b, off + 4)[0]
        out.append((magic, b[off + 16:off + 16 + size]))
        off += 16 + size; off = (off + 15) & ~15
    return out

def load(b):
    secs = _sections(b)
    d = dict(secs)
    # labels
    lbl = d[b'LBL1']; nslots = struct.unpack_from('<I', lbl, 0)[0]; labels = {}
    for i in range(nslots):
        cnt, o = struct.unpack_from('<II', lbl, 4 + i * 8)
        for _ in range(cnt):
            ln = lbl[o]; name = lbl[o + 1:o + 1 + ln].decode(); idx = struct.unpack_from('<I', lbl, o + 1 + ln)[0]
            labels[idx] = name; o += 1 + ln + 4
    txt = d[b'TXT2']; cnt = struct.unpack_from('<I', txt, 0)[0]
    offs = list(struct.unpack_from(f'<{cnt}I', txt, 4)) + [len(txt)]
    enc = 'utf-8' if b[0x0C] == 0 else 'utf-16le'
    texts = [txt[offs[i]:offs[i + 1]].decode(enc, 'surrogateescape') for i in range(cnt)]
    return {'header': b[:0x20], 'sections': secs, 'labels': labels, 'texts': texts, 'enc': enc}

def dump(m):
    cnt = len(m['texts']); body = b''; offs = []
    base = 4 + 4 * cnt
    for t in m['texts']:
        offs.append(base + len(body)); body += t.encode(m['enc'], 'surrogateescape')
    txt = struct.pack(f'<I{cnt}I', cnt, *offs) + body
    out = bytearray(m['header'])
    for magic, data in m['sections']:
        data = txt if magic == b'TXT2' else data
        sec = magic + struct.pack('<I', len(data)) + b'\0' * 8 + data
        sec += b'\xab' * ((-len(sec)) % 16)
        out += sec
    struct.pack_into('<I', out, 0x12, len(out))
    return bytes(out)

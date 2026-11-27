#!/usr/bin/env python3
"""Assemble the 27 Nov 2026 broadsheet from pre-rendered tiles.

Stdlib only (os, struct, zlib). No text rendering, no timestamps, no
randomness, no network: the same assets always produce the same bytes.
Layout is fixed here; every tile is pasted at a fixed (x, y).
    python3 main.py
Writes out/entry.png (1024x1024).
"""
import os
import struct
import zlib

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "assets")
OUT = os.path.join(ROOT, "out", "entry.png")

W, H = 1024, 1024
PAPER = (241, 236, 224)


def read_png(path):
    """Decode a non-interlaced 8-bit RGB/RGBA PNG into (w, h, pixels)."""
    data = open(path, "rb").read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", path
    pos, width, height, bitdepth, ctype = 8, 0, 0, 0, 0
    raw = b""
    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        kind = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + length]
        if kind == b"IHDR":
            width, height, bitdepth, ctype = struct.unpack(">IIBB", body[:10])
        elif kind == b"IDAT":
            raw += body
        elif kind == b"IEND":
            break
        pos += 12 + length
    assert bitdepth == 8 and ctype in (2, 6), (path, bitdepth, ctype)
    channels = 3 if ctype == 2 else 4
    pixels = zlib.decompress(raw)
    stride = width * channels
    rows = []
    prev = bytearray(stride)
    off = 0
    for _ in range(height):
        ftype = pixels[off]
        off += 1
        line = bytearray(pixels[off:off + stride])
        off += stride
        if ftype == 1:
            for i in range(channels, stride):
                line[i] = (line[i] + line[i - channels]) & 255
        elif ftype == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 255
        elif ftype == 3:
            for i in range(stride):
                a = line[i - channels] if i >= channels else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif ftype == 4:
            for i in range(stride):
                a = line[i - channels] if i >= channels else 0
                b = prev[i]
                c = prev[i - channels] if i >= channels else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        rows.append(bytes(line))
        prev = line
    return width, height, channels, rows


def paste(canvas, tile, ox, oy):
    """Alpha-composite an RGBA/RGB tile onto the RGB canvas."""
    tw, th, channels, rows = tile
    for y in range(th):
        cy = oy + y
        if cy < 0 or cy >= H:
            continue
        row = rows[y]
        base = cy * W * 3
        for x in range(tw):
            cx = ox + x
            if cx < 0 or cx >= W:
                continue
            i = x * channels
            r, g, b = row[i], row[i + 1], row[i + 2]
            a = row[i + 3] if channels == 4 else 255
            if a == 0:
                continue
            o = base + cx * 3
            if a == 255:
                canvas[o], canvas[o + 1], canvas[o + 2] = r, g, b
            else:
                canvas[o] = (r * a + canvas[o] * (255 - a)) // 255
                canvas[o + 1] = (g * a + canvas[o + 1] * (255 - a)) // 255
                canvas[o + 2] = (b * a + canvas[o + 2] * (255 - a)) // 255


def tile_at(name, ox, oy, canvas):
    paste(canvas, read_png(os.path.join(ASSETS, name)), ox, oy)


def write_png(path, width, height, rgb):
    """Encode RGB rows as a deterministic PNG (fixed filters, level 9)."""
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]

    def chunk(kind, body):
        out = struct.pack(">I", len(body)) + kind + body
        return out + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    canvas = bytearray(PAPER * W * H)
    margin = 20
    # Grain first, so every later tile sits on the same newsprint.
    grain = read_png(os.path.join(ASSETS, "grain_256.png"))
    for gy in range(0, H, 256):
        for gx in range(0, W, 256):
            paste(canvas, grain, gx, gy)
    tile_at("t_masthead.png", margin, 10, canvas)
    tile_at("t_regions.png", margin, 112, canvas)
    tile_at("t_utc.png", margin, 134, canvas)
    for i in range(3):
        tile_at("t_lead%d.png" % i, margin + i * 332, 156, canvas)
    for i in range(5):
        tile_at("t_mid%d.png" % i, margin + i * 198, 356, canvas)
    for i in range(5):
        tile_at("t_low%d.png" % i, margin + i * 198, 528, canvas)
    tile_at("t_numbers.png", margin, 700, canvas)
    tile_at("t_map.png", margin, 742, canvas)
    tile_at("t_also.png", margin + 332, 742, canvas)
    tile_at("t_crypto.png", margin, 902, canvas)
    tile_at("t_datecheck.png", margin, 934, canvas)
    tile_at("t_footer.png", margin, 996, canvas)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    write_png(OUT, W, H, bytes(canvas))
    print("wrote", OUT)


if __name__ == "__main__":
    main()

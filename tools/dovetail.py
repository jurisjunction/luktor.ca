"""Draw a through dovetail, pulled apart along the one way it goes together.

    python3 tools/dovetail.py > dovetail.svg.part

Cabinet oblique projection: depth (z) runs up and to the right at half
scale. Each part is a convex prism; faces are culled by their normal and
parts are painted back to front. The tail board's grain runs along x, the
pin board's along z, so end grain is where the grain meets the face.
"""
import math

C = 0.5 * math.cos(math.radians(45))          # depth offset per unit of z
VIEW = (-C, C, 1.0)                            # the projection direction, into the page
DZ = 150                                       # how far the pin board is drawn back
T = 60                                         # both boards' thickness
L = 210                                        # visible length of the pin board

# Tails at 1 in 6 over a depth of 60: each side flares 10.
TAILS = [((240, 25), (300, 15), (300, 75), (240, 65)),
         ((240, 100), (300, 90), (300, 150), (240, 140)),
         ((240, 175), (300, 165), (300, 225), (240, 215))]
PINS = [((240, 0), (300, 0), (300, 15), (240, 25)),
        ((240, 65), (300, 75), (300, 90), (240, 100)),
        ((240, 140), (300, 150), (300, 165), (240, 175)),
        ((240, 215), (300, 225), (300, 240), (240, 240))]


def proj(p):
    x, y, z = p
    return (x + C * z, y - C * z)


def dot(a, b):
    return sum(i * j for i, j in zip(a, b))


def prism(poly, z0, z1, board):
    """Faces of a polygon (x, y) extruded from z0 to z1: (points3d, normal, board)."""
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    faces = [([(x, y, z0) for x, y in poly], (0, 0, -1)),
             ([(x, y, z1) for x, y in poly], (0, 0, 1))]
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        dx, dy = x2 - x1, y2 - y1
        n = (dy, -dx)
        mx, my = (x1 + x2) / 2 - cx, (y1 + y2) / 2 - cy
        if n[0] * mx + n[1] * my < 0:
            n = (-n[0], -n[1])
        k = math.hypot(*n)
        faces.append(([(x1, y1, z0), (x2, y2, z0), (x2, y2, z1), (x1, y1, z1)], (n[0] / k, n[1] / k, 0)))
    centre = (cx, cy, (z0 + z1) / 2)
    return {"faces": faces, "board": board, "depth": dot(centre, VIEW)}


def grain(board, n):
    """face, edge or end, for the given board and face normal."""
    if board == "tail":                         # grain along x
        if abs(n[0]) > 0.9:
            return "end"
        return "face" if abs(n[2]) > 0.9 else "edge"
    if abs(n[2]) > 0.9:                          # pin board: grain along z
        return "end"
    return "face" if abs(n[0]) > 0.9 else "edge"


def svg():
    parts = [prism([(0, 0), (240, 0), (240, 240), (0, 240)], 0, T, "tail")]
    parts += [prism(list(t), 0, T, "tail") for t in TAILS]
    parts += [prism(list(p), DZ, DZ + T, "pin") for p in PINS]
    parts.append(prism([(240, 0), (300, 0), (300, 240), (240, 240)], DZ + T, DZ + T + L, "pin"))
    parts.sort(key=lambda p: -p["depth"])

    out = []
    for part in parts:
        for pts, n in part["faces"]:
            if dot(n, VIEW) >= -1e-9:
                continue
            g = grain(part["board"], n)
            d = " ".join(f"{x:.1f},{y:.1f}" for x, y in map(proj, pts))
            out.append(f'<polygon class="w {g}" points="{d}"/>')
            if g == "end":
                out.append(f'<polygon class="hatch" points="{d}"/>')

    # The way it goes together: along z, into the sockets.
    a, b = proj((336, 262, DZ + 40)), proj((336, 262, 6))
    out.append(f'<line class="way" x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" marker-end="url(#tip)"/>')

    # The slope, as a pencil note under the last tail: run 60, rise 10.
    out.append('<path class="note" d="M240,250 L300,250 M300,246 L300,254 M240,246 L240,254"/>')
    out.append('<path class="note" d="M312,215 L312,225 M308,215 L316,215 M308,225 L316,225"/>')
    out.append('<text class="label" x="270" y="268" text-anchor="middle">6</text>')
    out.append('<text class="label" x="322" y="224">1</text>')

    xs, ys = [], []
    for part in parts:
        for pts, _ in part["faces"]:
            for p in map(proj, pts):
                xs.append(p[0]); ys.append(p[1])
    pad = 12
    vb = (min(xs) - pad, min(ys) - pad, max(xs) - min(xs) + 2 * pad + 20, max(max(ys), 272) - min(ys) + 2 * pad)
    head = (f'<svg class="dovetail" viewBox="{vb[0]:.0f} {vb[1]:.0f} {vb[2]:.0f} {vb[3]:.0f}" role="img" '
            'aria-labelledby="dovetail-title">'
            '<title id="dovetail-title">A through dovetail joint, its two boards drawn apart along the one '
            'direction in which they fit together.</title>'
            '<defs><pattern id="rings" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            '<line x1="0" y1="0" x2="0" y2="6" class="ring"/></pattern>'
            '<marker id="tip" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            '<path d="M0,0 L10,5 L0,10 z" class="tip"/></marker></defs>')
    return head + "".join(out) + "</svg>"


if __name__ == "__main__":
    print(svg())

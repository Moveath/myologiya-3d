"""Post-process the figure renders into web assets.
- body outline (glass-like rim) from the silhouette, one per theme
- WebP layers for bones and region highlights
- region hit map as a small run-length string (bodymap.js)
"""
import sys, json
import numpy as np
from PIL import Image
from scipy import ndimage

src, dst = sys.argv[1], sys.argv[2]
W, H = 560, 1240

# ---- outline from the 2x silhouette ----
m2 = np.array(Image.open(f"{src}/mask2x.png"))[..., 3] > 127
m2 = ndimage.binary_closing(m2, iterations=2)
m2 = ndimage.binary_fill_holes(m2)
din = ndimage.distance_transform_edt(m2)            # inside distance (px at 2x)
dout = ndimage.distance_transform_edt(~m2)
sd = np.where(m2, din, -dout)                         # signed distance, positive inside
edge = np.clip(sd + 0.5, 0, 1)                        # anti-aliased edge
d = np.maximum(sd, 0) / 2.0                           # distance in final px
prof = 0.78 * np.exp(-d / 2.2) + 0.30 * np.exp(-d / 16.0) + 0.05


def outline(rgb, gain):
    a = np.clip(prof * edge * gain, 0, 1)
    img = np.zeros(m2.shape + (4,), dtype=np.float32)
    img[..., 0], img[..., 1], img[..., 2] = rgb
    img[..., 3] = a * 255
    im = Image.fromarray(img.astype(np.uint8), "RGBA").resize((W, H), Image.LANCZOS)
    return im


outline((47, 107, 100), 1.0).save(f"{dst}/body-outline-light.webp", "WEBP", quality=88, method=6)
outline((150, 214, 204), 0.9).save(f"{dst}/body-outline-dark.webp", "WEBP", quality=88, method=6)

# ---- bones and highlights ----
Image.open(f"{src}/bones.png").save(f"{dst}/body-bones.webp", "WEBP", quality=90, method=6)
for r in ["head", "neck", "trunk", "arm", "leg"]:
    Image.open(f"{src}/hl-{r}.png").save(f"{dst}/body-hl-{r}.webp", "WEBP", quality=86, method=6)

# ---- hit map: nearest bone region inside the (slightly grown) silhouette ----
idimg = np.array(Image.open(f"{src}/id.png").convert("RGBA"))
cols = {"h": (255, 0, 0), "n": (0, 255, 0), "t": (0, 0, 255), "a": (255, 255, 0), "l": (255, 0, 255)}
lab = np.zeros((H, W), dtype=np.uint8)
keys = list(cols)
for k_i, k in enumerate(keys, 1):
    c = cols[k]
    hit = (idimg[..., 3] > 0) & (np.abs(idimg[..., 0].astype(int) - c[0]) < 40) & (np.abs(idimg[..., 1].astype(int) - c[1]) < 40) & (np.abs(idimg[..., 2].astype(int) - c[2]) < 40)
    lab[hit] = k_i
# drop small islands (e.g. the shoulder blades seen through gaps between the ribs)
for k_i in range(1, len(keys) + 1):
    comp, n = ndimage.label(lab == k_i)
    if n == 0:
        continue
    sizes = ndimage.sum(np.ones_like(comp), comp, index=range(1, n + 1))
    for ci, sz in enumerate(sizes, 1):
        if sz < 1500:
            lab[comp == ci] = 0
sil = np.array(Image.fromarray((m2 * 255).astype(np.uint8)).resize((W, H), Image.NEAREST)) > 0
sil = ndimage.binary_dilation(sil, iterations=8)
_, (iy, ix) = ndimage.distance_transform_edt(lab == 0, return_indices=True)
near = lab[iy, ix]
full = np.where(sil, near, 0)
# downsample to a small grid for the page
GW, GH = 112, 248
small = np.array(Image.fromarray(full).resize((GW, GH), Image.NEAREST))
chars = " " + "".join(keys)
flat = "".join(chars[v] for v in small.flatten())
rle = []
i = 0
while i < len(flat):
    j = i
    while j < len(flat) and flat[j] == flat[i]:
        j += 1
    rle.append(f"{flat[i] if flat[i] != ' ' else '.'}{j - i}")
    i = j
anch = json.load(open(f"{src}/anchors.json"))
js = ("/* Карта нажатий по схеме тела: регион для каждой клетки сетки, сжатая по сериям. */\n"
      f"window.BODYMAP = {{ w: {GW}, h: {GH}, rle: {json.dumps(''.join(rle))}, img: [{W}, {H}], anchors: {json.dumps(anch['points'])} }};\n")
open(f"{dst}/bodymap.js", "w").write(js)
print("rle chars", len(''.join(rle)))
# preview of the hit map
pal = np.array([[0, 0, 0, 0], [230, 80, 80, 160], [80, 200, 80, 160], [80, 80, 230, 160], [230, 200, 60, 160], [200, 80, 200, 160]], dtype=np.uint8)
Image.fromarray(pal[full]).save(f"{src}/hitmap-preview.png")

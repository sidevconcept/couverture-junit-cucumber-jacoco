import sys
from PIL import Image, ImageChops

def autocrop(path, pad=18, bg=(255, 255, 255)):
    img = Image.open(path).convert("RGB")
    bg_img = Image.new("RGB", img.size, bg)
    diff = ImageChops.difference(img, bg_img)
    bbox = diff.getbbox()
    if not bbox:
        return
    l, t, r, b = bbox
    l = max(0, l - pad)
    t = max(0, t - pad)
    r = min(img.width, r + pad)
    b = min(img.height, b + pad)
    img.crop((l, t, r, b)).save(path)
    print(path, "->", (l, t, r, b))

for p in sys.argv[1:]:
    autocrop(p)

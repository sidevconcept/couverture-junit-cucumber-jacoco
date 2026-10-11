import qrcode
from qrcode.constants import ERROR_CORRECT_M

SCREENSHOTS = "/Users/sidneycohen/dev/projects/couverture-code/presentation/screenshots"

TARGETS = [
    ("https://github.com/sidevconcept/couverture-junit-cucumber-jacoco", f"{SCREENSHOTS}/qr-github.png"),
    ("https://www.linkedin.com/in/sidney-c-b98aab10/", f"{SCREENSHOTS}/qr-linkedin.png"),
]

for url, out in TARGETS:
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_M,
        box_size=20,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # navy modules on cream background, coherent avec la palette du support
    img = qr.make_image(fill_color="#0B1D36", back_color="#F4F1E9")
    img.save(out)
    print("saved", out, img.size)

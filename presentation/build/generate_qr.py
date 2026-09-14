import qrcode
from qrcode.constants import ERROR_CORRECT_M

URL = "https://github.com/sidevconcept/couverture-junit-cucumber-jacoco"
OUT = "/Users/sidneycohen/dev/projects/couverture-code/presentation/screenshots/qr-github.png"

qr = qrcode.QRCode(
    version=None,
    error_correction=ERROR_CORRECT_M,
    box_size=20,
    border=2,
)
qr.add_data(URL)
qr.make(fit=True)

# navy modules on cream background, coherent avec la palette du support
img = qr.make_image(fill_color="#0B1D36", back_color="#F4F1E9")
img.save(OUT)
print("saved", OUT, img.size)

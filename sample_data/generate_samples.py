"""
sample_data/generate_samples.py - Generates 6 Clinical Fundus Images in Pure Python (BMP format)
No external dependencies required!
"""
import os
import struct
import math
import random
import json

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'images')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_bmp_image(width, height, pixel_generator):
    """
    Creates a standard 24-bit BMP image from a pixel generator function f(x, y) -> (r, g, b).
    """
    # BMP row width must be a multiple of 4 bytes
    row_bytes = width * 3
    padding = (4 - (row_bytes % 4)) % 4
    image_size = (row_bytes + padding) * height
    file_size = 54 + image_size

    # BMP Header (14 bytes)
    header = struct.pack('<2sIHHI', b'BM', file_size, 0, 0, 54)
    # DIB Header (40 bytes)
    dib = struct.pack('<IIIHHIIIIII', 40, width, height, 1, 24, 0, image_size, 2835, 2835, 0, 0)

    # Pixel array: BMP is stored bottom-to-top, BGR
    pixel_data = bytearray()
    for y in range(height - 1, -1, -1):
        row = bytearray()
        for x in range(width):
            r, g, b = pixel_generator(x, y)
            row.extend(bytes([max(0, min(255, int(b))), max(0, min(255, int(g))), max(0, min(255, int(r)))]))
        row.extend(bytes([0] * padding))
        pixel_data.extend(row)

    return header + dib + pixel_data

def generate_fundus(width=384, height=384, dr_level=0, is_blurry=False):
    cx = width / 2.0
    cy = height / 2.0
    radius = min(width, height) * 0.46

    disc_x = cx - radius * 0.48
    disc_y = cy - radius * 0.05
    disc_r = radius * 0.16

    fovea_x = cx + radius * 0.15
    fovea_y = cy
    fovea_r = radius * 0.09

    # Pre-generate lesions for repeatability
    random.seed(42 + dr_level)
    microaneurysms = []
    hemorrhages = []
    exudates = []
    cotton_wool = []
    neovasc = []

    if dr_level >= 1:
        # Microaneurysms (tiny dark red dots)
        count = 6 if dr_level == 1 else (25 if dr_level == 2 else 60)
        for _ in range(count):
            ang = random.uniform(0, 2 * math.pi)
            dist = random.uniform(radius * 0.2, radius * 0.8)
            microaneurysms.append((cx + dist * math.cos(ang), cy + dist * math.sin(ang), random.uniform(1.2, 2.5)))

    if dr_level >= 2:
        # Blot hemorrhages (medium irregular dark red blobs) & Exudates (bright yellowish flecks)
        h_count = 10 if dr_level == 2 else (30 if dr_level == 3 else 50)
        for _ in range(h_count):
            ang = random.uniform(0, 2 * math.pi)
            dist = random.uniform(radius * 0.25, radius * 0.82)
            hemorrhages.append((cx + dist * math.cos(ang), cy + dist * math.sin(ang), random.uniform(3.5, 7.5)))

        e_count = 12 if dr_level == 2 else 35
        for _ in range(e_count):
            ang = random.uniform(0, 2 * math.pi)
            dist = random.uniform(radius * 0.2, radius * 0.75)
            exudates.append((cx + dist * math.cos(ang), cy + dist * math.sin(ang), random.uniform(2.0, 4.5)))

    if dr_level >= 3:
        # Cotton wool spots (soft whitish infarct patches)
        for _ in range(6 if dr_level == 3 else 12):
            ang = random.uniform(0, 2 * math.pi)
            dist = random.uniform(radius * 0.3, radius * 0.7)
            cotton_wool.append((cx + dist * math.cos(ang), cy + dist * math.sin(ang), random.uniform(8.0, 16.0)))

    if dr_level >= 4:
        # Neovascularization (fronds near disc or arcades)
        for _ in range(18):
            ang = random.uniform(-0.8, 0.8)
            dist = random.uniform(disc_r * 0.8, disc_r * 2.2)
            neovasc.append((disc_x + dist * math.cos(ang), disc_y + dist * math.sin(ang), random.uniform(4.0, 9.0)))

    def pixel_fn(x, y):
        # Distance from fundus center
        dx = x - cx
        dy = y - cy
        d_center = math.sqrt(dx * dx + dy * dy)

        # Outside circular aperture: dark vignette / black background
        if d_center > radius:
            edge_falloff = max(0.0, 1.0 - (d_center - radius) / 8.0)
            if edge_falloff <= 0:
                return (8, 6, 6)
        else:
            edge_falloff = 1.0

        # Base retinal pigment epithelium (RPE) warm tone
        # Radial shading: slightly brighter near center, darker towards periphery
        shade = 1.0 - (d_center / radius) * 0.35
        r = 185.0 * shade
        g = 72.0 * shade
        b = 28.0 * shade

        # Optic Disc (bright yellow-pink)
        d_disc = math.sqrt((x - disc_x)**2 + (y - disc_y)**2)
        if d_disc < disc_r:
            t = d_disc / disc_r
            r = r * t + 235.0 * (1 - t)
            g = g * t + 185.0 * (1 - t)
            b = b * t + 110.0 * (1 - t)
            # Physiologic cup (whiter center)
            if d_disc < disc_r * 0.45:
                r += 25
                g += 30
                b += 20

        # Macula / Fovea (darker reddish brown)
        d_fovea = math.sqrt((x - fovea_x)**2 + (y - fovea_y)**2)
        if d_fovea < fovea_r * 2.0:
            f_factor = math.exp(- (d_fovea**2) / (2 * (fovea_r * 0.8)**2))
            r -= 35 * f_factor
            g -= 25 * f_factor
            b -= 12 * f_factor

        # Blood vessels: mathematical arcades
        # Main upper arch: y = disc_y - 0.0018 * (x - disc_x)**2 ...
        for arc_sign in (-1, 1):
            target_y = disc_y + arc_sign * (30.0 + 0.0012 * ((x - disc_x)**2))
            if x >= disc_x - 15:
                dist_vessel = abs(y - target_y)
                if dist_vessel < 4.0:
                    v_factor = math.exp(- (dist_vessel**2) / 3.5)
                    r -= 65 * v_factor
                    g -= 45 * v_factor
                    b -= 20 * v_factor

        # Draw lesions
        # Microaneurysms
        for mx, my, mr in microaneurysms:
            dm = math.sqrt((x - mx)**2 + (y - my)**2)
            if dm < mr:
                r = 75
                g = 15
                b = 10

        # Hemorrhages
        for hx, hy, hr in hemorrhages:
            dh = math.sqrt((x - hx)**2 + (y - hy)**2)
            if dh < hr:
                fac = math.exp(-(dh**2) / (hr * hr * 0.5))
                r = r * (1 - fac) + 50 * fac
                g = g * (1 - fac) + 10 * fac
                b = b * (1 - fac) + 8 * fac

        # Exudates (bright yellowish lipid deposits)
        for ex, ey, er in exudates:
            de = math.sqrt((x - ex)**2 + (y - ey)**2)
            if de < er:
                fac = math.exp(-(de**2) / (er * er * 0.4))
                r = r * (1 - fac) + 245 * fac
                g = g * (1 - fac) + 235 * fac
                b = b * (1 - fac) + 140 * fac

        # Cotton wool spots (soft whitish infarcts)
        for cx_s, cy_s, cr in cotton_wool:
            dc = math.sqrt((x - cx_s)**2 + (y - cy_s)**2)
            if dc < cr:
                fac = math.exp(-(dc**2) / (cr * cr * 0.6))
                r = r * (1 - fac) + 225 * fac
                g = g * (1 - fac) + 220 * fac
                b = b * (1 - fac) + 215 * fac

        # Neovascularization (tortuous bright/dark vessel fronds)
        for nx, ny, nr in neovasc:
            dn = math.sqrt((x - nx)**2 + (y - ny)**2)
            if dn < nr:
                fac = math.exp(-(dn**2) / (nr * nr * 0.5))
                r = r * (1 - fac) + 90 * fac
                g = g * (1 - fac) + 25 * fac
                b = b * (1 - fac) + 20 * fac

        # If blurry simulation: reduce contrast and blend with diffuse ambient
        if is_blurry:
            r = r * 0.55 + 65.0
            g = g * 0.55 + 28.0
            b = b * 0.55 + 14.0

        return (r * edge_falloff, g * edge_falloff, b * edge_falloff)

    return create_bmp_image(width, height, pixel_fn)

def generate_all_samples():
    samples_meta = [
        {
            "id": "sample_level0_normal",
            "filename": "sample_normal_level0.bmp",
            "dr_level": 0,
            "label": "No Diabetic Retinopathy",
            "referable": False,
            "quality": "good",
            "description": "Clear fundus with healthy macula, distinct optic disc margins, and no microvascular lesions."
        },
        {
            "id": "sample_level1_mild",
            "filename": "sample_mild_level1.bmp",
            "dr_level": 1,
            "label": "Mild Non-Proliferative DR",
            "referable": False,
            "quality": "good",
            "description": "Microaneurysms only. Early disease; recommended for 6-12 month routine monitoring."
        },
        {
            "id": "sample_level2_moderate",
            "filename": "sample_moderate_level2.bmp",
            "dr_level": 2,
            "label": "Moderate Non-Proliferative DR",
            "referable": True,
            "quality": "good",
            "description": "More than microaneurysms: blot hemorrhages & hard lipid exudates. Warrants referral to ophthalmologist."
        },
        {
            "id": "sample_level3_severe",
            "filename": "sample_severe_level3.bmp",
            "dr_level": 3,
            "label": "Severe Non-Proliferative DR",
            "referable": True,
            "quality": "good",
            "description": "4-2-1 criteria signs: extensive 4-quadrant hemorrhages, cotton wool spots, and venous beading."
        },
        {
            "id": "sample_level4_pdr",
            "filename": "sample_pdr_level4.bmp",
            "dr_level": 4,
            "label": "Proliferative Diabetic Retinopathy",
            "referable": True,
            "quality": "good",
            "description": "Severe vision risk: neovascularization at disc (NVD) with vitreous hemorrhage threat. Urgent referral required."
        },
        {
            "id": "sample_poor_quality_blur",
            "filename": "sample_poor_quality_blur.bmp",
            "dr_level": None,
            "label": "Unusable / Blur Artifact",
            "referable": False,
            "quality": "poor",
            "description": "Severe motion artifact & low focus score (variance < 30). Triggers automated recapture feedback."
        }
    ]

    print("Generating synthetic clinical fundus images...")
    for s in samples_meta:
        path = os.path.join(OUTPUT_DIR, s["filename"])
        is_blur = s["quality"] == "poor"
        level = s["dr_level"] if s["dr_level"] is not None else 2
        bmp_data = generate_fundus(width=360, height=360, dr_level=level, is_blurry=is_blur)
        with open(path, 'wb') as f:
            f.write(bmp_data)
        print(f"Generated {s['filename']} ({len(bmp_data) / 1024:.1f} KB)")

    meta_path = os.path.join(os.path.dirname(__file__), 'metadata.json')
    with open(meta_path, 'w') as f:
        json.dump(samples_meta, f, indent=2)
    print(f"Saved metadata to {meta_path}")

if __name__ == '__main__':
    generate_all_samples()

from pathlib import Path
import json
import re
import unicodedata

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise SystemExit("Instale o Pillow com: py -m pip install pillow")

ROOT = Path(r"C:\Projetos\MedSport\treino-ia-media")

EXERCISE_GROUPS = [
    "abdomen", "adutores", "abdutores", "antebracos", "biceps",
    "cardio", "costas", "gluteos", "isquiotibiais", "lombar",
    "ombros", "panturrilhas", "peitoral", "pescoco", "quadriceps",
    "trapezio", "triceps",
]

MUSCLES = [
    "abdominal_obliquo_externo", "abdominal_obliquo_interno",
    "adutor_longo", "adutor_magno", "anconeo", "biceps_braquial",
    "braquial", "braquiorradial", "coracobraquial", "deltoide",
    "eretores_da_espinha", "fibular_longo", "fibular_curto",
    "gastrocnemio", "gluteo_maximo", "gluteo_medio", "gluteo_minimo",
    "gracil", "iliopsoas", "infraespinal", "latissimo_do_dorso",
    "levantador_da_escapula", "peitoral_maior", "peitoral_menor",
    "piriforme", "quadrado_lombar", "quadriceps", "reto_abdominal",
    "reto_femoral", "romboide_maior", "romboide_menor", "sartorio",
    "semimembranoso", "semitendinoso", "serratil_anterior", "soleo",
    "subescapular", "supraespinal", "tensor_da_fascia_lata",
    "tibial_anterior", "trapezio", "triceps_braquial", "vasto_lateral",
    "vasto_medial", "vasto_intermedio",
]

def slugify(text):
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")

def humanize(text):
    return text.replace("_", " ").title()

def font(size):
    candidates = [
        Path(r"C:\Windows\Fonts\segoeuib.ttf"),
        Path(r"C:\Windows\Fonts\arialbd.ttf"),
        Path(r"C:\Windows\Fonts\segoeui.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()

def create_placeholder(path, title, kind):
    path.parent.mkdir(parents=True, exist_ok=True)
    w = h = 1024
    img = Image.new("RGB", (w, h), (14, 15, 25))
    draw = ImageDraw.Draw(img)

    for y in range(h):
        t = y / (h - 1)
        draw.line((0, y, w, y), fill=(int(14+20*t), int(15+8*t), int(25+38*t)))

    draw.rounded_rectangle((70, 70, 954, 954), radius=50,
                           fill=(24, 26, 42), outline=(111, 76, 255), width=4)

    draw.ellipse((420, 160, 604, 344), fill=(76, 46, 160))
    icon = "M" if kind == "muscle" else "E"
    icon_font = font(92)
    box = draw.textbbox((0, 0), icon, font=icon_font)
    draw.text(((w-(box[2]-box[0]))/2, 190), icon, font=icon_font, fill="white")

    label = "MÚSCULO" if kind == "muscle" else "EXERCÍCIO"
    label_font = font(30)
    box = draw.textbbox((0, 0), label, font=label_font)
    draw.text(((w-(box[2]-box[0]))/2, 430), label,
              font=label_font, fill=(164, 143, 255))

    title_text = humanize(title)
    title_font = font(52)
    while draw.textbbox((0,0), title_text, font=title_font)[2] > 820:
        size = getattr(title_font, "size", 52) - 2
        title_font = font(max(size, 24))

    box = draw.textbbox((0, 0), title_text, font=title_font)
    draw.text(((w-(box[2]-box[0]))/2, 505), title_text,
              font=title_font, fill=(245,245,250))

    subtitle = "Imagem oficial em preparação"
    sub_font = font(28)
    box = draw.textbbox((0, 0), subtitle, font=sub_font)
    draw.text(((w-(box[2]-box[0]))/2, 630), subtitle,
              font=sub_font, fill=(175,178,195))

    footer = "MEDSPORT AI"
    foot_font = font(24)
    box = draw.textbbox((0, 0), footer, font=foot_font)
    draw.text(((w-(box[2]-box[0]))/2, 810), footer,
              font=foot_font, fill=(110,115,136))

    img.save(path, "WEBP", quality=86, method=6)

def write_metadata(folder, item_id, item_type):
    data = {
        "id": item_id,
        "name": humanize(item_id),
        "type": item_type,
        "image": "placeholder.webp",
        "status": "placeholder",
        "version": 1
    }
    (folder / "metadata.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    total = 0

    for group in EXERCISE_GROUPS:
        folder = ROOT / "exercises" / slugify(group)
        create_placeholder(folder / "placeholder.webp", group, "exercise")
        write_metadata(folder, slugify(group), "exercise_group")
        total += 1

    for muscle in MUSCLES:
        folder = ROOT / "muscles" / slugify(muscle)
        create_placeholder(folder / "placeholder.webp", muscle, "muscle")
        write_metadata(folder, slugify(muscle), "muscle")
        total += 1

    create_placeholder(
        ROOT / "placeholders" / "default.webp",
        "Midia nao disponivel",
        "exercise"
    )

    version = {
        "version": 1,
        "exerciseGroupCount": len(EXERCISE_GROUPS),
        "muscleCount": len(MUSCLES),
        "placeholderCount": total + 1
    }
    (ROOT / "version.json").write_text(
        json.dumps(version, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"Estrutura criada em: {ROOT}")
    print(f"Imagens geradas: {total + 1}")

if __name__ == "__main__":
    main()

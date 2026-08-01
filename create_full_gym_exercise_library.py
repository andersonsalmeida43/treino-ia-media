from __future__ import annotations

from pathlib import Path
import json
import re
import unicodedata

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:
    raise SystemExit(
        "Pillow não está instalado. Execute: py -m pip install pillow"
    ) from exc

ROOT = Path(r"C:\Projetos\MedSport\treino-ia-media")
OVERWRITE_EXISTING_MEDIA = False
IMAGE_SIZE = (1024, 1024)
MEDIA_FILES = ("full.webp", "start.webp", "end.webp", "thumb.webp")

CATALOG = {
    "peitoral": """
Supino reto com barra
Supino reto com halteres
Supino inclinado com barra
Supino inclinado com halteres
Supino declinado com barra
Supino declinado com halteres
Supino máquina horizontal
Supino máquina inclinado
Supino articulado convergente
Supino no smith reto
Supino no smith inclinado
Crucifixo reto com halteres
Crucifixo inclinado com halteres
Crucifixo declinado com halteres
Crossover polia alta
Crossover polia média
Crossover polia baixa
Peck deck
Flexão de braços
Flexão diamante
Flexão inclinada
Flexão declinada
Pullover com halter
Pullover na máquina
Svend press
""",
    "costas": """
Puxada frontal aberta
Puxada frontal fechada
Puxada neutra
Puxada supinada
Puxada unilateral na polia
Barra fixa pronada
Barra fixa supinada
Barra fixa neutra
Remada curvada com barra
Remada curvada supinada
Remada unilateral com halter
Remada cavalinho
Remada baixa aberta
Remada baixa fechada
Remada baixa neutra
Remada sentada na máquina
Remada articulada unilateral
Remada articulada bilateral
Remada no smith
Remada invertida
Pulldown com braços estendidos
Pullover na polia
Face pull
Levantamento terra convencional
Levantamento terra sumô
Rack pull
Good morning
Hiperextensão lombar
""",
    "ombros": """
Desenvolvimento militar com barra
Desenvolvimento com halteres sentado
Desenvolvimento com halteres em pé
Desenvolvimento Arnold
Desenvolvimento na máquina
Desenvolvimento no smith
Elevação lateral com halteres
Elevação lateral unilateral
Elevação lateral na polia
Elevação lateral na máquina
Elevação lateral inclinada
Elevação frontal com halteres
Elevação frontal com barra
Elevação frontal na polia
Crucifixo inverso com halteres
Crucifixo inverso na máquina
Crucifixo inverso na polia
Remada alta com barra
Remada alta na polia
Remada alta com halteres
Encolhimento com barra
Encolhimento com halteres
Encolhimento no smith
Rotação externa na polia
Rotação interna na polia
""",
    "biceps": """
Rosca direta com barra reta
Rosca direta com barra W
Rosca direta na polia
Rosca alternada com halteres
Rosca simultânea com halteres
Rosca martelo
Rosca martelo cruzada
Rosca martelo na corda
Rosca Scott com barra W
Rosca Scott unilateral com halter
Rosca Scott na máquina
Rosca concentrada
Rosca inclinada com halteres
Rosca spider
Rosca 21
Rosca inversa com barra
Rosca Zottman
Rosca alta na polia dupla
Rosca Bayesian na polia
""",
    "triceps": """
Tríceps na polia com barra reta
Tríceps na polia com barra V
Tríceps na polia com corda
Tríceps testa com barra W
Tríceps testa com halteres
Tríceps francês unilateral
Tríceps francês bilateral
Tríceps overhead na corda
Tríceps coice com halter
Tríceps coice na polia
Mergulho entre bancos
Paralelas para tríceps
Supino fechado com barra
Supino fechado no smith
JM press
Extensão unilateral de tríceps na polia
Extensão cruzada de tríceps na polia
""",
    "quadriceps": """
Agachamento livre
Agachamento frontal
Agachamento high bar
Agachamento low bar
Agachamento no smith
Agachamento hack
Agachamento pendular
Agachamento sissy
Agachamento goblet
Agachamento búlgaro
Afundo com barra
Afundo com halteres
Passada caminhando
Passada no smith
Step up
Leg press 45 graus
Leg press horizontal
Leg press vertical
Leg press unilateral
Cadeira extensora
Cadeira extensora unilateral
Spanish squat
Wall sit
""",
    "isquiotibiais": """
Mesa flexora
Mesa flexora unilateral
Cadeira flexora
Cadeira flexora unilateral
Flexora em pé
Stiff com barra
Stiff com halteres
Levantamento terra romeno
Levantamento terra romeno unilateral
Nordic curl
Glute ham raise
Pull through na polia
Swing com kettlebell
""",
    "gluteos": """
Hip thrust com barra
Hip thrust na máquina
Hip thrust no smith
Elevação pélvica no solo
Elevação pélvica unilateral
Coice na polia
Coice na máquina
Abdução de quadril na máquina
Abdução de quadril na polia
Caminhada lateral com miniband
Clamshell com miniband
Agachamento sumô
Afundo reverso
Step down
Extensão de quadril no banco romano
""",
    "adutores": """
Adução de quadril na máquina
Adução de quadril na polia
Copenhagen plank
Agachamento sumô profundo
Passada lateral
""",
    "panturrilhas": """
Panturrilha em pé na máquina
Panturrilha sentado na máquina
Panturrilha no leg press
Panturrilha no smith
Panturrilha unilateral em pé
Panturrilha donkey
Panturrilha no hack
Elevação de tibial anterior
""",
    "abdomen": """
Crunch abdominal
Crunch na máquina
Crunch na polia alta
Crunch declinado
Abdominal infra no banco
Elevação de pernas suspenso
Elevação de joelhos suspenso
Elevação de pernas na paralela
Ab wheel rollout
Prancha frontal
Prancha lateral
Prancha com toque no ombro
Prancha com elevação de perna
Dead bug
Bird dog
Russian twist
Wood chop alto para baixo
Wood chop baixo para alto
Pallof press
Mountain climber
Bicicleta abdominal
Hollow body hold
Dragon flag
""",
    "antebracos": """
Flexão de punho com barra
Flexão de punho com halteres
Extensão de punho com barra
Extensão de punho com halteres
Desvio radial com halter
Desvio ulnar com halter
Pronação de antebraço com halter
Supinação de antebraço com halter
Farmer walk
Pinça com anilhas
Wrist roller
""",
    "lombar": """
Extensão lombar no banco romano
Extensão lombar na máquina
Superman
Good morning sentado
Jefferson curl
""",
    "corpo_inteiro": """
Burpee
Thruster com barra
Thruster com halteres
Clean and press
Power clean
Hang clean
Snatch com barra
Snatch com halter
Turkish get up
Man maker
Sled push
Sled pull
Battle rope alternada
Battle rope ondas duplas
Box jump
Salto vertical
""",
    "cardio": """
Esteira caminhada
Esteira corrida
Esteira inclinada
Bicicleta ergométrica
Bicicleta spinning
Elíptico
Escada ergométrica
Remo ergométrico
Air bike
Ski erg
Pular corda
Polichinelo
""",
    "mobilidade": """
Alongamento peitoral na parede
Alongamento latíssimo na barra
Alongamento de quadríceps em pé
Alongamento de isquiotibiais sentado
Alongamento de flexores do quadril
Alongamento de glúteo piriforme
Alongamento de panturrilha na parede
Mobilidade de tornozelo na parede
Rotação torácica em quatro apoios
Cat cow
World greatest stretch
Face pull mobilidade
""",
}

PRIMARY_BY_CATEGORY = {
    "peitoral": "peitoral_maior",
    "costas": "latissimo_do_dorso",
    "ombros": "deltoide",
    "biceps": "biceps_braquial",
    "triceps": "triceps_braquial",
    "quadriceps": "quadriceps",
    "isquiotibiais": "isquiotibiais",
    "gluteos": "gluteo_maximo",
    "adutores": "adutores",
    "panturrilhas": "gastrocnemio",
    "abdomen": "reto_abdominal",
    "antebracos": "musculos_do_antebraco",
    "lombar": "eretores_da_espinha",
    "corpo_inteiro": "corpo_inteiro",
    "cardio": "sistema_cardiorrespiratorio",
    "mobilidade": "mobilidade_geral",
}

EQUIPMENT_RULES = [
    ("smith", "smith machine"),
    ("halter", "halteres"),
    ("barra", "barra"),
    ("polia", "polia"),
    ("máquina", "máquina"),
    ("maquina", "máquina"),
    ("leg press", "leg press"),
    ("kettlebell", "kettlebell"),
    ("banco", "banco"),
    ("miniband", "miniband"),
    ("corda", "corda"),
    ("esteira", "esteira"),
    ("bicicleta", "bicicleta ergométrica"),
    ("elíptico", "elíptico"),
    ("remo", "remo ergométrico"),
    ("air bike", "air bike"),
    ("ski erg", "ski erg"),
    ("peso corporal", "peso corporal"),
]


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in normalized if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def humanize(value: str) -> str:
    return value.replace("_", " ").strip().title()


def normalize_catalog() -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for category, raw in CATALOG.items():
        names = [line.strip() for line in raw.splitlines() if line.strip()]
        result[category] = sorted(set(names), key=str.casefold)
    return result


def infer_equipment(name: str) -> str:
    lowered = name.casefold()
    for token, equipment in EQUIPMENT_RULES:
        if token in lowered:
            return equipment
    return "peso corporal ou equipamento específico"


def infer_primary(category: str, name: str) -> str:
    lowered = name.casefold()
    if "tibial" in lowered:
        return "tibial_anterior"
    if "face pull" in lowered or "crucifixo inverso" in lowered:
        return "deltoide_posterior"
    if "elevação lateral" in lowered:
        return "deltoide_lateral"
    if "elevação frontal" in lowered or "desenvolvimento" in lowered:
        return "deltoide_anterior"
    if "martelo" in lowered:
        return "braquial"
    if "panturrilha sentado" in lowered:
        return "soleo"
    if "abdução" in lowered or "abducao" in lowered:
        return "gluteo_medio"
    if "addução" in lowered or "adução" in lowered or "aducao" in lowered:
        return "adutores"
    if "prancha lateral" in lowered or "wood chop" in lowered or "russian" in lowered:
        return "obliquos"
    return PRIMARY_BY_CATEGORY[category]


def load_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        Path(r"C:\Windows\Fonts\segoeuib.ttf"),
        Path(r"C:\Windows\Fonts\arialbd.ttf"),
        Path(r"C:\Windows\Fonts\segoeui.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_width: int, initial: int):
    size = initial
    while size >= 20:
        selected = load_font(size)
        box = draw.textbbox((0, 0), text, font=selected)
        if box[2] - box[0] <= max_width:
            return selected
        size -= 2
    return load_font(20)


def create_placeholder(path: Path, title: str, category: str, primary: str, compact: bool):
    if path.exists() and not OVERWRITE_EXISTING_MEDIA:
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    width, height = IMAGE_SIZE
    image = Image.new("RGB", IMAGE_SIZE, (12, 13, 22))
    draw = ImageDraw.Draw(image)

    for y in range(height):
        ratio = y / max(height - 1, 1)
        draw.line(
            (0, y, width, y),
            fill=(int(12 + 20 * ratio), int(13 + 8 * ratio), int(22 + 38 * ratio)),
        )

    draw.ellipse((590, -100, 1140, 450), fill=(44, 27, 93))
    draw.ellipse((-180, 640, 390, 1210), fill=(18, 44, 76))
    draw.rounded_rectangle(
        (72, 72, 952, 952),
        radius=50,
        fill=(22, 24, 38),
        outline=(107, 76, 255),
        width=4,
    )

    circle = 150 if compact else 184
    cx, cy = 512, 270
    radius = circle // 2
    draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=(73, 44, 154))

    icon_font = load_font(78 if compact else 92)
    icon_box = draw.textbbox((0, 0), "E", font=icon_font)
    draw.text(
        (cx - (icon_box[2]-icon_box[0])/2, cy - (icon_box[3]-icon_box[1])/2 - 8),
        "E",
        font=icon_font,
        fill="white",
    )

    category_text = humanize(category).upper()
    category_font = load_font(27)
    box = draw.textbbox((0, 0), category_text, font=category_font)
    draw.text(((width-(box[2]-box[0]))/2, 420), category_text, font=category_font, fill=(155,132,255))

    title_font = fit_font(draw, title, 830, 50 if compact else 58)
    box = draw.textbbox((0, 0), title, font=title_font)
    draw.text(((width-(box[2]-box[0]))/2, 500), title, font=title_font, fill=(245,245,250))

    primary_text = f"Principal: {humanize(primary)}"
    primary_font = fit_font(draw, primary_text, 790, 30)
    box = draw.textbbox((0, 0), primary_text, font=primary_font)
    draw.text(((width-(box[2]-box[0]))/2, 625), primary_text, font=primary_font, fill=(180,184,202))

    subtitle = "Imagem oficial em preparação"
    subtitle_font = load_font(26)
    box = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    draw.text(((width-(box[2]-box[0]))/2, 705), subtitle, font=subtitle_font, fill=(140,145,165))

    footer = "MEDSPORT AI"
    footer_font = load_font(24)
    box = draw.textbbox((0, 0), footer, font=footer_font)
    draw.text(((width-(box[2]-box[0]))/2, 825), footer, font=footer_font, fill=(104,108,128))

    image.save(path, "WEBP", quality=86, method=6)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def create_readme(folder: Path, metadata: dict) -> None:
    content = f"""# {metadata['exercise_pt']}

- **ID:** `{metadata['id']}`
- **Categoria:** {humanize(metadata['category'])}
- **Músculo principal:** {humanize(metadata['primary_muscle'])}
- **Equipamento:** {metadata['equipment']}
- **Status da mídia:** `{metadata['media_status']}`

## Arquivos

- `full.webp`
- `start.webp`
- `end.webp`
- `thumb.webp`
- `metadata.json`

Substitua os placeholders pelas imagens oficiais mantendo os mesmos nomes.
"""
    (folder / "README.md").write_text(content, encoding="utf-8")


def main() -> None:
    catalog = normalize_catalog()
    ROOT.mkdir(parents=True, exist_ok=True)

    complete_index = []
    generated = 0
    preserved = 0

    for category, names in catalog.items():
        category_folder = ROOT / "exercises" / slugify(category)
        category_index = []

        for name in names:
            exercise_id = slugify(name)
            folder = category_folder / exercise_id
            folder.mkdir(parents=True, exist_ok=True)
            metadata_path = folder / "metadata.json"

            if metadata_path.exists() and not OVERWRITE_EXISTING_MEDIA:
                try:
                    existing = json.loads(metadata_path.read_text(encoding="utf-8"))
                    if existing.get("media_status") == "complete":
                        preserved += 1
                        category_index.append(existing)
                        complete_index.append(existing)
                        continue
                except (OSError, json.JSONDecodeError):
                    pass

            primary = infer_primary(category, name)
            metadata = {
                "id": exercise_id,
                "exercise_pt": name,
                "exercise_en": "",
                "category": slugify(category),
                "aliases": [],
                "primary_muscle": primary,
                "secondary_muscles": [],
                "equipment": infer_equipment(name),
                "movement_type": "",
                "body_position": "",
                "difficulty": "",
                "movement_plane": "",
                "laterality": "bilateral",
                "kinetic_chain": "",
                "files": {
                    "thumb": "thumb.webp",
                    "full": "full.webp",
                    "start": "start.webp",
                    "end": "end.webp",
                },
                "media_status": "placeholder",
                "media_version": 1,
            }

            for media in MEDIA_FILES:
                create_placeholder(
                    folder / media,
                    name,
                    category,
                    primary,
                    compact=(media == "thumb.webp"),
                )

            write_json(metadata_path, metadata)
            create_readme(folder, metadata)
            category_index.append(metadata)
            complete_index.append(metadata)
            generated += 1

        write_json(category_folder / "index.json", category_index)

    complete_index.sort(key=lambda item: item["exercise_pt"].casefold())

    write_json(
        ROOT / "exercises" / "index.json",
        {
            "version": 1,
            "exercise_count": len(complete_index),
            "category_count": len(catalog),
            "categories": sorted(catalog.keys()),
            "exercises": complete_index,
        },
    )

    write_json(
        ROOT / "version.json",
        {
            "version": 1,
            "exercise_count": len(complete_index),
            "category_count": len(catalog),
            "generated_in_last_run": generated,
            "complete_media_preserved": preserved,
        },
    )

    (ROOT / "README.md").write_text(
        f"""# Treino IA Media

Biblioteca de mídia do Treino IA / MedSport AI.

- Categorias: {len(catalog)}
- Exercícios: {len(complete_index)}
- Arquivos por exercício: `full.webp`, `start.webp`, `end.webp`, `thumb.webp`, `metadata.json` e `README.md`.

Os arquivos WebP iniciais são placeholders. Substitua cada mídia oficial mantendo o mesmo nome e altere `media_status` para `complete` no `metadata.json`.
""",
        encoding="utf-8",
    )

    print("=" * 72)
    print("TREINO IA MEDIA - BIBLIOTECA COMPLETA DE EXERCÍCIOS")
    print("=" * 72)
    print(f"Destino: {ROOT}")
    print(f"Categorias: {len(catalog)}")
    print(f"Exercícios catalogados: {len(complete_index)}")
    print(f"Processados nesta execução: {generated}")
    print(f"Mídias completas preservadas: {preserved}")
    print("Concluído com sucesso.")


if __name__ == "__main__":
    main()

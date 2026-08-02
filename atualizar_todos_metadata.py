#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_REPO = Path(r"C:\Projetos\MedSport\treino-ia-media")

KNOWN_MEDIA = {
    "thumb": "thumb.webp",
    "full": "full.webp",
    "start": "start.webp",
    "end": "end.webp",
    "video_frontal": "video_frontal.mp4",
    "video_lateral": "video_lateral.mp4",
}

CATALOG_OVERRIDES: dict[str, dict[str, Any]] = {
    "supino_reto_com_barra": {
        "exercise_pt": "Supino reto com barra",
        "exercise_en": "Barbell Bench Press",
        "primary_muscle": "peitoral_maior",
        "secondary_muscles": ["triceps_braquial", "deltoide_anterior"],
        "equipment": "Barra e banco reto",
    },
    "remada_baixa": {
        "exercise_pt": "Remada baixa",
        "exercise_en": "Seated Cable Row",
        "primary_muscle": "latissimo_do_dorso",
        "secondary_muscles": ["romboides", "trapezio_medio", "biceps_braquial", "deltoide_posterior"],
        "equipment": "Polia baixa",
    },
    "agachamento_livre": {
        "exercise_pt": "Agachamento livre",
        "exercise_en": "Barbell Back Squat",
        "primary_muscle": "quadriceps",
        "secondary_muscles": ["gluteo_maximo", "isquiotibiais", "adutores", "eretores_da_espinha", "core"],
        "equipment": "Barra",
    },
    "mesa_flexora": {
        "exercise_pt": "Mesa flexora",
        "exercise_en": "Lying Leg Curl",
        "primary_muscle": "isquiotibiais",
        "secondary_muscles": ["gastrocnemio"],
        "equipment": "Mesa flexora",
    },
    "encolhimento_com_barra": {
        "exercise_pt": "Encolhimento com barra",
        "exercise_en": "Barbell Shrug",
        "primary_muscle": "trapezio_superior",
        "secondary_muscles": ["levantador_da_escapula", "antebracos"],
        "equipment": "Barra",
    },
    "desenvolvimento_na_maquina": {
        "exercise_pt": "Desenvolvimento na máquina",
        "exercise_en": "Machine Shoulder Press",
        "primary_muscle": "deltoide_anterior",
        "secondary_muscles": ["deltoide_lateral", "triceps_braquial", "trapezio_superior"],
        "equipment": "Máquina",
    },
    "rosca_martelo": {
        "exercise_pt": "Rosca martelo",
        "exercise_en": "Hammer Curl",
        "primary_muscle": "braquial",
        "secondary_muscles": ["biceps_braquial", "braquiorradial"],
        "equipment": "Halteres",
    },
    "puxada_neutra": {
        "exercise_pt": "Puxada neutra",
        "exercise_en": "Neutral Grip Lat Pulldown",
        "primary_muscle": "latissimo_do_dorso",
        "secondary_muscles": ["redondo_maior", "romboides", "biceps_braquial", "braquial"],
        "equipment": "Polia alta",
    },
    "stiff": {
        "exercise_pt": "Stiff",
        "exercise_en": "Romanian Deadlift",
        "primary_muscle": "isquiotibiais",
        "secondary_muscles": ["gluteo_maximo", "eretores_da_espinha"],
        "equipment": "Barra",
    },
    "abdominal_na_polia": {
        "exercise_pt": "Abdominal na polia",
        "exercise_en": "Cable Crunch",
        "primary_muscle": "reto_abdominal",
        "secondary_muscles": ["obliquo_externo", "obliquo_interno"],
        "equipment": "Polia alta",
    },
}


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    without_accents = "".join(c for c in normalized if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", without_accents.lower()).strip("_")


def humanize(slug: str) -> str:
    return " ".join(word.capitalize() for word in slug.replace("-", "_").split("_") if word)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError) as error:
        print(f"AVISO: JSON inválido em {path}: {error}")
        return {}


def write_json(path: Path, data: Any, dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def detect_files(exercise_dir: Path) -> tuple[dict[str, str], list[str]]:
    files: dict[str, str] = {}
    missing: list[str] = []
    for key, filename in KNOWN_MEDIA.items():
        if (exercise_dir / filename).is_file():
            files[key] = filename
        else:
            missing.append(filename)
    return files, missing


def calculate_media_status(files: dict[str, str]) -> str:
    all_images = all(key in files for key in ("thumb", "full", "start", "end"))
    both_videos = all(key in files for key in ("video_frontal", "video_lateral"))
    if all_images and both_videos:
        return "complete"
    if files:
        return "partial"
    return "missing"


def build_metadata(category: str, exercise_dir: Path, existing: dict[str, Any]) -> dict[str, Any]:
    exercise_id = slugify(exercise_dir.name)
    files, missing = detect_files(exercise_dir)
    override = CATALOG_OVERRIDES.get(exercise_id, {})

    metadata = dict(existing)
    metadata["id"] = exercise_id
    metadata["exercise_pt"] = override.get("exercise_pt") or metadata.get("exercise_pt") or metadata.get("name") or humanize(exercise_id)
    metadata["exercise_en"] = override.get("exercise_en") or metadata.get("exercise_en") or ""
    metadata["category"] = slugify(category)
    metadata.pop("name", None)
    metadata["aliases"] = list(metadata.get("aliases") or [])
    metadata["primary_muscle"] = override.get("primary_muscle") or metadata.get("primary_muscle") or ""
    metadata["secondary_muscles"] = list(override.get("secondary_muscles") or metadata.get("secondary_muscles") or [])
    metadata["equipment"] = override.get("equipment") or metadata.get("equipment") or ""

    for key in ("movement_type", "body_position", "difficulty", "movement_plane", "laterality", "kinetic_chain"):
        metadata.setdefault(key, "")

    metadata["files"] = files
    metadata["missing_files"] = missing
    metadata["media_status"] = calculate_media_status(files)
    try:
        metadata["media_version"] = max(int(metadata.get("media_version", 0)), 1)
    except (TypeError, ValueError):
        metadata["media_version"] = 1
    metadata["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    return metadata


def is_exercise_directory(path: Path) -> bool:
    if not path.is_dir() or path.name.startswith("."):
        return False
    if (path / "metadata.json").exists():
        return True
    return any((path / filename).exists() for filename in KNOWN_MEDIA.values())


def update_readme(exercise_dir: Path, metadata: dict[str, Any], dry_run: bool) -> None:
    secondary = metadata.get("secondary_muscles") or []
    secondary_text = "\n".join(f"- {humanize(str(item))}" for item in secondary) or "- Não informado"
    files_text = "\n".join(f"- `{filename}`" for filename in (metadata.get("files") or {}).values()) or "- Nenhuma mídia disponível"
    missing_text = "\n".join(f"- `{filename}`" for filename in (metadata.get("missing_files") or [])) or "- Nenhum"

    content = f'''# {metadata["exercise_pt"]}\n\n## Identificação\n\n- **ID:** `{metadata["id"]}`\n- **Categoria:** {humanize(metadata["category"])}\n- **Nome em inglês:** {metadata.get("exercise_en") or "Não informado"}\n- **Equipamento:** {metadata.get("equipment") or "Não informado"}\n\n## Musculatura\n\n- **Principal:** {humanize(metadata.get("primary_muscle") or "Não informado")}\n- **Secundários:**\n\n{secondary_text}\n\n## Mídia disponível\n\n{files_text}\n\n## Mídia pendente\n\n{missing_text}\n\n- **Status:** `{metadata["media_status"]}`\n- **Versão:** {metadata["media_version"]}\n'''
    if not dry_run:
        (exercise_dir / "README.md").write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Atualiza metadata.json de todos os exercícios.")
    parser.add_argument("--repo", type=Path, default=DEFAULT_REPO)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-backup", action="store_true")
    parser.add_argument("--no-readme", action="store_true")
    args = parser.parse_args()

    repo = args.repo.resolve()
    exercises_root = repo / "exercises"
    if not exercises_root.is_dir():
        print(f"ERRO: pasta não encontrada: {exercises_root}", file=sys.stderr)
        return 1

    all_exercises: list[dict[str, Any]] = []
    category_indexes: dict[str, list[dict[str, Any]]] = {}
    created = updated = unchanged = 0

    for category_dir in sorted((p for p in exercises_root.iterdir() if p.is_dir()), key=lambda p: p.name.casefold()):
        category = slugify(category_dir.name)
        category_items: list[dict[str, Any]] = []

        for exercise_dir in sorted((p for p in category_dir.iterdir() if is_exercise_directory(p)), key=lambda p: p.name.casefold()):
            metadata_path = exercise_dir / "metadata.json"
            existed = metadata_path.exists()
            existing = read_json(metadata_path)
            new_metadata = build_metadata(category, exercise_dir, existing)

            if json.dumps(existing, ensure_ascii=False, sort_keys=True) == json.dumps(new_metadata, ensure_ascii=False, sort_keys=True):
                unchanged += 1
                action = "SEM ALTERAÇÃO"
            else:
                action = "ATUALIZAR" if existed else "CRIAR"
                updated += 1 if existed else 0
                created += 0 if existed else 1
                if existed and not args.no_backup and not args.dry_run:
                    shutil.copy2(metadata_path, metadata_path.with_suffix(".json.bak"))
                write_json(metadata_path, new_metadata, args.dry_run)

            if not args.no_readme:
                update_readme(exercise_dir, new_metadata, args.dry_run)

            print(f"[{action:13}] {category}/{exercise_dir.name} -> {new_metadata['media_status']}")
            summary = {
                "id": new_metadata["id"],
                "exercise_pt": new_metadata["exercise_pt"],
                "exercise_en": new_metadata.get("exercise_en", ""),
                "category": new_metadata["category"],
                "primary_muscle": new_metadata.get("primary_muscle", ""),
                "secondary_muscles": new_metadata.get("secondary_muscles", []),
                "equipment": new_metadata.get("equipment", ""),
                "files": new_metadata.get("files", {}),
                "missing_files": new_metadata.get("missing_files", []),
                "media_status": new_metadata["media_status"],
                "media_version": new_metadata["media_version"],
            }
            category_items.append(summary)
            all_exercises.append(summary)

        category_indexes[category] = category_items
        write_json(category_dir / "index.json", category_items, args.dry_run)

    all_exercises.sort(key=lambda item: (item["category"].casefold(), item["exercise_pt"].casefold()))
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    write_json(exercises_root / "index.json", {
        "schema_version": 1,
        "generated_at": generated_at,
        "exercise_count": len(all_exercises),
        "category_count": len(category_indexes),
        "categories": {category: len(items) for category, items in sorted(category_indexes.items())},
        "exercises": all_exercises,
    }, args.dry_run)

    status_counts = {
        "complete": sum(1 for item in all_exercises if item["media_status"] == "complete"),
        "partial": sum(1 for item in all_exercises if item["media_status"] == "partial"),
        "missing": sum(1 for item in all_exercises if item["media_status"] == "missing"),
    }

    version_path = repo / "version.json"
    current_version = read_json(version_path)
    try:
        version_number = int(current_version.get("version", 0))
    except (TypeError, ValueError):
        version_number = 0
    write_json(version_path, {
        **current_version,
        "version": version_number + (0 if args.dry_run else 1),
        "updated_at": generated_at,
        "exercise_count": len(all_exercises),
        "category_count": len(category_indexes),
        "media": status_counts,
    }, args.dry_run)

    print("\nRESUMO")
    print(f"Exercícios encontrados: {len(all_exercises)}")
    print(f"Metadata criados: {created}")
    print(f"Metadata atualizados: {updated}")
    print(f"Sem alteração: {unchanged}")
    print(f"Mídia completa: {status_counts['complete']}")
    print(f"Mídia parcial: {status_counts['partial']}")
    print(f"Sem mídia: {status_counts['missing']}")
    print("Simulação concluída." if args.dry_run else "Atualização concluída. Revise com: git diff")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nOperação cancelada.", file=sys.stderr)
        raise SystemExit(130)
    except Exception as error:
        print(f"\nERRO: {error}", file=sys.stderr)
        raise SystemExit(1)

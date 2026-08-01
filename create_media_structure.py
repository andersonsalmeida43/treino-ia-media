from pathlib import Path
import json

ROOT = Path("treino-ia-media")

exercise_groups = [
    "abdomen",
    "adutores",
    "abdutores",
    "antebracos",
    "biceps",
    "cardio",
    "costas",
    "gluteos",
    "isquiotibiais",
    "lombar",
    "ombros",
    "panturrilhas",
    "peitoral",
    "pescoco",
    "quadriceps",
    "trapezio",
    "triceps",
]

muscles = [
    "abdominal_obliquo_externo",
    "abdominal_obliquo_interno",
    "adutor_longo",
    "adutor_magno",
    "ancôneo",
    "biceps_braquial",
    "braquial",
    "braquiorradial",
    "coracobraquial",
    "deltoide",
    "eretores_da_espinha",
    "fibular_longo",
    "fibular_curto",
    "gastrocnemio",
    "gluteo_maximo",
    "gluteo_medio",
    "gluteo_minimo",
    "gracil",
    "iliopsoas",
    "infraespinal",
    "latissimo_do_dorso",
    "levantador_da_escapula",
    "peitoral_maior",
    "peitoral_menor",
    "piriforme",
    "quadrado_lombar",
    "quadriceps",
    "reto_abdominal",
    "reto_femoral",
    "romboide_maior",
    "romboide_menor",
    "sartorio",
    "semimembranoso",
    "semitendinoso",
    "serratil_anterior",
    "soleo",
    "subescapular",
    "supraespinal",
    "tensor_da_fascia_lata",
    "tibial_anterior",
    "trapezio",
    "triceps_braquial",
    "vasto_lateral",
    "vasto_medial",
    "vasto_intermedio",
]

# raiz
ROOT.mkdir(exist_ok=True)

# pastas principais
for folder in [
    "exercises",
    "muscles",
    "body",
    "icons",
    "placeholders",
]:
    (ROOT / folder).mkdir(exist_ok=True)

# grupos de exercícios
for group in exercise_groups:
    p = ROOT / "exercises" / group
    p.mkdir(parents=True, exist_ok=True)
    (p / ".gitkeep").touch(exist_ok=True)

# músculos
for muscle in muscles:
    p = ROOT / "muscles" / muscle
    p.mkdir(parents=True, exist_ok=True)
    (p / ".gitkeep").touch(exist_ok=True)

# README
(ROOT / "README.md").write_text(
"""# Treino IA Media

Biblioteca oficial de mídias do Treino IA.

Estrutura:

- exercises/
- muscles/
- body/
- icons/
- placeholders/
""",
encoding="utf8")

# versão
version = {
    "version": 1,
    "exerciseCount": 0,
    "muscleCount": len(muscles),
}

(ROOT / "version.json").write_text(
    json.dumps(version, indent=4, ensure_ascii=False),
    encoding="utf8",
)

print("Estrutura criada com sucesso.")
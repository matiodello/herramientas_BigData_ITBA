"""Gráficos del caso de negocio a partir de los supuestos de volumen.

Los valores son estimaciones, no datos observados. Para actualizarlos hay que
cambiar el diccionario FUENTES y volver a correr:

    python graficos/generar_graficos.py
"""

from pathlib import Path

import matplotlib.pyplot as plt

OUT = Path(__file__).parent

# fuente: (eventos por día, bytes por evento en crudo). Son estimaciones.
FUENTES = {
    "Logs API Georef": (3_000_000, 600),
    "Logs API Series": (1_500_000, 600),
    "Logs portal datos.gob.ar": (400_000, 500),
    "Chequeos sintéticos": (57_600, 300),
    "Catálogo + metadatos de series": (1, 12_500_000),   # snapshot diario: catálogo ~10 MB + series ~2,5 MB
}
COMPRESION_PARQUET = 10      # JSON Lines a Parquet (orden de magnitud que vimos en la práctica 3)
COMPRESION_GZIP = 8          # Bronze: logs crudos comprimidos
RETENCION_BRONZE_DIAS = 30
RETENCION_SILVER_MESES = 13
GOLD_GB_MES = 0.4            # agregados horarios y diarios


def volumen_diario():
    return {k: ev * b / 1e9 for k, (ev, b) in FUENTES.items()}


def resumen():
    gb = volumen_diario()
    eventos = sum(ev for k, (ev, _) in FUENTES.items() if k.startswith(("Logs", "Chequeos")))
    total = sum(gb.values())
    print(f"Eventos/día: {eventos:,.0f} · promedio {eventos / 86400:,.0f} ev/s · pico (x10) {eventos / 8640:,.0f} ev/s")
    print(f"Crudo: {total:.2f} GB/día · Silver: {total / COMPRESION_PARQUET:.2f} GB/día")
    return gb, total


def grafico_volumen(gb):
    orden = sorted(gb.items(), key=lambda kv: kv[1])
    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.barh([k for k, _ in orden], [v for _, v in orden], color="#2563eb")
    for i, (_, v) in enumerate(orden):
        ax.text(v, i, f"  {v:.2f} GB" if v >= 0.01 else f"  {v * 1000:.0f} MB", va="center", fontsize=9)
    ax.set_xlabel("GB por día en crudo")
    ax.set_title("Volumen diario por fuente (valores estimados)", loc="left")
    ax.set_xlim(0, max(gb.values()) * 1.25)
    fig.tight_layout()
    fig.savefig(OUT / "volumen_estimado.png", dpi=150, metadata={"Software": None})


def grafico_almacenamiento(total):
    meses = list(range(1, 25))
    bronze = [min(m * 30, RETENCION_BRONZE_DIAS) * total / COMPRESION_GZIP for m in meses]
    silver = [min(m, RETENCION_SILVER_MESES) * 30 * total / COMPRESION_PARQUET for m in meses]
    gold = [m * GOLD_GB_MES for m in meses]
    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.stackplot(meses, bronze, silver, gold, labels=["Bronze (30 días)", "Silver (13 meses)", "Gold (sin vencimiento)"],
                 colors=["#f59e0b", "#94a3b8", "#16a34a"], alpha=0.85)
    ax.set_xlabel("Meses de operación")
    ax.set_ylabel("GB almacenados")
    ax.set_title("Almacenamiento acumulado según la retención (valores estimados)", loc="left")
    ax.legend(loc="upper left")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "almacenamiento_estimado.png", dpi=150, metadata={"Software": None})
    print(f"Mes 24: Bronze {bronze[-1]:.0f} GB · Silver {silver[-1]:.0f} GB · Gold {gold[-1]:.0f} GB · total {bronze[-1] + silver[-1] + gold[-1]:.0f} GB")


def grafico_latencias():
    usos = [("Alerta de caída", 1 / 60), ("Panel de uso", 15 / 60), ("Calidad del catálogo", 24), ("Reporte mensual", 24 * 30)]
    fig, ax = plt.subplots(figsize=(8, 3.2))
    colores = ["#dc2626", "#2563eb", "#7c3aed", "#64748b"]
    ax.barh([u for u, _ in usos][::-1], [h for _, h in usos][::-1], color=colores[::-1])
    ax.set_xscale("log")
    ax.set_xlabel("Frescura requerida (horas, escala log)")
    for i, (_, h) in enumerate(usos[::-1]):
        etiqueta = f"{h * 60:.0f} min" if h < 1 else (f"{h:.0f} h" if h < 48 else f"{h / 24:.0f} días")
        ax.text(h, i, f"  {etiqueta}", va="center", fontsize=9)
    ax.set_title("Latencia que tolera cada uso", loc="left")
    ax.set_xlim(0.01, 3000)
    fig.tight_layout()
    fig.savefig(OUT / "latencia_por_uso.png", dpi=150, metadata={"Software": None})


if __name__ == "__main__":
    gb, total = resumen()
    grafico_volumen(gb)
    grafico_almacenamiento(total)
    grafico_latencias()

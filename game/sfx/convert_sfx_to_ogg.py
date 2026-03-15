"""
Converte todos os arquivos de áudio nesta pasta (sfx/) para formato OGG.
Requer: pip install pydub
FFmpeg deve estar no PATH (necessário para exportar OGG).
"""

from pathlib import Path

try:
    from pydub import AudioSegment
except ImportError:
    print("Instale o pydub: pip install pydub")
    raise

# Pasta dos SFX = mesma pasta do script
SFX_DIR = Path(__file__).resolve().parent


def convert_to_ogg():
    if not SFX_DIR.is_dir():
        print(f"Pasta não encontrada: {SFX_DIR}")
        return

    # Formatos de entrada suportados
    exts = (".wav", ".mp3", ".flac", ".m4a")
    files = [f for f in SFX_DIR.iterdir() if f.is_file() and f.suffix.lower() in exts]

    if not files:
        print(f"Nenhum arquivo de áudio encontrado em {SFX_DIR}")
        return

    print(f"Convertendo {len(files)} arquivo(s) para OGG em {SFX_DIR}\n")

    for fp in sorted(files):
        out_path = fp.with_suffix(".ogg")
        try:
            seg = AudioSegment.from_file(str(fp), format=fp.suffix[1:].lower())
            seg.export(str(out_path), format="ogg", codec="libvorbis")
            print(f"  OK: {fp.name} -> {out_path.name}")
        except Exception as e:
            print(f"  ERRO: {fp.name} - {e}")


if __name__ == "__main__":
    convert_to_ogg()
    print("\nConcluído.")

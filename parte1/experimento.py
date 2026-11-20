"""Mide la compresión y compara los decodificadores de Huffman."""

import argparse
import csv
from pathlib import Path
from statistics import mean, stdev
from time import perf_counter_ns

from huffman import (
    decode_with_dictionary,
    decode_with_tree,
    encode_file,
    inverse_dictionary,
    read_archive,
)

ROOT = Path(__file__).resolve().parent
LANGUAGES = {"es": "Español", "fr": "Francés", "en": "Inglés"}


def write_table(destination, columns, rows):
    """Guarda una tabla CSV de resultados en UTF-8."""
    with destination.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(columns)
        writer.writerows(rows)


def benchmark(archive, iterations):
    """Mide la reconstrucción en memoria y alterna el orden de los métodos."""
    codes_dic, root, bits = read_archive(archive)
    inverse = inverse_dictionary(codes_dic)
    methods = (
        ("Diccionario inverso", decode_with_dictionary, inverse),
        ("Árbol de Huffman", decode_with_tree, root),
    )
    samples = {name: [] for name, _, _ in methods}
    for _, decode, structure in methods:
        decode(bits, structure)

    for iteration in range(iterations):
        order = methods if iteration % 2 == 0 else methods[::-1]
        for name, decode, structure in order:
            start = perf_counter_ns()
            text = decode(bits, structure)
            elapsed = perf_counter_ns() - start
            samples[name].append(elapsed / 1_000_000)
            del text

    return [(name, mean(times), stdev(times)) for name, times in samples.items()]


def run_experiment(corpus, results, iterations):
    """Comprime el corpus, comprueba ambos decodificadores y genera tres tablas."""
    files_by_language = {
        code: sorted((corpus / code).glob("*.txt")) for code in LANGUAGES
    }
    for code, sources in files_by_language.items():
        if len(sources) != 10 or any(source.stat().st_size == 0 for source in sources):
            raise ValueError(f"El corpus de {LANGUAGES[code]} debe tener 10 archivos .txt no vacíos.")

    rows_by_file = []
    rows_by_language = []
    rows_by_time = []
    benchmark_files = []
    for code, language in LANGUAGES.items():
        archive_dir = results / "comprimidos" / code
        archive_dir.mkdir(parents=True, exist_ok=True)
        factors = []
        averages = []
        for source in files_by_language[code]:
            archive, average = encode_file(source, archive_dir / f"{source.stem}.huff")
            codes_dic, root, bits = read_archive(archive)
            original = source.read_bytes()
            if (
                decode_with_tree(bits, root).encode("utf-8") != original
                or decode_with_dictionary(bits, inverse_dictionary(codes_dic)).encode("utf-8") != original
            ):
                raise ValueError(f"La descompresión de {source} difiere del original.")

            compressed_size = archive.stat().st_size
            factor = compressed_size / len(original)
            factors.append(factor)
            averages.append(average)
            rows_by_file.append(
                (source.name, language, len(original), compressed_size,
                 f"{factor:.8f}", f"{average:.8f}")
            )

        rows_by_language.append((language, f"{mean(factors):.8f}", f"{mean(averages):.8f}"))
        source = min(files_by_language[code], key=lambda path: path.stat().st_size)
        benchmark_files.append((language, source, archive_dir / f"{source.stem}.huff"))
        print(f"{language}: {len(factors)} archivos comprobados.", flush=True)

    write_table(
        results / "estadisticas_por_archivo.csv",
        ("archivo", "idioma", "tamano_original_bytes", "tamano_comprimido_bytes",
         "compression_factor", "bits_promedio_por_simbolo"),
        rows_by_file,
    )
    write_table(
        results / "estadisticas_por_idioma.csv",
        ("idioma", "compression_factor_promedio", "promedio_de_bits_por_simbolo"),
        rows_by_language,
    )

    for language, source, archive in benchmark_files:
        print(f"{language}: midiendo {iterations} decodificaciones por método de {source.name}.", flush=True)
        for method, average, deviation in benchmark(archive, iterations):
            rows_by_time.append(
                (language, source.name, method, iterations, f"{average:.6f}", f"{deviation:.6f}")
            )
    write_table(
        results / "tiempos_decodificacion.csv",
        ("idioma", "archivo", "metodo", "repeticiones", "promedio_ms", "desviacion_estandar_ms"),
        rows_by_time,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=ROOT / "corpus")
    parser.add_argument("--resultados", type=Path, default=ROOT / "resultados")
    parser.add_argument("--repeticiones", type=int, default=200)
    args = parser.parse_args()
    if args.repeticiones < 2:
        parser.error("--repeticiones debe ser al menos 2.")
    run_experiment(args.corpus, args.resultados, args.repeticiones)


if __name__ == "__main__":
    main()

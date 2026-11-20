"""
===============================================================
 Program : huffman.py
 Author  : Juan Manuel Ahuactzin y Juan Pablo Carrera
 Date    : 2025-10-13
 Version : 1.1
===============================================================
Description:
    Implementation of Huffman coding using a min-heap-based
    approach to build the optimal binary prefix tree.
    Each node represents a character and its frequency, and
    the resulting tree provides the Huffman code for each symbol.
    The class includes a __str__ method to visualize the tree
    structure and binary code paths (0/1).

    Adapted from: GeeksforGeeks. (s. f.). Huffman Coding | Greedy
    Algo-3. GeeksforGeeks.
    https://www.geeksforgeeks.org/dsa/huffman-coding-greedy-algo-3/

Usage:
    python huffman.py --help

Example:
    python huffman.py --help

Dependencies:
    - Python 3.x
    - bitarray, numpy, pandas y Graphviz (para el PDF)

Notes:
    - huffmanCodes builds the tree and returns the binary codes.
    - The __str__ method allows visualization of the recursive
      structure, indicating '0' for left edges and '1' for right
      edges.
===============================================================
"""


import argparse
import heapq
import json
import pickle
import subprocess
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from bitarray import bitarray


def show_dataframe(df, decimals=2):
    try:
        from IPython import get_ipython
        from IPython.display import display

        shell = get_ipython()

        if shell is not None and shell.__class__.__name__ == 'ZMQInteractiveShell':
            display(df.round(decimals))
            return

    except ImportError:
        pass

    print(df.round(decimals).to_string(index=False))


def print_huffman_solution(symbols, frequencies, codes):

    df, H, L = tabla_huffman(symbols, frequencies, codes)

    show_dataframe(df, 2)

    print(f"Entropía: {H:.4f} bits/símbolo")
    print(f"Longitud promedio Huffman: {L:.4f} bits/símbolo")


# Class to represent huffman tree
class Node:
    def __init__(self, x, character=""):
        self.data = x
        self.char = character
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.data < other.data

    def __str__(self, level=0, prefix="Root: ", cumchain=""):
        """Devuelve una representación jerárquica del árbol."""
        result = "   " * level + f"{prefix}({self.char}:{self.data}):{cumchain}\n"
        if self.left:
            result += self.left.__str__(level + 1, prefix="L-0- ", cumchain=cumchain + '0')
        if self.right:
            result += self.right.__str__(level + 1, prefix="R-1- ", cumchain=cumchain + '1')
        return result


# Function to traverse tree in preorder
# manner and push the huffman representation
# of each character.
def preOrder(root, ans, curr):
    if root is None:
        return

    # Leaf node represents a character.
    if root.left is None and root.right is None:
        ans[root.char] = curr or "0"
        return

    preOrder(root.left, ans, curr + '0')
    preOrder(root.right, ans, curr + '1')


def huffmanCodes(s, freq):
    n = len(s)

    # Min heap for node class.
    pq = []
    for i in range(n):
        tmp = Node(freq[i], s[i])
        heapq.heappush(pq, tmp)

    # Construct huffman tree.
    while len(pq) >= 2:
        # Left node
        l = heapq.heappop(pq)

        # Right node
        r = heapq.heappop(pq)

        newNode = Node(l.data + r.data)
        newNode.left = l
        newNode.right = r

        heapq.heappush(pq, newNode)

    root = heapq.heappop(pq) if pq else None
    codes_dic = {}
    preOrder(root, codes_dic, "")
    return codes_dic, root


def tabla_huffman(simbolos, frecuencias, codigos):
    """
    Genera una tabla de análisis de la codificación Huffman.

    Parámetros:
        simbolos: lista de símbolos
        frecuencias: lista de frecuencias
        codigos: diccionario {simbolo: codigo_binario}

    Retorna:
        df: DataFrame con los resultados
        H: entropía de Shannon (bits/símbolo)
        L: longitud promedio de Huffman (bits/símbolo)
    """

    if len(simbolos) != len(frecuencias):
        raise ValueError("Las listas deben tener igual longitud.")

    if (np.array(frecuencias) <= 0).any():
        raise ValueError("Las frecuencias deben ser positivas.")

    if set(simbolos) != set(codigos):
        raise ValueError("Los símbolos y códigos no coinciden.")

    # Probabilidades
    p = np.array(frecuencias) / sum(frecuencias)

    # Longitudes teóricas
    lt = -np.log2(p)

    # Longitudes de los códigos Huffman
    l = np.array([len(codigos[s]) for s in simbolos])

    # Construcción del DataFrame
    df = pd.DataFrame({
        'Caracter': simbolos,
        'Frecuencia': frecuencias,
        'Probabilidad': p,
        'Longitud teórica: lt': lt,
        'p*lt': p * lt,
        'Código': [codigos[s] for s in simbolos],
        'Longitud: l': l,
        'p*l': p * l
    })

    # Entropía y longitud promedio
    H = np.sum(p * lt)
    L = np.sum(p * l)

    return df, H, L


def character_frequencies(text):
    """Cuenta las apariciones de cada carácter Unicode."""
    return Counter(text)


def import_frequencies_from_txt(path):
    """Obtiene las listas de símbolos y frecuencias que recibe huffmanCodes."""
    frequencies = character_frequencies(Path(path).read_bytes().decode("utf-8"))
    return list(frequencies), list(frequencies.values())


def average_bits_per_symbol(frequencies, codes_dic):
    """Calcula Σ(frecuencia × longitud) / Σ(frecuencia)."""
    total_symbols = sum(frequencies.values())
    if not total_symbols:
        return 0.0
    total_bits = sum(
        count * len(codes_dic[character]) for character, count in frequencies.items()
    )
    return total_bits / total_symbols


def encode_text(text):
    """Devuelve el flujo de bits, los códigos, el árbol y la longitud media."""
    frequencies = character_frequencies(text)
    codes_dic, root = huffmanCodes(list(frequencies), list(frequencies.values()))
    codes = {character: bitarray(code) for character, code in codes_dic.items()}
    bits = bitarray(endian="big")
    if codes:
        bits.encode(codes, text)
    average = average_bits_per_symbol(frequencies, codes_dic)
    return bits, codes_dic, root, average


def compressBook(path):
    """Devuelve bytes, padding, códigos y árbol, como en el código original."""
    bits, codes_dic, root, _ = encode_text(Path(path).read_bytes().decode("utf-8"))
    return bits.tobytes(), (-len(bits)) % 8, codes_dic, root


def unpack_bits(payload, padding):
    """Recupera únicamente los bits útiles del archivo."""
    if not isinstance(padding, int) or not 0 <= padding <= min(7, len(payload) * 8):
        raise ValueError("Cantidad de bits de relleno inválida.")
    bits = bitarray(endian="big")
    bits.frombytes(payload)
    if padding:
        del bits[-padding:]
    return bits


def decode_with_tree(bits, root):
    """Recorre el árbol bit a bit y vuelve a la raíz después de cada hoja."""
    if root is None:
        if bits:
            raise ValueError("El archivo contiene bits sin árbol.")
        return ""
    if root.left is None and root.right is None:
        if bits.count(1):
            raise ValueError("Código inválido para un árbol de un solo símbolo.")
        return root.char * len(bits)

    characters = []
    current = root
    for bit in bits:
        current = current.right if bit else current.left
        if current.left is None and current.right is None:
            characters.append(current.char)
            current = root
    if current is not root:
        raise ValueError("El flujo termina con un código incompleto.")
    return "".join(characters)


def decompressBook(packed_bytes, padding, root):
    """Reconstruye el texto con los bytes y el árbol de compressBook."""
    return decode_with_tree(unpack_bits(packed_bytes, padding), root)


def inverse_dictionary(codes_dic):
    """Invierte los códigos y conserva sus ceros iniciales con un 1 de prefijo."""
    return {int("1" + code, 2): character for character, code in codes_dic.items()}


def decode_with_dictionary(bits, inverse):
    """Acumula cada prefijo y busca su símbolo en el diccionario inverso."""
    characters = []
    prefix = 1
    for bit in bits:
        prefix = (prefix << 1) | bit
        character = inverse.get(prefix)
        if character is not None:
            characters.append(character)
            prefix = 1
    if prefix != 1:
        raise ValueError("El flujo termina con un código desconocido o incompleto.")
    return "".join(characters)


def encode_file(source, output=None):
    """Escribe el encabezado pickle seguido de los bytes de compresión."""
    source = Path(source)
    output = Path(output) if output is not None else source.with_suffix(".huff")
    if output.suffix != ".huff":
        raise ValueError("El archivo comprimido debe tener la extensión .huff.")
    if source.resolve() == output.resolve():
        raise ValueError("Las rutas del original y del archivo comprimido deben ser distintas.")

    bits, codes_dic, root, average = encode_text(source.read_bytes().decode("utf-8"))
    with output.open("wb") as archive:
        pickle.dump((codes_dic, (-len(bits)) % 8, root), archive, protocol=4)
        archive.write(bits.tobytes())
    return output, average


class HuffmanUnpickler(pickle.Unpickler):
    """Restringe los objetos del encabezado a los nodos del árbol de Huffman."""

    def find_class(self, module, name):
        if name == "Node" and module in {"huffman", "parte1.huffman", "__main__"}:
            return Node
        raise pickle.UnpicklingError(f"Clase no admitida en el encabezado: {module}.{name}")


def read_archive(source):
    """Lee el encabezado y retira el relleno del flujo comprimido."""
    with Path(source).open("rb") as archive:
        codes_dic, padding, root = HuffmanUnpickler(archive).load()
        bits = unpack_bits(archive.read(), padding)
    return codes_dic, root, bits


def decode_file(source, output=None, method="arbol"):
    """Reconstruye un archivo UTF-8 con el decodificador solicitado."""
    if method not in {"arbol", "diccionario"}:
        raise ValueError(f"Decodificador desconocido: {method}.")
    source = Path(source)
    output = Path(output) if output is not None else source.with_suffix(".decodificado.txt")
    if source.resolve() == output.resolve():
        raise ValueError("Las rutas del comprimido y del archivo recuperado deben ser distintas.")

    codes_dic, root, bits = read_archive(source)
    if method == "arbol":
        text = decode_with_tree(bits, root)
    else:
        text = decode_with_dictionary(bits, inverse_dictionary(codes_dic))
    output.write_bytes(text.encode("utf-8"))
    return output


def visualize_tree(root, output):
    """Genera un PDF con Graphviz, etiquetando las ramas con sus bits."""
    graph = [
        "digraph Huffman {",
        'graph [labelloc=t, label="Árbol de Huffman", fontname="DejaVu Sans"];',
        'node [fontname="DejaVu Sans", style=filled, fillcolor="#e3eef8"];',
        'edge [fontname="DejaVu Sans"];',
    ]

    def add_node(node, name, code):
        if node.left is None and node.right is None:
            label = f"{node.char!r}\nFrecuencia {node.data}\nCódigo {code or '0'}"
            graph.append(f'{name} [shape=box, label={json.dumps(label, ensure_ascii=False)}];')
            return
        graph.append(f'{name} [label="{node.data}"];')
        for bit, child in (("0", node.left), ("1", node.right)):
            child_name = name + bit
            graph.append(f'{name} -> {child_name} [label="{bit}"];')
            add_node(child, child_name, code + bit)

    if root is None:
        graph.append('raiz [label="Texto vacío", shape=box];')
    else:
        add_node(root, "raiz", "")
    graph.append("}")
    subprocess.run(
        ["dot", "-Tpdf", "-o", str(output)],
        input="\n".join(graph),
        encoding="utf-8",
        check=True,
    )


def main():
    """Ejecuta las operaciones de compresión, descompresión o visualización."""
    parser = argparse.ArgumentParser(description="Compresión Huffman de archivos UTF-8.")
    commands = parser.add_subparsers(dest="command", required=True)

    encode = commands.add_parser("comprimir", help="Genera un archivo .huff.")
    encode.add_argument("entrada", type=Path)
    encode.add_argument("-o", "--salida", type=Path)
    decode = commands.add_parser("descomprimir", help="Recupera el texto original.")
    decode.add_argument("entrada", type=Path)
    decode.add_argument("-o", "--salida", type=Path)
    decode.add_argument("--metodo", choices=("arbol", "diccionario"), default="arbol")
    graph = commands.add_parser("graficar", help="Dibuja un árbol de Huffman en PDF.")
    graph.add_argument("entrada", type=Path)
    graph.add_argument("-o", "--salida", type=Path, default=Path("arbol_huffman.pdf"))

    args = parser.parse_args()
    try:
        if args.command == "comprimir":
            output, average = encode_file(args.entrada, args.salida)
            print(f"{output} ({average:.4f} bits por símbolo)")
        elif args.command == "descomprimir":
            print(decode_file(args.entrada, args.salida, args.metodo))
        else:
            symbols, frequencies = import_frequencies_from_txt(args.entrada)
            _, root = huffmanCodes(symbols, frequencies)
            visualize_tree(root, args.salida)
            print(args.salida)
    except (OSError, ValueError, EOFError, pickle.UnpicklingError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()

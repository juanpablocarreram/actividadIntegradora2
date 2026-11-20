"""
===============================================================
 Program : huffman.py
 Author  : Juan Manuel Ahuactzin
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
    python 05_huffman.py

Example:
    python 05_huffman.py

Dependencies:
    - Python 3.x
    - Standard libraries: heapq

Notes:
    - The program constructs the Huffman tree and prints its
      hierarchical representation, followed by the Huffman code
      assigned to each character.
    - The __str__ method allows visualization of the recursive 
      structure, indicating '0' for left edges and '1' for right 
      edges.
===============================================================
"""


import heapq
import pandas as pd
import numpy as np
import os
from collections import Counter

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
			result += self.left.__str__(level + 1, prefix="L-0- ", cumchain=cumchain+'0')
		if self.right:
			result += self.right.__str__(level + 1, prefix="R-1- ", cumchain=cumchain+'1')
		return result
	
# Function to traverse tree in preorder 
# manner and push the huffman representation 
# of each character.
def preOrder(root, ans, curr):
	if root is None:
		return

	# Leaf node represents a character.
	if root.left is None and root.right is None:
		ans[root.char] = curr
		return

	preOrder(root.left, ans, curr + '0')
	preOrder(root.right, ans, curr + '1')

def huffmanCodes(s, freq):
	# Code here
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

	root = heapq.heappop(pq)
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
def import_frequencies_from_txt(path):
    with open(path,"r",encoding='UTF-8') as file:
        content = file.read()
        frequencies = Counter(content).items()
        s , freq = [], []
        for key, value in frequencies:
            s.append(key)
            freq.append(value)
        return s, freq
"""
Function that takes the relative path of the book on the curr dir
and processes it by using huffman encoding returning an array of bytes, the padding used
for having bytes of exactly 8 bits, the dictionary of key (char) - values(huffman code) and
the root of the huffman code using the class Node defined below
"""
def compressBook(path):
	s, freq = import_frequencies_from_txt(path)
	codes_dic, root = huffmanCodes(s,freq)
	compressed_book = []
	total_chars = 0
	with open(path,"r",encoding = 'UTF-8') as file:
		for curr_char in file.read():
			code = codes_dic[curr_char]
			total_chars += len(code)
			compressed_book.append(code)
	padding = 8 - (total_chars % 8) if total_chars % 8 != 0 else 0
	compressed_book.append('0' * padding)
	bit_string = "".join(compressed_book)
	byte_len = (total_chars + padding) // 8
	packed_bytes = int(bit_string,2).to_bytes(byte_len,"big")
	return packed_bytes,padding, codes_dic, root

""" 
Function that takes the a byte array, the padding added by the compressor and the root
of the Huffman tree for returning the original string of the book
 """
def decompressBook(packed_bytes,padding,root):
	if not packed_bytes or not root:
		return ""
	book_rebuild = []
	curr_node = root
	for byte_idx, byte in enumerate(packed_bytes):
		lower_limit = -1 if byte_idx != len(packed_bytes) - 1 else padding - 1
		for curr_bit in range(7,lower_limit,-1):
			if (byte >> curr_bit) & 1:
				curr_node = curr_node.right
			else:
				curr_node = curr_node.left
			if not curr_node.left and not curr_node.right:
				book_rebuild.append(curr_node.char)
				curr_node = root
	return "".join(book_rebuild)

if __name__ == "__main__":
	book_path = "dracula.txt"
	with open(book_path,"r",encoding='UTF-8') as file:
		original_text = file.read()
		original_length_in_bytes = len(original_text.encode('UTF-8'))
	packed_bytes,trailing_zeros,codes, root = compressBook(book_path)
	print(f"Original Length (bytes): {original_length_in_bytes}\nCompressed Length (bytes): {len(packed_bytes)}")
	decompressed_original_string = decompressBook(packed_bytes,trailing_zeros,root)
	print(original_text == decompressed_original_string)
	
# Parte 1 · Compresión de Huffman

El programa comprime archivos de texto UTF-8 y permite recuperarlos por medio del árbol de Huffman o de un diccionario inverso. La compresión conserva los caracteres y los saltos de línea del original.

## Instalación y uso

Desde la carpeta `parte1`, instala las dependencias con Python 3.12. Para generar el PDF se requiere el ejecutable `dot` de Graphviz en el `PATH`.

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt

python huffman.py comprimir corpus/en/dracula.txt -o dracula.huff
python huffman.py descomprimir dracula.huff --metodo arbol -o dracula_arbol.txt
python huffman.py descomprimir dracula.huff --metodo diccionario -o dracula_diccionario.txt

printf 'café y té' > ejemplo.txt
python huffman.py graficar ejemplo.txt -o resultados/arbol_huffman.pdf
```

El encabezado pickle de cada `.huff` contiene `(codes_dic, padding, root)`. A continuación se guardan los bytes comprimidos, con el bit más significativo primero. `padding` indica cuántos bits de relleno hay al final del flujo, entre 0 y 7.

## Experimento reproducible

```bash
python experimento.py --repeticiones 200
```

El programa comprime los 30 textos del corpus a `resultados/comprimidos/`, comprueba ambos decodificadores y genera las tablas CSV. El corpus contiene diez archivos por idioma. En [fuentes.csv](corpus/fuentes.csv) se registra la edición de Project Gutenberg y la codificación de origen de cada archivo. Las ediciones en Latin-1 se convirtieron a UTF-8 para la medición.

- [Estadísticas por archivo](resultados/estadisticas_por_archivo.csv)
- [Estadísticas por idioma](resultados/estadisticas_por_idioma.csv)
- [Tiempos de decodificación](resultados/tiempos_decodificacion.csv)
- [Árbol de Huffman de «café y té»](resultados/arbol_huffman.pdf)
- [Reflexión sobre los algoritmos y resultados](reflexion.md)

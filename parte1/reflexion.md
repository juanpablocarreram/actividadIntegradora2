# Reflexión · Compresión y decodificación de Huffman

La construcción conserva el algoritmo de clase. Primero se cuenta cada carácter Unicode. Luego se introducen los símbolos en una cola de prioridad ordenada por frecuencia y se combinan los dos nodos de menor peso hasta obtener una raíz. La rama izquierda aporta un 0 y la derecha un 1. Como los caracteres aparecen en hojas, ningún código válido es prefijo de otro. Esto permite emitir un carácter en cuanto se reconoce su código y reiniciar la búsqueda. Para un texto de un solo carácter distinto se usa el código `0`, de modo que cada aparición quede registrada.

La longitud media se calcula como **Σ(frecuencia × longitud del código) / Σ(frecuencia)**. El cálculo equivale a dividir el número de bits útiles entre la cantidad de caracteres. Al codificar, las secuencias se convierten a `bitarray` y se empaquetan en bytes. El tamaño medido del archivo `.huff` incluye el encabezado con el diccionario, el árbol y el conteo de relleno.

## Complejidad computacional

Sea **N** la cantidad de caracteres, **K** la cantidad de caracteres distintos, **B** la cantidad de bits útiles y **S** la suma de las longitudes de los **K** códigos. La tabla usa el modelo habitual de acceso promedio constante a diccionarios y de operaciones constantes sobre enteros que caben en una palabra.

| Etapa | Tiempo | Memoria adicional |
| --- | --- | --- |
| Conteo de frecuencias con `Counter` | O(N) | O(K) |
| Construcción del árbol con `heapq` | O(K log K) | O(K) |
| Recorrido en preorden y generación de códigos | O(K + S) | O(K + S), incluido el diccionario |
| Cálculo de bits promedio por símbolo | O(K) | O(1), a partir de las frecuencias y los códigos |
| Conversión a `bitarray` y codificación del texto | O(S + N + B) | O(K + S + B), incluido el flujo comprimido |
| Preparación del diccionario inverso | O(K + S) | O(K + S), incluidas las claves enteras |
| Decodificación con diccionario inverso | O(B + N) | O(N), dado el diccionario inverso |
| Decodificación con el árbol | O(B + N) | O(N), dado el árbol |

En la versión con diccionario, el prefijo se representa como un entero con un 1 inicial. Así se distinguen códigos como `0` y `00` sin construir una cadena nueva por cada bit. Si los prefijos son lo bastante largos para abarcar varias palabras, el costo de desplazar, combinar y consultar esos enteros crece con su longitud. La versión con árbol realiza un salto de nodo por bit y, al llegar a una hoja, añade el carácter al resultado. Ambas versiones recorren el flujo una vez y reservan espacio para el texto reconstruido.

## Compresión del corpus

| Idioma | Compression factor promedio | Bits promedio por símbolo |
| --- | ---: | ---: |
| Español | 0.5799 | 4.5709 |
| Francés | 0.6027 | 4.6519 |
| Inglés | 0.5697 | 4.5328 |

Los valores son medias aritméticas de diez archivos por idioma, con el mismo peso para cada archivo. En esta muestra el inglés obtuvo el menor factor medio y el francés el mayor. El factor depende tanto de las frecuencias de los símbolos como de los bytes UTF-8 del original y del peso relativo del encabezado. Los resultados describen este corpus literario y su formato.

## Tiempos de decodificación

Se eligió el archivo más pequeño de cada idioma para realizar 200 repeticiones por método. Se utilizó `perf_counter_ns` con Python 3.12.3 en un Intel Core i9-13900HX. Se ejecutó una primera decodificación por método sin cronometrarla y se alternó el orden de ejecución durante las mediciones. El cronómetro cubrió la reconstrucción del texto en memoria. La lectura del archivo, la conversión del flujo a `bitarray` y la preparación del diccionario inverso se hicieron antes de medir. La desviación estándar es muestral.

| Idioma y archivo | Diccionario, media ± DE (ms) | Árbol, media ± DE (ms) |
| --- | ---: | ---: |
| Español · `el_si_de_las_ninas.txt` | 16.955 ± 0.299 | 25.028 ± 0.442 |
| Francés · `le_chat_du_neptune.txt` | 4.481 ± 0.056 | 6.190 ± 0.093 |
| Inglés · `jekyll_and_hyde.txt` | 20.574 ± 0.206 | 28.629 ± 0.303 |

El diccionario inverso reconstruyó los tres textos en menos tiempo que el árbol en esta ejecución. Las dos estrategias tienen el mismo orden de crecimiento bajo el modelo descrito. Sus constantes difieren porque una consulta una clave entera por bit y la otra lee atributos de los nodos para avanzar y reconocer hojas. La comparación usa el mismo flujo de bits para ambos métodos dentro de cada archivo.

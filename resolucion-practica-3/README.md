# Entrega práctica 3 — Bases de datos NoSQL

- **Nombre:** Matias Odello
- **student_id:** matio
- **Escala:** small

## CAP y PACELC

**1.** En CP, `C` devolvió error al leer y al escribir (no tenía quórum): pierde disponibilidad. En AP devolvió 100, un dato viejo, y aceptó escribir 50: pierde consistencia.

**2.** Quedaron las tres en 50. Se perdió el `saldo=80` escrito en `A`, porque last-write-wins se quedó con la escritura más nueva.

**3.** p99 de 9,6 ms con `W=1` y 55,6 ms con `W=3`. Esperar más réplicas da más consistencia a costa de latencia.

**4.** Siguió escribiendo `ABC`, porque tiene 3 de 5 réplicas (mayoría). `DE` no llega al quórum.

## Clave-valor

**5.** El GET en memoria fue ~1.800.000 veces más rápido (0,0003 ms contra 468 ms con Spark). Redis usa RAM para que buscar una clave tarde microsegundos.

**6.** Porque el valor es opaco: la base sólo conoce la clave y el país está dentro del JSON, así que para encontrar los 992 clientes de AR hubo que parsear los 5.000 valores. Ventaja: GET/SET en O(1) y fácil de distribuir. Desventaja: no se puede consultar por valor ni hacer joins.

**7.** Con `mod N` se movió el 79,6 % de las claves y con hashing consistente el 21,2 %. Conviene el segundo porque al agregar un nodo sólo se mueven las claves de su tramo del anillo.

## Documental

**8.** La relacional devolvió 11 filas y la documental 1 documento. Quedaron embebidos el perfil, las stats y las transacciones con una copia del producto.

**9.** Spark armó un esquema con la unión de todos los campos y puso `null` en los que faltaban. Es flexible porque cada documento puede tener campos distintos y el esquema se aplica al leer.

**10.** El más grande pesa 5,2 KB (unos 225 bytes por transacción, así que haría falta ~75.000 compras para llegar a 16 MB). Si crece sin límite se acerca al tope de 16 MB y leerlo o actualizarlo se vuelve cada vez más caro.

**11.** Le van bien las consultas por entidad (todo un cliente en una lectura). Le cuestan las agregaciones entre documentos, como el monto por categoría.

## Grafos

**12.** 5.000 nodos `Customer` (738 marcados), 2.361 nodos `Device` y 5.400 aristas `USES`.

**13.** 3 joins para 2 saltos (alcanzó 1.389 clientes) y 5 para 4 saltos (254). Neo4j guarda en cada nodo punteros a sus vecinos (index-free adjacency), así que saltar es seguir un puntero y no hacer un join contra toda la tabla.

**14.** Convergió en 14 iteraciones (en la 14 ya no cambió ningún nodo); el componente más grande tiene 23 nodos.

**15.** Con `hash(id) mod 4` quedó cortado el 74,4 % de las aristas, contra 0 % repartiendo por componente. Es difícil distribuir un grafo porque las consultas recorren aristas, y cada arista entre máquinas es un salto por la red.

## Vectorial

**16.** El vector resume el comportamiento del cliente: cómo reparte el gasto por categoría y por canal, y su ticket. La similitud coseno mide qué tan parecida es la dirección de dos vectores.

**17.** Entre los vecinos de marcados hay 31,6 % de marcados, contra una tasa base de 14,8 % (y 13,2 % entre los vecinos de no marcados). Buscar vecinos parecidos sirve para clasificar por similitud, detectar fraude o recomendar.

**18.** Con `nprobe=4`, recall@10 de 0,872 escaneando sólo el 6 % de los vectores. ANN es mucho más rápido, pero puede perder algunos vecinos verdaderos.

## Columnar

**19.** CSV 50,0 MB, JSON 121,1 MB y Parquet 5,3 MB (9,4 veces menos que CSV). El `ReadSchema` fue `struct<amount:decimal(12,2)>`: sólo se leyó `amount`. Con los datos ordenados se pueden saltear 7 de 8 archivos; al azar, 0.

**20.** Es bueno para analítica porque lee sólo las columnas que necesita, comprime mejor y saltea bloques con min/max. Para cambiar una fila hay que reescribir archivos comprimidos enteros.

# Entrega práctica 4 — Streaming

- **Nombre:** Matias Odello
- **student_id:** matio
- **Escala:** small

## Log y offsets

**1.** En la cola quedaron 2 mensajes y en el log siguieron los 5. En una cola leer borra el mensaje; en un log se conserva y cada consumidor sólo avanza su offset.

**2.** `antifraude` había leído 180 y `reportes` 0. El atraso de `reportes` no afectó a `antifraude`, porque cada uno tiene su propio checkpoint y leer no modifica el topic.

**3.** El offset es la posición del log hasta donde leyó cada consumidor. Acá se guarda en el checkpoint de cada consulta, como versión de la tabla Delta: al final los dos apuntaban a la versión 6, la siguiente a la última del topic (5).

**4.** El replay leyó 280 mensajes. Kappa reprocesa releyendo el log con el mismo código de streaming; Lambda mantiene un camino batch y otro streaming con la lógica duplicada.

## Ingesta y enriquecimiento

**5.** Bronze procesó 60, 120, 40, 40 y 20 filas en cada llegada, y 0 al reejecutar sin archivos nuevos. Lo evita el checkpoint de Auto Loader, que recuerda qué archivos ya leyó.

**6.** En la llegada 2 aparecieron `INVALID_AMOUNT` y `UNKNOWN_CUSTOMER`. Bronze guarda el texto original para no perder datos y poder reprocesarlos si se corrige la regla.

**7.** Agregó `country` y `category`. Es un join stream-tabla.

## Tiempo y ventanas

**8.** Event time es cuándo pasó el evento y processing time es cuándo llega. `late_ok` pasó a las 12:03 pero llegó en la llegada 2, y aun así se contó en la ventana de 12:00.

**9.** El watermark fue 11:54, 11:58, 12:16, 12:17 y 12:35. Se calcula como el máximo event time visto menos 10 minutos.

**10.** Aparecieron en la llegada 3. En append una ventana se emite recién cuando el watermark supera su fin, y antes el watermark no llegaba a 12:05.

**11.** `late_bad` (12:02) se descartó porque era más viejo que el watermark, que ya estaba en 12:16. `late_ok` llegó cuando el watermark era 11:54, dentro del margen.

**12.**
- **Tumbling:** ventanas fijas que no se solapan. Ejemplo: ventas cada 5 minutos.
- **Hopping:** ventanas que se solapan. Ejemplo: compras de los últimos 10 minutos, recalculadas cada 5.
- **Session:** ventanas por cliente que se cierran tras un rato sin actividad. Ejemplo: la sesión de compra de un usuario.

**13.** En update se emitió dos veces: 40 compras ($6.000) en la llegada 1 y 60 compras ($8.400) en la llegada 2. En append se emitió una sola vez, en la llegada 3, con 60 compras ($8.400). Update da resultados antes pero con correcciones; append es definitivo pero llega más tarde.

**14.** Con 1 minuto las ventanas cerrarían antes y habría menos estado en memoria. Pero se descartarían más eventos tardíos y los resultados quedarían incompletos.

## Garantías y fallas

**15.** Quedaron 220 filas sin deduplicar y 200 deduplicando. El productor reintenta cuando no sabe si el envío llegó, y así se duplica el evento.

**16.** Con el mismo checkpoint no se escribió nada nuevo (siguió en 200): exactly-once. Al perder el checkpoint se reprocesó todo y quedaron 400: at-least-once.

**17.** El `MERGE` sólo inserta los `event_id` que no existen, así que reprocesar no cambia nada. Idempotente significa que aplicar la operación varias veces da el mismo resultado que aplicarla una.

## CDC

**18.** El log tuvo 13 eventos: 6 `insert`, 3 `update_preimage`, 3 `update_postimage` y 1 `delete`. Un `UPDATE` genera dos eventos porque guarda la fila de antes y la de después.

**19.** Sí, la reconstrucción quedó igual a la tabla. El log además guarda la historia: que el cliente 2 pasó por CL y que el cliente 3 existió.

## Cierre

**20.**
- **Spark Structured Streaming:** si ya estoy en el Lakehouse; misma API para batch y streaming.
- **Flink:** si necesito latencia de milisegundos y mucho estado.
- **Kafka Streams:** si todo ya está en Kafka; es una librería liviana sin cluster aparte.

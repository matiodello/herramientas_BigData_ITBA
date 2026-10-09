## Matías Odello / student_id = matio


## Captura del DAG del job


## URL del Job + nombre exacto

https://dbc-a135d14b-b053.cloud.databricks.com/jobs/89629748561757?o=7474651089232214

bigdata_matio_silver_gold

## Resultados de la primera y segunda ejecucion

Primera ejecucion:

|job_run_id|expected_batch_id|silver_rows|quarantine_rows|gold_rows|gold_total_amount|recorded_at|idempotence_compared|
|---|---|---|---|---|---|---|---|
|826449793655254|batch_002|50149|53|598|50286183.33|2026-10-03T13:03:48.888Z|false|

Segunda ejecucion:

|job_run_id|expected_batch_id|silver_rows|quarantine_rows|gold_rows|gold_total_amount|recorded_at|idempotence_compared|
|---|---|---|---|---|---|---|---|
|355827486323868|batch_002|50149|53|598|50286183.33|2026-10-03T13:06:05.685Z|true|
|826449793655254|batch_002|50149|53|598|50286183.33|2026-10-03T13:03:48.888Z|false|

## Cantidades aceptadas y rechazadas para batch_002

|source_batch_id|accepted_transactions|rejected_transactions|total_amount|fraud_transactions|refreshed_at|
|---|---|---|---|---|---|
|batch_002|201|2|146812.99|28|2026-10-03T13:05:43.737Z|
|initial|49948|51|50139370.34|6560|2026-10-03T13:05:43.737Z|

## Explicacion breve de por que COPY INTO & MERGE resuelven problemas diferentes

## Diferencias entre `COPY INTO` y `MERGE`

### COPY INTO
Carga archivos desde el origen a una tabla, llevado un registro de lo que cargó, por lo que no duplica archivos.
No analiza el contenido, por lo que si un mismo `id` llega en dos archivos distintos, el contenido se duplica.

### MERGE
Compara el origen contra el destino por claves para operaciones de inserción y actualización.
Hace deduplicación por clave, por lo que si se reprocesa un mismo archivo y la lógica es la correcta, no genera duplicados.

## Explicacion del grano de cada tabla GOLD

La tabla gold esta a nivel dia, la granularidad seria esa.

## Visualizaciones:

![alt text](<Consigna 1 — Evolución temporal.png>)

Día de mayor monto: 2026-03-01 ($7,310,840.77, 7,236 transacciones, ticket promedio $1,010.34).
Día de más transacciones: 2026-03-01 (7,236 transacciones, ticket promedio $1,010.34).
Respuesta: Sí, ambos máximos coinciden. El día de mayor monto también fue el de más transacciones, por lo que el récord de ventas se explica principalmente por mayor volumen de operaciones y no por un ticket promedio inusualmente alto.

![alt text](<Consigna 2 — Canal y fraude.png>)

Respuesta: el canal con mayor tasa de fraude es 'transfer' (13.91% sobre 16,723 transacciones).
La conclusión es frágil: el intervalo de 'transfer' se solapa con el de 'wallet', por lo que con este volumen no se puede afirmar que su tasa sea realmente mayor.

![alt text](<Consigna 3 — Concentración geográfica y de producto.png>)

Respuesta: no hay una categoría dominante en todos los países. El liderazgo cambia según el mercado (home, books), por lo que la mezcla de producto depende del país.
La combinación de mayor monto es BR - home.

![alt text](<Consigna 4 — Calidad del pipeline.png>)

|source_batch_id|accepted_transactions|rejected_transactions|total|accepted_pct|rejected_pct|
|---|---|---|---|---|---|
|batch_002|200|2|202|99.01|0.99|
|batch_003|201|2|203|99.01|0.99|
|initial|49948|51|49999|99.9|0.1|



## Preguntas de análisis y compresión

#1: SELECT source_batch_id,
       COUNT(*)                       AS filas_fisicas,
       COUNT(DISTINCT transaction_id) AS ids_distintos
FROM bronze_transactions_incremental
GROUP BY source_batch_id
ORDER BY source_batch_id;

|source_batch_id|filas_fisicas|ids_distintos|
|---|---|---|
|batch_002|204|203|
|batch_003|204|203|

#2

WITH bronze AS (
  SELECT source_batch_id, COUNT(*) AS filas_fisicas
  FROM bronze_transactions_all GROUP BY source_batch_id
), aceptadas AS (
  SELECT source_batch_id, COUNT(*) AS aceptadas
  FROM silver_transactions GROUP BY source_batch_id
), rechazadas AS (
  SELECT source_batch_id, COUNT(*) AS rechazadas
  FROM silver_transactions_quarantine GROUP BY source_batch_id
)
SELECT g.source_batch_id,
       b.filas_fisicas,
       COALESCE(a.aceptadas, 0)  AS aceptadas_silver,
       g.accepted_transactions   AS aceptadas_gold,
       COALESCE(r.rechazadas, 0) AS rechazadas_silver,
       g.rejected_transactions   AS rechazadas_gold,
       b.filas_fisicas - g.accepted_transactions - g.rejected_transactions AS no_explicadas,
       (COALESCE(a.aceptadas, 0) = g.accepted_transactions
        AND COALESCE(r.rechazadas, 0) = g.rejected_transactions) AS reconcilia
FROM gold_batch_summary g
LEFT JOIN bronze     b ON b.source_batch_id = g.source_batch_id
LEFT JOIN aceptadas  a ON a.source_batch_id = g.source_batch_id
LEFT JOIN rechazadas r ON r.source_batch_id = g.source_batch_id
ORDER BY g.source_batch_id;


|source_batch_id|filas_fisicas|aceptadas_silver|aceptadas_gold|rechazadas_silver|rechazadas_gold|no_explicadas|reconcilia|
|---|---|---|---|---|---|---|---|
|batch_002|204|200|200|2|2|2|true|
|batch_003|204|201|201|2|2|1|true|
|initial|50011|49948|49948|51|51|12|true|

#3: SELECT source_batch_id,
       quality_reason,
       COUNT(*) AS registros
FROM silver_transactions_quarantine
GROUP BY source_batch_id, quality_reason
ORDER BY source_batch_id, quality_reason;

|source_batch_id|quality_reason|registros|
|---|---|---|
|batch_002|INVALID_AMOUNT|1|
|batch_002|UNKNOWN_CUSTOMER|1|
|batch_003|INVALID_AMOUNT|1|
|batch_003|UNKNOWN_CUSTOMER|1|
|initial|INVALID_AMOUNT|51|

|source_batch_id|transaction_id|customer_id|amount|quality_reason|
|---|---|---|---|---|
|batch_002|50620|19|N/A|INVALID_AMOUNT|
|batch_002|50621|5999|27.84|UNKNOWN_CUSTOMER|
|batch_003|50830|20|N/A|INVALID_AMOUNT|
|batch_003|50831|5999|28.85|UNKNOWN_CUSTOMER|



#4: Primero las consultas SQL que utilicé:

  SELECT transaction_id, source_batch_id, updated_at, event_ts,
         amount, device_id, is_fraud, customer_id, product_id
  FROM bronze_transactions_all
  WHERE transaction_id = '42'
  ORDER BY updated_at;

|transaction_id|source_batch_id|updated_at|event_ts|amount|device_id|is_fraud|customer_id|product_id|
|---|---|---|---|---|---|---|---|---|
|42|initial|2026-03-06 02:07:52|2026-03-06 02:07:52|600.11|device_893|0|317|273|
|42|batch_002|2026-03-10 02:00:00|2026-03-10 00:00:00|1999.99|device_corrected_42|1|0|0|
|42|batch_003|2026-03-11 02:00:00|2026-03-11 00:00:00|1999.99|device_corrected_42|1|0|0|


En bronce hay 3 versiones, la inicial, la batch_02 y la batch_03.

Con las siguientes consultas vemos que, en silver, sobrevive una sola basicamente porque al actualizarse batch_02 queda la segunda correccción con batch_03.

  SELECT transaction_id, source_batch_id, updated_at, amount,
         device_id, is_fraud, processed_at
  FROM silver_transactions
  WHERE transaction_id = 42;

  |transaction_id|source_batch_id|updated_at|amount|device_id|is_fraud|processed_at|
|---|---|---|---|---|---|---|
|42|batch_003|2026-03-11T02:00:00.000Z|1999.99|device_corrected_42|1|2026-10-03T13:07:58.891Z|

5. 

  SELECT COUNT(*)                       AS filas,
         COUNT(DISTINCT transaction_id) AS ids_distintos
  FROM silver_transactions;

  |filas|ids_distintos|
|---|---|
|50349|50349|

Con la consulta   SELECT transaction_id, COUNT(*) AS veces
  FROM silver_transactions
  GROUP BY transaction_id
  HAVING COUNT(*) > 1;

vemos si hay repetidos o no. no devuelve nada asique no los hay. Si devolviese una tupla sería un problema porque indicaría deduplicación.

6. Consulta SQL

  SELECT source_batch_id,
         accepted_transactions,
         rejected_transactions,
         accepted_transactions + rejected_transactions AS total,
         ROUND(100.0 * rejected_transactions
               / (accepted_transactions + rejected_transactions), 2) AS tasa_rechazo_pct
  FROM gold_batch_summary
  ORDER BY source_batch_id;


|source_batch_id|accepted_transactions|rejected_transactions|total|tasa_rechazo_pct|
|---|---|---|---|---|
|batch_002|200|2|202|0.99|
|batch_003|201|2|203|0.99|
|initial|49948|51|49999|0.10|

  - initial: 0,10% de rechazo.
  - Cada lote: 0,99%, unas 10 veces más.

7.   Consulta

  SELECT sale_date,
         SUM(total_amount)       AS monto_total,
         SUM(transaction_count)  AS transacciones,
         ROUND(SUM(total_amount) / SUM(transaction_count), 2) AS ticket_promedio
  FROM gold_daily_sales
  GROUP BY sale_date
  ORDER BY monto_total DESC;


  SELECT sale_date,
         SUM(transaction_count)  AS transacciones,
         SUM(total_amount)       AS monto_total
  FROM gold_daily_sales
  GROUP BY sale_date
  ORDER BY transacciones DESC;

 Sumando gold_daily_sales por sale_date (la tabla tiene grano día × país × categoría × canal, así que hay que agregar primero), el día de mayor monto es el 2026-03-01 ($7.310.840,77) y también es el de más transacciones (7.236). Ambos máximos coinciden. Como el ticket promedio de ese día ($1.010,34) es similar al promedio general (~$1.000), el récord de monto se explica por mayor volumen de operaciones y no por tickets más altos.


 8.   Consulta

  SELECT payment_channel,
         SUM(fraud_transactions)  AS fraudes,
         SUM(transaction_count)   AS transacciones,
         ROUND(100.0 * SUM(fraud_transactions) / SUM(transaction_count), 2) AS tasa_fraude_pct
  FROM gold_daily_sales
  GROUP BY payment_channel
  ORDER BY tasa_fraude_pct DESC;

El canal con mayor tasa global de fraude es transfer (13,91% sobre 16.723 transacciones), calculada como SUM(fraud_transactions) / SUM(transaction_count). No corresponde promediar fraud_rate porque cada fila de gold_daily_sales agrupa una cantidad distinta de transacciones: el promedio simple le daría el mismo peso a una fila con 1 transacción que a una con cientos, y distorsionaría el resultado. Sumar numeradores y denominadores pondera cada fila por su volumen.

9. consulta: 

 SELECT country, category,
         SUM(total_amount) AS monto_total
  FROM gold_daily_sales
  GROUP BY country, category
  ORDER BY monto_total DESC
  LIMIT 1;


  WITH por_pais_categoria AS (
    SELECT country, category,
           SUM(total_amount) AS monto_total
    FROM gold_daily_sales
    GROUP BY country, category
  ),
  ranking AS (
    SELECT *,
           row_number() OVER (PARTITION BY country ORDER BY monto_total DESC) AS puesto
    FROM por_pais_categoria
  )
  SELECT country, category, monto_total
  FROM ranking
  WHERE puesto = 1
  ORDER BY monto_total DESC;

10. Consulta:


  SELECT job_run_id, expected_batch_id, silver_rows, quarantine_rows,
         gold_rows, gold_total_amount, recorded_at, idempotence_compared
  FROM pipeline_run_audit
  WHERE expected_batch_id = 'batch_002'
  ORDER BY recorded_at;

En las dos ejecuciones de batch_002 permanecen iguales silver_rows (50149), quarantine_rows (53), gold_rows (598) y gold_total_amount (50.286.183,33). Solo cambian job_run_id y recorded_at. La columna que demuestra la comparación es idempotence_compared: vale false en la primera corrida porque no había una ejecución previa del mismo lote, y true en la segunda, donde el notebook 04_validate_pipeline comparó las métricas con la corrida anterior. Como coincidieron, el assert no falló y se registró la fila.


## Interpretación del código y del pipeline

11. (notebook 01, celda del COPY INTO)

COPY INTO sirve para cargar de forma incremental los archivos que van cayendo en la carpeta incoming/transactions. Cada vez que corre se fija qué archivos ya cargó antes (la tabla guarda un registro de los archivos cargados por su ruta) y solo trae los nuevos. Por eso cuando corrí el job dos veces con batch_002 no se duplicó nada. Lo que no hace es revisar el contenido: si el mismo transaction_id viene en dos archivos distintos se cargan los dos, y eso se arregla después en silver.

12. (notebook 01, vista bronze_transactions_all, y notebook 02)

Porque bronze es la capa cruda y la idea es guardar todo lo que llegó, aunque haya duplicados o versiones viejas, para poder auditar o volver a procesar si hace falta. Además un UNION solo saca las filas que son exactamente iguales, y los duplicados que importan no son así. La transacción 42 por ejemplo llega con otro monto y otra fecha, así que un UNION no la detectaría igual. Esos duplicados de negocio se resuelven en silver, que es donde se aplica la regla de quedarse con la versión con updated_at más nuevo (row_number + MERGE).

13. (notebook 01, vista bronze_transactions_all)

La tabla de la práctica 1 no tenía source_batch_id ni updated_at, y para hacer el UNION ALL con la tabla incremental las dos tienen que tener las mismas columnas. Entonces se completan: 'initial' para saber que vienen de la carga original, y event_ts como updated_at porque es lo más parecido que hay a una fecha de versión. En el caso de la 42, la versión inicial queda con un updated_at viejo (su event_ts), y las correcciones tienen updated_at 2026-03-10 02:00 (batch_002) y 2026-03-11 02:00 (batch_003), así que cuando silver ordena por updated_at gana la corrección.
Algo que me llamó la atención es que si hubiera empate en updated_at, el desempate es por source_batch_id descendente, y 'initial' queda antes que 'batch_...' por orden alfabético, así que ganaría la versión vieja.

14. (quality_rules.py, función add_transaction_types)

Con un cast normal (con ANSI activado, que es lo default en Databricks), si llega "N/A" en el amount la conversión tira error y se cae toda la tarea por una sola fila. try_cast en cambio devuelve NULL y el proceso sigue. Después la regla de calidad ve que amount_typed es NULL, le pone INVALID_AMOUNT y la fila va a cuarentena. Como también se guarda la columna original en texto, en la cuarentena queda el "N/A" tal cual llegó.

15. (quality_rules.py, función add_quality_reason)

Las reglas están armadas como una cadena de when, entonces se evalúan en orden y la primera que se cumple es la que queda como quality_reason. Si un registro tiene más de un problema solo se registra el primero, los otros no aparecen. Por eso el orden importa, porque cambia qué motivo se informa y cómo quedan los conteos en la cuarentena.
Además hay reglas que dependen de otras. Si el customer_id no es un número, customer_id_typed queda NULL y el join con clientes también da NULL. Si UNKNOWN_CUSTOMER estuviera antes, se informaría "cliente desconocido" cuando el problema real es que el id está mal formado. Por eso primero van las validaciones de formato y al final las de clientes y productos.

16. (notebook 02, celda de _record_key y row_number)

_record_key es el transaction_id convertido a número, y si no se puede convertir se usa un hash (sha2) de todas las columnas de la fila. Después row_number agrupa por esa clave, ordena por updated_at de más nuevo a más viejo y se queda con la fila 1, o sea una sola versión por transacción.
El hash está para cuando el transaction_id viene mal. Sin él, todas esas filas tendrían clave NULL, quedarían en el mismo grupo y row_number se quedaría con una sola, perdiendo las demás. Con el hash cada fila distinta tiene su propia clave y termina en cuarentena con INVALID_TRANSACTION_ID.

17. (notebook 02, MERGE de silver_transactions)

El MERGE compara lo que llega con lo que ya está en silver por transaction_id. Si la transacción ya existe y la que llega tiene un updated_at más nuevo, se actualiza la fila entera (UPDATE SET *). Eso es lo que pasó con la 42, que además quedó con source_batch_id = batch_003. Si la transacción no existe, se inserta, como las 200 nuevas de cada lote.
Y si existe pero lo que llega no es más nuevo, no pasa nada. Eso es lo que hace que volver a correr el job no cambie los datos, y también evita que una versión vieja pise a una más nueva.

18. (notebook 03 con CREATE OR REPLACE, notebook 02 con MERGE)

Gold se borra y se arma de nuevo en cada corrida. La ventaja es que es simple y siempre queda igual a silver: una corrección como la de la 42 cambia números en varios grupos a la vez (el lote, el día, el monto) y calcular eso de forma incremental sería complicado. La desventaja es que a medida que crecen los datos cada corrida tarda más, porque se recalcula todo aunque hayan llegado solo 200 filas.

Silver con MERGE solo toca lo que cambió: inserta lo nuevo, actualiza lo corregido y se puede reejecutar sin problema. La contra es que es más complejo, necesitás una clave confiable y una columna para saber qué versión es más nueva, y si eso está mal podés terminar con duplicados o pisando datos buenos. Igual en esta práctica silver lee toda la vista de bronze cada vez, así que la lectura tampoco es incremental del todo.

19. (notebook 01 y notebook 04)

Porque el que detecta los archivos nuevos es el COPY INTO del notebook 01, que carga cualquier archivo de la carpeta que todavía no haya cargado, sin importar el nombre ni el parámetro. Así no hay que tocar nada para procesar un lote nuevo.
expected_batch_id solo se usa en el notebook 04 para validar: que el lote llegó a bronze y a silver, que tiene sus rechazos en cuarentena, que aparece en gold_batch_summary, que la corrección de la 42 quedó con ese lote, y para decidir si compara la corrida con la anterior (idempotencia). Los notebooks 01 a 03 tienen el widget pero no lo usan. Si el parámetro se usara en la ingesta y te olvidás de cambiarlo, quedarían archivos sin procesar. Así como está, lo peor que puede pasar es que falle la validación.

20. (DAG del job y assert del notebook 03)

Las tareas están encadenadas (ingesta → silver → gold → validate) y cada una corre solo si la anterior terminó bien. Si falla build_silver, build_gold y validate no se ejecutan (aparecen como Upstream failed) y el job queda en error. De esta forma no se arma gold con un silver a medio hacer, gold se queda con la última versión buena, y tampoco se valida ni se escribe en pipeline_run_audit una corrida que falló. Como todo es idempotente, alcanza con arreglar el error y volver a correr.
Además los notebooks tienen un assert al principio que chequea que existan las tablas que necesitan, por si alguien los corre sueltos fuera del job.

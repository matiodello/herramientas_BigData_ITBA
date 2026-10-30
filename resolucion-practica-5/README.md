# Entrega práctica 5 — MLOps con MLflow

- **Nombre:** Matias Odello
- **student_id:** matio
- **Escala:** small

## Mis runs

| run | modelo | features | class_weight | umbral | hiperparametros | train_pr_auc | pr_auc | accuracy | precision | recall | f1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| max_depth=3 | gradient_boosting | completas | ninguno | 0.3 | learning_rate=0.1, max_depth=3 | 0.608 | 0.585 | 0.908 | 0.554 | 0.564 | 0.559 |
| max_depth=sin_limite | gradient_boosting | completas | ninguno | 0.3 | learning_rate=0.1, max_depth=sin_limite | 0.674 | 0.585 | 0.908 | 0.554 | 0.572 | 0.563 |
| max_depth=5 | gradient_boosting | completas | ninguno | 0.3 | learning_rate=0.1, max_depth=5 | 0.669 | 0.582 | 0.908 | 0.554 | 0.569 | 0.561 |
| max_depth=8 | gradient_boosting | completas | ninguno | 0.3 | learning_rate=0.1, max_depth=8 | 0.66 | 0.581 | 0.907 | 0.551 | 0.574 | 0.563 |
| gradient_boosting-completas-u0.3 | gradient_boosting | completas | ninguno | 0.3 | learning_rate=0.1, max_depth=8 | 0.66 | 0.581 | 0.907 | 0.551 | 0.574 | 0.563 |
| random_forest-completas-u0.3 | random_forest | completas | ninguno | 0.3 | n_estimators=100, max_depth=8 | 0.643 | 0.568 | 0.912 | 0.592 | 0.486 | 0.534 |
| max_depth=8 | random_forest | completas | ninguno | 0.5 | n_estimators=100, max_depth=8 | 0.643 | 0.568 | 0.914 | 0.799 | 0.226 | 0.352 |
| random_forest-completas-u0.5 | random_forest | completas | ninguno | 0.5 | n_estimators=100, max_depth=8 | 0.643 | 0.568 | 0.914 | 0.799 | 0.226 | 0.352 |
| max_depth=8 | random_forest | completas | balanced | 0.3 | n_estimators=100, max_depth=8 | 0.629 | 0.55 | 0.645 | 0.216 | 0.923 | 0.35 |
| random_forest-completas-u0.3 | random_forest | completas | balanced | 0.3 | n_estimators=100, max_depth=8 | 0.629 | 0.55 | 0.645 | 0.216 | 0.923 | 0.35 |
| max_depth=8 | random_forest | completas | balanced | 0.3 | n_estimators=100, max_depth=8 | 0.629 | 0.55 | 0.645 | 0.216 | 0.923 | 0.35 |
| random_forest-completas-u0.3 | random_forest | completas | balanced | 0.3 | n_estimators=100, max_depth=8 | 0.629 | 0.55 | 0.645 | 0.216 | 0.923 | 0.35 |
| logistic_regression-completas-u0.3 | logistic_regression | completas | ninguno | 0.3 | C=1.0 | 0.531 | 0.545 | 0.899 | 0.515 | 0.507 | 0.511 |
| max_depth=5 | random_forest | completas | ninguno | 0.5 | n_estimators=100, max_depth=5 | 0.561 | 0.541 | 0.903 | 0.906 | 0.078 | 0.144 |
| max_depth=5 | random_forest | completas | balanced | 0.3 | n_estimators=100, max_depth=5 | 0.557 | 0.539 | 0.529 | 0.174 | 0.949 | 0.295 |

Otros runs citados en las respuestas (fuera de los 15 mejores):

| run | modelo | features | umbral | pr_auc | alertas |
|---|---|---|---|---|---|
| logistic_regression-solo_regla-u0.3 | logistic_regression | solo_regla | 0.3 | 0.170 | 0 |
| 01_repro_a / 01_repro_b | random_forest (max_depth=8) | cliente | 0.5 | 0.510 | 212 |
| logistic_regression-basicas-u0.5 | logistic_regression | basicas | 0.5 | 0.339 | 67 |
| max_depth=8 | random_forest | basicas | 0.5 | 0.318 | — |

**Run registrado:** `max_depth=8` (random_forest, completas, n_estimators=100, max_depth=8, umbral 0.5), PR-AUC 0,568, como `workspace.bigdata_matio.fraud_model` versión 1, alias `champion`. Lo registré antes de probar boosting; ahora el mejor run es gradient_boosting con `max_depth=3` (PR-AUC 0,585), que sería el candidato a una versión 2.

## Datos y tracking

**1.** Filas y contracargos por split:
- `train`: 35.654 filas (11,05 % de contracargos)
- `test`: 7.129 filas (10,38 %)
- `nuevas`: 7.165 filas (11,05 %)

Se separa por fecha para entrenar con el pasado y evaluar con el futuro, como en producción.

**2.** Decir siempre "no" da 89,6 % de accuracy sin detectar ninguno de los 740 contracargos de test. Se usa PR-AUC porque se fija en la clase positiva y no depende del umbral (al azar da ≈ 0,104).

**3.** Quedó registrado:
- **Parámetros:** modelo, features, `C`, `class_weight`, umbral y versión de los datos.
- **Métricas:** PR-AUC 0,339, ROC-AUC 0,794, accuracy 0,896, precision 0,493, recall 0,045, F1 y alertas en test, más `train_pr_auc`.
- **Artefactos:** la matriz de confusión y el modelo.

Un experimento agrupa runs; un run es un entrenamiento concreto.

**4.** Autolog registró 46 parámetros (todos los del Pipeline) y métricas de entrenamiento: `training_accuracy_score`, `training_f1_score`, `training_precision_score`, `training_recall_score`, `training_roc_auc`, `training_log_loss` y `training_score`. No registra las métricas de test, el PR-AUC, el umbral ni las features elegidas.

**5.** Sí, `01_repro_a` y `01_repro_b` dieron lo mismo (PR-AUC 0,5099). Hay que fijar datos, código, semilla y entorno.

**6.** Tiró `Failed to enforce schema of data` porque faltaba `amount`, que la firma marca como obligatoria. La firma define qué entradas espera el modelo y las valida antes de predecir.

## Mis experimentos

**7.** Mi mejor run fue gradient_boosting con `completas`, `learning_rate=0.1` y `max_depth=3`, con PR-AUC 0,585. Con `solo_regla` dio 0,170 (y no generó ninguna alerta con umbral 0,3), así que el modelo mejoró 0,415 puntos: más de 3 veces.

**8.** Con random_forest (`max_depth=8`), el PR-AUC pasó de 0,318 con `basicas` a 0,510 con `cliente` y a 0,568 con `completas`. En ese bosque, las variables más importantes fueron `amount` (0,274) y `payment_channel` (0,170); bastante más abajo, `category`, `account_age_days` e `is_night`.

**9.** Con `completas` anduvo mejor el boosting: logística 0,545, bosque 0,568 y boosting 0,581 (0,585 con `max_depth=3`). Los árboles hacen cortes sucesivos (de noche *y* transferencia), así que captan combinaciones solos; la logística sólo suma efectos por separado.

**10.** Con el bosque y umbral 0,3, `balanced` subió el recall de 0,486 a 0,923 y las alertas de 608 a 3.158, y bajó la precision de 0,592 a 0,216. El PR-AUC casi no cambió (0,568 → 0,550): ordena parecido, pero las probabilidades se corren hacia arriba.

**11.** Con el bosque, bajar el umbral de 0,5 a 0,3 llevó las alertas de 209 a 608 y el recall de 0,226 a 0,486, y bajó la precision de 0,799 a 0,592 (el F1 subió de 0,352 a 0,534). El PR-AUC quedó igual: 0,568. El PR-AUC no depende del umbral porque mira todos los cortes posibles; el F1 se calcula con uno solo.

**12.** Barrí `max_depth` en random_forest con `completas`. El mejor fue 8 (PR-AUC 0,568 en test). Con `sin_limite` el train dio 1,0 y el test 0,537, y con `basicas` fue peor todavía: 0,998 en train contra 0,205 en test. Es sobreajuste. También barrí `max_depth` en boosting: todos dieron entre 0,581 y 0,585 en test, con train de 0,608 a 0,674, así que sobreajustó mucho menos que el bosque.

## Comparar y elegir

**13.** No coincidieron: el mejor por PR-AUC fue gradient_boosting con `max_depth=3` (0,585, accuracy 0,908) y el mejor por accuracy fue el bosque con `max_depth=sin_limite` y umbral 0,5 (0,916, PR-AUC 0,537). La accuracy casi no distingue entre modelos con tantos negativos; el PR-AUC mide si ordena bien a los positivos.

**14.** Los más alejados de la diagonal son los de `max_depth=sin_limite`, con PR-AUC 1,0 en train contra ~0,53 en test (y 0,998 contra 0,205 con `basicas`). Memorizan el entrenamiento: sobreajuste.

**15.** Con `search_runs` se pueden filtrar y comparar los runs por código, y automatizarlo; el filtro del notebook trajo 12 runs.

```python
filter_string = "tags.student_id = 'matio' AND params.model_type = 'random_forest' AND metrics.test_pr_auc > 0.55"
```

**16.** Cuesta más un contracargo no detectado que una alerta falsa. Si el equipo puede revisar K alertas por día, pondría el umbral para que alerten las K transacciones con mayor score.

## Registro, uso y monitoreo

**17.** Sí: `workspace.bigdata_matio.fraud_model`, versión 1, alias `champion`. Cargar por alias permite cambiar de modelo moviendo el alias, sin tocar el código que lo usa.

**18.** Se puntuaron 7.165 transacciones y 207 generaron alerta (2,9 %). Para auditar cada decisión están `score`, `threshold`, `model_name`, `model_version`, `run_id` y `scored_at`. El umbral va fuera del modelo porque es una decisión de negocio que puede cambiar sin reentrenar.

**19.** El PR-AUC sobre `nuevas` fue 0,554, contra 0,568 en test: parecido. Con la campaña, las alertas pasaron de 2,9 % a 7,6 % (el importe promedio subió de 989 a 1.218 y las transferencias de 33 % a 61 %). El drift es un cambio en la distribución de los datos; se ve antes en las entradas y en los scores que en las etiquetas, que llegan tarde.

## Cierre

**20.** Recorrí el ciclo de MLOps así:
- **Datos:** `ml_features`
- **Entrenamiento:** notebook 02
- **Tracking:** MLflow
- **Registro:** alias `champion`
- **Despliegue:** inferencia batch
- **Monitoreo:** métricas en producción y drift

Para producción real faltaría un job programado, alertas automáticas de drift y un proceso de reentrenamiento y validación antes de cambiar el champion.

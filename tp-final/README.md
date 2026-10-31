# TP final: Observatorio de servicios de datos abiertos

- **Nombre:** Matias Odello
- **student_id:** matio
- **Variante:** 1, Investigación (caso de negocio y arquitectura de datos), con la extensión opcional de MLOps

## Objetivo

Propongo una plataforma de datos que junte logs de acceso, chequeos de disponibilidad, ejecuciones de procesos y metadatos de los catálogos de **datos.gob.ar**, la **API de Series de Tiempo** y la **API Georef**. La idea es poder responder si los servicios funcionan, cuánto se usan y si los datos están al día.

## Contenido

| Archivo | Qué es |
|---|---|
| [`caso_de_negocio.md`](caso_de_negocio.md) | Documento principal: necesidad de negocio, datos, arquitectura, modelo de datos, justificación y extensión MLOps |
| [`diagramas/arbol_problemas.mmd`](diagramas/arbol_problemas.mmd) | Árbol de problemas (Mermaid) |
| [`diagramas/arquitectura.mmd`](diagramas/arquitectura.mmd) | Diagrama de arquitectura (Mermaid) |
| [`diagramas/modelo_datos.mmd`](diagramas/modelo_datos.mmd) | Modelo de datos de la capa Gold (Mermaid, entidad-relación) |
| [`graficos/generar_graficos.py`](graficos/generar_graficos.py) | Script con los supuestos de volumen; genera los tres gráficos |
| `graficos/*.png` | Volumen diario por fuente, almacenamiento acumulado y latencia requerida por uso |

## Datos y supuestos

Los servicios y sus metadatos son públicos. Los volúmenes, las tasas y las metas son estimaciones mías: están marcados con **(E)** en el documento y concentrados en el diccionario `FUENTES` del script. Esta variante no implementa la plataforma.

## Fuentes

- <https://datos.gob.ar>
- <https://github.com/datosgobar/series-tiempo-ar-api>
- <https://series-tiempo-ar-api-english.readthedocs.io/>
- <https://www.argentina.gob.ar/georef/normalizacion-de-direcciones>
- <https://datosgobar.github.io/paquete-apertura-datos/guia-apn/>
- <https://www.argentina.gob.ar/node/58714>
- Ley 25.326 de Protección de los Datos Personales

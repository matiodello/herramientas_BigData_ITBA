## Identificador de alumno

matio

## Respuestas

# CSV/JSON

Al registrar estos archivos, en el output de la columna "amount", se observa que el primer valor es N/A. Esto complica la operacion ya que detecta un string y convierte toda la columna (aun los valores numericos) a cadena de texto. Inferir el tipo de columna complica el tiempo de analisis y la salida propiamente dicha.

# Esquema bronce

El esquema parquet contiene el tipo de dato en su metadata. Al tener este diagrama se puede tener un mayor control en como se maneja la informacion y su trazabilidad.

# Delta y plan de ejecucion


El delta da mucha mas informacion, incluyendo que operaciones fueron hechas (CREATE OR REPLACE TABLE AS SELECT) y las operaciones. Da la mixtura de lo operacional y lo analitico dando mejor contexto. 
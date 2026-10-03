# CU-09 — Generar TXT del Libro de Sueldos Digital

## Objetivo

Permitir al contador generar un archivo de texto compatible con el sistema **Libro de Sueldos Digital de ARCA**, a partir de una liquidación de sueldos.

## Actor

Contador

## Precondiciones

* La liquidación debe estar registrada.
* La liquidación debe contener los empleados y resultados necesarios para generar el archivo.
* Los conceptos utilizados en la liquidación deben contar con la información necesaria para su correspondencia con los conceptos definidos por ARCA.

## Disparador

El contador selecciona una liquidación y solicita generar el archivo TXT para el Libro de Sueldos Digital.

## Flujo principal

1. El sistema identifica la liquidación seleccionada.
2. El sistema obtiene la información histórica de la empresa, los empleados y los conceptos utilizados en la liquidación.
3. El sistema obtiene los códigos y demás datos necesarios para asociar los conceptos de la liquidación con los conceptos de ARCA.
4. El sistema transforma la información de la liquidación al formato de intercambio requerido por el Libro de Sueldos Digital.
5. El sistema genera los registros correspondientes a los empleados y sus liquidaciones.
6. El sistema valida el formato y los datos requeridos para la generación del archivo.
7. El sistema genera el archivo de texto con extensión `.txt`.
8. El sistema entrega el archivo generado al contador.
9. El sistema modifica, de ser necesario, el estado de la liquidación a **Cerrada**.

## Excepciones

### EX-01 — Datos incompatibles con el formato

Si alguno de los datos no puede representarse de acuerdo con las especificaciones del diseño de registros vigente, el sistema informa el error y no genera el archivo.

## Postcondiciones

### Generación exitosa

El sistema entrega al contador un archivo `.txt` estructurado de acuerdo con el formato de intercambio requerido por el Libro de Sueldos Digital de ARCA.

La liquidación queda en estado **Cerrada**.

### Error

No se genera un archivo que contenga información incompleta o que no cumpla las validaciones establecidas por el sistema.

## Reglas de negocio

* RN-01: La información utilizada para generar el archivo debe corresponder al estado histórico de la liquidación.
* RN-02: Los conceptos utilizados en la liquidación deben estar asociados a los códigos de conceptos correspondientes de ARCA.
* RN-03: Los datos deben transformarse al diseño de registros vigente definido por ARCA.
* RN-04: Los campos alfanuméricos y numéricos deben respetar las longitudes y formatos establecidos para cada registro.
* RN-05: Los valores decimales deben representarse de acuerdo con las reglas establecidas por el diseño de registros correspondiente.
* RN-06: El archivo generado debe utilizar la extensión `.txt`.
* RN-07: La generación del archivo no modifica la liquidación ni sus resultados.
* RN-08: El archivo debe poder regenerarse a partir de la misma liquidación y su información histórica.
* RN-09: La generación del archivo no implica su presentación ni carga automática en el sistema de ARCA.
* RN-10: La generación del archivo automáticamente implica que la liquidación pase a estado **Cerrada**.

## Observaciones

El archivo generado constituye un archivo de intercambio destinado a ser utilizado posteriormente en el servicio **Libro de Sueldos Digital de ARCA**. El sistema no realiza una integración automática con ARCA ni efectúa la presentación del archivo.

La correspondencia entre los conceptos propios del empleador y los conceptos de ARCA forma parte de la parametrización requerida por el Libro de Sueldos Digital. ARCA indica que los conceptos utilizados en la liquidación deben asociarse con los conceptos predefinidos en su grilla universal.

Que una liquidación sea inmutable no implica necesariamente que la generación futura de los documentos derivados sea reproducible idénticamente. El sistema conserva los datos históricos, pero el formato y criterio utilizados para generar los recibos/TXT puede cambiar con el tiempo.

El formato concreto del archivo deberá mantenerse conforme a la versión vigente de las especificaciones publicadas por ARCA al momento de implementar o actualizar esta funcionalidad.

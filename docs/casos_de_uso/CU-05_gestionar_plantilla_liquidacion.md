# CU-05 — Gestionar plantillas de liquidación

## Objetivo

Permitir al contador definir y administrar plantillas de liquidación que puedan utilizarse como configuración inicial para incorporar conjuntos de conceptos a las liquidaciones de los empleados de una empresa.

## Actor

Contador

## Precondiciones

* La empresa a la que pertenece la plantilla debe estar registrada.
* Los conceptos utilizados por la plantilla deben pertenecer a la misma empresa.

## Disparador

El contador selecciona la opción de gestión de plantillas de liquidación de una empresa.

## Flujo principal

1. El sistema muestra las plantillas de liquidación registradas para la empresa.
2. El contador selecciona una operación sobre una plantilla: registrar, consultar, modificar o eliminar.
3. El sistema solicita o muestra la información correspondiente a la operación seleccionada.
4. El contador proporciona o modifica la información de la plantilla y sus detalles.
5. El sistema valida la información ingresada.
6. El sistema ejecuta la operación solicitada e informa su resultado.

## Flujos alternativos

### FA-01 — Cargar todos los conceptos

Al crear una plantilla, el usuario puede elegir cargar todos los conceptos asociados a la empresa.

1. El contador elige cargar todos los conceptos asociados a la empresa.
2. El sistema carga todos los conceptos y permite al usuario editarlos posteriormente.

### FA-02 — Duplicar plantilla

Al crear una plantilla, el usuario puede elegir duplicar una plantilla existente.

1. El contador elige duplicar una plantilla existente.
2. El sistema crea la plantilla duplicada.

## Excepciones

### EX-01 — Datos inválidos

Si alguno de los datos ingresados no cumple las validaciones establecidas, el sistema informa los errores y solicita su corrección.

### EX-02 — Plantilla ya registrada

Si se intenta registrar una plantilla con una denominación que ya existe para la misma empresa, el sistema informa el conflicto y no realiza la operación.

### EX-03 — Concepto no perteneciente a la empresa

Si se intenta incorporar a la plantilla una versión de concepto perteneciente a otra empresa, el sistema rechaza la operación.

## Postcondiciones

### Registro

La plantilla queda registrada con sus detalles y disponible para ser utilizada en futuras liquidaciones.

### Modificación

La configuración de la plantilla queda actualizada.

### Eliminación

La plantilla y sus detalles dejan de estar disponibles para ser utilizados en nuevas liquidaciones.

### Consulta

No se modifica el estado del sistema.

## Reglas de negocio

* RN-01: Cada plantilla pertenece a una única empresa.
* RN-02: La denominación de una plantilla debe ser única dentro de una empresa.
* RN-03: Cada detalle de una plantilla referencia un `Concepto`.
* RN-04: Una plantilla solamente puede contener conceptos pertenecientes a la misma empresa.
* RN-05: Los detalles de una plantilla almacenan la configuración inicial de los conceptos, incluyendo las unidades, fórmula base y otros datos.
* RN-06: La plantilla no almacena los valores calculados de base ni importe.
* RN-07: Al aplicar una plantilla se generan nuevos detalles independientes para la liquidación correspondiente.
* RN-08: Las modificaciones posteriores de una plantilla no alteran las liquidaciones que hayan sido creadas previamente a partir de ella.
* RN-09: Los detalles de las plantillas siempre referencian a las versiones vigentes de los conceptos, NO a la version del momento de crear dicho detalle.

## Observaciones

Una plantilla constituye una configuración reutilizable para facilitar la carga de conceptos en liquidaciones de empleados. Su aplicación no genera una dependencia entre la liquidación y la plantilla utilizada.

Las referencias entre conceptos no forman parte de la plantilla. Si una liquidación requiere que un concepto utilice el resultado de otro concepto, dichas referencias se configuran sobre los detalles de la liquidación generados al aplicar la plantilla.

La aplicación de una plantilla se realiza como parte de la preparación de una liquidación de empleado y no constituye una operación independiente de persistencia de la plantilla.

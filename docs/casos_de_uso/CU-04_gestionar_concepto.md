# CU-04 — Gestionar conceptos de liquidación

## Objetivo

Permitir al contador administrar los conceptos de liquidación de una empresa, incluyendo la creación de nuevas versiones, la consulta de conceptos eliminados, su restauración y su eliminación.

## Actor

Contador

## Precondiciones

* La empresa a la que pertenece el concepto debe estar registrada.

## Disparador

El contador selecciona la opción de gestión de conceptos de liquidación de una empresa.

## Flujo principal

1. El sistema muestra los conceptos activos registrados para la empresa.
2. El contador selecciona una operación: registrar, consultar, modificar, eliminar o restaurar un concepto.
3. El sistema solicita o muestra la información correspondiente a la operación seleccionada.
4. El contador proporciona o modifica la información requerida.
5. El sistema valida la información ingresada.
6. El sistema ejecuta la operación solicitada e informa su resultado.

## Flujos alternativos

### FA-01 — Consultar conceptos eliminados

En la gestión de conceptos, el contador solicita visualizar los conceptos eliminados.

1. El sistema muestra los conceptos que fueron eliminados, con los datos de la ultima version del mismo.
2. El contador puede seleccionar un concepto eliminado para restaurarlo o eliminarlo definitivamente.

### FA-02 — Restaurar concepto eliminado

Cuando el contador selecciona un concepto eliminado y solicita restaurarlo:

1. El sistema verifica que el concepto pueda ser restaurado.
2. El sistema marca el concepto como activo.
3. El concepto vuelve a estar disponible para nuevas liquidaciones y para la gestión de conceptos.

### FA-03 — Eliminar definitivamente un concepto

Cuando el contador solicita la eliminación definitiva de un concepto:

1. El sistema verifica que no existan referencias históricas a alguna version del concepto que impidan su eliminación.
2. El sistema elimina definitivamente el concepto y sus versiones.
3. El sistema informa el resultado de la operación.

## Excepciones

### EX-01 — Datos inválidos

Si alguno de los datos ingresados no cumple las validaciones establecidas, el sistema informa los errores y solicita su corrección.

### EX-02 — Concepto ya registrado

Si se intenta registrar un concepto que ya posee una identidad correspondiente dentro de la empresa, el sistema informa el conflicto y no realiza la operación.

### EX-03 — Concepto utilizado en una liquidación abierta

Si se intenta eliminar un concepto que está siendo utilizado por una liquidación abierta, el sistema rechaza la eliminación.

### EX-04 — Eliminación definitiva no permitida

Si se intenta eliminar definitivamente un concepto que posee referencias que impiden su eliminación, el sistema rechaza la operación.

## Postcondiciones

### Registro

El concepto queda registrado con su primera versión y disponible para ser utilizado en nuevas liquidaciones.

### Modificación

La información modificable del concepto queda actualizada mediante la creación de una nueva versión cuando corresponda.

### Eliminación

El concepto queda marcado como eliminado y deja de estar disponible para nuevas liquidaciones, mientras que sus versiones y referencias históricas se conservan.

### Restauración

El concepto vuelve a estar activo y disponible para nuevas operaciones.

### Eliminación definitiva

El concepto y sus versiones son eliminados definitivamente cuando no existen referencias que impidan la operación.

### Consulta

No se modifica el estado del sistema.

## Reglas de negocio

* RN-01: Cada concepto posee una identidad lógica independiente de sus versiones.
* RN-02: Cada versión de un concepto se identifica mediante un número de versión consecutivo y positivo.
* RN-03: La creación de una nueva versión no modifica las versiones anteriores.
* RN-04: Las versiones de concepto son inmutables.
* RN-05: Una versión de concepto utilizada por una liquidación debe conservarse para mantener la información histórica de dicha liquidación.
* RN-06: La eliminación normal de un concepto se realiza mediante un borrado lógico, sin eliminar sus versiones ni sus referencias históricas.
* RN-07: Los conceptos eliminados no están disponibles para ser utilizados en nuevas liquidaciones.
* RN-08: Los conceptos eliminados pueden ser consultados y restaurados.
* RN-09: La eliminación definitiva de un concepto solamente puede realizarse cuando no existen referencias que requieran conservarlo.
* RN-10: Al eliminar definitivamente un concepto se eliminan también sus versiones.
* RN-11: Cada concepto y sus versiones pertenecen a una única empresa.

## Observaciones

La eliminación lógica permite conservar los conceptos y sus versiones utilizados por liquidaciones históricas, evitando que estas pierdan sus referencias.

La restauración afecta al estado de la identidad del concepto, no modifica ni recrea sus versiones existentes.

La eliminación definitiva constituye una operación diferente de la eliminación lógica y debe considerarse una operación excepcional, dado que implica eliminar también las versiones asociadas al concepto.

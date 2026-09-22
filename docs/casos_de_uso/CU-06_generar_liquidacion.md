# CU-06 — Generar liquidación

## Objetivo

Permitir al contador generar y administrar una liquidación de sueldos correspondiente a una empresa y un período determinado, incorporando los empleados que serán liquidados y preparando la información necesaria para su posterior cálculo y cierre.

## Actor

Contador

## Precondiciones

* La empresa debe estar registrada.
* Debe existir al menos un empleado disponible para ser incluido en la liquidación.
* No debe existir otra liquidación para la misma empresa y período.

## Disparador

El contador selecciona la opción de generar una liquidación para una empresa y un período determinado.

## Flujo principal

1. El sistema solicita el período y la fecha de pago de la liquidación.
2. El contador proporciona los datos solicitados.
3. El sistema valida los datos de la liquidación.
4. El sistema crea la liquidación en estado **Borrador**.
5. El contador selecciona los empleados que participarán de la liquidación.
6. El sistema incorpora los empleados seleccionados a la liquidación y conserva la información histórica necesaria de cada uno.
7. El contador solicita la liquidación de los empleados mediante el CU-07.
8. El sistema registra los resultados de las liquidaciones individuales.
9. El contador verifica los resultados obtenidos.
10. El contador solicita cerrar la liquidación.
11. El sistema valida que la liquidación pueda cerrarse.
12. El sistema cambia el estado de la liquidación a **Cerrada** e impide modificaciones posteriores.

## Excepciones

### EX-01 — Datos de liquidación inválidos

Si alguno de los datos ingresados no cumple las validaciones establecidas, el sistema informa los errores y solicita su corrección.

### EX-02 — Liquidación ya existente

Si ya existe una liquidación para la misma empresa y período, el sistema informa el conflicto y no crea una nueva liquidación.

### EX-03 — Fecha de pago fuera del período

Si la fecha de pago no pertenece al período correspondiente a la liquidación, el sistema rechaza la operación.

### EX-04 — No existen empleados para liquidar

Si el contador intenta generar o cerrar una liquidación sin empleados incorporados, el sistema rechaza la operación.

### EX-05 — Liquidación con empleados sin liquidar

Si el contador intenta cerrar una liquidación que contiene empleados que aún no fueron liquidados, el sistema rechaza la operación.

### EX-06 — Liquidación ya cerrada

Si se intenta modificar una liquidación que se encuentra cerrada, el sistema rechaza la operación.

## Postcondiciones

### Generación

La liquidación queda registrada en estado **Borrador**, asociada a una empresa y un período, y puede ser modificada y completada.

### Incorporación de empleados

Los empleados seleccionados quedan asociados a la liquidación junto con la información histórica necesaria para reproducir sus resultados.

### Cierre

La liquidación queda en estado **Cerrada** y sus datos no pueden ser modificados.

## Reglas de negocio

* RN-01: Una liquidación pertenece a una única empresa.
* RN-02: Una liquidación corresponde a un único período.
* RN-03: No puede existir más de una liquidación para una misma empresa y período.
* RN-04: Una liquidación se crea inicialmente en estado **Borrador**.
* RN-05: Una liquidación en estado **Borrador** puede ser modificada.
* RN-06: Una liquidación **Cerrada** es inmutable.
* RN-07: Un empleado solamente puede participar de una liquidación de la empresa a la que pertenece.
* RN-08: La información necesaria para reproducir una liquidación debe conservarse independientemente de modificaciones posteriores de los datos maestros.
* RN-09: La fecha de pago debe pertenecer al período de la liquidación.
* RN-10: No puede cerrarse una liquidación mientras existan empleados incorporados que no hayan sido liquidados.
* RN-11: El cálculo de cada empleado se realiza mediante el CU-07 — Liquidar empleado.
* RN-12: El cierre de una liquidación confirma sus resultados y evita modificaciones posteriores.

## Observaciones

El período de la liquidación representa el período al que corresponden los haberes liquidados. Para este sistema se consideran períodos mensuales.

No se restringe la creación de una liquidación cuyo período sea posterior a la fecha actual, ya que el contador puede preparar una liquidación con anticipación.

La liquidación general constituye el contexto de trabajo para las liquidaciones individuales de sus empleados. El cálculo de conceptos, referencias y resultados de cada empleado se especifica en el CU-07.

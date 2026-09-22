# CU-07 — Liquidar empleado

## Objetivo

Permitir al contador calcular y registrar la liquidación correspondiente a un empleado dentro de una liquidación de su empresa, determinando los conceptos, bases, importes y subtotales que componen su remuneración.

## Actor

Contador

## Precondiciones

* La liquidación debe estar registrada y encontrarse en estado **Borrador**.
* El empleado debe pertenecer a la empresa de la liquidación.
* El empleado debe estar asociado a la liquidación.
* Los conceptos utilizados deben corresponder a versiones disponibles para la empresa.

## Disparador

El contador selecciona un empleado asociado a una liquidación y solicita realizar su liquidación individual.

## Flujo principal

1. El sistema muestra la información del empleado y los conceptos configurados para su liquidación.
2. El contador agrega, modifica o elimina los conceptos que correspondan.
3. El contador puede aplicar una plantilla de liquidación para incorporar una configuración inicial de conceptos.
4. El sistema incorpora los detalles de los conceptos seleccionados a la liquidación del empleado.
5. El contador configura las unidades y las expresiones base correspondientes a cada concepto.
6. El contador configura, cuando corresponda, las referencias entre conceptos utilizadas por las expresiones de cálculo.
7. El sistema identifica las referencias requeridas por las expresiones de cada concepto.
8. El sistema obtiene los importes de los conceptos referenciados y evalúa las expresiones de cálculo.
9. El sistema determina la base e importe de cada detalle de liquidación.
10. El sistema calcula los subtotales de la liquidación del empleado.
11. El sistema muestra los resultados obtenidos para su verificación.
12. El contador confirma la liquidación del empleado.
13. El sistema registra los resultados calculados.

## Flujos alternativos

### FA-01 — Aplicar plantilla de liquidación

En el paso 3 del flujo principal, el contador puede seleccionar una plantilla de liquidación disponible para la empresa.

1. El sistema muestra las plantillas disponibles.
2. El contador selecciona una plantilla.
3. El sistema incorpora a la liquidación los detalles configurados en la plantilla.
4. Los detalles incorporados pueden ser modificados por el contador antes de confirmar la liquidación.
5. La plantilla original no se modifica.

### FA-02 — Recalcular liquidación

Si el contador modifica unidades, expresiones o referencias después de un cálculo previo:

1. El sistema invalida los resultados afectados.
2. El sistema vuelve a resolver las referencias necesarias.
3. El sistema recalcula las bases e importes correspondientes.
4. El sistema actualiza los subtotales de la liquidación del empleado.

## Excepciones

### EX-01 — Empleado no perteneciente a la empresa

Si el empleado no pertenece a la empresa de la liquidación, el sistema rechaza la operación.

### EX-02 — Concepto no disponible

Si se intenta utilizar un concepto que no está disponible para nuevas liquidaciones, el sistema rechaza su incorporación.

### EX-03 — Referencia inexistente

Si una expresión requiere un identificador para el cual no existe una referencia configurada en la liquidación del empleado, el sistema informa el error y no permite completar el cálculo.

### EX-04 — Expresión inválida

Si una expresión de cálculo no cumple la sintaxis o las operaciones permitidas, el sistema informa el error y no permite completar el cálculo del concepto afectado.

### EX-05 — Dependencia circular

Si las referencias entre conceptos generan una dependencia circular que impide determinar los valores necesarios para el cálculo, el sistema informa el error y no permite completar la liquidación.

### EX-06 — Liquidación no modificable

Si la liquidación se encuentra cerrada, el sistema rechaza cualquier modificación o nuevo cálculo.

## Postcondiciones

### Liquidación calculada

La liquidación del empleado queda registrada con los detalles, bases, importes y subtotales calculados.

### Recalculo

Los resultados de los conceptos afectados y los subtotales quedan actualizados.

### Error de cálculo

Si ocurre una excepción durante el cálculo, no se confirma la liquidación del empleado con resultados incompletos o inválidos.

## Reglas de negocio

* RN-01: Un empleado solamente puede ser liquidado dentro de una liquidación correspondiente a su empresa.
* RN-02: Cada detalle de liquidación referencia una versión concreta de un concepto.
* RN-03: Las versiones de conceptos utilizadas en una liquidación deben conservarse para mantener la información histórica.
* RN-04: Una expresión de cálculo puede utilizar referencias a otros detalles de la misma liquidación del empleado.
* RN-05: Cada identificador utilizado en una expresión debe corresponder a una referencia configurada para el detalle que contiene dicha expresión.
* RN-06: Las referencias utilizan el importe del detalle referenciado como valor de entrada para la expresión.
* RN-07: Las expresiones de cálculo solamente pueden utilizar las operaciones admitidas por el sistema.
* RN-08: Las dependencias entre conceptos deben poder resolverse sin generar ciclos.
* RN-09: La base e importe de los conceptos son valores calculados por el sistema a partir de las unidades, expresiones y referencias configuradas.
* RN-10: Los resultados de la liquidación se agrupan en remunerativo, no remunerativo, bruto, descuentos, neto, contribuciones y costo laboral, según corresponda a los conceptos liquidados.
* RN-11: La aplicación de una plantilla genera detalles propios de la liquidación y no mantiene una dependencia posterior con la plantilla.
* RN-12: Modificar una plantilla no altera liquidaciones existentes.
* RN-13: Una liquidación cerrada no puede ser modificada ni recalculada.
* RN-14: La confirmación de la liquidación del empleado debe conservar toda la información necesaria para reproducir sus resultados posteriormente.

## Observaciones

La liquidación del empleado constituye la instancia en la que se aplican y calculan los conceptos concretos para un empleado determinado. La liquidación general definida en el CU-06 proporciona el período, la empresa y el conjunto de empleados sobre los cuales se trabaja.

Las expresiones de cálculo pueden utilizar identificadores correspondientes a otros conceptos de la misma liquidación del empleado. El sistema debe resolver estas dependencias antes de evaluar cada expresión.

La aplicación de una plantilla constituye únicamente una forma de cargar una configuración inicial. Una vez incorporados, los detalles pertenecen a la liquidación y pueden ser modificados independientemente de la plantilla.

Los resultados calculados forman parte de la información histórica de la liquidación y no deben depender de los valores actuales de los datos maestros ni de versiones posteriores de los conceptos.

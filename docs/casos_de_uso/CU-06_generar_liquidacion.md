# CU-06 — Generar liquidación

## Objetivo

Permitir al contador generar y administrar una liquidación de sueldos para una empresa y período determinados, incorporando los empleados a liquidar y calculando sus haberes, para posteriormente obtener los productos derivados correspondientes.

## Actor

Contador

## Precondiciones

* La empresa debe estar registrada.
* Los empleados que participen de la liquidación deben estar registrados y pertenecer a la empresa.
* Los conceptos y categorías laborales necesarios deben estar disponibles.

## Disparador

El contador inicia la generación de una liquidación para una empresa y un período determinado.

## Flujo principal

1. El contador selecciona la empresa y el período a liquidar.
2. El sistema crea la liquidación en estado **Borrador**.
3. El contador incorpora los empleados que serán incluidos en la liquidación.
4. Para cada empleado, se determinan los datos y conceptos que correspondan.
5. Se calculan los resultados de la liquidación de cada empleado.
6. El sistema consolida los resultados de los empleados incluidos en la liquidación.
7. El contador verifica los resultados obtenidos.
8. Mientras la liquidación se encuentre en estado **Borrador**, pueden modificarse los datos de la liquidación y recalcularse los resultados.
9. El contador puede obtener los recibos de sueldo correspondientes.
10. El contador puede generar el archivo TXT compatible con el Libro de Sueldos Digital de ARCA.
11. Si la generación del TXT finaliza correctamente, la liquidación pasa a estado **Cerrada**.

## Flujos alternativos

### FA-01 — Rectificar una liquidación cerrada

1. El contador selecciona una liquidación en estado **Cerrada**.
2. El contador inicia una rectificación.
3. La liquidación pasa a estado **Rectificación**.
4. El contador modifica la información necesaria.
5. Se recalculan los resultados afectados.
6. El contador verifica los nuevos resultados.
7. El contador puede obtener nuevamente los recibos de sueldo.
8. El contador puede generar nuevamente el archivo TXT.
9. Si la generación del TXT finaliza correctamente, la liquidación vuelve a estado **Cerrada**.

### FA-02 — Obtener recibo de sueldo

El contador puede obtener el recibo de sueldo de un empleado de la liquidación, independientemente de que la liquidación se encuentre en estado **Borrador**, **Rectificación** o **Cerrada**, siempre que exista información suficiente para generarlo.

La generación del recibo no modifica el estado ni los resultados de la liquidación.

El contador elige si quiere generar la version original o duplicado del recibo.

### FA-03 — Generar archivo TXT LSD

El contador puede generar el archivo TXT correspondiente a la liquidación, independientemente de que la liquidación se encuentre en estado **Borrador**, **Rectificación** o **Cerrada**, siempre que exista información suficiente para generarlo.

La generación del TXT se realiza a partir de la información histórica y los resultados registrados en la liquidación.

Si la generación finaliza correctamente, de no estarlo, la liquidación pasa a estado **Cerrada**.

## Excepciones

### EX-01 — Datos inválidos

Si la información necesaria para realizar la liquidación es inválida o insuficiente, el sistema informa el problema y no completa el cálculo correspondiente.

### EX-02 — Liquidación existente

Si ya existe una liquidación para la misma empresa y período, el sistema no permite crear una nueva liquidación para esa combinación.

### EX-03 — Fecha de pago fuera del período

Si la fecha de pago no pertenece al período de la liquidación o al siguiente, el sistema informa el problema y no permite continuar.

### EX-04 — Sin empleados

Si la liquidación no contiene empleados, el sistema informa el problema y no permite completar el proceso de generación correspondiente.

### EX-05 — Empleado sin liquidación

Si un empleado incluido no puede ser liquidado debido a información insuficiente o inválida, el sistema informa el problema correspondiente.

### EX-06 — Modificación de liquidación cerrada

Si se intenta modificar una liquidación en estado **Cerrada** sin iniciar previamente una rectificación, el sistema rechaza la operación.

### EX-07 — Error al generar el recibo

Si ocurre un error al generar un recibo de sueldo, el sistema informa el problema sin modificar la liquidación ni sus resultados.

### EX-08 — Error al generar el TXT

Si ocurre un error durante la generación del archivo TXT, el sistema informa el problema y la liquidación no pasa a estado **Cerrada**.

## Postcondiciones

### Generación

* La liquidación queda registrada en estado **Borrador**.
* Los empleados incorporados quedan asociados a la liquidación.
* Los resultados calculados quedan registrados.

### Generación exitosa del TXT

* El archivo TXT correspondiente a la liquidación es generado.
* La liquidación pasa a estado **Cerrada**.
* Los resultados de la liquidación quedan inmutables.

### Rectificación

* La liquidación pasa temporalmente a estado **Rectificación**.
* Los resultados pueden modificarse y recalcularse.
* Una generación exitosa del TXT vuelve a dejar la liquidación en estado **Cerrada**.

### Generación de recibo

* Se obtiene la representación documental de los resultados de un empleado.
* La generación del recibo no modifica la liquidación.

## Reglas de negocio

* **RN-01:** Una liquidación corresponde a una única empresa.
* **RN-02:** Una liquidación corresponde a un único período.
* **RN-03:** No puede existir más de una liquidación para una misma empresa y período.
* **RN-04:** Toda nueva liquidación comienza en estado **Borrador**.
* **RN-05:** Una liquidación en estado **Borrador** puede modificarse y recalcularse.
* **RN-06:** Una liquidación en estado **Cerrada** no puede modificarse directamente.
* **RN-07:** Una liquidación cerrada puede pasar a estado **Rectificación** para permitir modificaciones y nuevos cálculos.
* **RN-08:** Una liquidación en estado **Rectificación** puede modificarse y recalcularse.
* **RN-09:** La generación exitosa del archivo TXT LSD produce el cierre de la liquidación.
* **RN-10:** Una liquidación cerrada debe conservar los resultados necesarios para reproducir los documentos derivados de esa liquidación.
* **RN-11:** Cada empleado incluido en una liquidación debe pertenecer a la empresa correspondiente.
* **RN-12:** El cálculo de cada empleado se realiza de acuerdo con las reglas definidas para la liquidación de empleados.
* **RN-13:** La información histórica utilizada para los resultados de una liquidación no debe depender de modificaciones posteriores de los datos maestros.
* **RN-14:** La generación de un recibo no modifica el estado de la liquidación ni sus resultados.
* **RN-15:** El recibo de sueldo y el archivo TXT son productos derivados independientes y pueden generarse en cualquier orden.
* **RN-16:** La generación del recibo puede realizarse mientras la liquidación se encuentre en cualquiera de sus estados, siempre que exista información suficiente.
* **RN-17:** Si una liquidación en estado **Rectificación** vuelve a generar correctamente el TXT, retorna al estado **Cerrada**.
* **RN-18:** Una generación fallida del TXT no debe cerrar la liquidación.

## Observaciones

La liquidación representa el conjunto de resultados correspondientes a una empresa y período determinados.

El estado **Cerrada** representa que los resultados de la liquidación han quedado definitivos e inmutables. En la implementación actual, esta transición se produce como consecuencia de una generación exitosa del archivo TXT LSD.

Una liquidación cerrada puede ser sometida posteriormente a una **Rectificación**. En ese caso, los resultados vuelven a ser modificables y la liquidación debe volver a cerrarse mediante una nueva generación exitosa del archivo TXT.

La generación del recibo de sueldo y del archivo TXT son operaciones independientes. Ninguna de ellas requiere que la otra se haya realizado previamente.

La generación de documentos derivados no constituye una modificación de los resultados de la liquidación.

Que una liquidación sea inmutable no implica necesariamente que la generación futura de los documentos derivados sea reproducible idénticamente. El sistema conserva los datos históricos, pero el formato y criterio utilizados para generar los recibos/TXT puede cambiar con el tiempo.

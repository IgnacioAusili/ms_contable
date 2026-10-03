# CU-08 — Generar recibo de sueldo

## Objetivo

Permitir al contador generar el recibo de sueldo de un empleado a partir de una liquidación realizada, obteniendo un documento en formato PDF con la información correspondiente a los haberes liquidados.

## Actor

Contador

## Precondiciones

* La liquidación debe estar registrada.
* El empleado debe haber sido liquidado dentro de la liquidación.
* La liquidación debe contener la información histórica necesaria para generar el recibo.

## Disparador

El contador selecciona un empleado de una liquidación y solicita generar su recibo de sueldo.

## Flujo principal

1. El sistema identifica la liquidación del empleado seleccionada.
2. El sistema obtiene la información histórica de la empresa y del empleado correspondiente a la liquidación.
3. El sistema obtiene los detalles de la liquidación y las versiones de los conceptos y empleado utilizados.
4. El sistema determina la información que debe incluirse en el recibo.
5. El sistema genera la representación del recibo de sueldo.
6. El sistema incorpora la composición de los haberes y los subtotales correspondientes.
7. El sistema genera el recibo en vista previa.
8. El sistema muestra la vista previa al contador.
9. El sistema, en la vista previa, ofrece la opción de descargar el recibo como PDF.
10. El contador puede, desde la vista previa, descargar el recibo como PDF.

## Excepciones

### EX-01 — Error al generar el PDF

Si ocurre un error durante la generación del documento PDF, el sistema informa el problema y no entrega un archivo incompleto o inválido.

## Postcondiciones

### Generación exitosa

El sistema entrega al contador un archivo PDF que representa el recibo de sueldo correspondiente al empleado y liquidación seleccionados.

### Error

No se modifica la información de la liquidación ni se genera un recibo válido.

## Reglas de negocio

* RN-01: El recibo debe corresponder a un único empleado dentro de una liquidación.
* RN-02: La información utilizada para generar el recibo debe corresponder al estado histórico de los datos al momento de la liquidación.
* RN-03: Los datos del empleado incluidos en el recibo deben corresponder a la versión del mismo que fue utilizada en la liquidación.
* RN-04: Los conceptos incluidos en el recibo deben corresponder a las versiones de conceptos utilizadas en la liquidación.
* RN-05: Los importes y subtotales mostrados en el recibo deben corresponder a los resultados registrados en la liquidación del empleado.
* RN-06: El recibo debe incluir la composición de los haberes de acuerdo con las categorías de conceptos correspondientes.
* RN-07: El recibo debe incluir los subtotales de remunerativo, no remunerativo, bruto, descuentos y neto, según corresponda.
* RN-08: El recibo debe incluir la información necesaria para identificar al empleador, al empleado, el período liquidado y la fecha de pago.
* RN-09: El recibo debe ser conforme a la regulación legal vigente aplicable en Argentina.
* RN-10: La generación del recibo no modifica la liquidación ni sus resultados.
* RN-11: La generación del recibo debe poder realizarse nuevamente a partir de la misma liquidación sin depender de modificaciones posteriores de los datos maestros.

## Observaciones

El recibo de sueldo no constituye una entidad independiente persistida por el sistema. Se genera a partir de la información histórica almacenada en la liquidación del empleado.

La generación del PDF constituye la representación documental de dicha información. Por lo tanto, volver a generar el recibo no implica modificar ni crear una nueva liquidación.

Que una liquidación sea inmutable no implica necesariamente que la generación futura de los documentos derivados sea reproducible idénticamente. El sistema conserva los datos históricos, pero el formato y criterio utilizados para generar los recibos/TXT puede cambiar con el tiempo.

La apariencia o plantilla visual del PDF puede modificarse posteriormente sin alterar los datos históricos ni los resultados de las liquidaciones ya realizadas.

El contenido del recibo debe mantenerse conforme a la normativa laboral vigente aplicable en la República Argentina.

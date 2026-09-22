# CU-03 — Gestionar empleados

## Objetivo

Permitir al contador administrar la información de los empleados de una empresa que será utilizada en las liquidaciones de sueldos.

## Actor

Contador

## Precondiciones

* La empresa a la que pertenece el empleado debe estar registrada.

## Disparador

El contador selecciona la opción de gestión de empleados de una empresa.

## Flujo principal

1. El sistema muestra los empleados registrados para la empresa.
2. El contador selecciona una operación sobre un empleado: registrar, consultar, modificar o eliminar.
3. El sistema solicita o muestra la información correspondiente a la operación seleccionada.
4. El contador proporciona o modifica la información requerida.
5. El sistema valida la información ingresada.
6. El sistema ejecuta la operación solicitada e informa su resultado.

## Excepciones

### EX-01 — Datos inválidos

Si alguno de los datos ingresados no cumple las validaciones establecidas, el sistema informa los errores y solicita su corrección.

### EX-02 — Empleado asociado a otra empresa

Si se intenta asociar un empleado a una empresa diferente de la que corresponde a la operación, el sistema rechaza la operación.

### EX-03 — Empleado utilizado en una liquidación

Si se intenta eliminar un empleado que participa en una liquidación que requiere conservar su información, el sistema rechaza la operación.

## Postcondiciones

### Registro

El empleado queda registrado y disponible para ser incluido en futuras liquidaciones de la empresa.

### Modificación

Los datos del empleado quedan actualizados.

### Eliminación

El empleado deja de estar disponible para nuevas liquidaciones.

### Consulta

No se modifica el estado del sistema.

## Reglas de negocio

* RN-01: Cada empleado pertenece a una única empresa.
* RN-02: Un empleado solamente puede participar en liquidaciones de la empresa a la que pertenece.
* RN-03: Los datos necesarios para identificar al empleado son obligatorios.
* RN-04: La categoría laboral asignada al empleado debe pertenecer a la misma empresa.
* RN-05: La información de un empleado que resulte necesaria para reproducir una liquidación debe conservarse en la información histórica de dicha liquidación.

## Observaciones

La información histórica de los empleados utilizada en liquidaciones no depende de los valores actuales de sus datos maestros. Por lo tanto, una modificación posterior de los datos del empleado no debe alterar liquidaciones ya realizadas.

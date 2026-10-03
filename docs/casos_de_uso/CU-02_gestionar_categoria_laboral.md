# CU-02 — Gestionar categorías laborales

## Objetivo

Permitir al contador administrar las categorías laborales utilizadas para clasificar a los empleados de una empresa.

## Actor

Contador

## Precondiciones

* La empresa a la que pertenece la categoría debe estar registrada.

## Disparador

El contador selecciona la opción de gestión de categorías laborales.

## Flujo principal

1. El sistema muestra las categorías laborales registradas.
2. El contador selecciona una operación sobre una categoría: registrar, consultar, modificar o eliminar.
3. El sistema solicita o muestra la información correspondiente a la operación seleccionada.
4. El contador proporciona o modifica la información requerida.
5. El sistema valida la información ingresada.
6. El sistema ejecuta la operación solicitada e informa su resultado.

## Excepciones

### EX-01 — Datos inválidos

Si alguno de los datos ingresados no cumple las validaciones establecidas, el sistema informa los errores y solicita su corrección.

## Postcondiciones

### Registro

La categoría laboral queda registrada y disponible para ser asignada a los empleados de la empresa.

### Modificación

Los datos de la categoría laboral quedan actualizados.

### Eliminación

La categoría laboral deja de estar disponible para nuevas asignaciones.

### Consulta

No se modifica el estado del sistema.

## Reglas de negocio

* RN-01: Cada categoría laboral pertenece a una única empresa.
* RN-02: Una categoría laboral solamente puede ser asignada a empleados de la empresa a la que pertenece.
* RN-03: La denominación de la categoría laboral es obligatoria.

## Observaciones

La categoría laboral asignada a un empleado se asocia a una version particular de los datos de dicho empleado, de modo que modificaciones posteriores de la categoría no alteren liquidaciones ya realizadas.

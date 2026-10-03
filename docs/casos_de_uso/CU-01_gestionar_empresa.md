# CU-01 — Gestionar empresas

## Objetivo

Permitir al contador administrar la información básica de las empresas para las cuales se realizarán liquidaciones de sueldos.

## Actor

Contador

## Precondiciones

No se requieren precondiciones.

## Disparador

El contador selecciona la opción de gestión de empresas.

## Flujo principal

1. El sistema muestra las empresas registradas y las operaciones disponibles.
2. El contador selecciona una operación sobre una empresa: registrar, consultar, modificar o eliminar.
3. El sistema solicita o muestra la información correspondiente a la operación seleccionada.
4. El contador proporciona o modifica la información requerida.
5. El sistema valida la información ingresada.
6. El sistema ejecuta la operación solicitada e informa su resultado.

## Excepciones

### EX-01 — Datos inválidos

Si alguno de los datos ingresados no cumple las validaciones establecidas, el sistema informa los errores y solicita su corrección.

### EX-02 — Empresa ya registrada

Si se intenta registrar una empresa cuyo CUIT ya se encuentra registrado, el sistema informa el conflicto y no realiza la operación.

## Postcondiciones

### Registro

La empresa queda registrada y disponible para las operaciones posteriores del sistema.

### Modificación

Los datos de la empresa quedan actualizados.

### Eliminación

La empresa deja de estar disponible para las operaciones posteriores del sistema.

### Consulta

No se modifica el estado del sistema.

## Reglas de negocio

* **RN-01:** Cada empresa se identifica de manera única mediante su CUIT.
* **RN-02:** El nombre y tipo de empleador de la empresa es obligatorio.

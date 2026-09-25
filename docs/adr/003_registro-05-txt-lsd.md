# No modelar trabajadores eventuales en v1 -- ADR

### Contexto

El Libro de Sueldos Digital de ARCA contempla el Registro 05, correspondiente a trabajadores eventuales. Este registro contiene datos específicos de esta modalidad, como categoría profesional, puesto desempeñado, período trabajado y CUIT de la empresa de servicios eventuales.

Estos datos no forman parte del flujo habitual de liquidación modelado actualmente. Además, soportar el Registro 05 implicaría introducir en el dominio conceptos y relaciones específicas de los trabajadores eventuales y de las empresas de servicios eventuales.

### Alternativas

1. Incorporar desde ahora el Registro 05 y modelar los datos necesarios en el dominio.
2. Incorporar los campos del Registro 05 dentro de `EMPLEADO` o `VERSION_EMPLEADO`.
3. No soportar trabajadores eventuales en la primera versión y dejar el Registro 05 fuera del alcance.

### Decisión y Justificación

Se decide **no soportar trabajadores eventuales ni generar el Registro 05 en la primera versión**.

El Registro 05 corresponde a una situación laboral específica que requiere información y relaciones que no son necesarias para el flujo principal del sistema. Incorporarlas únicamente para satisfacer la estructura del TXT agregaría complejidad al modelo sin aportar funcionalidad al alcance actual.

Cuando se incorpore el soporte para trabajadores eventuales, se evaluará su modelado como una extensión específica del dominio, en lugar de incorporar estos datos como atributos genéricos de `EMPLEADO` o `VERSION_EMPLEADO`.

### Consecuencias

* El sistema no podrá liquidar ni generar el Registro 05 para trabajadores eventuales en v1.
* Se evita incorporar al modelo datos y relaciones específicas de una modalidad no soportada.
* Se mantiene `EMPLEADO` y `VERSION_EMPLEADO` enfocados en los datos necesarios para el flujo habitual.
* La generación del TXT deberá contemplar explícitamente que el Registro 05 está fuera del alcance de v1.
* Incorporar trabajadores eventuales posteriormente requerirá una decisión de diseño específica para modelar esta modalidad.

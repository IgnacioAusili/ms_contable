# Plantillas para Liquidación por Empleado -- ADR (Architecture Decision Record)

### Contexto

La generación de una liquidación puede requerir la incorporación de múltiples conceptos para cada empleado.
Muchos empleados de una misma empresa pueden utilizar conjuntos similares de conceptos, por lo que cargarlos individualmente genera trabajo repetitivo.

Se busca permitir reutilizar una configuración inicial de conceptos sin introducir complejidad adicional en el cálculo de las liquidaciones.

### Alternativas

1. **Sin plantillas:** cargar manualmente todos los conceptos para cada empleado.
2. **Plantillas con conceptos:** definir plantillas asociadas a una empresa que contengan los conceptos y parámetros iniciales a aplicar.
3. **Plantillas con dependencias:** además de los conceptos, almacenar en la plantilla las referencias entre detalles para representar expresiones que utilicen otros conceptos.

La tercera alternativa implicaría replicar en las plantillas parte de la lógica existente en los `DETALLE_LIQUIDACION` y posteriormente transformar las referencias de los detalles de la plantilla en referencias a los nuevos detalles generados.

### Decisión y Justificación

Se utilizarán **plantillas de liquidación asociadas a una empresa**, compuestas por detalles que referencian una `VERSION_CONCEPTO` y contienen las unidades y la expresión base inicial.

Al aplicar una plantilla se crearán nuevos `DETALLE_LIQUIDACION` para la liquidación correspondiente.

Las referencias entre detalles no serán almacenadas en la plantilla. Estas se configurarán sobre los `DETALLE_LIQUIDACION` generados cuando sean necesarias.

Esta decisión reduce la complejidad de la primera versión y evita duplicar en las plantillas el mecanismo de dependencias y cálculo de los detalles de liquidación.

Si en el futuro se requiere expresar dependencias dentro de las plantillas, se evaluará una solución más general que permita reutilizar el mecanismo de cálculo en lugar de mantener dos implementaciones equivalentes.

### Consecuencias

* Se reduce la carga manual de conceptos para empleados con liquidaciones similares.
* Las plantillas pueden reutilizarse para distintos empleados de una misma empresa.
* Las liquidaciones mantienen sus propios detalles, independientes de la plantilla utilizada.
* Las dependencias entre conceptos deben configurarse al crear los detalles de cada liquidación.
* Se evita duplicar la lógica de referencias y cálculo en dos modelos diferentes.
* Existe cierta carga manual adicional cuando las expresiones utilizan otros conceptos.
* Una solución futura para dependencias en plantillas podría requerir rediseñar este mecanismo de forma más general.

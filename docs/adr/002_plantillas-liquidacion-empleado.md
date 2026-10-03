# Plantillas para Liquidación por Empleado -- ADR (Architecture Decision Record)

### Contexto

La generación de una liquidación puede requerir la incorporación de múltiples conceptos para cada empleado.
Muchos empleados de una misma empresa pueden utilizar conjuntos similares de conceptos, por lo que cargarlos individualmente genera trabajo repetitivo.

Se busca permitir reutilizar una configuración inicial de conceptos sin introducir complejidad adicional en el cálculo de las liquidaciones.

### Alternativas

1. **Sin plantillas:** cargar manualmente todos los conceptos para cada empleado.
2. **Plantillas con conceptos:** definir plantillas asociadas a una empresa que contengan los conceptos y parámetros iniciales a aplicar.

### Decisión y Justificación

Se utilizarán **plantillas de liquidación asociadas a una empresa**, compuestas por detalles que referencian siempre a la version vigente del concepto y contienen las unidades, fórmula base inicial y otros datos.

Al aplicar una plantilla se crearán nuevos `DETALLE_LIQUIDACION` para la liquidación correspondiente.

Se le permite al usuario duplicar plantillas y, al crear una plantilla nueva, cargar todos los conceptos asociados a la empresa en cuestión.

### Consecuencias

* Se reduce la carga manual de conceptos para empleados con liquidaciones similares.
* Las plantillas pueden reutilizarse para distintos empleados de una misma empresa.
* Las liquidaciones mantienen sus propios detalles, independientes de la plantilla utilizada.
* Se evita duplicar la lógica de referencias y cálculo en dos modelos diferentes.

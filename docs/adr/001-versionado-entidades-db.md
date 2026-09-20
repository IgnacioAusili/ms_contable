# Conservar resultados de las Liquidaciones -- ADR (Architecture Decision Record)

- Estado: Vigente

### Contexto

Las liquidaciones cerradas deben conservar sus resultados aunque posteriormente cambien los datos maestros. Esto implica que, una vez cerrada una liquidación, se debe poder volver a consultar/generar el recibo correspondiente y obtener el mismo documento, aunque posteriormente cambien los datos maestros.

### Alternativas

1. Considerar que los datos maestros representan el estado actual, mientras que los datos de LIQUIDACION_* representan el estado utilizado al momento de realizar la liquidación y, por consiguiente, guardar en DETALLE_LIQUIDACION una snapshot con los valores necesarios para reproducir el resultado.

```
LIQUIDACION_EMPLEADO
    empleado_id
    domicilio_empresa
    categoria_empleado
    bancoDeCobro
    ...
```

2. Versionar realmente el historico de cambios de los datos maestros y, de esa manera, ser capaz de reconstruir estados previos.

### Decisión y Justificación

Para empresa y empleado se utilizan snapshots selectivos en cada liquidacion, dado que la cantidad de atributos pasibles de cambios y que son relevantes para reproducir una liquidación es reducida. Respecto a los conceptos de liquidación, se opta por versionarlos debido a que casi todos sus atributos intervienen tanto en el cálculo como en la clasificación y generación de documentos, y pueden modificarse a lo largo del tiempo. 

De esta forma se preserva la reproducibilidad de las liquidaciones cerradas manteniendo una implementación simple y un alcance acotado. En futuras versiones, si el sistema necesita escalar hacia algo mas robusto, se puede considerar migrar completamente hacia la alternativa 2.

### Consecuencias

Las liquidaciones quedan históricamente estables manteniendo una implementación relativamente simple.

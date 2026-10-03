# Dominio y Semántica

## Propósito

Este documento describe los principales conceptos y relaciones del dominio de la liquidación de sueldos que son relevantes para comprender el funcionamiento del sistema.

Su objetivo es proporcionar una referencia sobre la lógica de dominio implementada en el sistema. El documento se centra en el **dominio del problema** y no en su implementación técnica.

Los detalles correspondientes a formatos de archivos, códigos de conceptos, parametrizaciones, aplicativos, procedimientos operativos y especificaciones de organismos externos se documentan por separado.

## Datos maestros y datos históricos

La información gestionada por el sistema puede clasificarse en dos grandes grupos.

### Datos maestros

Son los datos que representan la situación actual de las empresas y de las reglas utilizadas para realizar nuevas liquidaciones.

Entre ellos se encuentran:

* empresas;
* empleados;
* categorías laborales;
* conceptos de liquidación;
* grupos de conceptos;
* plantillas de liquidación.

Estos datos pueden evolucionar con el transcurso del tiempo. Por ejemplo, un empleado puede cambiar de categoría o un concepto puede modificar alguna de sus características.

### Datos históricos de las liquidaciones

Una liquidación representa los resultados obtenidos para una empresa y un período determinados, incluyendo los resultados individuales de los empleados involucrados.

Una vez cerrada, la liquidación debe conservar la información necesaria para conocer qué se liquidó y reproducir los documentos derivados de ella, independientemente de las modificaciones posteriores que sufran los datos maestros.

Por este motivo, los datos históricos de una liquidación no se consideran simplemente una referencia a la situación actual de la empresa o del empleado.

El sistema conserva, junto con la liquidación, los valores necesarios para representar su situación histórica, incluyendo, según corresponda, información del empleador, del empleado, de su categoría y de los conceptos utilizados.

El objetivo es que una liquidación cerrada constituya un registro histórico de los resultados obtenidos.

## Principio de histórico de una liquidación

Una liquidación cerrada debe poder interpretarse como una **fotografía de la situación considerada al momento de su realización**.

Por lo tanto:

> **Los documentos generados a partir de una liquidación cerrada deben depender de la información histórica de esa liquidación y no de modificaciones posteriores realizadas sobre los datos maestros.**

Este principio permite conservar la coherencia de los resultados históricos y regenerar los documentos asociados sin necesidad de mantener un historial general de todos los datos maestros.

Sin embargo,

> **Que una liquidación conserve su información histórica no implica necesariamente que la generación futura de los documentos derivados sea reproducible idénticamente. El sistema conserva los datos históricos, pero el formato y criterio utilizados para generar los recibos/TXT puede cambiar con el tiempo.**

## Período y liquidación

Una **liquidación** es el proceso mediante el cual se determinan los haberes correspondientes a los empleados de una empresa para un determinado período. En el sistema, dicho proceso queda representado por un registro que conserva sus resultados.

El **período** identifica el intervalo de tiempo al que corresponden los haberes liquidados.

La **fecha de pago** indica cuándo se abonarán esos haberes. El período y la fecha de pago son conceptos relacionados, pero no equivalentes.

Una liquidación puede incluir a varios empleados. Para cada empleado se obtiene un resultado individual que contiene los conceptos liquidados, sus importes y los subtotales correspondientes.

Durante su preparación, una liquidación puede modificarse y recalcularse. Una vez cerrada, sus resultados pasan a considerarse históricos y no deben modificarse.

## Conceptos de liquidación

La liquidación está compuesta por diferentes **conceptos**, cada uno de los cuales representa un componente particular de los haberes del trabajador, una retención o un costo a cargo del empleador.

Un concepto puede representar, por ejemplo: sueldo básico, antigüedad, etc.

Cada concepto posee características que determinan cómo interviene en la liquidación.

### Tipos de conceptos

Los conceptos se clasifican de acuerdo con su naturaleza. Esta clasificación determina cómo participa cada concepto en los distintos resultados de la liquidación. Ver [tipos de concepto](tipos_conceptos.md).

## Versionado

Un **concepto** representa la identidad lógica de un componente de liquidación, mientras que una **versión del concepto** representa las características que ese concepto posee en un determinado momento.

Esta distinción permite que un concepto pueda evolucionar sin alterar la interpretación de los conceptos que fueron utilizados en liquidaciones anteriores.

Por ejemplo, si cambian las características de un concepto, las nuevas liquidaciones pueden utilizar una nueva versión mientras que las liquidaciones históricas continúan haciendo referencia a la versión que correspondía en el momento en que fueron realizadas.

De esta forma, el historial necesario para interpretar una liquidación se conserva a nivel de los conceptos utilizados en ella, sin requerir que todos los datos maestros del sistema posean un mecanismo general de versionado.

Lo mismo aplica para los datos editables de **Empleado**.

## Grupos de conceptos

Los **grupos de conceptos** permiten clasificar determinados conceptos de acuerdo con el destino o naturaleza del costo que representan.

Esta clasificación es independiente del tipo de concepto.

Por ejemplo, un concepto puede ser una **contribución** a cargo del empleador y, al mismo tiempo, pertenecer al grupo **Seguridad social**.

Los grupos son utilizados principalmente para representar la **composición del costo laboral**, permitiendo agrupar varios conceptos individuales en categorías de mayor nivel.

Por defecto, el sistema incorpora los grupos mínimos requeridos por la legislación vigente para conformar la composición del costo laboral. Ver sección "Composición del costo laboral" más abajo.

Los grupos de conceptos no reemplazan la clasificación entre remunerativos, no remunerativos, descuentos y contribuciones. Ambas clasificaciones responden a dimensiones diferentes del dominio.

## Determinación de los importes

Los conceptos de liquidación pueden determinar sus importes a partir de una **base de cálculo** y una cantidad o porcentaje asociado.

Las **unidades** representan el valor que interviene en el cálculo.

La **unidad** determina cómo debe interpretarse ese valor, por ejemplo como una cantidad o como un porcentaje.

La **base de cálculo** representa el valor sobre el cual se aplica el concepto.

La **fórmula de cálculo** determina cómo se obtiene la base de cálculo y puede utilizar otros conceptos o bases imponibles de la misma liquidación.

El **importe** se obtiene aplicando las unidades a la base de cálculo de acuerdo con la unidad correspondiente.

### Ejemplo

| Concepto                 | Unidad     | Unidades |           Base |    Importe |
| ------------------------ | ---------- | -------: | -------------: | ---------: |
| Sueldo básico            | Cantidad   |       30 |        $65.000 | $1.950.000 |
| Adicional por antigüedad | Porcentaje |      2 % | $1.950.000 (*) |    $39.000 |

*(\*) La base corresponde al importe del Sueldo básico.*

Por lo tanto, los conceptos de una liquidación pueden depender de otros conceptos o bases imponibles (Ver sección "Bases imponibles" más abajo). El cálculo completo de una liquidación debe respetar dichas dependencias.

## Composición de la remuneración

El resultado de una liquidación puede analizarse agrupando los conceptos según su naturaleza.

### Remuneración bruta

La **remuneración bruta** representa la suma de los conceptos remunerativos y no remunerativos que corresponden al trabajador en el período.

`Remuneración bruta = conceptos remunerativos + conceptos no remunerativos`

Esta definición es utilizada también por ARCA en el contexto del Libro de Sueldos Digital. Los descuentos no forman parte de la remuneración bruta, aunque intervengan en la determinación del importe neto a cobrar.

### Descuentos

Los descuentos representan importes retenidos al trabajador.

Partiendo de la remuneración bruta, los descuentos reducen el importe que queda disponible para el trabajador.

Los eventuales ajustes de redondeo pueden modificar el importe final a percibir.

Conceptualmente:

`Remuneración neta = remuneración bruta − descuentos + ajustes`

### Contribuciones del empleador

Las contribuciones son obligaciones económicas a cargo del empleador derivadas de la relación laboral.

A diferencia de los descuentos, no se restan de la remuneración del trabajador. Constituyen un costo adicional para el empleador.

## Costo laboral

El **costo laboral** representa el costo económico que implica para el empleador la remuneración de un trabajador y las obligaciones asociadas a ella.

A efectos del dominio del sistema, puede entenderse conceptualmente como:

`Costo laboral total = remuneración bruta + contribuciones del empleador`

Los conceptos a cargo del empleador pueden incluir contribuciones y otros conceptos originados en disposiciones legales o convencionales.

## Composición del costo laboral

El formato de recibo reglamentado por el Decreto 407/2026 incorpora, además del detalle de los conceptos a cargo del empleador, un resumen de la **composición total del costo laboral**. Los conceptos a cargo del empleador deben agruparse, como mínimo, en los siguientes rubros:

1. Sindical.
2. Seguridad social.
3. Obra social.
4. I.N.S.S.J.P.
5. A.R.T.
6. Cámaras o entidades empresariales.
7. Otros rubros.

Por lo tanto, esta clasificación permite pasar del detalle de conceptos individuales a una visión agrupada del costo laboral.

Por ejemplo, varias contribuciones diferentes pueden pertenecer al grupo **Seguridad social** y ser consideradas conjuntamente al representar la composición del costo laboral.

El **costo laboral total** utilizado para esta representación incluye la remuneración bruta, descuentos y contribuciones del empleador.

### Representación en el recibo

La composición del costo laboral se presenta separadamente del detalle de los haberes del trabajador.

El recibo también presenta los conceptos a cargo del empleador, la remuneración bruta, las deducciones y la remuneración neta, de acuerdo con la estructura establecida para el recibo de haberes.

Los conceptos deben poder interpretarse indicando su base de cálculo, unidad de medida y monto resultante.

El sistema utiliza además una representación gráfica de la composición del costo laboral para facilitar su interpretación.

## Bases imponibles

Las **bases imponibles** son valores utilizados para determinar sobre qué importe se calculan determinados aportes y contribuciones de la seguridad social.

Una base imponible no representa necesariamente un importe que el trabajador recibe o que el empleador paga directamente. Es una **base de cálculo** utilizada para determinar una obligación específica.

Por este motivo, una misma liquidación puede tener varias bases imponibles diferentes.

ARCA utiliza bases identificadas del 1 al 10 para distintos subsistemas. Entre ellas se encuentran:

| Base | Finalidad                                                                     |
| ---- | ----------------------------------------------------------------------------- |
| 1    | Aportes previsionales                                                         |
| 2    | Contribuciones previsionales e I.N.S.S.J.P.                                   |
| 3    | Contribuciones al Fondo Nacional de Empleo, asignaciones familiares y RENATRE |
| 4    | Aportes de obra social y FSR                                                  |
| 5    | Aportes al I.N.S.S.J.P.                                                       |
| 6    | Aportes diferenciales                                                         |
| 7    | Aportes personales de regímenes especiales                                    |
| 8    | Contribuciones de obra social y FSR                                           |
| 9    | Ley de Riesgos del Trabajo                                                    |
| 10   | Contribuciones relacionadas con la Ley 27.430                                 |

Además de estas bases, existen bases destinadas al cálculo de diferenciales de aportes y contribuciones de seguridad social. Las bases 6 y 7 tienen aplicación en situaciones específicas y no necesariamente intervienen en todas las relaciones laborales.

Por lo tanto, **remuneración bruta** y **base imponible** son conceptos diferentes que pueden, o no, coincidir según las reglas aplicables.

Ver [Bases Imponibles ARCA](../specs_externas/arca_bases_imponibles.md).

## Detracciones

Una **detracción** es un importe que puede restarse de una base utilizada para el cálculo de determinadas contribuciones.

En el contexto del Libro de Sueldos Digital, ARCA identifica un **importe a detraer** utilizado para determinar la Base Imponible 10. ARCA define esta base como la correspondiente a las contribuciones relacionadas con la Ley 27.430.

Conceptualmente, la Base Imponible 10 se determina a partir de la Base Imponible 2 y el importe a detraer, de acuerdo con las reglas y límites aplicables al período. El resultado no puede quedar por debajo del mínimo previsional vigente cuando corresponde aplicar dicha regla.

La detracción no representa:

* un descuento aplicado al trabajador;
* una reducción de la remuneración bruta;
* ni un importe adicional pagado al trabajador.

Se trata de un mecanismo aplicado sobre una base de cálculo de determinadas contribuciones.

La posibilidad de aplicar una detracción, su importe y las condiciones para hacerlo dependen de la normativa vigente y de las características de la relación laboral y del período liquidado.

Por este motivo, una detracción no debe interpretarse como un importe fijo que forme parte de la definición general de una liquidación.

## Relación entre los principales resultados

La liquidación puede entenderse conceptualmente como una transformación de los conceptos liquidados en diferentes resultados:

```text
                     Conceptos liquidados
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
   Remunerativos       No remunerativos       Descuentos
          │                   │                   │
          └────────────┬──────┘                   │
                       ▼                          │
              Remuneración bruta                  │
                       │                          │
                       └──────────┬───────────────┘
                                  ▼
                         Remuneración neta


       Conceptos a cargo del empleador
                       │
                       ▼
               Costo laboral total
                       │
                       ▼
            Composición por rubros
```

Las bases imponibles constituyen otra dimensión de la liquidación:

```text
                    Conceptos liquidados
                            │
                            ▼
                Remuneración y características
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
     Base 1             Base 2            Base 3 ...
          │                 │
          │                 ├──────► Detracción
          │                 │
          │                 └──────► Base 10
          │
          └──────────────────────────────►
                        Aportes y
                      contribuciones
```

Estas perspectivas no son equivalentes:

* la primera describe **cómo se compone el ingreso y el costo laboral**;
* la segunda describe **sobre qué importes se calculan determinadas obligaciones**.

Una misma liquidación puede, por lo tanto, tener una única remuneración bruta y varias bases imponibles diferentes.

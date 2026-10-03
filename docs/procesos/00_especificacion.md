# Especificación y representación de procesos

## 1. Propósito

Los procesos del sistema se documentan mediante modelos inspirados en **SPEM (Software & Systems Process Engineering Metamodel)**.

El objetivo de esta documentación es representar la lógica de negocio asociada a los principales procesos del sistema, haciendo especial énfasis en aquellas reglas, decisiones, dependencias y comportamientos que pueden resultar poco evidentes durante la realización de las actividades.

Para la representación gráfica se utiliza **Mermaid**, debido a su integración con Markdown y GitHub. Por este motivo, los modelos utilizados en el proyecto no siguen estrictamente la nomenclatura ni la notación gráfica oficial, aunque estan inspirados en SPEM.

La adaptación busca conservar el significado conceptual sin introducir una herramienta adicional de modelado que dificulte el mantenimiento y versionado de la documentación.

# 2. Vistas utilizadas

Cada proceso puede documentar, principalmente, alguna de las siguientes vistas complementarias:

1. **Vista funcional y organizacional**
2. **Vista de comportamiento**
3. **Vista de información**

Las vistas representan diferentes aspectos del mismo proceso y deben interpretarse conjuntamente.

## 2.1. Vista funcional y organizacional

Esta vista representa:

* las tareas que componen el proceso;
* las entradas requeridas por cada tarea;
* las salidas o productos generados;
* los roles responsables de realizar las tareas.

La vista funcional responde principalmente:

> **¿Qué actividades se realizan y qué información consumen y producen?**

La dimensión organizacional responde:

> **¿Quién realiza cada actividad?**

En este proyecto existe actualmente un único actor/rol involucrado en los procesos: **Contador**. Por lo tanto, no es necesario introducir una estructura organizacional compleja. La asignación de las tareas al contador se representa directamente en el modelo.

Las actividades triviales de interacción con el sistema, como seleccionar opciones, completar formularios o navegar entre pantallas, no se representan salvo que tengan relevancia para la lógica del proceso; el foco está puesto en las actividades que representan comportamiento o reglas de negocio.

## 2.2. Vista de comportamiento

Esta vista representa la dinámica del proceso y la relación temporal entre sus actividades.

Permite expresar:

* secuencialidad;
* decisiones y condiciones;
* actividades opcionales;
* ciclos y repeticiones;
* caminos alternativos;
* condiciones de finalización;
* dependencias entre actividades;
* paralelismo cuando resulte relevante.

La vista de comportamiento responde principalmente:

> **¿En qué orden se realizan las actividades y bajo qué condiciones se continúa, repite o modifica el flujo?**

Esta vista es especialmente importante para procesos con lógica de negocio compleja.

## 2.3. Vista de información

La vista de información representa los principales productos de información que intervienen en el proceso y las relaciones entre ellos.

Su objetivo no es reemplazar el modelo de datos ni repetir el DER.

La vista responde principalmente:

> **¿Qué información se utiliza, qué información se produce y cómo se relacionan los documentos o productos de información durante el proceso?**

No se incluyen en esta vista atributos, claves, cardinalidades ni detalles de persistencia que ya estén documentados en el DER.

# 3. Relación entre la vista de información y el DER

La vista de información y el [diagrama Entidad-Relación (DER)](./db/der.md) son complementarios y no representan exactamente lo mismo.

La vista de información describe los elementos desde la perspectiva del **proceso**, mientras que el DER describe los elementos desde la perspectiva de la **estructura de datos del sistema**.

La lectura conjunta de ambos modelos permite comprender tanto **qué información necesita y produce el proceso** como **cómo dicha información se encuentra estructurada y persistida en el sistema**.

# 4. Lectura conjunta

Las tres vistas deben considerarse representaciones complementarias del mismo proceso.

La **vista funcional y organizacional** permite identificar qué se hace y quién lo realiza.

La **vista de comportamiento** permite comprender cuándo y bajo qué condiciones se realizan las actividades.

La **vista de información** permite comprender qué información se utiliza y cómo se transforma o relaciona durante el proceso.

Finalmente, el [DER](./db/der.md) permite profundizar en la estructura persistente de esa información.

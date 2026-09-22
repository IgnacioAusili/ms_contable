# Sistema de liquidación de sueldos

Sistema para la gestión y liquidación de sueldos de empresas y la generación de documentación asociada, desarrollado como una aplicación local.

## Descripción

El sistema permite administrar la información necesaria para realizar liquidaciones de sueldos y generar los documentos correspondientes.

Entre sus principales funcionalidades se encuentran:

* Gestión de empresas.
* Gestión de empleados y categorías laborales.
* Gestión de conceptos de liquidación y sus versiones.
* Gestión de plantillas de liquidación.
* Generación y cálculo de liquidaciones de sueldos.
* Generación de recibos de sueldo en formato PDF.
* Generación de archivos TXT compatibles con el sistema Libro de Sueldos Digital de ARCA.
* Conservación de la información histórica necesaria para reproducir liquidaciones y documentos generados.

El sistema está orientado a su utilización por parte de un contador para la gestión de las liquidaciones de una o más empresas.

## Alcance

El sistema contempla la gestión de empresas, empleados, conceptos de liquidación, categorías laborales y plantillas, así como la realización de liquidaciones y la generación de sus documentos asociados.

Las liquidaciones cerradas son inmutables y conservan la información necesaria para reproducir sus resultados independientemente de modificaciones posteriores en los datos maestros.

Los conceptos de liquidación utilizan un esquema de versionado para conservar las versiones utilizadas en liquidaciones históricas.

## Fuera de alcance

El proyecto no contempla:

* Uso simultáneo por múltiples usuarios.
* Acceso remoto o funcionamiento como servicio en línea.
* Autenticación y autorización de usuarios.
* Integración automática con ARCA.
* Presentación automática del Libro de Sueldos Digital.
* Auditoría y trazabilidad integral de las operaciones.
* Historial de versiones de los datos maestros de empresas y empleados.

## Tecnologías

* Django, Python
* DB Relacional, SQLite
* HTML, CSS y JavaScript

## Requisitos

Para ejecutar el proyecto se requiere Docker.

## Instalación

Ver el artefacto de instalacion y uso en el Release de la version que se desea instalar.

## Estructura de la documentación

La documentación funcional y de diseño se encuentra dentro del directorio `docs/`.

```text
docs/
│   contexto.md
│   operations.md
│   
├───adr
│       000_plantilla.md
│       xyz_nombre_adr.md
│       ...
│       
├───casos_de_uso
│       00_modelo_uml.md
│       CU-00_plantilla.md
│       CU-xy_nombre.md
│       ...
│       
├───db
│       der.md
│       
└───procesos
│       00_especificacion.md
│       PROC-00_plantilla.md
│       PROC-xy_nombre.md
│       ...
└───interfaces
│       recibo_sueldo.md
│       ...
└───imagenes
        liquidacion.jpg
        ...
```

### Casos de uso

Los casos de uso describen las funcionalidades del sistema desde la perspectiva del contador, incluyendo objetivos, flujos, excepciones y reglas de negocio.

### Procesos

Los procesos describen los procedimientos de negocio que involucran varias funcionalidades del sistema.

Su representación utiliza modelos inspirados en SPEM, adaptados a Mermaid para facilitar su mantenimiento e integración con el repositorio.

### Decisiones de arquitectura

Los ADR (*Architecture Decision Records*) documentan decisiones relevantes de diseño, las alternativas consideradas y los motivos de la decisión adoptada.

### Interfaces

Documentación sobre detalles de implementación.

### Imagenes

Las imagenes muestran algunas vistas del sistema a fin de que se entienda mejor como y que funciones ofrece.

## Modelo de dominio

El sistema se estructura alrededor de los siguientes conceptos principales:

```text
Empresa
 ├── Empleados
 ├── Categorías laborales
 ├── Conceptos
 │    └── Versiones de conceptos
 ├── Plantillas de liquidación
 └── Liquidaciones
      └── Liquidaciones de empleados
           └── Detalles de liquidación
                └── Referencias entre conceptos
```

Las liquidaciones conservan referencias a las versiones concretas de los conceptos utilizadas durante su cálculo, permitiendo mantener la información histórica necesaria para su posterior reproducción.



## Modelo de Casos de Uso

Ver [modelo UML de casos de uso](./docs/casos_de_uso/00_modelo_uml.md) y sus definiciones adjuntas.

## Diagrama Entidad-Relación

Ver [modelo UML del DER](./docs/db/der.md).

## Flujo general

A grandes rasgos, el funcionamiento del sistema sigue el siguiente flujo:

```text
Empresa
   │
   ├── Empleados
   ├── Categorías
   └── Conceptos
          │
          └── Versiones
                │
                ▼
         Generar liquidación
                │
                ▼
         Liquidar empleados
                │
                ▼
        Cerrar liquidación
             /       \
            /         \
           ▼           ▼
     Recibo PDF     TXT LSD
```

## Conformidad con Normativa Legal y Sistemas Externos

Ver [Especificaciones externas](./docs/specs_externas.md)

## Licencia

[Definir licencia del proyecto]

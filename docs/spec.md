# Usuarios

Este sistema esta pensado y orientado a contadores que necesitan una solución inicial simple y económica para liquidar sueldos.

# Alcance

Este sistema permite:
- Ser utilizado de forma local en una única PC, almacenando los datos en el disco local.
- Mantener un conjunto de empresas con sus datos básicos.
- Mantener un conjunto de empleados, cada uno vinculado a una única empresa.
- Liquidar sueldos.
- Generar archivos TXT compatibles con el sistema Libro de Sueldos Digital de ARCA.
- Generar recibos de sueldo para cada empleado.
- Exportar recibos de sueldo en formato PDF.
- Mantener un historial de las liquidaciones realizadas y la información necesaria para regenerar sus recibos de sueldo y archivos TXT compatibles con el sistema Libro de Sueldos Digital de ARCA.
- Mantener el historial de versiones de los conceptos de liquidación.

Queda fuera del alcance:
- Rectificar una liquidación ya cerrada.
- Uso compartido o acceso simultáneo desde múltiples equipos.
- Autenticación y autorización de usuarios.
- Mantener un historial de versiones de los datos de las empresas y los empleados.
- Interactuar automática con los sistemas de ARCA.
- Cumplir requisitos de auditoría y trazabilidad contable.

# Dominio y Semántica

La información gestionada por el sistema puede clasificarse en dos grandes grupos:

1. Datos propios de las liquidaciones: corresponden a los resultados y valores utilizados durante el proceso de liquidación. Estos datos adquieren carácter histórico una vez que la liquidación es cerrada, por lo que no requieren un mecanismo adicional de versionado para preservar los resultados obtenidos.

2. Datos maestros: corresponden a la información utilizada como base para realizar las liquidaciones, como los datos de las empresas, empleados, categorías laborales y conceptos de liquidación. A diferencia de los datos propios de una liquidación, estos pueden modificarse a lo largo del tiempo, por lo que es necesario considerar mecanismos que permitan preservar la información relevante utilizada en liquidaciones anteriores.

# Casos de Uso

```mermaid
flowchart LR
    CRUD_Empresa([CRUD_Empresa])
    CRUD_Concepto_Liquidacion([CRUD_Concepto_Liquidacion])
    CRUD_Categoria_Laboral([CRUD_Categoria_Laboral])
    CRUD_Empleado([CRUD_Empleado])

    Generar_Plantillas([Generar_Plantillas])
    Generar_Liquidacion([Generar_Liquidacion])
    Liquidar_Empleado([Liquidar_Empleado])

    Generar_Recibo_Sueldo([Generar_Recibo_Sueldo])
    Exportar_Recibo_PDF([Exportar_Recibo_PDF])
    Generar_Grafico([Generar_Grafico])

    Generar_TXT_LSD_ARCA([Generar_TXT_LSD_ARCA])

    Generar_Liquidacion -.->|include| Generar_Plantillas
    Generar_Liquidacion -.->|include| Liquidar_Empleado
    Liquidar_Empleado -.->|include| Generar_Recibo_Sueldo
    Generar_Recibo_Sueldo -.->|include| Exportar_Recibo_PDF
    Generar_Recibo_Sueldo -.->|include| Generar_Grafico

    Generar_Liquidacion -.->|include| Generar_TXT_LSD_ARCA
```

# Diagrama Entidad-Relación

```mermaid
erDiagram
    CONCEPTO ||--|{ VERSION_CONCEPTO : tiene
    VERSION_CONCEPTO }o--|| GRUPO_CONCEPTO : pertenece_a

    EMPRESA ||--o{ PLANTILLA_LIQUIDACION : tiene
    PLANTILLA_LIQUIDACION || --o{ DETALLE_PLANTILLA_LIQUIDACION : "se compone de"
    DETALLE_PLANTILLA_LIQUIDACION }o -- || VERSION_CONCEPTO : referente_a

    EMPRESA ||--o{ CONCEPTO : define
    EMPRESA ||--o{ CATEGORIA_LABORAL : tiene
    EMPRESA ||--o{ EMPLEADO : emplea

    CATEGORIA_LABORAL ||--o{ EMPLEADO : asignada_a

    EMPRESA ||--o{ LIQUIDACION : realiza
    LIQUIDACION ||--|{ LIQUIDACION_EMPLEADO : incluye
    EMPLEADO ||--o{ LIQUIDACION_EMPLEADO : participa

    LIQUIDACION_EMPLEADO ||--|{ DETALLE_LIQUIDACION : contiene
    VERSION_CONCEPTO ||--o{ DETALLE_LIQUIDACION : aplicado

    DETALLE_LIQUIDACION ||--o{ DETALLE_LIQUIDACION : utiliza
    
    EMPRESA {
        int id PK
        %% DJANGO BLANK: false 
        %% Reglas de Negocio: immutable 
        string cuit "NOT_NULL"
        %% DJANGO BLANK: false 
        %% Reglas de Negocio: immutable 
        string nombre "NOT_NULL"
        string domicilio "NOT_NULL"
    }

    PLANTILLA_LIQUIDACION {
        int id PK
        %% DJANGO BLANK: false 
        %% DJANGO UniqueConstraint: fields=["empresa", "denominacion"]
        string denominacion "NOT_NULL"
    }

    DETALLE_PLANTILLA_LIQUIDACION {
        int id PK
        decimal unidades "NOT_NULL"
        %% DJANGO BLANK: false
        string expresion_base "NOT_NULL"
    }

    CATEGORIA_LABORAL {
        int id PK
        %% DJANGO BLANK: false 
        %% DJANGO UniqueConstraint: fields=["empresa", "denominacion"]
        %% DJANGO HELP_TEXT: Ej: Personal de Obra, Administrativo, etc 
        string denominacion "NOT_NULL"
    }

    CONCEPTO {
        int id PK
    }

    GRUPO_CONCEPTO {
        int id PK
        %% DJANGO BLANK: false
        %% DJANGO HELP_TEXT: Ej: Seguridad Social, INSSJP, Obra Social, etc
        %% Reglas de Negocio: immutable 
        string denominacion "NOT_NULL, UNIQUE"
    }

    VERSION_CONCEPTO {
        int id PK
        %% DJANGO BLANK: false 
        %% DJANGO UniqueConstraint: fields=["concepto", "version"]
        int version "NOT_NULL, POSITIVE"
        %% DJANGO BLANK: false 
        %% DJANGO HELP_TEXT: Ej: Sueldo Basico, Obra Social, etc
        string denominacion "NOT_NULL"
        %% DJANGO BLANK: false 
        %% DJANGO HELP_TEXT: Referencia a un concepto de ARCA 
        string codigo_arca "NOT_NULL"
        %% DJANGO BLANK: false 
        %% DJANGO CHOICES: trabajador, empleador
        CATEGORIA_CONCEPTO categoria "NOT_NULL"
        %% DJANGO BLANK: false 
        %% DJANGO CHOICES: remunerativo, no remunerativo, descuento, redondeo, contribucion
        TIPO_CONCEPTO tipo "NOT_NULL"
        %% DJANGO BLANK: false 
        %% DJANGO CHOICES: cantidad, porcentaje
        UNIDAD_CONCEPTO unidad "NOT_NULL"
    }

    %% Reglas de Negocio: la categoria_laboral tiene que pertenecer a la misma empresa que el empleado 
    EMPLEADO {
        int id PK
        %% DJANGO BLANK: false 
        %% Reglas de Negocio: immutable 
        string dni "NOT_NULL"
        %% DJANGO BLANK: false 
        %% Reglas de Negocio: immutable 
        string cuil "NOT_NULL"
        %% DJANGO BLANK: false 
        %% Reglas de Negocio: immutable 
        string apellidos "NOT_NULL"
        %% DJANGO BLANK: false 
        %% Reglas de Negocio: immutable 
        string nombres "NOT_NULL"
        %% DJANGO UniqueConstraint: fields=["empresa", "legajo"]
        %% Reglas de Negocio: immutable 
        string legajo "NOT_NULL"
        %% Reglas de Negocio: immutable 
        date fecha_ingreso
        %% DJANGO HELP_TEXT: Ej: Nacion, Bco. Pcia. BS AS, Santander, etc 
        string banco_de_cobro "NOT_NULL"
    }

    LIQUIDACION {
        int id PK
        %% DJANGO BLANK: false 
        %% DJANGO UniqueConstraint: fields=["empresa", "periodo"]
        date periodo "NOT_NULL"
        %% DJANGO BLANK: false 
        date fecha_pago "NOT_NULL"
        %% DJANGO BLANK: false 
        %% DJANGO CHOICES: borrador, cerrada
        %% Reglas de Negocio: una vez cerrada no se puede modificar
        ESTADO_LIQUIDACION estado "NOT_NULL"
        %% snapshot de los datos maestros que son necesarios y que podrian cambiar
        string domicilio_empresa "NOT_NULL"
    }

    %% DJANGO UniqueConstraint: fields=["liquidacion", "empleado"]
    LIQUIDACION_EMPLEADO {
        int id PK
        decimal remunerativo
        decimal no_remunerativo
        decimal bruto
        decimal descuentos
        decimal neto
        decimal contribuciones
        decimal costo_laboral
        %% snapshot de los datos maestros que son necesarios y que podrian cambiar
        %% DJANGO BLANK: false
        string categoria "NOT_NULL"
        string banco_de_cobro "NOT_NULL"
    }

    DETALLE_LIQUIDACION {
        int id PK
        decimal unidades "NOT_NULL"
        %% DJANGO BLANK: false
        string expresion_base "NOT_NULL"
        %% puede estar expresado en terminos de otros conceptos
        decimal base "NOT_NULL"
        %% DJANGO HELP_TEXT: unidades * base
        decimal importe "NOT_NULL"
    }
```

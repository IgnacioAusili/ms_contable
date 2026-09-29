# Estructura del proyecto

El proyecto se organiza principalmente por **aplicaciones Django**, agrupando en cada una la funcionalidad correspondiente a un dominio o conjunto de responsabilidades relacionadas.

## Estructura general

```text
django-app/
├── django-app-1/
├── django-app-2/
│
├── core/                   # utilidades y validaciones compartidas y agnósticas del dominio
│   ├── utils.py
│   └── validators.py
│
├── ms_contable/
│   ├── settings.py
│   ├── urls.py
│
├── templates/              # Templates globales
├── static/                 # CSS y JS globales
├── docs/                   # Documentación del proyecto
├── manage.py
├── requirements.txt
```

## Estructura de las aplicaciones

Una aplicación simple puede mantener sus responsabilidades separadas mediante módulos:

```text
django-app/
├── models.py
├── admin.py
├── forms.py
├── services.py
├── validators.py
├── rules.py
├── utils.py
├── templates/
├── static/
└── tests/
```

### Responsabilidad de cada módulo

* `models.py`: modelos y comportamiento directamente asociado a las entidades.
* `admin.py`: configuración de Django Admin.
* `forms.py`: formularios y lógica específica de presentación.
* `services.py`: casos de uso y coordinación de operaciones de negocio.
* `validators.py`: validaciones reutilizables sobre valores o campos.
* `rules.py`: reglas de negocio que involucran contexto o múltiples campos.
* `utils.py`: utilidades de uso interno que no justifican un módulo con responsabilidad propia.
* `templates/`: templates específicos de la aplicación.
* `static/`: CSS, JavaScript y otros recursos específicos de la aplicación.
* `tests/`: pruebas de la aplicación.

Las restricciones que pueda garantizar directamente la base de datos deben modelarse mediante `constraints`, índices o relaciones apropiadas en los modelos, en lugar de duplicarlas en validadores.

La lógica de una misma regla debe mantenerse en una única fuente de verdad. Los formularios, modelos y servicios pueden invocar validaciones y reglas existentes, evitando implementar la misma condición en varios lugares.

## Aplicaciones grandes o complejas

Cuando una aplicación crece y alguno de sus módulos adquiere suficiente complejidad conceptual, puede convertirse en un paquete:

```text
django-app/
├── models/
│   ├── __init__.py
│   ├── modelo_1.py
│   └── modelo_2.py
│
├── admin/
│   ├── __init__.py
│   ├── modelo_1.py
│   └── modelo_2.py
│
├── forms/
├── services/
├── validators/
├── rules/
├── templates/
├── static/
├── tests/
└── paquete-1/              # si fuera necesario encapsular un modulo por si mismo
```

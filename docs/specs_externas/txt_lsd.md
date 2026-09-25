# Generar TXT - LSD ARCA

### Situaciones de Revista (Registro 04)

El registro 04 tiene

```
Código Situación
Situación de Revista 1 + día inicio
Situación de Revista 2 + día inicio
Situación de Revista 3 + día inicio
```

Código Situación es el código utilizado para indicar la situación de la relación a efectos de alta/baja; por ejemplo, mientras está activa se informa 01, y al registrar una baja se informa el código correspondiente al motivo de baja.

En cambio, las Situaciones de Revista representan la situación laboral del trabajador durante el período liquidado, y por eso cada una lleva un día de inicio. El Registro 04 permite informar hasta tres pares situación+día.

Ejemplo 1:

```
01/09 ─────────────────────────────── 30/09
      Activo
```

No hay ningún cambio de situación durante el mes. Entonces:

```
Situación de revista 1:
    Activo
    inicio: día 1
```

Ejemplo 2:

```
01/09 ───── 14/09 ───── 30/09
   Activo       Licencia
```

Entonces:

```
Situación de revista 1:
    Activo
    inicio: 1

Situación de revista 2:
    Licencia
    inicio: 15
```


### Observación sobre Registro 06

En la guia de uso se documenta un campo "id_liquidacion" que no esta en la implementacion en excel q ofrece ARCA.

¿Por qué no está en el Excel oficial? En las planillas Excel provistas en la sección de Herramientas de trabajo de ARCA, este campo no aparece de forma explícita porque la macro o fórmula de concatenación del archivo asume que vas a subir una sola liquidación por archivo TXT.Al procesarse de esta manera, la plataforma web de ARCA asigna o machea el contenido del archivo con el número de liquidación que vos creás manualmente en la pantalla previa del sistema (por ejemplo, Liquidación N° 1).

¿Qué pasa si estás unificando registros? Si estás armando el TXT manualmente o editando la planilla, debés tener en cuenta que el id_liquidacion forma parte de la clave primaria que vincula los distintos registros en el diseño general:Registro 01 (Cabecera): Ahí se define el número de liquidación (por ejemplo, 00001).Registro 02, 03, 04, 05 y 06: Deben llevar obligatoriamente en sus primeros caracteres el mismo número de liquidación para que el sistema sepa a qué cabecera corresponde cada CUIL y cada concepto liquidado.

# Referencias

- Guia de 2018: [Libros de Sueldo Digital - Conceptos Basicos y Guia de Uso 2018](https://www.afip.gob.ar/librodesueldosdigital/documentos/nuevos/LS_Conceptos_Basicos_y_Guia_de_Uso_V2.0.pdf)

- Guia de 2026. Esta es la mas reciente, pero las tablas estan un poco cortadas: [Libros de Sueldo Digital - Conceptos Basicos y Guia de Uso 2026](https://arca.gob.ar/LibrodeSueldosDigital/documentos/nuevos/Conceptos-Basicos-y-Guia-de-Uso.pdf). 

    Tener cuidado porque en esta actualización hubo cambios, incluyendo la adición de un nuevo registro (Registro 06 para observaciones).

- [Guia de Interfaz de Liquidacion LSD](https://www.afip.gob.ar/LibrodeSueldosDigital/documentos/nuevos/G15_interfaz_de_liquidacion_LSD.pdf). Se puede encontrar en las [guias](https://www.afip.gob.ar/LibrodeSueldosDigital/ayuda/guias/default.asp)

- Implementacion oficial en excel: [Libros de Sueldo Digital - Como generar el TXT](https://www.afip.gob.ar/librodesueldosdigital/documentos/nuevos/LSD-ARMADO-TXT-Liquidaciones.zip)

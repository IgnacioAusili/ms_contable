# Dominio y Semántica

La información gestionada por el sistema puede clasificarse en dos grandes grupos:

1. Datos propios de las liquidaciones: corresponden a los resultados y valores utilizados durante el proceso de liquidación. Estos datos adquieren carácter histórico una vez que la liquidación es cerrada, por lo que no requieren un mecanismo adicional de versionado para preservar los resultados obtenidos.

2. Datos maestros: corresponden a la información utilizada como base para realizar las liquidaciones, como los datos de las empresas, empleados, categorías laborales y conceptos de liquidación. A diferencia de los datos propios de una liquidación, estos pueden modificarse a lo largo del tiempo, por lo que es necesario considerar mecanismos que permitan preservar la información relevante utilizada en liquidaciones anteriores.

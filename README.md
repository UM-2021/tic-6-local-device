Para correr en el coral el proyecto es necesario docker, pero para levantar docker en Mendel (una distribucion de linux que tiene la coral), es necesario hacer algunos workaround para ejecutar correctamente docker.

Dichos atajos estan explicados en este issue de github: https://github.com/f0cal/google-coral/issues/32

Una vez instalado docker, cada vez que se prenda la coral, se tiene que ejecutar: sudo dockerd & 
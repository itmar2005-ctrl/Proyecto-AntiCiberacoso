# HOJA DE PRESENTACION

**Titulo del trabajo:** Aprendizaje Automatico: Regresion y Clasificacion

**Asignatura:** Machine Learning / Inteligencia Artificial

**Estudiante:** [Tu nombre completo]

**Docente:** [Nombre del docente]

**Institucion:** [Nombre de la institucion]

**Programa:** [Nombre del programa]

**Fecha:** [Ciudad, dia mes ano]

---

# Aprendizaje Automatico: Regresion y Clasificacion

## Introduccion

El aprendizaje automatico, conocido como Machine Learning (ML), es una rama de la inteligencia artificial que permite a las computadoras aprender patrones a partir de los datos y mejorar su desempeno sin ser programadas de manera explicita para cada situacion. Su importancia ha crecido de forma acelerada debido a la disponibilidad de grandes volumentes de datos y al aumento de la capacidad computacional.

Este trabajo presenta una revision organizada de los fundamentos del ML, con enfasis en algoritmos de regresion y clasificacion, su funcionamiento, aplicaciones y usos practicos. Ademas, se incluye una explicacion conceptual de herramientas ampliamente utilizadas en la analisis de datos, como Pandas y Matplotlib, las cuales facilitan la preparacion, exploracion y visualizacion de la informacion.

## 1. Introduccion al Machine Learning (ML)

### 1.1. ¿Que es el aprendizaje automatico?

El aprendizaje automatico es el conjunto de tecnicas que permiten construir modelos capaces de identificar relaciones en los datos y realizar predicciones o clasificaciones. En lugar de programar reglas fijas, el sistema aprende a partir de ejemplos historicos.

En terminos simples, un algoritmo de ML recibe datos de entrada, detecta patrones y genera un modelo que luego puede usarse para predecir resultados sobre informacion nueva.

### 1.2. Principales aplicaciones en la industria y la vida cotidiana

El ML se utiliza en numerosos sectores:

| Sector | Aplicacion |
|---|---|
| Salud | Diagnostico asistido, prediccion de enfermedades, analisis de imagenes medicas |
| Finanzas | Deteccion de fraude, evaluacion de riesgo crediticio, deteccion de clientes morosos |
| Comercio electronico | Recomendaciones de productos, segmentacion de clientes, prediccion de demanda |
| Industria | Mantenimiento predictivo, control de calidad, automatizacion de procesos |
| Transporte | Vehiculos autonomos, optimizacion de rutas, prediccion de trafico |
| Vida cotidiana | Asistentes virtuales, filtros de spam, reconocimiento facial, traduccion automatica |

### 1.3. Tipos de aprendizaje

#### Aprendizaje supervisado

El modelo aprende a partir de datos etiquetados, es decir, cada ejemplo de entrada tiene una salida conocida. Se usa para regresion y clasificacion.

#### Aprendizaje no supervisado

Trabaja con datos sin etiquetas. El objetivo es descubrir estructuras ocultas, como grupos o patrones. Un ejemplo comun es la agrupacion de clientes mediante clustering.

#### Aprendizaje por refuerzo

Un agente aprende mediante ensayo y error dentro de un entorno. Recibe recompensas o penalizaciones segun sus acciones y busca maximizar la recompensa acumulada.

### 1.4. Diagrama explicativo

```text
                APRENDIZAJE AUTOMATICO
                         |
     -------------------------------------------------
     |                      |                        |
 Supervisado           No supervisado         Por refuerzo
     |                      |                        |
 Entrada + etiqueta     Solo entrada            Agente + entorno
     |                      |                        |
 Prediccion             Descubrimiento          Acciones y recompensas
 de valores             de patrones             para aprender
```

## 2. Algoritmos de Regresion

### 2.1. ¿Que son los algoritmos de regresion?

Los algoritmos de regresion son tecnicas de aprendizaje supervisado que se emplean para predecir un valor continuo. Por ejemplo, precio de una vivienda, temperatura, ventas mensuales o nivel de produccion.

### 2.2. Casos de uso

Los problemas de regresion aparecen cuando el resultado no es una clase, sino un numero real. Se utilizan en economia, ingenieria, salud, ciencias ambientales y negocios.

### 2.3. Representacion general

```text
Variables de entrada (X) ---> Modelo de regresion ---> Valor numerico predicho (Y)
```

### 2.4. Regresion lineal simple

La regresion lineal simple relaciona una variable independiente con una variable dependiente mediante una recta. Su forma general es:

`y = mx + b`

Se utiliza cuando existe una relacion aproximadamente lineal entre dos variables.

**Ejemplo:** predecir el salario segun los anos de experiencia.

### 2.5. Regresion lineal multiple

Extiende la regresion lineal simple al usar dos o mas variables independientes. Su forma general es:

`y = b0 + b1x1 + b2x2 + ... + bnxn`

**Ejemplo:** predecir el precio de una casa segun tamano, numero de habitaciones y ubicacion.

### 2.6. Regresion polinomica

Es una extension de la regresion lineal que incorpora potencias de las variables para modelar relaciones no lineales. Aunque el modelo sigue siendo lineal en los parametros, la curva resultante puede ajustarse mejor a datos curvos.

**Ejemplo:** crecimiento de poblacion o trayectorias fisicas.

### 2.7. Support Vector Machine (SVM) para regresion

La SVM para regresion, o SVR, busca una funcion que se mantenga dentro de un margen de tolerancia alrededor de los valores reales. Es util cuando se requiere buen control del error y robustez frente a ruido.

### 2.8. Arboles de decision para regresion

Un arbol de decision divide el espacio de entrada en regiones segun reglas secuenciales. En regresion, cada region produce un valor numerico, normalmente el promedio de las observaciones en esa hoja.

### 2.9. Bosques aleatorios para regresion

Random Forest Regressor combina varios arboles de decision y promedia sus predicciones. Esto reduce la varianza y mejora la generalizacion.

### 2.10. Esquemas visuales de regresion

```text
Regresion lineal simple
Puntos:   .   . .    .
Recta:   -----------

Regresion polinomica
Puntos:   .  .   .   .
Curva:   ~~~~~~~~~~~~~

Arbol de decision
          [X1 < t?]
          /      \
        si        no
      [X2<t?]    Valor
      /    \
   Valor  Valor
```

### 2.11. Tabla comparativa de algoritmos de regresion

| Algoritmo | Ventaja principal | Limitacion principal | Uso comun |
|---|---|---|---|
| Regresion lineal simple | Facil interpretacion | Solo relaciones lineales | Prediccion basica |
| Regresion lineal multiple | Usa varias variables | Puede sufrir multicolinealidad | Analisis economico |
| Regresion polinomica | Captura no linealidad | Riesgo de sobreajuste | Series con curvatura |
| SVR | Robusto y flexible | Requiere ajuste fino | Datos con ruido |
| Arbol de decision | Interpretable y visual | Puede sobreajustar | Casos con reglas claras |
| Random Forest Regressor | Mejor generalizacion | Menos interpretable | Prediccion estable |

## 3. Problemas de Clasificacion

### 3.1. ¿Que es un problema de clasificacion?

Un problema de clasificacion consiste en asignar una etiqueta a cada observacion dentro de un conjunto de categorias posibles. A diferencia de la regresion, aqui la salida no es un valor continuo, sino una clase.

**Ejemplos:** correo spam o no spam, tumor benigno o maligno, imagen de gato o perro.

### 3.2. Clasificacion binaria y multiclase

La clasificacion binaria tiene solo dos clases posibles. La clasificacion multiclase tiene tres o mas clases.

| Tipo | Descripcion | Ejemplo |
|---|---|---|
| Binaria | Dos categorias | Fraude / No fraude |
| Multiclase | Tres o mas categorias | Tipo de flor, reconocimiento de digitos |

### 3.3. Casos de uso

La clasificacion se usa en diagnostico medico, reconocimiento de imagenes, analisis de sentimiento, deteccion de spam, autenticacion biometrica y deteccion de fallas.

### 3.4. Esquema visual

```text
Entrada de datos ---> Modelo clasificador ---> Clase predicha

Ejemplo binario:
[Correo] ---> [Modelo] ---> [Spam / No spam]

Ejemplo multiclase:
[Imagen] ---> [Modelo] ---> [Gato / Perro / Pajaro]
```

## 4. Algoritmos de Clasificacion

### 4.1. ¿Que son los algoritmos de clasificacion?

Son modelos de aprendizaje supervisado que aprenden a distinguir entre categorias a partir de ejemplos etiquetados. Su objetivo es estimar la clase correcta de una nueva observacion.

### 4.2. Tipos de algoritmos de clasificacion

Entre los algoritmos mas usados se encuentran la regresion logistica, SVM, K-NN, Naive Bayes, arboles de decision y bosques aleatorios.

### 4.3. Regresion logistica

A pesar de su nombre, es un algoritmo de clasificacion. Calcula la probabilidad de pertenencia a una clase mediante la funcion sigmoide. Es muy util en problemas binarios.

**Ejemplo:** predecir si un cliente comprara o no un producto.

### 4.4. Support Vector Machine (SVM)

SVM busca el hiperplano que mejor separe las clases maximizando el margen entre ellas. Funciona muy bien en espacios de alta dimensionalidad.

**Ejemplo:** clasificacion de textos o imagenes.

### 4.5. K-Nearest Neighbors (K-NN)

K-NN clasifica una observacion segun la clase mayoritaria entre sus vecinos mas cercanos. Es simple, intuitivo y no requiere entrenamiento complejo.

**Ejemplo:** clasificar especies o patrones similares.

### 4.6. Naive Bayes

Se basa en el teorema de Bayes y asume independencia condicional entre las variables. Es rapido y funciona bien en filtrado de spam y clasificacion textual.

### 4.7. Arboles de decision para clasificacion

Dividen los datos en ramas segun reglas. Cada hoja representa una clase. Son faciles de interpretar, aunque pueden sobreajustar si crecen demasiado.

### 4.8. Bosques aleatorios para clasificacion

Combinan varios arboles de decision y votan por la clase mas probable. Mejoran la estabilidad y reducen el sobreajuste.

### 4.9. Esquemas visuales de clasificacion

```text
Regresion logistica
Entrada ---> Sigmoide ---> Probabilidad ---> Clase

SVM
Clase A   | margen |   Clase B
          -----------

K-NN
Nuevo punto rodeado por vecinos -> clase mayoritaria

Naive Bayes
Caracteristicas + probabilidades -> clase mas probable

Arbol de decision
          [X1 < t?]
          /      \
       Clase A   [X2<t?]
                   /   \
               Clase B  Clase C
```

### 4.10. Tabla comparativa de algoritmos de clasificacion

| Algoritmo | Ventaja principal | Limitacion principal | Uso comun |
|---|---|---|---|
| Regresion logistica | Rapida e interpretable | No captura relaciones muy complejas | Riesgo, marketing |
| SVM | Buen margen de separacion | Costosa con grandes volumentes de datos | Texto e imagenes |
| K-NN | Muy sencillo | Lento al predecir | Clasificacion basica |
| Naive Bayes | Eficiente y rapido | Suposicion fuerte de independencia | Spam y texto |
| Arbol de decision | Facil de entender | Puede sobreajustar | Diagnostico y reglas |
| Random Forest Classifier | Alta precision y robustez | Menor interpretabilidad | Clasificacion general |

## 5. Aplicacion con herramientas computacionales

### 5.1. Google Colab

Google Colab es un entorno en la nube que permite ejecutar notebooks de Python sin instalacion local. Es muy util para experimentar con modelos de ML, compartir codigo y documentar resultados.

### 5.2. Pandas

Pandas facilita la carga, limpieza, transformacion y analisis de datos tabulares. Con DataFrame, el estudiante puede inspeccionar variables, detectar valores faltantes y preparar conjuntos de entrenamiento y prueba.

### 5.3. Matplotlib

Matplotlib permite crear graficas para visualizar tendencias, distribuciones, correlaciones y resultados de modelos. Es esencial para ilustrar rectas de regresion, curvas polinomicas, matrices de confusion y comparaciones de desempeno.

## 6. Conclusiones

El aprendizaje automatico representa una herramienta fundamental en la solucion de problemas reales porque permite construir modelos que aprenden de los datos y automatizan tareas de prediccion y clasificacion. Dentro de este campo, la regresion se enfoca en valores continuos y la clasificacion en categorias discretas.

Los algoritmos analizados presentan ventajas distintas segun el problema. La regresion lineal destaca por su simplicidad, mientras que modelos como Random Forest y SVM ofrecen mayor flexibilidad y rendimiento en escenarios complejos. En clasificacion, la regresion logistica, Naive Bayes, K-NN y los arboles de decision constituyen opciones fundamentales por su eficacia y aplicabilidad.

El uso de Google Colab, Pandas y Matplotlib complementa el aprendizaje teorico al permitir experimentar con datos reales, organizar la informacion y representar visualmente los resultados. En conjunto, estos conceptos constituyen una base solida para el estudio y aplicacion del Machine Learning.

## Bibliografia

Bishop, C. M. (2006). *Pattern recognition and machine learning*. Springer.

Géron, A. (2022). *Hands-on machine learning with Scikit-Learn, Keras, and TensorFlow* (3rd ed.). O'Reilly Media.

Hastie, T., Tibshirani, R., & Friedman, J. (2009). *The elements of statistical learning: Data mining, inference, and prediction* (2nd ed.). Springer.

James, G., Witten, D., Hastie, T., & Tibshirani, R. (2021). *An introduction to statistical learning: With applications in Python*. Springer.

Murphy, K. P. (2022). *Probabilistic machine learning: An introduction*. The MIT Press.

Russell, S. J., & Norvig, P. (2021). *Artificial intelligence: A modern approach* (4th ed.). Pearson.

Scikit-learn developers. (n.d.). *Scikit-learn user guide*. https://scikit-learn.org/stable/user_guide.html

Google. (n.d.). *Colab research*. https://colab.research.google.com/

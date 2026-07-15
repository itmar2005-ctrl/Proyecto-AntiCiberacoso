const comparisons = [
  {
    index: 1,
    leftTitle: '8 Puzzle',
    rightTitle: 'Torre de Hanoi (3 discos)',
    relation: 'Los dos muestran busqueda en espacio de estados, pero el primero mueve una casilla vacia y el segundo mueve discos entre torres.',
    leftExplain: 'La lamina 1 superior desarrolla el 8 puzzle como una secuencia de movimientos del espacio vacio. Cada tablero es un estado, cada flecha es una accion valida y el objetivo es llegar a la configuracion ordenada con el minimo numero de pasos.',
    rightExplain: 'La lamina 1 inferior explica Hanoi con dos representaciones: arbol de ruta y grafo de estados. El estado inicial pone los tres discos en la torre A y la solucion minimiza movimientos respetando la regla clave: nunca un disco grande sobre uno pequeno.',
    details: [
      'En 8 puzzle importa la posicion relativa de 9 casillas; en Hanoi importa la distribucion de 3 discos entre 3 torres.',
      'El puzzle superior enfatiza operadores locales: mover arriba, abajo, izquierda o derecha.',
      'Hanoi enfatiza restricciones jerarquicas: que disco se puede mover y en que torre puede colocarse.',
      'Ambos sirven para ensenar nodos, transiciones y camino mas corto, pero con logicas de restriccion distintas.'
    ],
    takeaway: 'Este par ayuda a distinguir dos clases clasicas de busqueda: reordenamiento por deslizamiento frente a transferencia estructurada con reglas de tamano.'
  },
  {
    index: 2,
    leftTitle: '8 Reinas',
    rightTitle: '8 Reinas',
    relation: 'Es el par mas directo: ambas laminas explican exactamente el mismo problema desde enfoques visuales distintos.',
    leftExplain: 'La lamina 2 superior ordena el problema por filas y columnas. Va mostrando en que columna se coloca una reina por fila hasta construir una configuracion valida donde ninguna reina se ataca.',
    rightExplain: 'La lamina 2 inferior combina definicion formal, arbol de decisiones y grafo de estados. Tambien incluye una solucion expresada como vector de columnas, lo que vuelve la representacion mas matematica.',
    details: [
      'En ambos casos el estado puede leerse como una secuencia de decisiones fila por fila.',
      'La condicion de exito es la misma: evitar ataques por fila, columna y diagonal.',
      'La lamina superior es mas procedimental: muestra avance por posiciones concretas del tablero.',
      'La inferior es mas academica: resume operadores, costo y estado objetivo en formato formal.'
    ],
    takeaway: 'Las dos imagenes se complementan muy bien: una muestra la construccion paso a paso y la otra formaliza el problema como busqueda combinatoria.'
  },
  {
    index: 3,
    leftTitle: 'Cruce del Acantilado',
    rightTitle: 'Laberinto (camino mas corto)',
    relation: 'Los dos son problemas de desplazamiento, pero el primero es un cruce con grupos y tiempos/reglas, mientras el segundo es una ruta sobre un mapa.',
    leftExplain: 'La lamina 3 superior modela un cruce por turnos entre lados opuestos. Los estados describen quien queda en cada lado y las flechas representan cruces o regresos permitidos hasta alcanzar la meta.',
    rightExplain: 'La lamina 3 inferior reduce el problema a un laberinto. El arbol enumera decisiones desde el nodo S y el grafo sobre la cuadricula destaca un camino rojo hasta G.',
    details: [
      'El cruce del acantilado trabaja con combinaciones de personas u objetos y restricciones de traslado.',
      'El laberinto trabaja con vecindad espacial: solo puedes pasar por celdas validas.',
      'En el superior, un error deja una composicion insegura o no permitida; en el inferior, un error te mete en un callejon o camino mas largo.',
      'Ambos ilustran la idea de explorar estados, retroceder y elegir la ruta valida o minima.'
    ],
    takeaway: 'Este par contrasta busqueda sobre conjuntos de actores contra busqueda geografica sobre posiciones en una cuadricula.'
  },
  {
    index: 4,
    leftTitle: 'Cruzar el rio',
    rightTitle: 'Misioneros y Canibales',
    relation: 'Ambos pertenecen a la familia de cruces de rio con restricciones de seguridad.',
    leftExplain: 'La lamina 4 superior presenta varias opciones de cruce entre padre, madre, hijos, policia y ladron. La estructura no se enfoca tanto en una sola ruta, sino en patrones de movimientos seguros que conservan las restricciones familiares y de vigilancia.',
    rightExplain: 'La lamina 4 inferior formaliza el clasico problema de 3 misioneros y 3 canibales. Cada estado se escribe como una tupla y el objetivo es llevar a todos a la orilla derecha sin dejar que los canibales superen a los misioneros donde estos esten presentes.',
    details: [
      'El superior maneja un conjunto heterogeneo de personajes con permisos especificos de conduccion o acompanamiento.',
      'El inferior usa una regla numerica simple pero estricta sobre cantidades relativas.',
      'En ambos casos la clave no es solo cruzar, sino preservar estados intermedios validos.',
      'Los dos son ejemplos fuertes de poda: muchas acciones posibles se descartan por inseguras.'
    ],
    takeaway: 'Este par muestra como una misma idea de transporte con restricciones puede modelarse con personajes concretos o con conteos abstractos.'
  },
  {
    index: 5,
    leftTitle: 'Cruce de los Sapitos',
    rightTitle: 'Puzzle 8 (deslizante)',
    relation: 'Ambos son rompecabezas de reordenamiento, donde una accion local cambia la configuracion global.',
    leftExplain: 'La lamina 5 superior representa el intercambio de sapitos que miran en direcciones opuestas. Cada movimiento es salto o avance corto segun el lado al que pertenece cada grupo, y la solucion minimiza pasos hasta invertir posiciones.',
    rightExplain: 'La lamina 5 inferior presenta otra vez el puzzle deslizante, pero de manera mas formal: estado inicial, operadores, objetivo, arbol de ruta y grafo del espacio de estados.',
    details: [
      'En los sapitos hay dos tipos de piezas con direccion fija; en el puzzle 8 hay fichas numeradas y un espacio vacio.',
      'Los sapitos tienen movimientos semidirigidos; el puzzle 8 permite mover el vacio en cuatro direcciones si existe casilla vecina.',
      'Ambos problemas muestran que una secuencia corta y legal puede no ser obvia si no exploras sistematicamente el espacio de estados.',
      'Los dos son utiles para explicar heuristicas y minimizacion de movimientos.'
    ],
    takeaway: 'Este par compara dos rompecabezas pequenos donde la dificultad real no es la accion individual sino el orden correcto de acciones.'
  },
  {
    index: 6,
    leftTitle: 'El Granjero',
    rightTitle: 'Viajero (4 ciudades)',
    relation: 'Los dos exigen planificar una secuencia completa, pero uno cuida compatibilidades y el otro optimiza distancia.',
    leftExplain: 'La lamina 6 superior corresponde al problema del granjero con lobo, cabra y col. Cada cruce debe evitar dejar combinaciones peligrosas sin supervision. El diagrama enumera viajes seguros y resalta una secuencia minima.',
    rightExplain: 'La lamina 6 inferior transforma el recorrido entre ciudades en un problema de costo. Las aristas llevan pesos y la solucion encontrada visita todas las ciudades y regresa al origen con costo total indicado.',
    details: [
      'El granjero es un problema de restriccion logica: ciertos estados son invalidos aunque parezcan cercanos a la meta.',
      'El viajero es un problema de optimizacion: muchos estados son validos, pero unos cuestan mas que otros.',
      'En el superior el costo suele medirse en cruces; en el inferior, en distancia acumulada.',
      'Ambos son excelentes para explicar por que no basta con avanzar: hay que evaluar consecuencias globales.'
    ],
    takeaway: 'Este par separa dos objetivos clasicos de IA: llegar de forma segura frente a llegar con el menor costo posible.'
  },
  {
    index: 7,
    leftTitle: 'Grundy - 7 monedas',
    rightTitle: 'Carga de camion (capacidad 7)',
    relation: 'Ambos trabajan con descomposiciones numericas, aunque uno es juego combinatorio y el otro es llenado de capacidad.',
    leftExplain: 'La lamina 7 superior muestra particiones de 7 monedas en montones siguiendo reglas del juego de Grundy. El arbol refleja como un estado se divide en subestados hasta llegar a configuraciones terminales.',
    rightExplain: 'La lamina 7 inferior modela un camion con capacidad 7 y acciones de cargar cajas de distintos pesos. El objetivo es alcanzar exactamente la carga 7 con costo uniforme por accion.',
    details: [
      'En Grundy el estado es una particion de enteros; en el camion el estado es una suma parcial de capacidad ocupada.',
      'El primero explora jugadas legales; el segundo explora combinaciones factibles de carga.',
      'Grundy se entiende mejor como juego de decision y teoria de posiciones; el camion como problema de satisfaccion de capacidad.',
      'Los dos ayudan a visualizar como un numero puede transformarse paso a paso bajo reglas.'
    ],
    takeaway: 'Este par enseña que una misma base numerica puede representar un juego competitivo o una planificacion utilitaria.'
  },
  {
    index: 8,
    leftTitle: 'Grundy - 9 monedas',
    rightTitle: 'Robot aspiradora',
    relation: 'Los dos implican cubrir estados sucesivos, pero uno se enfoca en particiones de monedas y el otro en recorrer celdas hasta limpiar todo.',
    leftExplain: 'La lamina 8 superior amplía Grundy a 9 monedas, por lo que el arbol crece y aparecen mas particiones posibles. Eso hace visible como aumenta la complejidad al crecer el estado inicial.',
    rightExplain: 'La lamina 8 inferior presenta una aspiradora que debe limpiar todas las casillas. El problema combina posicion del robot y estado de limpieza de cada celda, de modo que no solo importa donde esta, sino que ya hizo.',
    details: [
      'Grundy 9 incrementa la ramificacion combinatoria respecto a Grundy 7.',
      'La aspiradora introduce memoria del entorno: cada casilla puede estar sucia o limpia.',
      'Ambos muestran explosion del espacio de estados cuando aumentan variables o recursos.',
      'El superior sirve para razonamiento combinatorio; el inferior para planificacion secuencial en ambientes discretos.'
    ],
    takeaway: 'Este par deja claro que el tamano del espacio de estados crece rapido tanto por mas elementos numericos como por mas atributos del entorno.'
  },
  {
    index: 9,
    leftTitle: 'Jarras de agua',
    rightTitle: 'Cruzar puente con linterna',
    relation: 'Ambos son problemas pequenos pero muy conocidos de planificacion con restricciones de accion.',
    leftExplain: 'La lamina 9 superior usa jarras de 4 y 3 litros. Los nodos son cantidades de agua en cada jarra y las transiciones son llenar, vaciar o verter hasta alcanzar el volumen objetivo.',
    rightExplain: 'La lamina 9 inferior organiza el cruce de puente con personas de tiempos distintos y una linterna obligatoria. El costo de una accion depende del integrante mas lento del grupo que cruza.',
    details: [
      'Jarras es un problema de transformacion de cantidades discretas.',
      'Puente con linterna es un problema de coordinacion temporal y costo desigual.',
      'En ambos, una accion que parece avanzar mucho puede empeorar el total si obliga a retornos caros.',
      'Los dos se usan para introducir estrategias optimas frente a secuencias ingenuas.'
    ],
    takeaway: 'Este par compara dos rompecabezas de planificacion donde la mejor solucion surge al pensar varios pasos por adelantado, no solo el siguiente.'
  },
  {
    index: 10,
    leftTitle: '6 damas en esquina',
    rightTitle: 'Dieta optima',
    relation: 'Uno es un problema espacial de piezas sobre tablero y el otro es un problema de seleccion con restricciones nutricionales.',
    leftExplain: 'La lamina 10 superior muestra un tablero con 6 damas ubicadas en una esquina y una secuencia de movimientos o saltos para llevarlas a otra configuracion. El foco esta en como una pieza libera o bloquea trayectorias para las siguientes.',
    rightExplain: 'La lamina 10 inferior formula una dieta optima donde cada alimento aporta nutrientes y tiene costo. El objetivo es cubrir requerimientos minimos al menor precio posible.',
    details: [
      'Las damas trabajan con geometria, ocupacion de casillas y secuencia de movimientos.',
      'La dieta trabaja con combinacion de recursos, cumplimiento de restricciones y minimizacion de costo.',
      'En el superior una mala jugada bloquea posicionamiento; en el inferior una mala seleccion incumple nutrientes o encarece la solucion.',
      'Ambos son ejemplos de busqueda guiada por objetivo, aunque la naturaleza del estado cambia por completo.'
    ],
    takeaway: 'Este par ayuda a ver que la idea de “resolver un problema” no siempre es moverse en un tablero; a veces es escoger una combinacion optima.'
  },
  {
    index: 11,
    leftTitle: '9 damas en esquina',
    rightTitle: 'Jarras de agua (4L y 3L)',
    relation: 'El emparejamiento muestra un contraste fuerte entre una configuracion espacial mas grande y un problema aritmetico de medicion exacta.',
    leftExplain: 'La lamina 11 superior es una version mas grande del reto de damas en esquina. Al crecer el numero de piezas aumenta mucho la dificultad porque hay mas interferencia entre trayectorias y mas decisiones de orden.',
    rightExplain: 'La lamina 11 inferior vuelve al problema de jarras pero en formato formal. Resume estado inicial, operadores, objetivo y camino encontrado, lo que facilita leerlo como ejemplo canonico de espacio de estados.',
    details: [
      '9 damas amplifica la complejidad del caso de 6 damas.',
      'Jarras mantiene pocas variables, pero exige aplicar operaciones exactas en un orden inteligente.',
      'El superior destaca complejidad por densidad de piezas; el inferior por secuencia logica de transformaciones.',
      'En ambos la solucion correcta depende del orden, no solo de los operadores disponibles.'
    ],
    takeaway: 'Este par contrasta complejidad por congestion espacial frente a complejidad por encadenamiento exacto de acciones.'
  },
  {
    index: 12,
    leftTitle: 'Intercambio de piramides',
    rightTitle: 'Colorear mapa (3 colores)',
    relation: 'Ambos trabajan con asignaciones validas, aunque uno reubica fichas y el otro asigna colores a regiones.',
    leftExplain: 'La lamina 12 superior presenta dos piramides de fichas de distinto color y busca intercambiarlas de posicion mediante movimientos permitidos. La dificultad esta en conservar la forma y permitir el paso gradual entre estructuras.',
    rightExplain: 'La lamina 12 inferior presenta un grafo de regiones adyacentes. Colorear el mapa significa asignar un color a cada nodo sin repetir color en nodos vecinos.',
    details: [
      'Intercambio de piramides es un problema de permutacion espacial.',
      'Colorear mapa es un problema de consistencia entre vecinos.',
      'En el superior importan huecos y desplazamientos; en el inferior importan conflictos de adyacencia.',
      'Ambos son buenos ejemplos de restricciones globales que dependen de decisiones locales.'
    ],
    takeaway: 'Este par enseña dos formas distintas de asignar estructura: mover piezas hasta un patron final o etiquetar nodos sin romper compatibilidad.'
  },
  {
    index: 13,
    leftTitle: 'Misioneros y canibales',
    rightTitle: 'Juego del 15 (deslizante)',
    relation: 'Ambos son problemas clasicos de aula para explicar estados, operadores y solucion objetivo, pero con reglas muy diferentes.',
    leftExplain: 'La lamina 13 superior vuelve a misioneros y canibales de forma compacta. El camino mas corto se expresa como una secuencia de cruces y regresos, destacando que la validez de cada estado intermedio es fundamental.',
    rightExplain: 'La lamina 13 inferior muestra el juego del 15, una version mas grande del puzzle deslizante. El espacio de estados es mucho mayor porque hay 15 fichas y un hueco, y no todas las configuraciones son alcanzables desde cualquier inicio.',
    details: [
      'Misioneros y canibales depende de una restriccion social o de seguridad.',
      'Juego del 15 depende de paridad y de desplazamiento del hueco en una cuadricula mayor.',
      'El superior tiene pocos objetos pero reglas muy estrictas; el inferior tiene muchas permutaciones posibles.',
      'Los dos sirven para explicar por que el tamano y el tipo de restriccion determinan la dificultad.'
    ],
    takeaway: 'Este par enfrenta un problema pequeno pero delicado contra uno enorme y mecanico, mostrando dos fuentes distintas de complejidad.'
  },
  {
    index: 14,
    leftTitle: 'Tic Tac Toe',
    rightTitle: 'Cruzar animales (zorro, cabra, repollo)',
    relation: 'Ambos requieren anticipacion, pero uno es competitivo y el otro es de transporte seguro.',
    leftExplain: 'La lamina 14 superior representa un arbol de decisiones para tres en raya. Cada nodo es un tablero parcial y cada jugada busca una linea ganadora o evitar que el rival la forme.',
    rightExplain: 'La lamina 14 inferior presenta el clasico problema de zorro, cabra y repollo. El granjero debe trasladarlos sin dejar al zorro con la cabra ni a la cabra con el repollo.',
    details: [
      'Tic tac toe es adversarial: debes pensar tu jugada y la respuesta del oponente.',
      'Cruzar animales es no adversarial: el “enemigo” son las restricciones del entorno.',
      'En el superior el estado incluye marcas X y O; en el inferior incluye posiciones de cuatro entidades entre orillas.',
      'Ambos muestran por que anticipar consecuencias futuras es central en IA y resolucion de problemas.'
    ],
    takeaway: 'Este par compara planificacion competitiva contra planificacion segura, dos estilos muy distintos de razonamiento secuencial.'
  },
  {
    index: 15,
    leftTitle: 'Torres de Hanoi (3 discos)',
    rightTitle: 'Camino minimo en grafo (Dijkstra)',
    relation: 'Los dos cierran la coleccion con rutas optimas, pero uno lo hace sobre reglas de manipulacion y el otro sobre pesos de aristas.',
    leftExplain: 'La lamina 15 superior desarrolla Hanoi destacando el camino mas corto de 7 movimientos. Es un caso perfecto para mostrar recursion, estructura de subproblemas y secuencia minima garantizada.',
    rightExplain: 'La lamina 15 inferior explica camino minimo sobre un grafo ponderado. La solucion recorre nodos y suma pesos hasta llegar al destino con costo total minimo, siguiendo la logica que inspira algoritmos como Dijkstra.',
    details: [
      'Hanoi tiene costo uniforme por movimiento y restricciones estrictas de legalidad.',
      'Dijkstra trabaja con costos variables y compara acumulados para elegir la mejor ruta.',
      'El superior se entiende como una estructura recursiva; el inferior como optimizacion sobre red ponderada.',
      'Ambos son esenciales para estudiar estrategias de minimizacion, pero en dominios muy diferentes.'
    ],
    takeaway: 'Este ultimo par resume muy bien la diferencia entre resolver por reglas internas del problema y resolver por evaluacion de costos sobre un grafo.'
  }
];

function renderComparison(item) {
  return `
    <article class="comparison-card card" id="pair-${item.index}">
      <div class="comparison-header">
        <div>
          <p class="eyebrow">Par ${item.index}</p>
          <h2>${item.leftTitle} vs ${item.rightTitle}</h2>
        </div>
        <span class="pill info">${item.leftTitle} <-> ${item.rightTitle}</span>
      </div>

      <div class="comparison-columns">
        <section class="comparison-panel">
          <h3>Imagen ${item.index} superior</h3>
          <p class="comparison-title">${item.leftTitle}</p>
          <p>${item.leftExplain}</p>
        </section>

        <section class="comparison-panel">
          <h3>Imagen ${item.index} inferior</h3>
          <p class="comparison-title">${item.rightTitle}</p>
          <p>${item.rightExplain}</p>
        </section>
      </div>

      <section class="comparison-summary">
        <h3>Relacion entre ambas</h3>
        <p>${item.relation}</p>
      </section>

      <section class="comparison-summary">
        <h3>Lectura detallada</h3>
        <ul>
          ${item.details.map((detail) => `<li>${detail}</li>`).join('')}
        </ul>
      </section>

      <section class="comparison-summary">
        <h3>Que debes aprender de este par</h3>
        <p>${item.takeaway}</p>
      </section>
    </article>
  `;
}

window.addEventListener('DOMContentLoaded', () => {
  const container = document.querySelector('#comparisonGrid');
  container.innerHTML = comparisons.map(renderComparison).join('');
});

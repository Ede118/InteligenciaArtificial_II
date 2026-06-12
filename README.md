# Repositorio de Trabajos Prácticos - Inteligencia Artificial II 🤖🧠

Este repositorio contiene los trabajos prácticos, proyectos y ejercicios desarrollados durante el cursado de la materia **Inteligencia Artificial II** 2026, en la Facultad de Ingeniería de la Universidad Nacional de Cuyo.

## 👥 Integrantes:

$$
\begin{array}{l|l} 
 \text{Integrantes} & \text{Legajos}  \\
 \hline 
 \text{Avila, Julieta} & 14099 \\
 \text{Barraquero, Ignacio} & 14060 \\
 \text{Barrios, Federico} & 14101 \\
 \text{Campo, Camila} & 13667 \\
 \text{Patricceli, Nicolas} & 14090 
\end{array}
$$

---

## 📋 Descripción de los Trabajos Prácticos

A lo largo del semestre, exploramos e implementamos diversos algoritmos y modelos de la Inteligencia Artificial. A continuación se detalla el contenido de cada trabajo práctico:

* **TP 1: Búsqueda y Optimización**
  * **Objetivo:** Implementar algoritmos de búsqueda global y local para optimizar la navegación y recolección (*picking*) de un montacargas en un almacén logístico.
  * **Conceptos clave:** Algoritmo A* (con diseño de heurística propia), Búsqueda en entornos dinámicos (evasión de colisiones entre múltiples agentes), y Búsqueda Local utilizando Temple Simulado (Simulated Annealing).

* **TP 2: Inferencia Lógica y Sistemas Difusos**
  * **Objetivo:** Analizar los fundamentos de la lógica proposicional y de primer orden frente a los algoritmos de búsqueda, además de modelar matemáticamente las ecuaciones de movimiento de un sistema físico de carro-péndulo. 
  * **Conceptos clave:** Base de Conocimientos vs. Ground Truth, Motores de Inferencia (Forward/Backward Chaining), Planificadores (Fast Downward, PDDL), y modelado para Lógica Difusa.

* **TP 3: Redes Neuronales y Algoritmos Genéticos (Neuroevolución)**
  * **Objetivo:** Desarrollar modelos de aprendizaje profundo para regresión y clasificación de imágenes, y aplicar algoritmos genéticos para optimizar los pesos de una red neuronal capaz de jugar automáticamente al "Dino Game" de Google Chrome.
  * **Conceptos clave:** Redes Neuronales Multicapa (Fully-Connected), Clasificación con el dataset MNIST, TensorFlow, Algoritmos Genéticos (Selección, Cruce y Mutación aplicados a pesos de redes neuronales).
---

## 🛠️ Tecnologías y Librerías Utilizadas

El código fue desarrollado principalmente en **Python 3.x**. Las librerías más destacadas incluyen:

* `numpy` y `pandas`: Para manipulación matemática y análisis de datos.
* `scikit-learn`: Para modelos clásicos de Machine Learning.
* `matplotlib` y `seaborn`: Para visualización de datos y resultados.
* Jupyter Notebooks (`.ipynb`): Para la presentación interactiva de los resultados.

---

## 📁 Estructura del Repositorio

```text
.
├── dependencias.md
├── README.md
├── requirements.txt
├── TP1
│   ├── Ejercicio1.py
│   ├── Ejercicio2.py
│   ├── Ejercicio3.py
│   ├── Ejercicio4.py
│   ├── Ejercicio4torneo.py
│   ├── TP1.ipynb
│   └── utilities
├── TP2
│   ├── attachments
│   ├── Controller A.J. - Python
│   ├── Controller B.F. - MATLAB
│   ├── Controller C.C. - Python
│   ├── Controller P.N. - Python
│   ├── planta.py
│   └── TP2.ipynb
└── TP3
    ├── E1
    ├── E2
    ├── E3
    ├── E4 wo velocity
    ├── E4 w velocity
    ├── Imagen
    └── TrabajoPractico3.ipynb
```

---

## 🚀 Instalación y Uso

Si deseas clonar este repositorio y probar los algoritmos localmente, sigue estos pasos:

1. **Clonar el repositorio:**
```bash
git clone [https://github.com/](https://github.com/)[TU-USUARIO]/[NOMBRE-DEL-REPO].git
cd [NOMBRE-DEL-REPO]

```


2. **Crear un entorno virtual (Recomendado):**
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
venv\Scripts\activate     # En Windows

```


3. **Instalar las dependencias:**
Asegúrate de tener instaladas las librerías necesarias ejecutando:
```bash
pip install -r requirements.txt

```


4. **Ejecutar los notebooks:**
```bash
jupyter notebook

```

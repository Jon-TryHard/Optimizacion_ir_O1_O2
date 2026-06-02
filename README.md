# Optimización de Representación Intermedia (IR) - O1 y O2

Este repositorio contiene la implementación en Python de un optimizador de Representación Intermedia (IR), enfocado en el desarrollo y análisis de técnicas de optimización correspondientes a los niveles **O1** y **O2**.

## 🚀 Descripción del Proyecto

El objetivo principal es demostrar cómo se transforma y mejora el código intermedio mediante algoritmos escritos en Python. El proyecto analiza las diferencias entre el código IR original y las optimizaciones progresivas aplicadas (como la eliminación de código muerto, propagación de constantes, plegado de constantes, optimización de ciclos, entre otras).

## 🛠️ Tecnologías y Entorno

* **Lenguaje de Programación:** Python 3.x
* **Entorno recomendado:** Linux / Debian
* **Librerías/Módulos:** Estándar de Python (o especificar si usas paquetes adicionales como `llvmlite`, `graphviz`, etc.)

## ⚙️ Instalación y Requisitos

Para clonar y ejecutar este optimizador en tu máquina local, sigue estos pasos:

```bash
# Clona el repositorio
git clone [https://github.com/Jon-TryHard/Optimizacion_ir_O1_O2.git](https://github.com/Jon-TryHard/Optimizacion_ir_O1_O2.git)
cd Optimizacion_ir_O1_O2

# (Opcional) Configurar un entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias (en caso de tener un archivo requirements.txt)
# pip install -r requirements.txt
💻 Uso
[Modifica el nombre del script principal según cómo lo hayas estructurado en tu proyecto]

Para ejecutar el analizador y aplicar las optimizaciones sobre un archivo de entrada:

Bash
# Ejecutar optimización nivel O1
python main.py --level O1 --file codigo_intermedio.txt

# Ejecutar optimización nivel O2
python main.py --level O2 --file codigo_intermedio.txt
👨‍💻 Autor
Jonathan David Ochoa Echeverri - Jon-TryHard

Estudiante de Ingeniería de Sistemas y Computación - Universidad Tecnológica de Pereira (UTP).

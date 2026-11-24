# BookScope — Web Scraping + Streamlit

Proyecto académico de scraping y análisis de libros con **Requests, BeautifulSoup, Pandas, Plotly y Streamlit**.

## 1. Requisitos

- Python 3.10 o superior.
- Conexión a Internet para consultar Books to Scrape.
- Instalar dependencias:

```bash
pip install -r requirements.txt
```

## 2. Ejecutar el scraping

Desde la carpeta raíz del proyecto:

```bash
python scraper.py --max-pages 5 --delay 1.2
```

Cada página contiene aproximadamente 20 libros. Por defecto se consultan 5 páginas y se guarda el resultado en `data/libros.csv`.

Para ampliar la extracción:

```bash
python scraper.py --max-pages 10 --delay 1.5
```

El programa:
1. Consulta `robots.txt` antes de iniciar.
2. Identifica las peticiones con un User-Agent propio.
3. Utiliza pausas entre las peticiones.
4. Extrae título, precio, disponibilidad, valoración, categoría y enlaces.
5. Convierte los precios a números, transforma las valoraciones a escala numérica, limpia espacios y elimina duplicados.
6. Guarda el resultado en CSV con Pandas.

El scraper consulta la ficha de cada libro para obtener su categoría. Por respeto al servidor, no reduzcas el retardo configurado.

## 3. Ejecutar el dashboard

Después de generar el CSV:

```bash
streamlit run app.py
```

Streamlit abrirá el dashboard en el navegador. Incluye:
- Filtro múltiple por categoría.
- Rango de precios.
- Filtro por valoración.
- Indicadores de cantidad y medias.
- Gráfico de precio medio por categoría.
- Dispersión de precio frente a valoración.
- Histograma de precios.
- Tabla interactiva y descarga de los resultados filtrados.

## 4. Estructura

```text
Proyecto_Scraping_Streamlit/
├── app.py
├── scraper.py
├── requirements.txt
├── README.md
└── data/
    └── .gitkeep
```

`data/libros.csv` se crea al ejecutar `scraper.py`; no se incluyen datos inventados.

## 5. Ética y limitaciones

Books to Scrape es un sitio de demostración para practicar scraping. Aun así, el programa comprueba `robots.txt`, se identifica, aplica pausas y limita el número de páginas. Antes de adaptar el scraper a otra web, revisa sus términos de uso y sus reglas de acceso automatizado. No recopiles datos personales ni contenido protegido sin autorización.

## 6. Preguntas para defender la práctica

**¿Qué hace BeautifulSoup?**  
Analiza el HTML descargado y permite localizar elementos mediante selectores CSS.

**¿Para qué sirve Requests?**  
Realiza peticiones HTTP para obtener el contenido HTML de las páginas.

**¿Por qué se utiliza Pandas?**  
Para estructurar los registros en un DataFrame, limpiar y convertir datos y exportarlos a CSV.

**¿Qué es un User-Agent?**  
Es una cabecera HTTP que identifica al cliente que realiza la petición.

**¿Qué es robots.txt?**  
Es un archivo que comunica qué partes de un sitio permite o desaconseja rastrear a los robots automatizados.

**¿Por qué se usa time.sleep()?**  
Para espaciar las peticiones y evitar cargar innecesariamente el servidor.

**¿Qué diferencia hay entre scraping y una API?**  
El scraping extrae información del contenido de una web; una API ofrece una interfaz estructurada para consultar datos.

**¿Qué hace Streamlit?**  
Convierte un script de Python en una aplicación web interactiva.

**¿Qué representa el gráfico de dispersión?**  
Muestra cómo se distribuyen los precios frente a las valoraciones. Permite observar patrones, pero no demuestra que el precio cause una valoración mayor o menor.

**¿Por qué se convierte el precio a float?**  
Para poder calcular medias, máximos, mínimos y filtrar por rangos numéricos.

## 7. Entrega en GitHub

Crea un repositorio y sube los archivos del proyecto. No es necesario subir el entorno virtual. Incluye el CSV generado si el profesor quiere comprobar los datos extraídos.

```bash
git init
git add .
git commit -m "Proyecto de scraping y dashboard con Streamlit"
git branch -M main
git remote add origin URL_DE_TU_REPOSITORIO
git push -u origin main
```

Antes de entregar, ejecuta el scraper y el dashboard en tu equipo y comprueba que los datos se cargan correctamente.

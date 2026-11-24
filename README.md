# BookScope — Web Scraping + Streamlit

Proyecto académico de scraping y análisis de libros con **Requests, BeautifulSoup, Pandas, Plotly y Streamlit**.

## Requisitos

- Python 3.10 o superior.
- Conexión a Internet para consultar Books to Scrape.
- Instalar las dependencias:

```bash
pip install -r requirements.txt
```

## Ejecutar el scraping

Desde la carpeta raíz, ejecuta:

```bash
python scraper.py
```

Por defecto, el scraper intenta recopilar **100 libros** y guarda los resultados en `data/libros.csv`. Puedes indicar otra cantidad y el tiempo de espera entre peticiones:

```bash
python scraper.py --target-books 100 --delay 1.0
python scraper.py --target-books 150 --delay 1.5
```

El retardo mínimo permitido es de 0,5 segundos. El scraper comprueba `robots.txt`, se identifica con un User-Agent propio, recorre las páginas de categorías y evita duplicados por URL. Extrae título, precio, disponibilidad, valoración, categoría y enlaces; después limpia los datos y los guarda en CSV. No visita las fichas individuales de cada libro.

## Ejecutar el dashboard

Después de generar el CSV:

```bash
streamlit run app.py
```

El dashboard permite filtrar por categoría, precio y valoración; muestra indicadores y gráficos de precios y valoraciones; y ofrece una tabla interactiva con descarga de los resultados filtrados.

## Estructura

```text
Proyecto_Scraping_Streamlit/
├── app.py
├── scraper.py
├── requirements.txt
├── README.md
└── data/
    ├── .gitkeep
    └── libros.csv
```

El repositorio incluye `data/libros.csv` con los 100 registros recopilados para que el dashboard pueda abrirse directamente. Ejecutar el scraper vuelve a generar ese archivo.

## Ética y limitaciones

Books to Scrape es un sitio de demostración para practicar scraping. Aun así, el programa comprueba `robots.txt`, se identifica, aplica pausas y limita la cantidad solicitada. Antes de adaptar el scraper a otra web, revisa sus términos de uso y sus reglas de acceso automatizado. No recopiles datos personales ni contenido protegido sin autorización.

## Preguntas para defender la práctica

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

## Actualizar el proyecto en GitHub

El repositorio está en [github.com/ikermayorr/BookScope](https://github.com/ikermayorr/BookScope). Después de clonar el proyecto y hacer cambios, puedes publicarlos así:

```bash
git add README.md
git commit -m "Update BookScope documentation"
git push origin main
```


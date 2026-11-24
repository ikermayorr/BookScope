
"""
BookScope - Web Scraper

Extraccion de libros de Books to Scrape.
Tecnologias: Requests, BeautifulSoup y Pandas.

Uso:
    python scraper.py
    python scraper.py --target-books 100 --delay 0.5
"""

import argparse
import re
import time
from pathlib import Path
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import requests
import pandas as pd
from bs4 import BeautifulSoup


# --------------------------------------------------
# CONFIGURACION
# --------------------------------------------------

BASE_URL = "https://books.toscrape.com/"
ROBOTS_URL = urljoin(BASE_URL, "robots.txt")

USER_AGENT = "BookScope/2.0 (educational project)"

HEADERS = {
    "User-Agent": USER_AGENT
}

OUTPUT = Path(__file__).parent / "data" / "libros.csv"

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


# --------------------------------------------------
# CREAR SESION
# --------------------------------------------------

def create_session():
    """Crea una sesion HTTP reutilizable."""

    session = requests.Session()
    session.headers.update(HEADERS)

    return session


# --------------------------------------------------
# COMPROBAR ROBOTS.TXT
# --------------------------------------------------

def check_robots(session):
    """
    Comprueba las reglas de robots.txt.

    Si el servidor devuelve 404, se interpreta
    que no existe un archivo robots.txt publicado.
    """

    response = session.get(
        ROBOTS_URL,
        timeout=20
    )

    parser = RobotFileParser()
    parser.set_url(ROBOTS_URL)

    if response.status_code == 404:
        print(
            "Aviso: robots.txt no encontrado. "
            "Se continua con pausas entre peticiones."
        )
        parser.parse([])
        return parser

    response.raise_for_status()

    parser.parse(response.text.splitlines())

    if not parser.can_fetch(USER_AGENT, BASE_URL):
        raise PermissionError(
            "robots.txt no permite el acceso automatizado."
        )

    return parser


# --------------------------------------------------
# DESCARGAR Y ANALIZAR HTML
# --------------------------------------------------

def get_soup(session, url, robots):
    """Descarga una pagina y devuelve su contenido HTML."""

    if not robots.can_fetch(USER_AGENT, url):
        raise PermissionError(
            f"Acceso no permitido por robots.txt: {url}"
        )

    response = session.get(
        url,
        timeout=20
    )

    response.raise_for_status()

    return BeautifulSoup(
        response.text,
        "html.parser"
    )


# --------------------------------------------------
# LIMPIAR PRECIOS
# --------------------------------------------------

def parse_price(text):
    """Convierte el precio en un numero decimal."""

    match = re.search(
        r"\d+(?:[.,]\d+)?",
        text
    )

    if match:
        return float(
            match.group().replace(",", ".")
        )

    return None


# --------------------------------------------------
# EXTRAER VALORACIONES
# --------------------------------------------------

def parse_rating(book):
    """Extrae la valoracion del libro."""

    rating_tag = book.select_one(
        "p.star-rating"
    )

    if not rating_tag:
        return "No disponible"

    classes = rating_tag.get("class", [])

    for class_name in classes:
        if class_name != "star-rating":
            return class_name

    return "No disponible"


# --------------------------------------------------
# EXTRAER LIBROS
# --------------------------------------------------

def extract_books(soup, category, page_url):
    """
    Extrae los libros de una pagina de categoria.
    No visita las fichas individuales.
    """

    records = []

    books = soup.select(
        "article.product_pod"
    )

    for book in books:

        title_tag = book.select_one("h3 a")
        price_tag = book.select_one(".price_color")
        availability_tag = book.select_one(".availability")
        image_tag = book.select_one("img")

        if not title_tag or not price_tag:
            continue

        # Titulo
        title = (
            title_tag.get("title")
            or title_tag.get_text(strip=True)
        )

        # URL de la ficha
        detail_url = urljoin(
            page_url,
            title_tag.get("href", "")
        )

        # Precio
        price = parse_price(
            price_tag.get_text(strip=True)
        )

        # Valoracion
        rating = parse_rating(book)

        # Disponibilidad
        availability = "No disponible"

        if availability_tag:
            availability = " ".join(
                availability_tag.stripped_strings
            )

        # Imagen
        image_url = ""

        if image_tag:
            image_url = urljoin(
                page_url,
                image_tag.get("src", "")
            )

        records.append({
            "titulo": title,
            "precio_gbp": price,
            "disponibilidad": availability,
            "valoracion": rating,
            "categoria": category,
            "url_libro": detail_url,
            "url_portada": image_url
        })

    return records


# --------------------------------------------------
# OBTENER CATEGORIAS
# --------------------------------------------------

def get_categories(session, robots):
    """Obtiene las categorias de la pagina principal."""

    soup = get_soup(
        session,
        BASE_URL,
        robots
    )

    category_links = soup.select(
        "div.side_categories ul li ul li a"
    )

    categories = []

    for link in category_links:

        name = link.get_text(strip=True)

        category_url = urljoin(
            BASE_URL,
            link.get("href", "")
        )

        if name and category_url:
            categories.append({
                "nombre": name,
                "url": category_url
            })

    if not categories:
        raise RuntimeError(
            "No se han encontrado categorias."
        )

    return categories


# --------------------------------------------------
# SCRAPING PRINCIPAL
# --------------------------------------------------

def scrape(target_books=100, delay=0.5):
    """
    Recorre las categorias hasta conseguir
    el numero solicitado de libros unicos.
    """

    if target_books < 1:
        raise ValueError(
            "El numero de libros debe ser mayor que cero."
        )

    if delay < 0.5:
        raise ValueError(
            "La pausa minima es de 0.5 segundos."
        )

    print("\nIniciando BookScope Scraper...")
    print("----------------------------------")

    session = create_session()

    try:

        # Comprobar robots.txt
        print("Comprobando robots.txt...")

        robots = check_robots(session)

        # Obtener todas las categorias
        print("Obteniendo categorias...")

        categories = get_categories(
            session,
            robots
        )

        records = []

        # Evitar duplicados mediante las URL
        seen_urls = set()

        pages_processed = 0

        # Recorrer todas las categorias
        for category in categories:

            if len(records) >= target_books:
                break

            category_name = category["nombre"]
            next_url = category["url"]

            print(
                f"\nCategoria: {category_name}"
            )

            # Recorrer las paginas de cada categoria
            while next_url and len(records) < target_books:

                soup = get_soup(
                    session,
                    next_url,
                    robots
                )

                books = extract_books(
                    soup,
                    category_name,
                    next_url
                )

                new_books = 0

                # Guardar solamente libros nuevos
                for book in books:

                    book_url = book["url_libro"]

                    if book_url in seen_urls:
                        continue

                    if book["precio_gbp"] is None:
                        continue

                    records.append(book)
                    seen_urls.add(book_url)

                    new_books += 1

                    if len(records) >= target_books:
                        break

                pages_processed += 1

                print(
                    f"Pagina {pages_processed} | "
                    f"Libros nuevos: {new_books} | "
                    f"Total: {len(records)}/{target_books}"
                )

                # Buscar la siguiente pagina
                next_link = soup.select_one(
                    "li.next a"
                )

                if next_link:
                    next_url = urljoin(
                        next_url,
                        next_link.get("href")
                    )
                else:
                    next_url = None

                # Esperar entre peticiones
                if next_url and len(records) < target_books:
                    time.sleep(delay)

            # Esperar antes de cambiar de categoria
            if len(records) < target_books:
                time.sleep(delay)

        # Comprobar resultados
        if not records:
            raise RuntimeError(
                "No se han encontrado libros."
            )

        # Crear DataFrame
        df = pd.DataFrame(records)

        # Convertir precios
        df["precio_gbp"] = pd.to_numeric(
            df["precio_gbp"],
            errors="coerce"
        )

        # Convertir valoraciones
        df["valoracion_num"] = (
            df["valoracion"]
            .map(RATING_MAP)
            .astype("Int64")
        )

        # Limpiar textos
        text_columns = [
            "titulo",
            "disponibilidad",
            "categoria"
        ]

        for column in text_columns:

            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
            )

        # Eliminar duplicados
        df = df.drop_duplicates(
            subset=["url_libro"]
        )

        # Eliminar registros invalidos
        df = df.dropna(
            subset=["titulo", "precio_gbp"]
        )

        if df.empty:
            raise RuntimeError(
                "No quedan registros validos."
            )

        # Crear carpeta data
        OUTPUT.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # Guardar CSV
        df.to_csv(
            OUTPUT,
            index=False,
            encoding="utf-8-sig"
        )

        # Resumen final
        print("\n==================================")
        print("SCRAPING FINALIZADO")
        print("==================================")

        print(
            f"Paginas consultadas: {pages_processed}"
        )

        print(
            f"Libros guardados: {len(df)}"
        )

        print(
            f"Categorias encontradas: "
            f"{df['categoria'].nunique()}"
        )

        print(
            f"Precio medio: "
            f"£{df['precio_gbp'].mean():.2f}"
        )

        rating_mean = df["valoracion_num"].mean()

        if pd.notna(rating_mean):
            print(
                f"Valoracion media: {rating_mean:.2f}/5"
            )

        if len(df) < target_books:
            print(
                f"AVISO: Se solicitaron {target_books} "
                f"libros y se encontraron {len(df)}."
            )

        print(
            f"\nArchivo CSV: {OUTPUT}"
        )

        print("==================================")

        return df

    finally:
        session.close()


# --------------------------------------------------
# EJECUCION
# --------------------------------------------------

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="BookScope - Web Scraper"
    )

    parser.add_argument(
        "--target-books",
        type=int,
        default=100,
        help="Numero de libros que se quieren extraer."
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Pausa entre peticiones en segundos."
    )

    args = parser.parse_args()

    scrape(
        target_books=args.target_books,
        delay=args.delay
    )

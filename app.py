
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# CONFIGURACION

st.set_page_config(
    page_title="BookScope",
    layout="wide"
)

DATA_FILE = Path(__file__).parent / "data" / "libros.csv"


# CARGAR DATOS

@st.cache_data
def load_data(path, modified):

    df = pd.read_csv(path)

    required_columns = [
        "titulo",
        "precio_gbp",
        "disponibilidad",
        "valoracion",
        "categoria",
        "url_libro"
    ]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(
                f"Falta la columna: {column}"
            )

    df["precio_gbp"] = pd.to_numeric(
        df["precio_gbp"],
        errors="coerce"
    )

    rating_map = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    if "valoracion_num" in df.columns:
        df["valoracion_num"] = pd.to_numeric(
            df["valoracion_num"],
            errors="coerce"
        )
    else:
        df["valoracion_num"] = df["valoracion"].map(
            rating_map
        )

    df = df.dropna(
        subset=["titulo", "precio_gbp"]
    )

    df["categoria"] = df["categoria"].fillna(
        "Sin categoría"
    )

    df["disponibilidad"] = df["disponibilidad"].fillna(
        "No disponible"
    )

    return df


# COMPROBAR ARCHIVO

if not DATA_FILE.exists():

    st.error(
        "No se encuentra el archivo data/libros.csv. "
        "Ejecuta primero scraper.py."
    )

    st.stop()


try:

    df = load_data(
        str(DATA_FILE),
        DATA_FILE.stat().st_mtime
    )

except Exception as error:

    st.error(f"Error al cargar los datos: {error}")
    st.stop()


if df.empty:

    st.warning("No hay registros disponibles.")
    st.stop()


# CABECERA

st.title("BookScope")

st.write(
    "Explorador y análisis de datos de libros "
    "extraídos de Books to Scrape."
)

st.divider()


# FILTROS

st.sidebar.title("Filtros")

categories = sorted(
    df["categoria"].unique().tolist()
)

selected_categories = st.sidebar.multiselect(
    "Categorías",
    options=categories,
    default=categories
)

min_price = float(df["precio_gbp"].min())
max_price = float(df["precio_gbp"].max())

if min_price < max_price:

    price_range = st.sidebar.slider(
        "Rango de precios (£)",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price)
    )

else:

    price_range = (min_price, max_price)


ratings = sorted(
    df["valoracion_num"].dropna().unique().tolist()
)

selected_ratings = st.sidebar.multiselect(
    "Valoración",
    options=ratings,
    default=ratings
)


# APLICAR FILTROS

filtered = df[
    df["categoria"].isin(selected_categories)
    & df["precio_gbp"].between(
        price_range[0],
        price_range[1]
    )
]

filtered = filtered[
    filtered["valoracion_num"].isin(selected_ratings)
]

st.sidebar.divider()

st.sidebar.write(
    f"Resultados: {len(filtered)} de {len(df)} libros"
)


if filtered.empty:

    st.info("No hay libros que coincidan con los filtros.")
    st.stop()


# INDICADORES

st.header("Resumen general")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total de libros",
    len(filtered)
)

col2.metric(
    "Precio medio",
    f"£{filtered['precio_gbp'].mean():.2f}"
)

col3.metric(
    "Precio máximo",
    f"£{filtered['precio_gbp'].max():.2f}"
)

rating_mean = filtered["valoracion_num"].mean()

col4.metric(
    "Valoración media",
    f"{rating_mean:.2f} / 5"
    if pd.notna(rating_mean)
    else "Sin datos"
)

st.divider()


# PRECIO MEDIO POR CATEGORIA

st.header("Análisis de precios")

st.subheader("Precio medio por categoría")

category_prices = (
    filtered.groupby("categoria", as_index=False)
    ["precio_gbp"]
    .mean()
    .sort_values("precio_gbp", ascending=False)
)

fig1 = px.bar(
    category_prices,
    x="categoria",
    y="precio_gbp",
    labels={
        "categoria": "Categoría",
        "precio_gbp": "Precio medio (£)"
    },
    color_discrete_sequence=["#416A91"]
)

fig1.update_layout(
    template="plotly_white",
    showlegend=False,
    xaxis_tickangle=-35
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


# RELACION PRECIO Y VALORACION

st.subheader("Relación entre precio y valoración")

relation = filtered.dropna(
    subset=["valoracion_num"]
)

fig2 = px.scatter(
    relation,
    x="precio_gbp",
    y="valoracion_num",
    color="categoria",
    hover_name="titulo",
    labels={
        "precio_gbp": "Precio (£)",
        "valoracion_num": "Valoración",
        "categoria": "Categoría"
    }
)

fig2.update_layout(
    template="plotly_white"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.divider()


# DISTRIBUCION DE PRECIOS

st.header("Distribución de datos")

st.subheader("Distribución de precios")

fig3 = px.histogram(
    filtered,
    x="precio_gbp",
    nbins=20,
    labels={
        "precio_gbp": "Precio (£)",
        "count": "Número de libros"
    },
    color_discrete_sequence=["#416A91"]
)

fig3.update_layout(
    template="plotly_white"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# DISTRIBUCION DE VALORACIONES

st.subheader("Distribución de valoraciones")

rating_counts = (
    filtered["valoracion_num"]
    .value_counts()
    .sort_index()
    .rename_axis("Valoración")
    .reset_index(name="Número de libros")
)

fig4 = px.bar(
    rating_counts,
    x="Valoración",
    y="Número de libros",
    text="Número de libros",
    color_discrete_sequence=["#6688A8"]
)

fig4.update_layout(
    template="plotly_white",
    showlegend=False
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

st.divider()


# TABLA DE LIBROS

st.header("Catálogo de libros")

columns = [
    "titulo",
    "categoria",
    "precio_gbp",
    "valoracion",
    "disponibilidad"
]

display_df = filtered[columns].rename(
    columns={
        "titulo": "Título",
        "categoria": "Categoría",
        "precio_gbp": "Precio (£)",
        "valoracion": "Valoración",
        "disponibilidad": "Disponibilidad"
    }
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# DESCARGAR CSV

st.download_button(
    "Descargar resultados CSV",
    data=filtered.to_csv(
        index=False
    ).encode("utf-8-sig"),
    file_name="bookscope_resultados.csv",
    mime="text/csv"
)

st.divider()


# CONCLUSIONES

st.header("Conclusiones")

average_price = filtered["precio_gbp"].mean()

most_expensive = category_prices.iloc[0]
cheapest = category_prices.iloc[-1]

col1, col2 = st.columns(2)

with col1:

    st.subheader("Análisis de precios")

    st.write(
        f"Se han encontrado {len(filtered)} libros."
    )

    st.write(
        f"El precio medio es de £{average_price:.2f}."
    )

    st.write(
        f"La categoría con mayor precio medio es "
        f"{most_expensive['categoria']}."
    )

    st.write(
        f"La categoría con menor precio medio es "
        f"{cheapest['categoria']}."
    )


with col2:

    st.subheader("Análisis de valoraciones")

    if pd.notna(rating_mean):

        st.write(
            f"La valoración media es de "
            f"{rating_mean:.2f} sobre 5."
        )

        correlation_data = filtered[
            ["precio_gbp", "valoracion_num"]
        ].dropna()

        if (
            len(correlation_data) >= 2
            and correlation_data["precio_gbp"].nunique() > 1
            and correlation_data["valoracion_num"].nunique() > 1
        ):

            correlation = correlation_data[
                "precio_gbp"
            ].corr(
                correlation_data["valoracion_num"]
            )

            st.write(
                f"Correlación entre precio y valoración: "
                f"{correlation:.2f}."
            )

            st.caption(
                "La correlación no implica causalidad."
            )

    else:

        st.write("No hay valoraciones disponibles.")


# PIE DE PAGINA

st.divider()

st.caption(
    "BookScope | Proyecto de Web Scraping con Python"
)

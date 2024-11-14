import requests
import pandas as pd
import matplotlib as plt
import streamlit as st
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import plotly.graph_objects as go

def main():

    engine = create_engine('mysql+pymysql://root:Estela080702.@localhost:3306/AEMET')

    menu = ['Inicio', 'Valores climatológicos por comunidad', 'Comparador de valores climatológicos',
            'Mapa coroplético']

    choice = st.sidebar.selectbox("Selecciona una opción", menu, key="menu_selectbox_unique")

    if choice == "Inicio":
        st.image(
            image="https://facuso.es/wp-content/uploads/2023/09/6de3b76f2eeed4e2edfa5420ad9630bd.jpg",
            caption="Imagen oficial de la AEMET",
            width=500,
            use_column_width=True
        )
        # Título de la aplicación
        st.markdown("# AEMET (Agencia Estatal Meteorológica)")

        # Introducción
        st.markdown(
            "### Bienvenido a la aplicación de la AEMET, donde podrás explorar y comparar datos históricos de España desde 2014 "
        )

    if choice == "Valores climatológicos por comunidad":
        st.header("Valores Climatológicos por Comunidad")

        ciudades_df = pd.read_sql("SELECT * FROM ciudades", engine)
        provincias_df = pd.read_sql("SELECT * FROM provincias", engine)
        valores_climatologicos_df = pd.read_sql("SELECT * FROM valores_climatologicos", engine)

        # Selección de ciudad
        ciudad_seleccionada = st.selectbox("Selecciona una ciudad", ciudades_df['ciudad'].tolist())
        ciudad_id = ciudades_df.loc[ciudades_df['ciudad'] == ciudad_seleccionada, 'ciudad_id'].values

        # Verificación y obtención de la provincia
        if ciudad_id.size > 0:
            ciudad_id = ciudad_id[0]
            provincia = provincias_df[provincias_df['provincia_id'] == ciudad_id]

            if not provincia.empty:
                st.write("Provincia:", provincia['provincia'].values[0])

                # Mensaje introductorio sobre los datos
                st.write(
                    "Este análisis incluye datos climatológicos que reflejan las condiciones meteorológicas promedio y extremas en el tiempo.")
                st.write(
                    "Los datos presentados aquí pueden ayudar a entender las tendencias climáticas y las variaciones en los patrones meteorológicos a lo largo del tiempo.")

                def run_query(query):
                    with engine.connect() as connection:
                        return pd.read_sql(query, connection)


                # Define consultas SQL predefinidas
                queries = {
                    "Promedio de Temperatura": "SELECT fecha, AVG(tmed) AS average_temperature FROM valores_climatologicos GROUP BY fecha ORDER BY fecha;",
                    "Total de Precipitación": "SELECT fecha, SUM(prec) AS total_precipitation FROM valores_climatologicos GROUP BY fecha ORDER BY fecha;",
                    "Temperatura Media General": "SELECT AVG(tmed) AS average_temperature FROM valores_climatologicos;",
                    "Temperaturas Máxima y Mínima": "SELECT fecha, MAX(tmax) AS max_temperature, MIN(tmin) AS min_temperature FROM valores_climatologicos GROUP BY fecha ORDER BY fecha;",
                    "Humedad Promedio": "SELECT fecha, AVG(hrMedia) AS average_humidity FROM valores_climatologicos GROUP BY fecha ORDER BY fecha;",
                    "Velocidad del Viento Promedio": "SELECT fecha, AVG(velmedia) AS average_wind_speed FROM valores_climatologicos GROUP BY fecha ORDER BY fecha;",
                    "Radiación Solar Total": "SELECT fecha, SUM(sol) AS total_solar_radiation FROM valores_climatologicos GROUP BY fecha ORDER BY fecha;",
                    "Presión Máxima y Mínima": "SELECT fecha, MAX(presMax) AS max_pressure, MIN(presMin) AS min_pressure FROM valores_climatologicos GROUP BY fecha ORDER BY fecha;",
                    "Registros de Temperatura": "SELECT fecha, tmed, tmax, tmin FROM valores_climatologicos ORDER BY fecha;",
                    "Temperatura Promedio Mensual": "SELECT DATE_FORMAT(fecha, '%Y-%m') AS month, AVG(tmed) AS average_temperature FROM valores_climatologicos GROUP BY month ORDER BY month;",
                    "Precipitación Total Mensual": "SELECT DATE_FORMAT(fecha, '%Y-%m') AS month, SUM(prec) AS total_precipitation FROM valores_climatologicos GROUP BY month ORDER BY month;",
                    "Rango de Temperatura": "SELECT fecha, (MAX(tmax) - MIN(tmin)) AS temperature_range FROM valores_climatologicos GROUP BY fecha ORDER BY fecha;",
                    "Velocidad del Viento Promedio Mensual": "SELECT DATE_FORMAT(fecha, '%Y-%m') AS month, AVG(velmedia) AS average_wind_speed FROM valores_climatologicos GROUP BY month ORDER BY month;",
                    "Estadísticas de Humedad Mensual": "SELECT DATE_FORMAT(fecha, '%Y-%m') AS month, AVG(hrMedia) AS average_humidity, MAX(hrMax) AS max_humidity, MIN(hrMin) AS min_humidity FROM valores_climatologicos GROUP BY month ORDER BY month;",
                    "Radiación Solar Mensual": "SELECT DATE_FORMAT(fecha, '%Y-%m') AS month, SUM(sol) AS total_solar_radiation FROM valores_climatologicos GROUP BY month ORDER BY month;",
                    "Registros de Presión": "SELECT fecha, presMax, presMin FROM vc_22 ORDER BY fecha;"
                }


                # Selección de consulta
                selected_query = st.selectbox("Selecciona una consulta para visualizar:", list(queries.keys()))
                data = run_query(queries[selected_query])

                # Mostrar los datos
                st.subheader(selected_query)
                st.dataframe(data)

                # Gráficos de los datos
                if 'fecha' in data.columns:
                    plt.figure(figsize=(10, 5))

                    if "average_temperature" in data.columns:
                        plt.plot(data['fecha'], data['average_temperature'], label='Temperatura Promedio', color='blue')

                    if "total_precipitation" in data.columns:
                        plt.bar(data['fecha'], data['total_precipitation'], label='Precipitación Total', color='orange',
                                alpha=0.5)

                    if "max_temperature" in data.columns and "min_temperature" in data.columns:
                        plt.fill_between(data['fecha'], data['min_temperature'], data['max_temperature'],
                                         color='lightgray', label='Rango de Temperatura')

                    if "average_humidity" in data.columns:
                        plt.plot(data['fecha'], data['average_humidity'], label='Humedad Promedio', color='green')

                    if "average_wind_speed" in data.columns:
                        plt.plot(data['fecha'], data['average_wind_speed'], label='Velocidad del Viento Promedio',
                                 color='red')

                    if "total_solar_radiation" in data.columns:
                        plt.plot(data['fecha'], data['total_solar_radiation'], label='Radiación Solar Total',
                                 color='yellow')

                    if "max_pressure" in data.columns and "min_pressure" in data.columns:
                        plt.fill_between(data['fecha'], data['min_pressure'], data['max_pressure'], color='lightblue',
                                         label='Rango de Presión')

                    plt.title(selected_query)
                    plt.xlabel('Fecha')
                    plt.ylabel('Valores')
                    plt.xticks(rotation=45)
                    plt.legend()
                    plt.tight_layout()
                    st.pyplot(plt)
                else:
                    st.write("No hay datos disponibles para la consulta seleccionada.")
            else:
                st.write("No se encontró la provincia para la ciudad seleccionada.")
        else:
            st.write("No se encontró el ID de la ciudad seleccionada.")
            st.write("Selecciona una opción del menú para comenzar.")

    elif choice == "Comparador de valores climatológicos":
        st.header("Comparativa de los valores climatologicos")
        st.write("Aqui podrás comparar una provincia y los datos de las fechas de los años:")

        def load_data(provincia_id, year1, year2):
            query = f"""
                    SELECT vc.Fecha, vc.Tmed, p.provincia
                    FROM valores_climatologicos vc
                    JOIN provincias p ON vc.Provincia_id = p.provincia_id
                    WHERE vc.Provincia_id = '{provincia_id}' AND (YEAR(vc.Fecha) = {year1} OR YEAR(vc.Fecha) = {year2})
                """
            return pd.read_sql(query, engine)

        # Título de la aplicación
        st.subheader("Comparación de la temperatura por Provincia")

        # Selección de provincia y años
        provincias_df = pd.read_sql("SELECT * FROM provincias", engine)
        provincia = st.selectbox("Selecciona una provincia", provincias_df["provincia"].tolist())

        provincia_id = provincias_df.loc[provincias_df['provincia'] == provincia, 'provincia_id'].values[0]

        year1 = st.selectbox("Selecciona el primer año", [2022, 2023, 2024])
        year2 = st.selectbox("Selecciona el segundo año", [2022, 2023, 2024])

        # Cargar datos
        data = load_data(provincia_id, year1, year2)
        st.write(data)

        # Calcular estadísticas
        data['Year'] = pd.to_datetime(data['Fecha']).dt.year
        stats = data.groupby(['Year', 'Fecha'])['Tmed'].agg(['mean', 'median', 'min', 'max']).reset_index()

        st.write(stats)  # Esto te permitirá ver las estadísticas calculadas

        # Graficar
        fig, ax = plt.subplots(figsize=(16,8))
        for year in stats['Year'].unique():
            year_data = stats[stats['Year'] == year]
            ax.plot(year_data['Fecha'], year_data['mean'], label=f'Media {year}', marker='o')
            ax.plot(year_data['Fecha'], year_data['median'], label=f'Mediana {year}', marker='o')
            ax.plot(year_data['Fecha'], year_data['min'], label=f'Mínimo {year}', linestyle='--', marker='o')
            ax.plot(year_data['Fecha'], year_data['max'], label=f'Máximo {year}', linestyle='--', marker='o')

        # Personalizar gráfico
        ax.set_title(f'Comparación de Climatología en {provincia} entre {year1} y {year2}', fontsize=16)
        ax.set_xlabel('Fecha', fontsize=14)
        ax.set_ylabel('Temperatura Media (°C)', fontsize=14)
        ax.legend(fontsize=12)
        ax.grid(True)
        plt.xticks(rotation=45)
        st.pyplot(fig)

if __name__ == "__main__":
    main()

    # Text
    # st.text("New Line.")
    # name = "Daniel"
    # st.text(f"Hola soy {name}")
    # print("hola soy daniel")


    # st.dataframe(dir(st))

    # # Help
    # st.help(range)

    # Display Data
    #df = pd.read_csv(filepath_or_buffer="sources/AccidentesBicicletas_2021.csv", sep=";")

    # Dinamic Data
    #st.dataframe(df)
    # st.write(df)

    # Static Table
    # st.table(df)

    # Adding Color
    #st.dataframe(df.select_dtypes(include=np.number).style.highlight_max(axis=0))

    pass




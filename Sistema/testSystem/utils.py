import pandas as pd
import joblib
import os

# Carga del modelo y vectorizador
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
modelo_path = os.path.join(BASE_DIR, 'ml/modelo_rf.pkl')
vector_path = os.path.join(BASE_DIR, 'ml/tfidf_vectorizer.pkl')

modelo = joblib.load(modelo_path)
vectorizador = joblib.load(vector_path)


def analizar_csv(archivo_csv):
    try:
        df = pd.read_csv(archivo_csv)
    except pd.errors.EmptyDataError:
        raise ValueError("El archivo está vacío o no tiene columnas.")
    except Exception as e:
        raise ValueError(f"Error al leer el archivo CSV: {e}")

    if 'code' not in df.columns:
        raise ValueError("El CSV debe contener una columna 'code'.")

    X = vectorizador.transform(df['code'])
    predicciones = modelo.predict(X)
    probabilidades = modelo.predict_proba(X)

    resultados = []
    for i, row in df.iterrows():
        resultados.append({
            'nombre_test': row.get('Test Name', f"Test-{i}"),
            'clasificacion_ml': predicciones[i],
            'score_probabilidad_flaky': max(probabilidades[i]),
            'estado': True
        })

    return resultados

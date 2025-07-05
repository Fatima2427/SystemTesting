import pandas as pd
import joblib
import os

# Carga del modelo y vectorizador
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
modelo_path = os.path.join(BASE_DIR, 'ml/modelo_rf.pkl')
vector_path = os.path.join(BASE_DIR, 'ml/tfidf_vectorizer.pkl')

modelo = joblib.load(modelo_path)
vectorizador = joblib.load(vector_path)
CLASES = modelo.classes_


def analizar_csv(archivo_csv, umbral_estabilidad=60):
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
        proba_fila = probabilidades[i]
        probabilidad_maxima = max(proba_fila)
        categoria_predicha = CLASES[proba_fila.argmax()]

        # Decisión basada en umbral: ¿es estable o no?
        if probabilidad_maxima < umbral_estabilidad / 100:
            categoria_final = "Estable"
        else:
            categoria_final = categoria_predicha

        resultado = {
            'nombre_test': row.get('Test Name', f"Test-{i}"),
            'clasificacion_ml': categoria_final,
            # porcentaje
            'score_probabilidad_flaky': round(probabilidad_maxima * 100, 2),
            'detalle_probabilidades': {
                clase: round(prob * 100, 2) for clase, prob in zip(CLASES, proba_fila)
            },
            'estado': True
        }

        resultados.append(resultado)

    return resultados

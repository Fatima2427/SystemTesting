import joblib

# Ruta al archivo de tu modelo
ruta_modelo = 'ML/modelo_rf.pkl'

# Cargar sin ejecutar completamente
model = joblib.load(ruta_modelo)

# Verifica si tiene información de versión
if hasattr(model, '__module__'):
    print("Módulo principal:", model.__module__)

print("Tipo:", type(model))

# Algunos modelos tienen metainformación del entorno de entrenamiento
if hasattr(model, '__dict__'):
    for key in model.__dict__:
        print(f"{key}: {type(model.__dict__[key])}")

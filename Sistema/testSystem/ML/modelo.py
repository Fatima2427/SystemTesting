import pandas as pd
import os
from git import Repo
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import joblib
df = pd.read_csv("py-data.csv")
df_sample = df.head(800)


def clone_and_get_test_code(project_url, sha, test_path):
    repo_name = project_url.split('/')[-1]
    if not os.path.exists(repo_name):
        try:
            Repo.clone_from(project_url, repo_name)
        except Exception as e:
            print(f"Error clonando {project_url}: {e}")
            return None
    try:
        repo = Repo(repo_name)
        repo.git.checkout(sha)
    except Exception as e:
        print(f"Error haciendo checkout {sha} en {repo_name}: {e}")
        return None

    path = test_path.split("::")[0]
    test_file_path = os.path.join(repo_name, path)
    if os.path.exists(test_file_path):
        try:
            with open(test_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except:
            return None
    return None


# Paso 6: Extraer el código y almacenarlo
df_sample['code'] = df_sample.apply(
    lambda row: clone_and_get_test_code(
        row['Project URL'],
        row['SHA Detected'],
        row['Pytest Test Name (PathToFile::TestClass::TestMethod or PathToFile::TestMethod)']
    ), axis=1
)

df_sample = df_sample.dropna(subset=['code'])

vectorizer = TfidfVectorizer(max_features=1000)
X_tfidf = vectorizer.fit_transform(df_sample['code'])
print("TF-IDF shape:", X_tfidf.shape)
# Limpiar filas sin categoría y resetear índice
df_sample = df_sample.dropna(subset=['Category']).reset_index(drop=True)
df_sample['Category'] = df_sample['Category'].astype(str)
X = X_tfidf[df_sample.index]  # filtramos también X
y = df_sample['Category']
# Dividir en datos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)
# Paso: Entrenamiento del modelo
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
print("📊 Reporte de Clasificación:")
print(classification_report(y_test, y_pred))
# Guardar
joblib.dump(clf, "modelo_rf.pkl")
joblib.dump(vectorizer, "tfidf_vectorizer.pkl")

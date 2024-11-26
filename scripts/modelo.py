from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, f1_score
from sklearn.model_selection import train_test_split
import pandas as pd

# Función para predecir la próxima ubicación del barco y calcular métricas
def rand_class(df, ship_name=None):
  if ship_name==None:
    return 0, 0, 0, "No se seleccionó ningun barco"
  # Filtrar los datos del barco especificado
  df_ship = df[df['Ship Name'] == ship_name].copy()

  # Convertir columnas de fechas y agregar variables temporales
  df_ship['Arrival_ordinal'] = df_ship['Arrival'].map(pd.Timestamp.toordinal)
  df_ship['Departure_ordinal'] = df_ship['Departure'].map(pd.Timestamp.toordinal)
  df_ship['Arrival_Month'] = df_ship['Arrival'].dt.month
  df_ship['Arrival_Year'] = df_ship['Arrival'].dt.year
  df_ship['Arrival_DayOfWeek'] = df_ship['Arrival'].dt.dayofweek

  # Verificar que la variable objetivo 'Location' esté en el DataFrame
  if 'Location' not in df_ship.columns:
      print("La columna 'Location' no está disponible en el DataFrame.")
      return None

  # Variables categóricas para One-Hot Encoding
  categorical_features = ['Vessel Type', 'Country', 'Region Name']
  categorical_transformer = OneHotEncoder(handle_unknown='ignore')

  # Column Transformer para preprocesar características
  preprocessor = ColumnTransformer(
      transformers=[('cat', categorical_transformer, categorical_features)],
      remainder='passthrough'
  )

  # Convertir la variable objetivo 'Location' a categorías numéricas
  label_encoder = LabelEncoder()
  df_ship['Location'] = label_encoder.fit_transform(df_ship['Location'])

  # Definir características (X) y variable objetivo (y) - 'Location'
  X = df_ship[['Vessel Type', 'Country', 'Region Name', 'Arrival_ordinal',
    'Departure_ordinal', 'Arrival_Month', 'Arrival_Year', 'Arrival_DayOfWeek']]
  y = df_ship['Location']

  # Dividir los datos en conjuntos de entrenamiento y prueba
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

  # Crear pipeline con preprocesamiento y clasificador Random Forest
  model = Pipeline(steps=[
      ('preprocessor', preprocessor),
      ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
  ])

  # Entrenar el modelo
  model.fit(X_train, y_train)

  # Evaluación del modelo
  y_pred = model.predict(X_test)
  # Asegurarse de que y_test y y_pred sean del mismo tipo (int)
  y_test = y_test.astype(int)
  y_pred = y_pred.astype(int)

  location_accuracy = accuracy_score(y_test, y_pred)
  location_precision = precision_score(y_test, y_pred, average='weighted')
  location_f1 = f1_score(y_test, y_pred, average='weighted')

  # Decodificar la predicción para la próxima ubicación
  predicted_location = label_encoder.inverse_transform([y_pred[-1]])[0]

  print(predicted_location, location_accuracy, location_precision, location_f1)

  return predicted_location, location_accuracy, location_precision, location_f1


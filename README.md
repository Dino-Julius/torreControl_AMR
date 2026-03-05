# TI3005B.102.M2 Actividades "TorreControl_AMR"

## Data

- A01749879 - Julio Vivas
- TI3005B.102.M2: Implementación de la Transformación Digital

## Descripcion

Proyecto Azure Functions para exponer endpoints HTTP de:

- calculo de ruta
- prediccion de ETA

## Instrucciones

```bash
source .venv/bin/activate
func host start --verbose
```

## Pruebas Con Postman

1. Importa el archivo `api/TI3005B.102.M2.postman_collection.json` en Postman.
2. Levanta el host local con `func host start --verbose`.
3. Ejecuta `LocalTest Calculate Route` y `LocalTest Predict ETA`.
4. La coleccion usa `http://localhost:7071` por defecto.
5. Para probar en Azure, crea requests POST en Postman con tus endpoints de Azure y usa los mismos parametros de `body` que en las pruebas locales.

## Deploy Automatico

- La rama `deploy` realiza deploy automatico a Azure Functions.
- El trigger esta automatizado con GitHub Actions (integracion Azure + GitHub).
- Flujo recomendado:
  1.  Trabajar cambios en `master`.
  2.  Crear Pull Request de `master` hacia `deploy`.
  3.  Hacer merge a `deploy` para disparar el workflow y ejecutar el deploy.

## Comentarios

- Usa `--verbose` para ver logs detallados del arranque, carga de funciones y errores.
- Si falla por dependencias, ejecuta: `python -m pip install -r requirements.txt`.

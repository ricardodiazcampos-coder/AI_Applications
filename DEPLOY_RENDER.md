# Despliegue en Render (recomendado para Flask)

Flask **no puede ejecutarse en Netlify Functions** porque Netlify solo soporta funciones en **JavaScript, TypeScript y Go** ([documentación oficial](https://docs.netlify.com/build/functions/overview/)). Por eso ves:

- **200** en `/` → solo archivos estáticos (si existen)
- **404** en `/.netlify/functions/api/` → la función Python nunca se despliega

Para esta app Flask + SQLite, usa **Render** (plan free).

## Pasos

1. Cuenta en [render.com](https://render.com) (puedes usar GitHub).
2. **New → Blueprint** o **New → Web Service**.
3. Conecta el repo `ricardodiazcampos-coder/AI_Applications`.
4. Render detectará `render.yaml` automáticamente (Blueprint), o configura manualmente:
   - **Runtime:** Python 3
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
5. Agrega variable de entorno:
   - `FLASK_SECRET_KEY` = clave aleatoria larga
6. **Create Web Service** y espera el deploy.

## Local

```powershell
python -m pip install -r requirements-local.txt
python app.py
```

(`requirements-local.txt` incluye matplotlib para la versión de escritorio.)

## URL pública

Render asignará una URL como `https://gestion-financiera.onrender.com`.

## Netlify

Puedes dejar el sitio Netlify o eliminarlo. No es compatible con Flask sin reescribir todo el backend en JavaScript.

# Despliegue en Netlify

> **Importante:** Netlify **no soporta funciones Python**. Esta app Flask **no funcionará** en Netlify Functions (ver [Functions overview](https://docs.netlify.com/build/functions/overview/)). Usa **[DEPLOY_RENDER.md](DEPLOY_RENDER.md)** para publicar la aplicación.

Guía histórica / referencia para archivos estáticos en Netlify:

## Requisitos previos

1. Cuenta en [Netlify](https://app.netlify.com/signup).
2. Repositorio Git (GitHub, GitLab o Bitbucket) con el código del proyecto.
3. Archivos de configuración incluidos en este repositorio:
   - `netlify.toml`
   - `netlify/functions/api.py`
   - `netlify/functions/requirements.txt`
   - `netlify/functions/.python-version`

## Cómo funciona

| Componente | Rol |
|------------|-----|
| `static/` | CSS y JS servidos por la CDN de Netlify |
| `netlify/functions/api.py` | Función serverless que ejecuta Flask con `serverless-wsgi` |
| `netlify.toml` | Build atómico, redirects y archivos incluidos en la función |
| SQLite en `/tmp` | Base de datos temporal en el entorno serverless |

## Pasos para publicar

### 1. Subir el código a Git

```powershell
git init
git add .
git commit -m "Preparar despliegue Netlify"
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

### 2. Conectar el repositorio en Netlify

1. Entrar a [app.netlify.com](https://app.netlify.com).
2. **Add new site → Import an existing project**.
3. Elegir el proveedor Git y el repositorio.
4. Netlify detectará `netlify.toml`; no hace falta cambiar el comando de build.
5. Clic en **Deploy site**.

### 3. Variables de entorno (obligatorio)

En **Site configuration → Environment variables**, agregar:

| Variable | Valor | Alcance |
|----------|-------|---------|
| `FLASK_SECRET_KEY` | Una cadena larga y aleatoria (ej. salida de `python -c "import secrets; print(secrets.token_hex(32))"`) | **Functions** |
| `PYTHON_VERSION` | `3.11` | **Functions** (nunca en Builds) |
| `NETLIFY` | `true` | **Functions** (opcional) |

**Importante:** si `PYTHON_VERSION` está en scope **All** o **Builds**, Netlify intenta instalar Python en el build y el deploy falla. Usa solo scope **Functions**.

Sin `FLASK_SECRET_KEY` estable, las sesiones se invalidan en cada despliegue o reinicio de función.

### 4. Verificar el sitio

Tras el deploy, abrir la URL asignada (ej. `https://tu-sitio.netlify.app`):

1. Registrar un usuario nuevo.
2. Ingresar salario y un gasto.
3. Confirmar que el resumen y los gráficos cargan.

## Ejecución local (sin Netlify)

```powershell
python -m pip install -r requirements-local.txt
python app.py
```

Abrir http://127.0.0.1:5000

## Limitaciones importantes

1. **SQLite en `/tmp`**: Los datos se guardan en almacenamiento efímero de la función. Pueden perderse al redeploy, al escalar o tras inactividad prolongada. Para producción real conviene [Netlify DB](https://docs.netlify.com/build/data-and-storage/netlify-db/) u otro servicio persistente.
2. **Cold starts**: La primera petición tras inactividad puede tardar unos segundos.
3. **Alternativa más simple**: Si el curso no exige Netlify, [Render](https://render.com) permite Flask + SQLite persistente con menos adaptación.

## Estructura de despliegue

```
proyecto/
├── app.py                 # Factory create_app()
├── netlify.toml           # Configuración Netlify
├── netlify/functions/
│   ├── api.py             # Handler serverless
│   └── requirements.txt   # Dependencias de la función
├── static/                # Publicado en CDN (+ _redirects)
├── templates/             # Incluido en la función
└── netlify/functions/.python-version
```

## Solución de problemas

| Problema | Posible causa |
|----------|----------------|
| 502 / Function error | Revisar **Functions → Logs** en el panel de Netlify |
| CSS no carga | Confirmar que `static/` está en el repo y `publish = "static"` en `netlify.toml` |
| Sesión se cierra sola | Definir `FLASK_SECRET_KEY` en variables de entorno |
| Usuarios desaparecen | Comportamiento esperado con SQLite en `/tmp`; usar BD externa para persistencia |
| 404 cacheado tras arreglar deploy | **Deploys → Clear cache and deploy site** |
| Build falla en pip/matplotlib | No uses `requirements.txt` en la raíz; localmente usa `requirements-local.txt` |

## Referencias

- [Deploy overview](https://docs.netlify.com/deploy/deploy-overview/)
- [Netlify Functions](https://docs.netlify.com/build/functions/overview/)
- [File-based configuration](https://docs.netlify.com/build/configure-builds/file-based-configuration/)

# Laboratorio 3 — Persistencia y usuarios

**Estudiante:** Ricardo Díaz  
**Curso:** Cenfotec Curso 2  
**Fecha:** 5 de agosto de 2026  
**Tema:** Planeamiento e implementación de persistencia y autenticación para una aplicación web de gestión financiera personal  
**Herramienta:** Cursor (asistente de código con IA)

---

## Ejercicio 1 — Expresa una intención precisa y completa

### Contexto

Voy a estar trabajando en el planeamiento de unos cambios que necesito realizar para una aplicación que estoy desarrollando con Cursor. La aplicación es una herramienta de gestión financiera personal. Su propósito es ayudar al usuario a planear los gastos del mes, evitar gastar más de lo presupuestado y, preferiblemente, poder ahorrar.

Cursor ya interpretó un master prompt y creó una aplicación base. Actualmente, la aplicación es web, corre en Python y se accede localmente desde la siguiente dirección:

```text
http://127.0.0.1:5000/
```

En este momento, la aplicación funciona correctamente a nivel general. Sin embargo, todavía no tiene una forma de guardar información de manera persistente. Esto significa que los cambios realizados por el usuario no quedan almacenados después de cerrar la aplicación o finalizar la sesión.

La intención principal de este laboratorio es planear el desarrollo de un sistema que permita guardar los cambios por usuario. Posiblemente, también se introducirán cuentas de usuario y autenticación mediante nombre de usuario y contraseña.

### Entradas

El programa debe recibir los siguientes datos:

- Nombre de usuario.
- Contraseña.
- Salario del usuario.
- Ingresos diarios, semanales o mensuales.
- Ingresos adicionales opcionales.
- Gastos fijos.
- Gastos imprevistos.
- Ahorro mensual planificado.
- Movimientos financieros registrados por el usuario.

La parte de gestión financiera ya se encuentra funcionando en la aplicación generada por Cursor. El objetivo de esta nueva etapa es agregar persistencia de datos y manejo de usuarios.

### Proceso

El programa debe realizar los siguientes pasos, en orden lógico:

1. Crear un sistema de perfiles de usuario.
2. Permitir que un usuario nuevo se registre con nombre de usuario y contraseña.
3. Validar que el nombre de usuario no exista previamente.
4. Validar que la contraseña cumpla con las reglas definidas.
5. Guardar la información del usuario registrado.
6. Permitir que el usuario inicie sesión con sus credenciales.
7. Asociar los datos financieros al usuario autenticado.
8. Guardar salario, ingresos adicionales, gastos fijos, gastos imprevistos y ahorro mensual planificado.
9. Calcular el salario restante después de restar los gastos fijos e imprevistos.
10. Calcular el ahorro total o disponible con base en el salario restante.
11. Recuperar la información guardada cuando el usuario vuelva a acceder a la aplicación.
12. Mostrar al usuario los datos que había guardado previamente.

### Salidas

Cuando el usuario vuelva a acceder a la aplicación, todos los cambios realizados anteriormente deben ser visibles.

La aplicación debe mostrar:

- Confirmación de registro exitoso.
- Mensaje de error si el nombre de usuario ya existe.
- Mensaje de error si la contraseña no cumple con las reglas.
- Confirmación de inicio de sesión exitoso.
- Salario guardado del usuario.
- Ingresos adicionales guardados.
- Gastos fijos registrados.
- Gastos imprevistos registrados.
- Ahorro mensual planificado.
- Salario restante calculado.
- Ahorro total disponible.
- Resumen financiero del usuario.

### Restricciones

El código debe cumplir con las siguientes reglas técnicas y funcionales:

- Los nombres de usuario no se pueden repetir.
- Si un nuevo perfil intenta crearse con un nombre de usuario existente, la aplicación debe informar que ese usuario ya existe.
- Las contraseñas deben tener mínimo 5 caracteres.
- Las contraseñas deben incluir al menos un carácter especial.
- Las contraseñas no expiran.
- La información financiera debe guardarse de forma persistente, no solamente en memoria temporal.
- La información financiera debe estar asociada al usuario autenticado.
- Cada usuario solamente debe poder ver su propia información financiera.
- El sistema debe separar la lógica de autenticación de la lógica financiera.
- El código debe organizarse mediante funciones.

### Criterios de éxito

El programa se considerará exitoso si cumple con los siguientes criterios:

- Permite crear un nuevo usuario válido.
- Impide crear usuarios duplicados.
- Rechaza contraseñas que no cumplan con las reglas establecidas.
- Permite iniciar sesión con credenciales correctas.
- Guarda correctamente los datos financieros del usuario.
- Al cerrar y volver a abrir el programa, la información previamente guardada sigue disponible.
- Al modificar salario, ingresos o gastos, los cambios se guardan correctamente.
- El cálculo de salario restante se actualiza correctamente.
- El cálculo de ahorro total se actualiza correctamente.
- Cada usuario solamente puede ver la información relacionada con su propia cuenta.

---

## Ejercicio 2 — Descompón el problema

Sin generar código todavía, la aplicación se puede descomponer en subproblemas más pequeños. Esta descomposición permite organizar mejor el desarrollo antes de implementar la solución.

### 1. Creación de cuentas

#### `registrar_usuario(usuario, contrasena)`

**Entrada:** nombre de usuario, contraseña.

**Proceso:** verificar usuario único, validar contraseña, agregar a almacenamiento persistente.

**Salida:** usuario registrado, o mensaje de error.

---

### 2. Validación de usuario único

#### `validar_usuario_unico(usuario, user_accounts)`

**Salida:** `True` si disponible; `False` si ya existe.

---

### 3. Validación de contraseña

#### `validar_contrasena(contrasena)`

**Proceso:** mínimo 5 caracteres y al menos un carácter especial.

**Salida:** `True` / `False` (en la implementación: tupla con mensaje de error).

---

### 4. Inicio de sesión

#### `iniciar_sesion(usuario, contrasena)`

**Salida:** acceso permitido o mensaje de error.

---

### 5–9. Guardar datos financieros

Funciones planificadas: `guardar_salario`, `guardar_ingresos_adicionales`, `guardar_ahorro_planificado`, `guardar_gastos_fijos`, `guardar_gastos_imprevistos`.

**Implementación real:** se unificaron en `guardar_datos_usuario(user_id, profile)` que persiste el perfil completo en SQLite.

---

### 10. Calcular salario restante

#### `calcular_salario_restante(...)`

**Fórmula:**

```text
salario_restante = ingresos_totales - gastos_fijos - gastos_imprevistos
```

**Implementación:** propiedad `available_balance` en `FinancialProfile` (`models.py`).

---

### 11. Calcular ahorro total

**Implementación:** propiedad `effective_savings` en `FinancialProfile`.

---

### 12. Cargar datos del usuario

#### `cargar_datos_usuario(usuario)`

**Implementación:** `cargar_datos_usuario(user_id)` en `persistence.py`.

---

### 13. Mostrar resumen financiero

**Implementación:** pestaña Resumen + `web_logic.build_view_context()`.

---

### Flujo general de la aplicación

```text
Usuario abre la aplicación
        ↓
Crea cuenta o inicia sesión
        ↓
Sistema valida usuario y contraseña
        ↓
Usuario ingresa o modifica información financiera
        ↓
Sistema guarda los datos de forma persistente (finanzas.db)
        ↓
Sistema calcula salario restante y ahorro total
        ↓
Sistema muestra resumen financiero
        ↓
Usuario cierra la aplicación / cierra sesión
        ↓
Usuario vuelve a abrir la aplicación e inicia sesión
        ↓
Sistema carga la información guardada del usuario
```

---

## Ejercicio 3 — Genera código con restricciones y criterios

### Prompt utilizado en la sesión (Cursor)

> Implementar un sistema de cuentas de usuario y autenticación mediante nombre de usuario y contraseña, además de persistencia de cambios cuando el usuario cierre el programa o cambie de usuario. Separar autenticación de lógica financiera. Contraseña: mínimo 5 caracteres y un carácter especial. Usuarios únicos. Persistencia no volátil asociada a cada usuario.

### Archivos creados o modificados

| Archivo | Rol |
|---------|-----|
| `auth_validators.py` | `validar_contrasena`, `validar_nombre_usuario` |
| `auth_service.py` | `registrar_usuario`, `iniciar_sesion` (auth separada) |
| `persistence.py` | SQLite `finanzas.db`, `cargar_datos_usuario`, `guardar_datos_usuario` |
| `app.py` | Rutas login/register/logout; `@login_required`; carga/guardado por `current_user.id` |
| `templates/login.html` | Formulario inicio de sesión |
| `templates/register.html` | Formulario registro |
| `templates/base.html` | Navbar con usuario y cerrar sesión |
| `requirements.txt` | Agregado `flask-login` |
| `consultar_usuario.py` | Script auxiliar para ver datos en la BD (evidencia) |

**Sin cambios en la lógica de cálculo:** `models.py`, `validators.py`, `web_logic.py`.

### Mapeo Ejercicio 2 → código implementado

| Función planificada | Implementación |
|-------------------|----------------|
| `validar_usuario_unico` | `persistence.validar_usuario_unico()` |
| `validar_contrasena` | `auth_validators.validar_contrasena()` |
| `registrar_usuario` | `auth_service.registrar_usuario()` |
| `iniciar_sesion` | `auth_service.iniciar_sesion()` |
| `cargar_datos_usuario` | `persistence.cargar_datos_usuario(user_id)` |
| `guardar_*` (salario, gastos, etc.) | `persistence.guardar_datos_usuario(user_id, profile)` |
| `calcular_salario_restante` | `FinancialProfile.available_balance` |
| `calcular_ahorro_total` | `FinancialProfile.effective_savings` |
| `mostrar_resumen_financiero` | Pestaña Resumen + tarjetas y gráficos |

### Fragmentos clave del código generado

**Registro con validaciones** (`auth_service.py`):

```python
def registrar_usuario(usuario: str, contrasena: str) -> Tuple[bool, Optional[str]]:
    username, err = validar_nombre_usuario(usuario)
    if err:
        return False, err
    ok, pwd_err = validar_contrasena(contrasena)
    if not ok:
        return False, pwd_err
    if not validar_usuario_unico(username):
        return False, "Ese nombre de usuario ya existe."
    password_hash = generate_password_hash(contrasena)
    crear_usuario(username, password_hash)
    return True, None
```

**Persistencia por usuario** (`persistence.py`):

```python
DB_PATH = Path(__file__).parent / "finanzas.db"

def guardar_datos_usuario(user_id: int, profile: FinancialProfile) -> None:
    payload = json.dumps(profile_to_dict(profile))
    # INSERT ... ON CONFLICT UPDATE en tabla user_profiles
```

**Rutas protegidas** (`app.py`):

```python
def _load_profile() -> FinancialProfile:
    return cargar_datos_usuario(current_user.id)

@app.post("/income")
@login_required
def save_income():
    profile = _load_profile()
    # ... validar y actualizar ...
    _save_profile(profile)
```

### Dónde se guarda la información

| Elemento | Ubicación |
|----------|-----------|
| Archivo | `Cenfotec Curso 2/finanzas.db` |
| Tabla `users` | id, username, password_hash (hash, no texto plano), created_at |
| Tabla `user_profiles` | user_id, profile_json (salario, gastos, metas en JSON), updated_at |

### Evidencia de funcionamiento

#### Prueba 1 — Usuario real `RicardoDiazCampos`

Consulta con `python consultar_usuario.py`:

| Campo | Valor guardado |
|-------|----------------|
| ID usuario | 2 |
| Salario mensual | ₡350,000.00 |
| Ingresos adicionales | ₡0.00 |
| Gastos fijos | ninguno |
| Gastos imprevistos | ninguno |
| Última actualización | 2026-08-06 02:54:42 |

**Salario restante (balance):** ₡350,000.00  
**Ahorro efectivo:** ₡350,000.00 (sin gastos ni ahorro planificado definido)

#### Prueba 2 — Reglas de contraseña

| Contraseña | Resultado esperado |
|------------|-------------------|
| `abc` | Rechazada (< 5 caracteres) |
| `abcde` | Rechazada (sin carácter especial) |
| `Test1!` | Aceptada |

#### Prueba 3 — Usuario duplicado

Registrar dos veces el mismo nombre → mensaje: *«Ese nombre de usuario ya existe.»*

#### Prueba 4 — Persistencia tras cerrar sesión

1. Login → guardar salario → logout  
2. Login de nuevo → el salario sigue visible en el formulario y en Resumen  

#### Prueba 5 — Aislamiento entre usuarios

Usuario A guarda datos; usuario B inicia sesión → perfil vacío o con sus propios datos únicamente.

### Cómo ejecutar

```powershell
cd "c:\Users\RicardoDiaz\Documents\Cenfotec Curso 2"
python -m pip install -r requirements.txt
python app.py
```

Abrir: **http://127.0.0.1:5000** → Registrarse o iniciar sesión.

---

## Ejercicio 4 — Compara y selecciona una solución

Se evaluaron **dos enfoques estructurales** para resolver el mismo problema (usuarios + persistencia + finanzas).

### Solución A — Funciones por módulo (implementada)

```text
auth_validators.py  → validar_contrasena, validar_nombre_usuario
auth_service.py     → registrar_usuario, iniciar_sesion
persistence.py      → cargar_datos_usuario, guardar_datos_usuario
models.py           → FinancialProfile (cálculos)
app.py              → rutas Flask
```

**Ventajas:**

- Fácil de leer **archivo por archivo** (adecuado para laboratorio y primera implementación).
- Coincide con la descomposición del Ejercicio 2 (una función por responsabilidad).
- Cambios acotados: la app financiera existente siguió funcionando.
- Separación clara: auth vs finanzas vs persistencia.

**Desventajas:**

- Muchas funciones sueltas si el proyecto crece mucho.
- `app.py` concentra varias rutas HTTP.

---

### Solución B — Clases agregadas (alternativa no implementada)

```text
ReglasAutenticacion     → validaciones
RepositorioFinanzas     → SQLite
GestorCuentas           → registro/login
PerfilUsuario           → objeto con métodos actualizar_ingresos(), agregar_gasto(), _persistir()
AplicacionFinanzas      → fachada única para Flask
```

**Ventajas:**

- Estado y comportamiento encapsulados (similar a una clase `Pedido` con ítems).
- Escalable en proyectos grandes.
- Rutas Flask más delgadas (`perfil.actualizar_ingresos(...)`).

**Desventajas:**

- Más abstracción para un primer laboratorio.
- Más clases que explicar al docente.
- Reescritura mayor sobre código ya funcional.

---

### Comparación directa

| Criterio | Solución A (funciones) | Solución B (clases) |
|----------|------------------------|---------------------|
| Misma funcionalidad lab | Sí | Sí |
| Alineada con Ejercicio 2 | Alta | Media (nombres distintos) |
| Facilidad de lectura inicial | Alta | Media |
| Esfuerzo de migración | Bajo (ya hecho) | Alto |
| Escalabilidad futura | Suficiente para MVP | Mayor |

---

### Selección final

**Se selecciona la Solución A (funciones por módulo)** por:

1. **Simplicidad** y claridad pedagógica.  
2. Cumple **todas las restricciones** del laboratorio (funciones, auth separada, persistencia, usuarios únicos).  
3. Ya está **probada** con el usuario `RicardoDiazCampos` y SQLite.  
4. La Solución B queda documentada como **alternativa válida** para una fase posterior (nube, más usuarios).

---

## Autoevaluación según rúbrica

| Criterio | Descripción | Evidencia |
|----------|-------------|-----------|
| **1. Comprensión del enunciado** | Intención clara, completa y coherente | Ejercicio 1: entradas, proceso, salidas, restricciones y criterios de éxito alineados con gestión financiera + usuarios |
| **2. Aplicación del proceso requerido** | Intención, descomposición, restricciones, comparación | Ejercicios 1 → 2 → 3 → 4 en orden; restricciones aplicadas en código (auth_validators, hash, SQLite) |
| **3. Funcionalidad** | Cálculos correctos y restricciones cumplidas | *Nota: la rúbrica menciona subtotal/descuento/IVA como ejemplo genérico; este proyecto calcula **ingresos, gastos, salario restante (balance), ahorro efectivo y progreso de metas**.* Evidencia: usuario `RicardoDiazCampos`, pruebas de validación y persistencia en Ejercicio 3 |

---

## Archivos para entrega al profesor

**Código (mínimo):**

```text
app.py, auth_service.py, auth_validators.py, persistence.py
models.py, validators.py, utils.py, web_logic.py, serialization.py
requirements.txt
templates/ (base.html, index.html, login.html, register.html)
static/ (css, js)
finanzas.db          ← se genera al usar la app; incluir si tiene datos de prueba
consultar_usuario.py ← opcional, para demostrar persistencia
```

**Documentación:**

- Este archivo: `entregable_laboratorio_3.md`

---

**Fin del entregable — Laboratorio 3, sesión del 5 de agosto de 2026**

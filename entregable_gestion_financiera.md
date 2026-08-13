# Entregable — Aplicación de gestión financiera personal (`main.py`)

**Estudiante:** Ricardo Díaz  
**Curso:** Cenfotec Curso 2  
**Fecha:** 23 de julio de 2026  
**Herramienta:** Cursor (asistente de código con IA)

**Archivos del proyecto:** `main.py`, `models.py`, `validators.py`, `requirements.txt`

---

## 5. Ejercicio 1 — Intención redactada

**Problema:** Crear una aplicación en Python que permita al usuario administrar sus finanzas personales, controlar gastos, evitar exceder su presupuesto y hacer seguimiento a metas de ahorro, con una interfaz gráfica sencilla.

**Datos de entrada (vía formularios en la GUI):**

- **Ingresos:** salario mensual, ingresos adicionales (opcional), ahorro mensual planificado (opcional).
- **Gastos fijos:** concepto y monto mensual (alquiler, servicios, créditos, transporte, etc.).
- **Gastos imprevistos:** concepto y monto (médicos, mantenimiento, emergencias u otro nombre personalizado).
- **Metas de ahorro:** nombre, monto objetivo, lo ya ahorrado y aporte mensual.

**Procesamiento requerido:**

1. Total de ingresos = salario + ingresos adicionales.
2. Total de gastos = suma de gastos fijos + suma de gastos imprevistos.
3. Balance disponible = ingresos − gastos totales.
4. Ahorro efectivo = ahorro planificado (limitado al balance) o suma de aportes a metas; si no hay plan, usar el balance positivo como referencia según la lógica definida en `FinancialProfile`.
5. Progreso de cada meta = porcentaje `ahorrado / objetivo` (máximo 100%).

**Resultado esperado:**

- Resumen con ingresos, gastos, dinero restante, ahorro y estado de metas.
- Pestañas con tablas, barras de progreso y gráficos (matplotlib) de ingresos, gastos y ahorro.
- Validación de entradas para evitar montos negativos o campos obligatorios vacíos.

---

## 6. Ejercicio 2 — Prompts, código generado y evidencia

### Prompt 1 (generación inicial)

> Actúa como un asistente experto en programación en Python. Desarrolla una aplicación para la gestión financiera personal: solicitar salario, ingresos adicionales, gastos obligatorios, metas de ahorro; calcular totales, balance, ahorro y progreso de metas; mostrar resumen; interfaz gráfica con Tkinter (tablas, barras de progreso, gráficos). Organizar en funciones y clases, validar entradas, código limpio.

### Código generado (estructura inicial — Ejercicio 2)

La IA generó un proyecto modular con tres módulos. Fragmentos representativos de la **primera versión** (sin gastos imprevistos ni nombre personalizado):

**`models.py` (núcleo de cálculos):**

```python
@dataclass
class FinancialProfile:
    monthly_salary: float = 0.0
    additional_income: float = 0.0
    fixed_expenses: List[FixedExpense] = field(default_factory=list)
    savings_goals: List[SavingsGoal] = field(default_factory=list)

    @property
    def total_income(self) -> float:
        return self.monthly_salary + self.additional_income

    @property
    def total_expenses(self) -> float:
        return sum(e.amount for e in self.fixed_expenses)

    @property
    def available_balance(self) -> float:
        return self.total_income - self.total_expenses
```

**`main.py` (interfaz con pestañas):**

```python
class FinanzasPersonalesApp:
    def __init__(self, root: tk.Tk) -> None:
        self.profile = FinancialProfile()
        self._build_ui()
        self.refresh_all_views()

    def _build_ui(self) -> None:
        self.notebook = ttk.Notebook(self.root)
        # Pestañas: Ingresos, Gastos fijos, Metas de ahorro, Resumen, Gráficos
        ...
```

**`validators.py`:** funciones `parse_positive_amount` y `parse_required_text` para validar montos y textos antes de guardar.

### Evidencia de funcionamiento

#### A) Cálculos automáticos (consola)

Comando:

```text
python evidencia_calculos.py
```

Salida (23/07/2026):

```text
=== Evidencia: cálculos financieros (models.py) ===

Ingresos totales                 850,000.00
Gastos fijos                     295,000.00
Gastos imprevistos               155,000.00
Gastos totales                   450,000.00
Balance (ingresos - gastos)      400,000.00
Ahorro mensual planificado       80,000.00
Dinero libre tras ahorro         320,000.00
Total acumulado en metas         200,000.00

Progreso meta "Fondo de emergencia": 20.0% (falta 800,000.00)

Importación de main.py: OK (la GUI se ejecuta con: python main.py)
```

**Verificación manual:** ingresos 850 000 − gastos 450 000 = balance 400 000; tras ahorro planificado 80 000 quedan 320 000 libres.

#### B) Interfaz gráfica

Comando:

```text
python main.py
```

Se abre la ventana **Gestión financiera personal** con las pestañas de ingresos, gastos, imprevistos, metas, resumen y gráficos.

> **Para el LMS:** adjuntar una **captura de pantalla** de la aplicación en ejecución (pestaña Resumen o Gráficos) junto con este documento.

---

## 7. Ejercicio 3 — Código modificado e indicación de cambios

Después de la generación inicial, se **modificó el código directamente** (y con apoyo puntual de la IA) en dos ampliaciones funcionales.

### Cambio 1 — Pestaña «Gastos imprevistos»

**Prompt de ampliación:**

> Agregar una parte para gastos no previstos: gastos médicos, mantenimiento casa, mantenimiento vehículo, emergencias.

| Qué se cambió | Dónde |
|---------------|--------|
| Nueva clase `UnexpectedExpense` y lista `unexpected_expenses` | `models.py` |
| `total_expenses` ahora incluye fijos + imprevistos | `models.py` |
| Nueva pestaña con combobox, tabla y totales | `main.py` |
| Tabla de imprevistos en Resumen; gráficos separan fijos e imprevistos | `main.py` |

Fragmento en `models.py`:

```python
@dataclass
class UnexpectedExpense:
    name: str
    amount: float

@property
def total_expenses(self) -> float:
    return self.total_fixed_expenses + self.total_unexpected_expenses
```

### Cambio 2 — Nombre personalizado en «Otro imprevisto»

**Prompt de ampliación:**

> Cuando el usuario seleccione «Otro imprevisto», permitir definir un nombre personalizado.

| Qué se cambió | Dónde |
|---------------|--------|
| Campo «Nombre del gasto» visible solo si el concepto es «Otro imprevisto» | `main.py` |
| Métodos `_on_unexpected_type_changed` y `_resolve_unexpected_name` | `main.py` |
| Al guardar, se usa el nombre personalizado en lugar de la etiqueta genérica | `main.py` |

Fragmento en `main.py`:

```python
OTHER_UNEXPECTED_LABEL = "Otro imprevisto"

def _on_unexpected_type_changed(self, *_args) -> None:
    if self.var_unexpected_name.get().strip() == OTHER_UNEXPECTED_LABEL:
        self.lbl_unexpected_custom.grid()
        self.entry_unexpected_custom.grid()
    else:
        self.lbl_unexpected_custom.grid_remove()
        self.entry_unexpected_custom.grid_remove()
        self.var_unexpected_custom.set("")

def _resolve_unexpected_name(self) -> Tuple[Optional[str], Optional[str]]:
    category = self.var_unexpected_name.get().strip()
    if category == OTHER_UNEXPECTED_LABEL:
        return parse_required_text(self.var_unexpected_custom.get(), "Nombre del gasto")
    return category, None
```

### Estado final del proyecto

- **`main.py`:** clase `FinanzasPersonalesApp` (~670 líneas), GUI completa.
- **`models.py`:** dataclasses y propiedades de cálculo.
- **`validators.py`:** validación reutilizable en todos los formularios.

La lógica base de ingresos, gastos fijos, metas y gráficos de la versión generada en el Ejercicio 2 **se conservó**; las modificaciones **extendieron** el programa sin reescribirlo por completo.

---

## 8. Ejercicio 4 — Dos soluciones alternativas y comparación

### Solución A — Arquitectura modular (la implementada)

Separar **modelo** (`models.py`), **validación** (`validators.py`) e **interfaz** (`main.py`).

```text
main.py          → Tkinter, eventos, tablas, gráficos
models.py        → FinancialProfile, cálculos con @property
validators.py    → parse_positive_amount, parse_required_text
```

**Ventajas:** Cálculos probables sin abrir la GUI; código más fácil de mantener y de extender (como los imprevistos).  
**Desventajas:** Más archivos; hay que entender imports entre módulos.

---

### Solución B — Aplicación monolítica en un solo archivo

Todo en un único `finanzas.py`: dataclasses, validadores y clase GUI juntos.

```python
# finanzas.py (alternativa no usada)
@dataclass
class FinancialProfile:
    ...

def parse_positive_amount(value: str):
    ...

class FinanzasPersonalesApp:
    ...
```

**Ventajas:** Un solo archivo para entregar o revisar; útil para prototipos muy pequeños.  
**Desventajas:** Con ~700+ líneas mezcla interfaz y lógica; más difícil de probar y de modificar sin errores.

---

### Comparación escrita

Ambas soluciones pueden cumplir **los mismos requisitos funcionales** del enunciado.

Para este laboratorio elegí la **Solución A** porque el enunciado pide buenas prácticas, funciones/clases y código mantenible: los cambios del Ejercicio 3 (imprevistos y nombre personalizado) solo tocaron `models.py` y partes concretas de `main.py`, sin mezclar cálculos con widgets.

La **Solución B** sería razonable solo si el alcance fuera mínimo (por ejemplo, una sola pantalla sin gráficos). En un proyecto con varias pestañas, validación y matplotlib, la separación por capas reduce riesgo al agregar funcionalidades.

Como alternativa de diseño **dentro del modelo**, también se pudo implementar el balance con funciones sueltas (`calcular_balance(perfil)`) en lugar de `@property` en `FinancialProfile`; las propiedades hacen el código más legible cuando los cálculos dependen siempre del estado actual del perfil.

---

## Retroalimentación del docente (criterio 4)

*(Completar después de la sesión si el docente sugirió cambios — por ejemplo, persistencia en archivo, más categorías de gasto, otro formato de moneda — e indicar cómo se aplicaron en el código.)*

---

## Autoevaluación según rúbrica

| Criterio | Descripción | Máx. | Cómo se cumple en este entregable |
|----------|-------------|------|-----------------------------------|
| 1 | Comprensión del enunciado | 10 | Sección 5: problema, entradas, cálculos y salidas. |
| 2 | Aplicación del proceso requerido | 10 | Secciones 5→8: intención, prompts/código IA, modificaciones, comparación. |
| 3 | Funcionalidad | 10 | Evidencia en sección 6; balance y progreso de metas verificables. |
| 4 | Retroalimentación del docente | 10 | Sección dedicada (completar tras la sesión). |
| 5 | Entrega del laboratorio | 10 | Documento único `.md` listo para el LMS + proyecto ejecutable. |

---

## Cómo ejecutar el programa

```text
python -m pip install -r requirements.txt
python main.py
```

*(Opcional: `python evidencia_calculos.py` para evidencia en consola sin capturas de la GUI.)*

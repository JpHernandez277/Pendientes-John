import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate
import sympy as sp
from sympy import symbols, sympify, lambdify, integrate as sp_integrate
import warnings
warnings.filterwarnings('ignore')

def safe_eval_function(func_str, x_val):
    """Evalúa una función de forma segura"""
    try:
        # Reemplazar funciones comunes
        func_str = func_str.replace('^', '**')
        func_str = func_str.replace('ln', 'log')
        
        # Crear función con numpy
        x = x_val
        result = eval(func_str, {
            "x": x, "np": np, "sin": np.sin, "cos": np.cos, "tan": np.tan,
            "exp": np.exp, "log": np.log, "sqrt": np.sqrt, "abs": np.abs,
            "pi": np.pi, "e": np.e
        })
        return result
    except:
        return None

def parse_function(func_str):
    """Convierte string a función sympy"""
    try:
        # Limpiar la función
        func_str = func_str.replace('^', '**')
        func_str = func_str.replace('ln', 'log')
        
        x = symbols('x')
        expr = sympify(func_str)
        return expr, x
    except:
        return None, None

def calculate_definite_integral(func_str, a, b, method='scipy'):
    """Calcula integral definida"""
    if method == 'scipy':
        try:
            # Usar scipy para integración numérica
            def f(x):
                return safe_eval_function(func_str, x)
            
            result, error = integrate.quad(f, a, b)
            return result, error
        except:
            return None, None
    
    elif method == 'sympy':
        try:
            # Usar sympy para integración simbólica
            expr, x = parse_function(func_str)
            if expr is None:
                return None, None
            
            result = sp_integrate(expr, (x, a, b))
            return float(result), 0
        except:
            return None, None

def calculate_indefinite_integral(func_str):
    """Calcula integral indefinida"""
    try:
        expr, x = parse_function(func_str)
        if expr is None:
            return None
        
        integral_expr = sp_integrate(expr, x)
        return integral_expr
    except:
        return None

def plot_function_and_integral(func_str, a=None, b=None, show_area=True):
    """Crea gráfico de la función y área bajo la curva"""
    try:
        # Rango para el gráfico
        if a is not None and b is not None:
            x_min = a - abs(b - a) * 0.2
            x_max = b + abs(b - a) * 0.2
        else:
            x_min, x_max = -10, 10
        
        x = np.linspace(x_min, x_max, 1000)
        
        # Evaluar la función
        y = []
        for xi in x:
            yi = safe_eval_function(func_str, xi)
            if yi is not None:
                y.append(yi)
            else:
                y.append(np.nan)
        
        y = np.array(y)
        
        # Crear el gráfico
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plotear la función
        ax.plot(x, y, 'b-', linewidth=2, label=f'f(x) = {func_str}')
        
        # Mostrar área bajo la curva si es integral definida
        if a is not None and b is not None and show_area:
            x_fill = np.linspace(a, b, 200)
            y_fill = []
            for xi in x_fill:
                yi = safe_eval_function(func_str, xi)
                if yi is not None:
                    y_fill.append(yi)
                else:
                    y_fill.append(0)
            
            y_fill = np.array(y_fill)
            ax.fill_between(x_fill, 0, y_fill, alpha=0.3, color='green', 
                           label=f'Área entre x={a} y x={b}')
            
            # Líneas verticales en los límites
            ax.axvline(x=a, color='red', linestyle='--', alpha=0.7, label=f'x = {a}')
            ax.axvline(x=b, color='red', linestyle='--', alpha=0.7, label=f'x = {b}')
        
        # Configurar el gráfico
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('x', fontsize=12)
        ax.set_ylabel('f(x)', fontsize=12)
        ax.set_title('Función y su Integral', fontsize=14, fontweight='bold')
        ax.legend()
        ax.axhline(y=0, color='k', linewidth=0.5)
        ax.axvline(x=0, color='k', linewidth=0.5)
        
        return fig
        
    except Exception as e:
        st.error(f"Error al crear el gráfico: {str(e)}")
        return None

def main():
    st.set_page_config(page_title="Calculadora de Integrales", page_icon="∫", layout="wide")
    
    st.title("∫ Calculadora de Integrales")
    st.markdown("---")
    
    # Sidebar para configuración
    st.sidebar.header("⚙️ Configuración")
    integral_type = st.sidebar.selectbox(
        "Tipo de integral:",
        ["Definida", "Indefinida"]
    )
    
    method = st.sidebar.selectbox(
        "Método de cálculo:",
        ["scipy (numérico)", "sympy (simbólico)"]
    )
    
    # Entrada de la función
    st.subheader("📝 Ingresa la función")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        func_input = st.text_input(
            "Función f(x):",
            value="x**2",
            help="Ejemplos: x**2, sin(x), exp(x), x**3 + 2*x - 1"
        )
    
    with col2:
        st.markdown("**Funciones disponibles:**")
        st.markdown("""
        - `x**2` (potencias)
        - `sin(x)`, `cos(x)`, `tan(x)`
        - `exp(x)` (exponencial)
        - `log(x)` (logaritmo natural)
        - `sqrt(x)` (raíz cuadrada)
        - `abs(x)` (valor absoluto)
        - `pi`, `e` (constantes)
        """)
    
    # Límites de integración para integral definida
    if integral_type == "Definida":
        st.subheader("🎯 Límites de integración")
        col1, col2 = st.columns(2)
        
        with col1:
            a = st.number_input("Límite inferior (a):", value=0.0, step=0.1, format="%.2f")
        
        with col2:
            b = st.number_input("Límite superior (b):", value=1.0, step=0.1, format="%.2f")
        
        if a >= b:
            st.warning("⚠️ El límite superior debe ser mayor que el inferior")
            return
    
    st.markdown("---")
    
    # Calcular integral
    if func_input:
        if integral_type == "Definida":
            # Integral definida
            st.subheader("📊 Resultado de la Integral Definida")
            
            method_key = 'scipy' if 'scipy' in method else 'sympy'
            result, error = calculate_definite_integral(func_input, a, b, method_key)
            
            if result is not None:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Valor de la integral", f"{result:.8f}")
                    
                    if error is not None and error > 0:
                        st.metric("Error estimado", f"{error:.2e}")
                    
                    # Mostrar la integral matemáticamente
                    st.markdown("**Integral calculada:**")
                    st.latex(f"\\int_{{{a}}}^{{{b}}} {func_input} \\, dx = {result:.6f}")
                    
                with col2:
                    st.subheader("🔍 Información adicional")
                    
                    # Área absoluta
                    abs_area = abs(result)
                    st.metric("Área absoluta", f"{abs_area:.8f}")
                    
                    # Interpretación geométrica
                    if result > 0:
                        st.success("✅ Área neta positiva")
                    elif result < 0:
                        st.error("❌ Área neta negativa")
                    else:
                        st.info("⚪ Área neta cero")
                    
                    # Valor promedio de la función
                    avg_value = result / (b - a)
                    st.metric("Valor promedio de f(x)", f"{avg_value:.6f}")
                
            else:
                st.error("❌ No se pudo calcular la integral. Verifica la función ingresada.")
        
        else:
            # Integral indefinida
            st.subheader("📊 Resultado de la Integral Indefinida")
            
            indefinite_result = calculate_indefinite_integral(func_input)
            
            if indefinite_result is not None:
                st.success("✅ Integral indefinida calculada exitosamente")
                
                # Mostrar el resultado
                st.markdown("**Integral indefinida:**")
                st.latex(f"\\int {func_input} \\, dx = {indefinite_result} + C")
                
                # Mostrar en formato más legible
                st.markdown("**Resultado:**")
                st.code(f"∫ {func_input} dx = {indefinite_result} + C", language="text")
                
                # Verificación por derivación
                try:
                    x = symbols('x')
                    derivative = sp.diff(indefinite_result, x)
                    st.markdown("**Verificación (derivada del resultado):**")
                    st.latex(f"\\frac{{d}}{{dx}}[{indefinite_result}] = {derivative}")
                except:
                    pass
                    
            else:
                st.error("❌ No se pudo calcular la integral indefinida. Verifica la función ingresada.")
    
    # Visualización gráfica
    st.markdown("---")
    show_plot = st.checkbox("📈 Mostrar gráfico", value=True)
    
    if show_plot and func_input:
        st.subheader("📈 Visualización Gráfica")
        
        if integral_type == "Definida":
            fig = plot_function_and_integral(func_input, a, b, True)
        else:
            fig = plot_function_and_integral(func_input)
        
        if fig is not None:
            st.pyplot(fig)
            
            # Información sobre el gráfico
            with st.expander("ℹ️ Información sobre el gráfico"):
                if integral_type == "Definida":
                    st.markdown("""
                    - La **línea azul** representa la función f(x)
                    - El **área verde** representa la integral definida
                    - Las **líneas rojas punteadas** marcan los límites de integración
                    - El **área por encima del eje x** es positiva
                    - El **área por debajo del eje x** es negativa
                    """)
                else:
                    st.markdown("""
                    - La **línea azul** representa la función f(x)
                    - La integral indefinida representa la familia de funciones cuya derivada es f(x)
                    - Cada función de esta familia difiere por una constante C
                    """)
    
    # Ejemplos y ayuda
    with st.expander("📚 Ejemplos y Ayuda"):
        st.markdown("""
        ### Ejemplos de funciones:
        
        **Polinomios:**
        - `x**2` → integral: x³/3
        - `2*x + 1` → integral: x² + x
        - `x**3 - 2*x**2 + x` → integral: x⁴/4 - 2x³/3 + x²/2
        
        **Funciones trigonométricas:**
        - `sin(x)` → integral: -cos(x)
        - `cos(x)` → integral: sin(x)
        - `tan(x)` → integral: -log(cos(x))
        
        **Funciones exponenciales y logarítmicas:**
        - `exp(x)` → integral: exp(x)
        - `1/x` → integral: log(x)
        - `x*exp(x)` → integral: (x-1)*exp(x)
        
        **Funciones con raíces:**
        - `sqrt(x)` → integral: (2/3)*x^(3/2)
        - `1/sqrt(x)` → integral: 2*sqrt(x)
        
        ### Sintaxis:
        - Use `**` para potencias: `x**2`, `x**3`
        - Use `*` para multiplicación: `2*x`, `x*sin(x)`
        - Funciones: `sin()`, `cos()`, `tan()`, `exp()`, `log()`, `sqrt()`, `abs()`
        - Constantes: `pi`, `e`
        
        ### Métodos de cálculo:
        - **Scipy (numérico)**: Más rápido, funciona con cualquier función
        - **Sympy (simbólico)**: Más preciso, da resultados exactos cuando es posible
        """)
    
    # Información adicional
    with st.expander("🔬 Información técnica"):
        st.markdown("""
        ### Métodos de integración:
        
        **Integración numérica (Scipy):**
        - Utiliza el algoritmo de cuadratura adaptativa
        - Proporciona estimación del error
        - Funciona con funciones complejas
        
        **Integración simbólica (Sympy):**
        - Encuentra la forma analítica exacta
        - Utiliza reglas de integración matemáticas
        - Puede fallar con funciones muy complejas
        
        ### Interpretación geométrica:
        - La integral definida representa el área bajo la curva
        - Áreas por encima del eje x son positivas
        - Áreas por debajo del eje x son negativas
        - La integral indefinida es la antiderivada de la función
        """)

if __name__ == "__main__":
    main()
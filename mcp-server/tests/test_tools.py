from src.database import TransactionType
from src.tools import (
    obtener_balance, 
    obtener_resumen_por_categoria, 
    registrar_transaccion,
    listar_transacciones,
    actualizar_transaccion,
    eliminar_transaccion,
    vaciar_transacciones,
)
import uuid

def test_registrar_transaccion_expense() -> None:
    resultado = registrar_transaccion(TransactionType.EXPENSE, 20000, "comida", "almuerzo")
    assert "gasto de 20000.00" in resultado
    assert "comida" in resultado


def test_registrar_transaccion_con_descripcion() -> None:
    resultado = registrar_transaccion(TransactionType.EXPENSE, 1000000, "Transporte", "Compra de moto")
    assert "Compra de moto" in resultado


def test_registrar_transaccion_income() -> None:
    resultado = registrar_transaccion(TransactionType.INCOME, 500000, "salario", None)
    assert "ingreso de 500000.00" in resultado
    assert "salario" in resultado


def test_obtener_balance_sin_transacciones() -> None:
    resultado = obtener_balance()
    assert "Ingresos totales: 0.00" in resultado
    assert "Gastos totales: 0.00" in resultado
    assert "Balance neto disponible: 0.00" in resultado


def test_obtener_balance_con_transacciones() -> None:
    registrar_transaccion(TransactionType.INCOME, 1000, "salario", None)
    registrar_transaccion(TransactionType.EXPENSE, 200, "comida", None)

    resultado = obtener_balance()
    assert "Ingresos totales: 1000.00" in resultado
    assert "Gastos totales: 200.00" in resultado
    assert "Balance neto disponible: 800.00" in resultado


def test_obtener_resumen_por_categoria_vacio() -> None:
    resultado = obtener_resumen_por_categoria()
    assert resultado == "No hay transacciones registradas todavía."


def test_obtener_resumen_por_categoria_con_datos() -> None:
    registrar_transaccion(TransactionType.EXPENSE, 200, "comida", None)
    registrar_transaccion(TransactionType.INCOME, 1000, "salario", None)

    resultado = obtener_resumen_por_categoria()
    assert "comida (expense): 200.00" in resultado
    assert "salario (income): 1000.00" in resultado

def test_listar_transacciones_vacio() -> None:
    resultado = listar_transacciones()
    assert "No se encontraron transacciones" in resultado


def test_listar_transacciones_con_datos() -> None:
    registrar_transaccion(TransactionType.EXPENSE, 5000, "Transporte", "Taxi")
    registrar_transaccion(TransactionType.INCOME, 12000, "Ventas", "Venta de libro")

    resultado = listar_transacciones()
    assert "EXPENSE: 5000.00" in resultado
    assert "Transporte" in resultado
    assert "INCOME: 12000.00" in resultado
    assert "Ventas" in resultado


def test_listar_transacciones_con_filtros() -> None:
    registrar_transaccion(TransactionType.EXPENSE, 5000, "Transporte", "Taxi")
    registrar_transaccion(TransactionType.INCOME, 12000, "Ventas", "Venta de libro")

    # Filtrar por tipo
    resultado_tipo = listar_transacciones(tipo=TransactionType.INCOME)
    assert "INCOME: 12000.00" in resultado_tipo
    assert "EXPENSE: 5000.00" not in resultado_tipo

    # Filtrar por categoría
    resultado_cat = listar_transacciones(categoria="Transporte")
    assert "Transporte" in resultado_cat
    assert "Ventas" not in resultado_cat


def test_actualizar_transaccion_exito() -> None:
    registrar_transaccion(TransactionType.EXPENSE, 150, "Comida", "Café")
    
    # Obtenemos el ID listando transacciones
    lista = listar_transacciones()
    # Extraer el ID de la cadena (ej. "ID: <uuid> | ...")
    tx_id = lista.split("ID: ")[1].split(" |")[0]

    resultado = actualizar_transaccion(
        id_transaccion=tx_id,
        monto=180.0,
        categoria="Alimentación",
        descripcion="Café y pan"
    )
    
    assert "actualizada" in resultado
    assert "monto a 180.00" in resultado
    assert "categoría a 'Alimentación'" in resultado
    assert "descripción a 'Café y pan'" in resultado

    # Verificar que los cambios se reflejen en el balance/lista
    nueva_lista = listar_transacciones()
    assert "EXPENSE: 180.00" in nueva_lista
    assert "Alimentación" in nueva_lista


def test_actualizar_transaccion_id_invalido_o_inexistente() -> None:
    # ID inválido
    resultado_inv = actualizar_transaccion("no-un-uuid", monto=100.0)
    assert "no es un UUID válido" in resultado_inv

    # ID inexistente pero con formato UUID válido
    id_falso = str(uuid.uuid4())
    resultado_inex = actualizar_transaccion(id_falso, monto=100.0)
    assert "No se encontró la transacción solicitada" in resultado_inex


def test_eliminar_transaccion_exito() -> None:
    registrar_transaccion(TransactionType.EXPENSE, 300, "Otros", "Prueba")
    
    lista = listar_transacciones()
    tx_id = lista.split("ID: ")[1].split(" |")[0]

    resultado = obtener_balance() # Cargar el balance antes para asegurar consistencia
    resultado_del = eliminar_transaccion(tx_id)
    assert "eliminó correctamente" in resultado_del

    # Confirmar que ya no está en la base de datos
    lista_despues = listar_transacciones()
    assert "No se encontraron transacciones" in lista_despues


def test_eliminar_transaccion_no_encontrada() -> None:
    id_falso = str(uuid.uuid4())
    resultado = eliminar_transaccion(id_falso)
    assert "No se encontró la transacción especificada" in resultado

def test_vaciar_transacciones_sin_confirmacion() -> None:
    # Registrar un dato para asegurarnos de que no se borre
    registrar_transaccion(TransactionType.EXPENSE, 100, "Comida", "Almuerzo")
    
    # Intentar vaciar sin confirmación (por defecto es False)
    resultado = vaciar_transacciones(confirmar=False)
    assert "ADVERTENCIA" in resultado
    assert "Esta acción es destructiva e irreversible" in resultado
    
    # Verificar que el registro aún existe
    balance_resultado = obtener_balance()
    assert "Gastos totales: 100.00" in balance_resultado


def test_vaciar_transacciones_con_confirmacion() -> None:
    registrar_transaccion(TransactionType.EXPENSE, 100, "Comida", "Almuerzo")
    
    # Vaciar confirmando la acción
    resultado = vaciar_transacciones(confirmar=True)
    assert "1 registros eliminados" in resultado
    
    # Verificar que quedó completamente vacío
    balance_resultado = obtener_balance()
    assert "Ingresos totales: 0.00. Gastos totales: 0.00. Balance neto disponible: 0.00." in balance_resultado
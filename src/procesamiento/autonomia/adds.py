import polars as pl
from controles_informacion.controles_informacion import read_sap
import constantes as ct
import xlwings as xw
import os


def cantidades_sap(hojas_afo: list[str]) -> pl.DataFrame:
    return read_sap(
        ["Generales", "Vida"],
        hojas_afo,
        int(ct.PARAMS_FECHAS[1][1]),
    ).filter(pl.col("mes_mov") == int(ct.PARAMS_FECHAS[1][1])).collect()


def crear_hoja_segmentacion(df: pl.DataFrame, nombre_hoja: str) -> None:
    xw.Book(f"{os.getcwd()}/data/segmentacion_autonomia.xlsx").set_mock_caller()
    wb = xw.Book.caller()

    try:
        wb.sheets.add(name=nombre_hoja, after="Fechas")
    except ValueError:
        wb.sheets[nombre_hoja].delete()
        wb.sheets.add(name=nombre_hoja, after="Fechas")

    wb.sheets[nombre_hoja].range("A1:A500").number_format = "@"
    wb.sheets[nombre_hoja].range("B1:B500").number_format = "@"
    wb.sheets[nombre_hoja]["A1"].options(index=False).value = df.to_pandas()


def main() -> None:
    df_sinis = cantidades_sap(["pago_cedido", "aviso_cedido"])
    crear_hoja_segmentacion(df_sinis, "SAP_Sinis_Ced")

    df_primas = cantidades_sap(
        [
            "prima_bruta",
            "prima_retenida",
            "prima_bruta_devengada",
            "prima_retenida_devengada",
            "rpnd_bruto",
            "rpnd_cedido",
        ]
    ).with_columns(
        rpnd_retenido=pl.col("rpnd_bruto") - pl.col("rpnd_cedido"),
        prima_cedida=pl.col("prima_bruta") - pl.col("prima_retenida"),
    )
    crear_hoja_segmentacion(df_primas, "add_p_SAP_Primas_Ced")

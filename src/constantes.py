import xlwings as xw
import polars as pl
import pandas as pd
from math import ceil, floor
from datetime import date


BASE_COLS = ["ramo_desc", "apertura_canal_desc", "apertura_amparo_desc"]

PARAMS_FECHAS = pl.read_excel(
    "data/segmentacion.xlsx", sheet_name="Fechas", has_header=False
).rows()

INI_DATE = date(int(PARAMS_FECHAS[0][1]) // 100, int(PARAMS_FECHAS[0][1]) % 100, 1)
END_DATE = date(int(PARAMS_FECHAS[1][1]) // 100, int(PARAMS_FECHAS[1][1]) % 100, 1)
MES_CORTE = int(PARAMS_FECHAS[1][1])
TIPO_ANALISIS = PARAMS_FECHAS[2][1]

PERIODICIDADES = {"Mensual": 1, "Trimestral": 3, "Semestral": 6, "Anual": 12}


HEADER_TRIANGULOS = 2
SEP_TRIANGULOS = 2
COL_OCURRS_PLANTILLAS = 6
FILA_INI_PLANTILLAS = 7


def num_ocurrencias(sheet: xw.Sheet) -> int:
    return sheet.range(
        sheet.cells(FILA_INI_PLANTILLAS + HEADER_TRIANGULOS, COL_OCURRS_PLANTILLAS),
        sheet.cells(FILA_INI_PLANTILLAS + HEADER_TRIANGULOS, COL_OCURRS_PLANTILLAS).end(
            "down"
        ),
    ).count


def num_alturas(sheet: xw.Sheet) -> int:
    return (
        sheet.range(
            sheet.cells(
                FILA_INI_PLANTILLAS + HEADER_TRIANGULOS - 1, COL_OCURRS_PLANTILLAS + 1
            ),
            sheet.cells(
                FILA_INI_PLANTILLAS + HEADER_TRIANGULOS - 1, COL_OCURRS_PLANTILLAS + 1
            ).end("right"),
        ).count
        // 2
    )


def mes_del_periodo(mes_corte: int, num_ocurrencias: int, num_alturas: int) -> int:
    anno = mes_corte // 100
    mes = mes_corte % 100
    periodicidad = ceil(num_alturas / num_ocurrencias)

    if mes < periodicidad:
        mes_periodo = mes
    else:
        mes_periodo = mes_corte - (
            anno * 100 + floor(mes / periodicidad) * periodicidad
        )
    return mes_periodo


def sheet_to_dataframe(
    wb: xw.Book, sheet_name: str, schema: pl.Schema | None = None
) -> pl.LazyFrame:
    return pl.from_pandas(
        wb.sheets[sheet_name]
        .cells(1, 1)
        .options(pd.DataFrame, header=1, index=False, expand="table")
        .value,
        schema_overrides=schema,
    ).lazy()


def path_plantilla(wb: xw.Book) -> str:
    return wb.fullname.replace(wb.name, "")

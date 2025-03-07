import asyncio
import time

import xlwings as xw
from src import utils
from src.logger_config import logger
from src.metodos_plantilla.generar import generar_plantilla
from src.models import ModosPlantilla

from .guardar_apertura import guardar_apertura
from .traer_apertura import traer_apertura


async def traer_y_guardar_todas_las_aperturas(
    wb: xw.Book,
    modos: ModosPlantilla,
    mes_corte: int,
    negocio: str,
    traer: bool = False,
) -> None:
    s = time.time()

    hoja_plantilla = modos.plantilla.capitalize()
    aperturas = (
        utils.obtener_aperturas(negocio, "siniestros")
        .get_column("apertura_reservas")
        .to_list()
    )
    atributos = ["bruto", "retenido"] if hoja_plantilla != "Frecuencia" else ["bruto"]

    num_apertura = 0
    for apertura in aperturas:
        for atributo in atributos:
            modos_actual = modos.model_copy()
            modos_actual.apertura = apertura
            modos_actual.atributo = atributo  # type: ignore

            if modos.plantilla == "severidad":
                modos_frec = modos_actual.model_copy(
                    update={"plantilla": "frecuencia", "atributo": "bruto"}
                )
                generar_plantilla(
                    wb, negocio, modos_frec, mes_corte, solo_triangulo=True
                )
            generar_plantilla(wb, negocio, modos_actual, mes_corte)
            if traer:
                traer_apertura(wb, modos_actual)
            guardar_apertura(wb, modos_actual)

            await asyncio.sleep(0)

            logger.info(
                utils.limpiar_espacios_log(
                    f"""
                    Apertura {num_apertura + 1} de {len(aperturas) * len(atributos)}
                    terminada.
                    """
                )
            )
            num_apertura += 1

    if traer:
        logger.success("Todas las aperturas se han traido y guardado correctamente.")
    else:
        logger.success("Todas las aperturas se han guardado correctamente.")

    logger.info(f"Tiempo total: {round(time.time() - s, 2)} segundos.")

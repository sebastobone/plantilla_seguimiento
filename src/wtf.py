import xlwings as xw

import plantilla as plant

wb = xw.Book("src/plantilla.xlsm")

plant.guardar_traer_fn(wb, "traer", "frec", "01_001_A_D", "bruto", 202312)

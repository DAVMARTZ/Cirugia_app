import pandas as pd
import random
from datetime import date, timedelta

nombres = ["Juan Pérez", "María García", "Luis Rodríguez", "Ana Martínez", "Carlos López", 
           "Elena Gómez", "Pedro Sánchez", "Laura Díaz", "Jorge Torres", "Marta Ruiz",
           "Gabriel Castro", "Lucía Morales", "Andrés Silva", "Sofía Vargas", "Diego Mendoza"]

instituciones = ["Sura", "Sanitas", "Compensar", "Nueva EPS", "Salud Total"]
tipos_doc = ["C.C", "T.I", "C.C", "C.C", "C.C"]
sexos = ["Masculino", "Femenino"]

data = []
for i in range(15):
    nombre = nombres[i]
    documento = str(random.randint(1000000000, 1999999999))
    institucion = random.choice(instituciones)
    tipo = random.choice(tipos_doc)
    
    # Fecha de nacimiento aleatoria entre 1950 y 2010
    start_date = date(1950, 1, 1)
    end_date = date(2010, 12, 31)
    days_between_dates = (end_date - start_date).days
    random_number_of_days = random.randrange(days_between_dates)
    fecha_nac = start_date + timedelta(days=random_number_of_days)
    
    sexo = random.choice(sexos) if i > 0 else "Masculino" # Mezcla
    edad = date.today().year - fecha_nac.year
    
    data.append([nombre, documento, institucion, tipo, str(fecha_nac), sexo, edad])

df = pd.DataFrame(data, columns=["nombre_paciente", "numero_documento", "institucion", "tipo_documento", "fecha_nacimiento", "sexo", "edad"])
df.to_csv("/home/luis/Escritorio/Cirugia_app/data/pacientes.csv", index=False)
print("15 pacientes generados con éxito.")

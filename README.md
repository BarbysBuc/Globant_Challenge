# API para migración de CSV a Base de Datos (Globant Challenge)

## Descripción

Esta REST API sirve para cargar datos históricos desde CSV a una base de datos SQL en PostgreSQL,
Procesa en batches de hasta 1000 registros.

## Funcionalidades

- Recibir datos históricos desde archivos CSV.
- Subir estos archivos a la nueva base de datos.
- Transacciones por lotes (1 hasta 1000 filas) en una sola solicitud.

## Requisitos Previos
Tener Python, Git y PostgreSQL instalados.

### Instalación de PostgreSQL
Las siguientes instrucciones son para Windows.
Descarga el instalador desde la página oficial de [PostgreSQL](https://www.postgresql.org/download/windows/) y sigue las instrucciones de instalación y recuerda la contraseña que configures para el usuario postgres.
Luego de la instalación el servidor se inicia automáticamente

### Creación de la base de datos
Acceder a la base de datos
`psql -U postgres -d postgres`

Para verificar que recibe conexiones desde cualquier IP, una vez accedemos, buscamos el archivo hba
`SHOW hba_file;`
y agregamos la siguiente línea si no se encuentra con cualquier editor de texto:
`host    all             all             0.0.0.0/0               md5`

Reiniciamos Postgre desde la consola (iniciada con permisos de administrador)
`net stop postgresql-x64-16`
`net start postgresql-x64-16`
El 16 en el comando corresponde a la versión de Postgre que instalamos

Crear la base de datos
`CREATE DATABASE g_challenge;`

Conectarse a la base de datos
`psql -U postgres -d g_challenge`

## Configuración del proyecto

### Clonar el repositorio
```
git clone https://github.com/BarbysBuc/Globant_Challenge.git
cd Globant_Challenge
```

### Instalar dependencias
```
pip install -r requirements.txt
```

### Configurar la Base de datos
Edita el archivo api/database.py y actualiza la variable DATABASE_URL con los detalles de tu base de datos.
```
DATABASE_URL = "postgresql+asyncpg://postgres:contraseña_elegida@localhost/nombre_base_datos"
```

### Ejecutar el Servidor
```
uvicorn main:app --reload
```

## Uso
Usa el endpoint /upload_csv para subir los archivos CSV.
y los endpoints /departments_above_mean o /employees_per_quarter para las consultas.

## Endpoints

### Subir CSV
- URL: /upload_csv
- Método: POST
- Descripción: Sube un archivo CSV y lo carga a la base de datos
- Solicitud:
    - Archivo: .csv con datos históricos
- Respuesta:
    - 200 OK: Cuando el archivo se procesa correctamente
    - 400 Bad Request: Cuando el formato de archivo no es .csv
    - 500 Internal Server Error: Cuando ocurre un error al procesar el archivo

### Consulta empleados contratados para cada job en cada quarter del 2021
- URL: /employees_per_quarter
- Método: GET
- Descripción: Realiza la consulta a la Base de datos
- Respuesta:
    - 200 OK: Se realizó la consulta.


### Consulta empleados contratados para cada departamentoique contrató más empleados que la media en 2021
- URL: /employees_per_quarter
- Método: GET
- Descripción: Realiza la consulta a la Base de datos
- Respuesta:
    - 200 OK: Se realizó la consulta.
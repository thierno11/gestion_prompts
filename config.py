import os

DATABASE_INFO = {
    "host":os.getenv("DATABASE_HOST"),
    "database":os.getenv("DATABASE_NAME"),
    "user":os.getenv("DATABASE_USER"),
    "password":os.getenv("DATABASE_PASSWORD"),
    "port":os.getenv("DATABASE_PORT")
}

import psycopg2
from config import load_config

def connect():
    return psycopg2.connect(**load_config())
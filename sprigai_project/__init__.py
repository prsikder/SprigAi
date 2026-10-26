"""Install the pure-Python MySQL driver before Django loads its backend."""
import pymysql

pymysql.install_as_MySQLdb()

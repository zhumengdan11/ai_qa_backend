import sys
# 强制设置标准输入、输出、错误流为UTF‑8编码，解决ASCII编码报错 \u2011
sys.stdout.reconfigure(encoding="utf-8")
sys.stdin.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

import pymysql
pymysql.install_as_MySQLdb()
RPMS PYTHON PYCHARM PROJECT
===========================

1. Extract RPMS_Python_PyCharm_Project.zip
2. Open PyCharm
3. File > Open
4. Select folder: RPMS_Python_PyCharm
5. Select/Open the project
6. Configure Python interpreter if PyCharm asks
7. Open Terminal
8. Run:
   pip install -r requirements.txt
9. Check database configuration:
   rpms/util/db_connection.py
10. Run:
   rpms/app/main.py

Current database name:
recruitment_portal

Default configuration:
host=localhost
port=3306
user=root
password=root

Change password if required.

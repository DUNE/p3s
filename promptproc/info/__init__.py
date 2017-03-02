# from django.db	import connection
# from django.db.backends.signals import connection_created

# def setTO(sender, connection, **kwargs):
#     sqliteTO = 'PRAGMA busy_timeout = 50000;'
    
#     cursor = connection.cursor()
#     cursor.execute(sqliteTO)
    


# connection_created.connect(setTO)

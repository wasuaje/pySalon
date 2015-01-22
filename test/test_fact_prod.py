#ejecutar asi:
#python web2py.py -S pysalon -M -R applications/pysalon/test/test_cobros.py
import unittest

from gluon.globals import Request
from gluon.shell import *
auth=Auth(db)
a=db.auth_user(1)		#id del usuario que quieras loguear para pruebas
auth.login_user(a)
#print a
env=exec_environment()

execfile("applications/pysalon/controllers/pos.py", globals())


class TestFactProdIns(unittest.TestCase):
    def setUp(self):
    	# Opcional borrar la data de las tablas
		db(db.fc_factura.id>0).delete()  # Clear the database
		db(db.fc_factura_det.id>0).delete()  # Clear the database
		db(db.in_mov.id>0).delete()  # Clear the database
		db.commit()
    	#self.env = unittest.new_env(app='pysalon', controller='pos')
    	#self.env, self.db = setup('pos', 'default',                            db_name='db', db_link='sqlite:memory:')
		self.env = Storage(env)
		request = Request(env)  # Use a clean Request object

    def testinsert(self):
        # Set variables for the test function        
        request.vars["prodid"] = 13
        request.vars["clteid"] =12 
        request.vars["perid"] = 1
        request.vars["fact_id"] = "0"

        resp = fact_prod()        
        db.commit()
        #debe traer registro >0
        self.assertNotEquals(0, resp[0])

class TestFactDelFact(unittest.TestCase):
    def setUp(self):
    	#self.env = unittest.new_env(app='pysalon', controller='pos')
    	#self.env, self.db = setup('pos', 'default',                            db_name='db', db_link='sqlite:memory:')
    	self.env = Storage(env)
        request = Request(env)  # Use a clean Request object

    def testdeletes(self):
        # Set variables for the test function        
        #request.vars["prodid"] = 1
        #request.vars["clteid"] =12 
        #request.vars["perid"] = 1
        request.vars["fact_id"] = 33

        resp = fact_del() 
        db.commit()
        #debe traer registro >0
        self.assertNotEquals(0, resp[0])

class TestFactDelLin(unittest.TestCase):
    def setUp(self):
    	#self.env = unittest.new_env(app='pysalon', controller='pos')
    	#self.env, self.db = setup('pos', 'default',                            db_name='db', db_link='sqlite:memory:')
    	self.env = Storage(env)
        request = Request(env)  # Use a clean Request object

    def testdeletes(self):
        # Set variables for the test function        
        #request.vars["prodid"] = 1
        #request.vars["clteid"] =12 
        #request.vars["perid"] = 1
        request.vars["det_id"] = 21

        resp = det_del() 
        db.commit()
        #debe traer registro >0
        self.assertNotEquals(0, resp[0])



suite = unittest.TestSuite()

#para insert
suite.addTest(unittest.makeSuite(TestFactProdIns))

#para delete
#suite.addTest(unittest.makeSuite(TestFactDelFact))

#para delete linea
#suite.addTest(unittest.makeSuite(TestFactDelLin))

unittest.TextTestRunner(verbosity=3).run(suite)
# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
    #db = DAL('sqlite://storage.sqlite',fake_migrate_all=True)
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth, filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

import datetime

db.define_table('cf_empresa',
    Field('id','integer'),
    Field('nombre','string', label=T('Nombre')),
    Field('razon_social','string', label=T('Razon Social')),
    Field('direccion','text', label=T('Direccion')),
    Field('rif','string', label=T('Rif')),
    Field('nit','string', label=T('Nit')),
    Field('email','string', label=T('Email')),
    Field('tlf','string', label=T('Tlf')),
    Field('fax','string', label=T('Fax')),
    Field('ruta_foto','upload',autodelete=True, label=T('Imagen'))
    )


db.define_table('cf_proveedor',
    Field('id','integer'),
    Field('nombre','string', label=T('Nombre')),
    Field('razon_social','string', label=T('Razon Social')),
    Field('direccion','text', label=T('Direccion')),
    Field('rif','string', label=T('R.I.F')),
    Field('nit','string', label=T('N.I.T')),
    Field('email','string', label=T('E-Mail')),
    Field('tlf','string', label=T('Tlf.')),
    Field('fax','string', label=T('Fax.')),
    Field('ruta_foto','upload',autodelete=True, label=T('Imagen')),format='%(razon_social)s'
    )

db.define_table('cf_cliente',
    Field('id','integer'),
    Field('nombre','string', label=T('Nombre')),
    Field('razon_social','string', label=T('Razon Social')),
    Field('direccion','text', label=T('Direccion')),
    Field('rif','string', label=T('R.I.F')),
    Field('nit','string', label=T('N.I.T')),
    Field('email','string', label=T('E-Mail')),
    Field('tlf','string', label=T('Tlf.')),
    Field('fax','string', label=T('Fax.')),
    Field('juridico','boolean', label=T('Es Juridico')),
    Field('ruta_foto','upload',autodelete=True, label=T('Imagen')),format='%(razon_social)s'
    )


db.define_table('cf_especialidad',
    Field('id','integer'),
    Field('codigo','string', label=T('Codigo')),
    Field('nombre','string', label=T('Nombre')),    
    format='%(codigo)s - %(nombre)s'
    )
db.cf_especialidad.codigo.requires=IS_NOT_IN_DB(db, db.cf_especialidad.codigo)

#--------
db.define_table('cf_persona',
    Field('id','integer'),
    Field('cedula','string',unique=True, label=T('Cedula')),
    Field('nombres','string', label=T('Nombres')),
    Field('apellidos','string' , label=T('Apellidos')),
    Field('ruta_foto','upload',autodelete=True, label=T('Foto')),
    Field('sexo','string',requires=IS_IN_SET(['M', 'F', 'O']),label=T('Sexo')),
    Field('usuario','string', label=T('Usuario')),
    Field('password','password', label=T('Pass')),
    Field('especialidad_id','integer', label=T('Especialidad')),
    Field('tlf_hab','string' , label=T('Tlf.Hab.')) ,
    Field('tlf_cel','string', label=T('Cel.')),  
    Field('direccion','string', label=T('Direccion')),
    Field('comision','float', label=T('Comision'), default=0.00),
    Field('email','string', label=T('Email')),    
    )
db.cf_persona.especialidad_id.requires = IS_IN_DB(db,db.cf_especialidad.id,'%(nombre)s')
db.cf_persona.cedula.requires = IS_NOT_IN_DB(db,db.cf_persona.cedula)

#Susbsistema inventario productos
#--------

db.define_table('in_categoria',
    Field('id','integer'),
    Field('codigo','string', label=T('Codigo')),
    Field('nombre','string', label=T('Nombre')),
    Field('show_in_menu','boolean', label=T('Mostrar en menu')),
    Field('ruta_foto','upload',autodelete=True, label=T('Imagen')), 
    format='%(codigo)s - %(nombre)s'
    )
db.in_categoria.codigo.requires=IS_NOT_IN_DB(db, db.in_categoria.codigo)


db.define_table('in_producto',
    Field('id','integer'),
    Field('codigo','string', label=T('Codigo')),
    Field('nombre','string', label=T('Nombre')),
    Field('importe','float',  label=T('Importe'), default=0.00),  
    Field('iva','float',  label=T('I.V.A'), default=0.00),  
    Field('imp1','float',  label=T('Impuesto 1'), default=0.00),  
    Field('imp2','float',  label=T('Impuesto 2'), default=0.00),  
    Field('descuento','float', label=T('Descuento'), default=0.00),
    Field('costo','float', label=T('Costo'), default=0.00),
    Field('comision','float', label=T('Comision'), default=0.00),
    Field('inventario','string',requires=IS_IN_SET(['S', 'N']),default="N" ,label=T('Inventario?')),
    Field('show_in_menu','boolean', label=T('Mostrar en menu')),
    Field('ruta_foto','upload',autodelete=True, label=T('Imagen')), 
    Field('categoria_id','integer', requires=IS_IN_DB(db, db.in_categoria, '%(codigo)s - %(nombre)s')),  
    format='%(codigo)s - %(nombre)s'
    )   
db.in_producto.codigo.requires=IS_NOT_IN_DB(db, db.in_producto.codigo)

#tipos
#IInicial, Ventas, Compras, Movmiento Manuales
#Con una cada linea de factura guardada un movimiento aqui
#Con cada compra otra linea aca 
db.define_table('in_mov',
    Field('id','integer'),  
    Field('fecha','date', label=T('Fecha')),        
    Field('registro','datetime', label=T('Registro')),        
    Field('tipo','string',requires=IS_IN_SET(['I', 'V', 'C','M']),label=T('Tipo Mov.')),
    Field('documento','string', label=T('Nro.Doc.')),
    Field('descripcion','string', label=T('Descripcion')),
    Field('entrada','integer', label=T('Entrada')),  
    Field('costo','float',  label=T('Costo'), default=0.00),  
    Field('salida','integer', label=T('Salida')),  
    Field('precio','float',  label=T('Precio'), default=0.00),  
    Field('producto_id','integer', requires=IS_IN_DB(db, db.in_producto, '%(codigo)s - %(nombre)s')),          
    Field('usuario_id','integer', requires=IS_IN_DB(db, db.cf_persona, '%(nombres)s - %(apellidos)s')),  
    format='%(fecha)s',
    )

#Susbsistema caja
#--------

db.define_table('mv_caja',
    Field('id','integer'),  
    Field('fecha','date', label=T('Fecha')),
    Field('apertura','datetime', label=T('Apertura')),
    Field('cierre','datetime', label=T('Cierre')),
    Field('descripcion','string', label=T('Descripcion')),
    Field('monto_apertura','float',  label=T('Monto Apertura'), default=0.00),  
    Field('monto_cierre','float',  label=T('Monto Cierre'), default=0.00),      
    Field('usuario_id','integer', requires=IS_IN_DB(db, db.cf_persona, '%(nombres)s - %(apellidos)s')),  
    format='%(fecha)s',
    )

db.define_table('mv_caja_det',
    Field('id','integer'),  
    Field('fecha','datetime', label=T('Fecha')),    
    Field('concepto','string', label=T('Concepto')),          
    Field('entrada','float',  label=T('Entrada'), default=0.00),  
    Field('salida','float',  label=T('Salida'), default=0.00),  
    Field('mv_caja_id','integer', requires=IS_IN_DB(db, db.mv_caja, '%(fecha)s')),      
    Field('usuario_id','integer', requires=IS_IN_DB(db, db.cf_persona, '%(nombres)s - %(apellidos)s')),  
    format='%(fecha)s',
    )


#Susbsistema facturas
#--------
#--------
db.define_table('fc_factura',
    Field('id','integer'),
    Field('codigo','string',label=T('Codigo')),
    Field('fecha','date',label=T('Fecha')),
    Field('nota','string',label=T('Nota')),    
    Field('referencia','string',label=T('Referencia')),   #referencia a facturas o presupuestos o notas de la misma tables
    Field('iva','float',default=0.00,label=T('I.V.A')),
    Field('descuento','float',default=0.00,label=T('Descuento')),
    Field('recargo','float',default=0.00,label=T('Recargo')),
    Field('estado','integer', default=0,label=T('Estado')), #status  0 creada, 1 cobrada 
    Field('cliente_id','integer', requires=IS_IN_DB(db, db.cf_cliente, '%(nombre)s')),
    Field('usuario_id','integer', requires=IS_IN_DB(db, db.cf_persona, '%(nombres)s - %(apellidos)s')),  
    )


db.define_table('fc_factura_det',
    Field('id','integer'),
    Field('descripcion','string',label=T('Descripcion')),
    Field('cantidad','integer',default=0,label=T('Cantidad')),
    Field('importe','float',default=0.00,label=T('Importe')),    
    Field('impuesto','float',default=0.00,label=T('Impuesto')),    
    Field('total','float',default=0.00,label=T('Total')),    
    Field('comision','float',default=0.00,label=T('Comision')),    
    Field('factura_id','integer'),
    Field('producto_id','integer'),
    Field('persona_id','integer'), #para pago de comisiones, una persona la puede atender varios especialistas
    )


#Susbsistema cobros
#--------
db.define_table('fc_forma_pago',
    Field('id','integer'),  
    Field('codigo','string', label=T('Codigo')),
    Field('nombre','string', label=T('Nombre')),format='%(nombre)s',
    )


#--------
db.define_table('fc_cobro_det',
    Field('id','integer'),
    Field('fecha','date', label=T('Fecha')),
    Field('registro','datetime', label=T('Registro')),
    Field('referencia','string', label=T('Referencia')),   
    Field('monto','float', label=T('Monto'), default=0.00),
    Field('descripcion','string', label=T('Descripcion')),  
    Field('forma_pago_id','integer',requires=IS_IN_DB(db, db.fc_forma_pago, '%(codigo)s - %(nombre)s')),
    Field('factura_id','integer',requires=IS_IN_DB(db, db.fc_factura, '%(codigo)s')),    
    Field('usuario_id','integer', requires=IS_IN_DB(db, db.cf_persona, '%(nombres)s - %(apellidos)s')),  
    )


class Factura:
    def __init__(self):
        self.fact='fc_factura'    
        self.det='fc_factura_det'    

    def insertar_fact(self,nota,referencia,descuento,recargo,cliente,personaid,prodid,fact_id=None):
        if fact_id == None:
            row=db[self.fact].insert(fecha=datetime.datetime.now().date(),
                            nota=nota,
                            referencia=referencia,
                            descuento=descuento,
                            iva=settings.impuesto,
                            recargo=recargo,
                            cliente_id=cliente,                            
                            usuario_id=session.auth.user.id
                            )
            if row:
                rowdet=self.insertar_det(row,prodid,personaid)
                if rowdet:
                    return row
                else:
                    return 0
            else:
                return 0
        else:
            rowdet=self.insertar_det(fact_id,prodid,personaid)
            if rowdet:
                return rowdet
            else:
                return 0
                                    

    def insertar_det(self,facid,prodid,perid):
        rowprod=self.get_prod_data(prodid)
        rowper=self.get_person_data(perid)
        
        if rowprod:
            importe=rowprod[0].importe
            desc=rowprod[0].nombre
            impuesto=importe*(settings.impuesto/100)
            total=importe+impuesto
            if rowprod[0].inventario=='S':
                comision=0.00
            else:
                comision=importe*(rowper[0].comision/100)
            row=db[self.det].insert(cantidad=1,
                            factura_id=facid,
                            persona_id=perid,
                            producto_id=prodid,
                            importe=importe,
                            impuesto=impuesto,
                            total=total,
                            comision=comision,
                            descripcion=desc
                            )
            if row:
                if rowprod[0].inventario=='S':     #solo si el producto es marcado como inventariable
                    rw=self.sale_inv(prodid,"Salida por venta Factura id: %s" % facid,rowprod.importe)

            return row            

    #si eliminas la factura doy por sentado que se eliminan las lineas
    #y hace resverso de todas las lineas contra el inventario
    #por eso hay que llamar  eliminar det tantas lineas como tenga
    #
    #VERIFICAR que no tenga cobros la factura para poder borrarla
    #
    def eliminar_fact(self,factid):        

        #selecta para ver si no tiene estatus 1 cobrada
        row3=db( (db[self.fact].id == factid) & (db[self.fact].estado == 0) ).select()
        if row3:
            row3=db(db[self.det].factura_id == factid).select()
            for row in row3:
                self.eliminar_det(row.id)
            row2=db(db[self.fact].id == factid).delete()

        return row2
        
    #Soolo elimino la linea solicitada
    def eliminar_det(self,detid):
        rw=db(db[self.det].id == detid).select()
        row=db(db[self.det].id == detid).delete()
        facid=rw[0].factura_id
        prodid=rw[0].producto_id
        costo=rw[0].importe
        rowprod=self.get_prod_data(prodid)

        if row:
            if rowprod[0].inventario=='S': #solo si el producto es marcado como inventariable
                rw=self.entra_inv(prodid,costo,"Entrada por reverso de linea de factura id: %s" % facid)
            return row
        
    def entra_inv(self,prodid,costo,desc):        #con cada borrado de linea de factura por ejemplo
        inv=Inventario()
        row=inv.insertar("RV",prodid,"",desc,Costo=costo,Cant_Entra=1)      #RV reverso de venta
        return row

    def sale_inv(self,prodid,desc,precio):         #con cada venta o linea de factura por ejemplo
        inv=Inventario()
        row=inv.insertar("V",prodid,"",desc,Cant_Sale=1,Precio=precio)      #RV reverso de venta
        return row
    
    def get_prod_data(self,prodid):
        row=db(db.in_producto.id == prodid).select()        
        return row
    
    def get_person_data(self,perid):
        row=db(db.cf_persona.id == perid).select()
        return row

    def get_head(self,fact_id):        
        row=db( (db.fc_factura.id == fact_id) & (db.fc_factura.cliente_id == db.cf_cliente.id) ).select()
        
        return row[0]


    def get_lines(self,fact_id):
        row=db( (db.fc_factura_det.factura_id==fact_id) & (db.fc_factura_det.producto_id == db.in_producto.id) ).select()

        return row


class Inventario:

    def __init__(self):
        self.tabla='in_mov'

    def insertar(self,Tipo,Producto,Documento,Descripcion,Cant_Entra=0,Costo=0.00,Cant_Sale=0,Precio=0.00):
        row=db[self.tabla].insert(fecha=datetime.datetime.now().date(),
                            registro=datetime.datetime.now(),
                            tipo=Tipo,
                            producto_id=Producto,
                            documento=Documento,
                            descripcion=Descripcion,
                            entrada=Cant_Entra,
                            costo=Costo,
                            salida=Cant_Sale,
                            precio=Precio,
                            usuario_id=session.auth.user.id
                                    )

        return row

    def eliminar(self,id):
        row=db(db[self.tabla].id == id).delete()
        return row



class Cliente:

    def __init__(self):
        self.tabla='cf_cliente'

    def quick_insert(self,rif,nombre,juridico=0):
        row=db[self.tabla].insert(nombre=nombre,
                            rif=rif,
                            juridico=juridico                            
                                    )

        return row

    def eliminar(self,id):
        row=db(db[self.tabla].id == id).delete()
        return row

class Cobro:
    
    def __init__(self):
        self.tabla='fc_cobro_det'

    def insert(self,formpago,factura,monto,referencia="",descripcion=""):
        
        if request.cookies.has_key('caja_id'):
            row=db[self.tabla].insert(registro=datetime.datetime.now(),
                            fecha=datetime.datetime.now().date(),                   
                            referencia=referencia,
                            monto=float(monto),
                            descripcion=descripcion,
                            forma_pago_id=formpago,
                            factura_id=factura,                            
                            usuario_id=session.auth.user.id)            
            if row:
                rc=db(db.fc_forma_pago.id == formpago).select()
                if rc:
                    if rc[0].nombre in "EFECTIVO,efectivo,Efectivo":
                        rw=self.insert_caja(monto,descripcion,factura)
            
            return row

    def delete(self,id):
        rc=db(db[self.tabla].id == id).select()
        row=db(db[self.tabla].id == id).delete()        
        if row:
            rc2=db(db.fc_forma_pago.id == rc[0].forma_pago_id).select()
            if rc2:
                if rc2[0].nombre in "EFECTIVO,efectivo,Efectivo":
                    rw=self.insert_caja(rc[0].monto,"Reverso de de pago en efectivo","")

        return row

    def insert_caja(self,monto,referencia,factura):
        #ukltima caja abierta, debe haber una        
        if request.cookies.has_key('caja_id'):
            elid=request.cookies['caja_id'].value
            #print "caja",request.cookies['caja_id'].value
            if elid:
                rc2=db.mv_caja_det.insert(fecha=datetime.datetime.now(),
                            concepto=referencia,
                            entrada=monto,                
                            mv_caja_id=elid,
                            usuario_id=session.auth.user.id)        
        
        return rc2










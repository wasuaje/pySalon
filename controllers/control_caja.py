# -*- coding: utf-8 -*-
### required - do no delete
import json
import math 
import datetime

def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call(): return service()
### end requires
@auth.requires_login()
def index():	
	#response.cookies['caja_id'] = None
	#response.cookies['caja_id']['expires'] = -10000
	#response.cookies['caja_id']['path'] = '/'
	#print response.cookies['caja_id']
	if request.cookies.has_key('caja_id'):
		msg="ya hay una caja abierta!"		
		wrt=False			
		form=FORM()
	else:
		msg="no hay una caja abierta"
		exito=2
		wrt=True
		#master form para apertura cierre	
		form = SQLFORM.factory(							
        	Field('Fecha_Caja', type='date',requires=IS_NOT_EMPTY(),writable=wrt),
        	Field('Monto_Apertura', type='float',default='0.00',writable=wrt),        					
        	formstyle='bootstrap')
	
	if request.vars.exito!=None:
		exito=int(request.vars.exito)
	else:
		exito=2
	
	if form.process(onvalidation=apertura_validate).accepted:			
		#aunque exito viene del redirect del onvalidate
		exito=1					
	elif form.errors:
		exito=0
	
	#si la respuesta que viene desde validate es exito o no
	#no me traigo el mensaje de error desde validate porque
	#sal en la barra de url como paremetro se ve feo
	if exito==1:
		msg="Caja abierta exitosamente"
	elif exito==0:
		msg="Error la caja ya esta abierta"	

	return dict(exito=exito,form=form,msg=msg)

def apertura_validate(form):
	tabla='mv_caja'
	tabla2='mv_caja_det'
	#primero valido que no exista la caja
	dt_str = form.vars.Fecha_Caja
	
	dt_obj = datetime.datetime.strptime(dt_str, '%d/%m/%Y')
	rw=db( db[tabla].fecha == dt_obj ).select().first()
	
	if rw:
		redirect(URL('control_caja','index',vars=dict(exito=0)))
	else:
		#despues que se inserte todo ok
		record=db[tabla].insert(fecha=dt_obj,
									apertura=datetime.datetime.now(),
									monto_apertura=form.vars.Monto_Apertura,
									descripcion='Movimiento inicial de Apertura de caja',									
									usuario_id=session.auth.user.id)
		if record>0:
			record2=db[tabla2].insert(fecha=datetime.datetime.now(),
									concepto='Movimiento de Apertura de caja',
									entrada=form.vars.Monto_Apertura,
									mv_caja_id=record,
									usuario_id=session.auth.user.id
									)
			if record2:							
				response.cookies['caja_id'] = record
				response.cookies['caja_id']['expires'] = 24 * 3600
				response.cookies['caja_id']['path'] = '/'				
				redirect(URL('control_caja','index',vars=dict(exito=1)))								
			else:			
				redirect(URL('control_caja','index',vars=dict(exito=0)))

#esta funcion se llama desde ajax en control_caja.html
def get_monto_apertura():
	#caja_fecha=request.args[0]
	#dt_str = caja_fecha
	#dt_obj = datetime.datetime.strptime(dt_str, '%d/%m/%Y')
	tabla='mv_caja'
	tabla2='mv_caja_det'
	#
	#traigo el monto de cierre de la ultima caja cerrada para ese caja id
	#
	rw=db( (db[tabla].cierre != None) ).select(orderby=~db[tabla].fecha).first()
	if rw:
		#print rw.fecha,rw.monto_apertura,rw.monto_cierre
		valor=rw.monto_cierre
	else:
		valor=0.00
	#print db._lastsql
	return valor


def cierre():
	
	msg=""
	if request.vars.exito!=None:
		exito=int(request.vars.exito)
	else:
		exito=2	

	form = SQLFORM.factory(			
    		Field('Fecha_Caja', type='date',requires=IS_NOT_EMPTY()),        					
    		formstyle='bootstrap')
	
	if form.process(onvalidation=cierre_prevalidate).accepted:			
		#aunque exito viene del redirect del onvalidate
		exito=1					
	elif form.errors:
		exito=0
	#con esta busco los detalles
	if exito==0:		
		msg="Error la caja para esa fecha no existe"		

	return dict(exito=exito,form=form,msg=msg)	

def cierre_prevalidate(form):
	tabla='mv_caja'
	tabla2='mv_caja_det'
	#primero valido que no exista la caja
	dt_str = form.vars.Fecha_Caja
	dt_obj = datetime.datetime.strptime(dt_str, '%d/%m/%Y')
	rw=db( (db[tabla].fecha == dt_obj) & (db[tabla].cierre == None ) ).select().first()
	#print db._lastsql
	if rw:
		redirect(URL('control_caja','cierre_fin',vars=dict(mov_id=rw.id)))
	else:
		redirect(URL('control_caja','cierre',vars=dict(exito=0)))

def cierre_fin():
	tabla='mv_caja'
	tabla2='mv_caja_det'	
	msg=""
	url=""
	if request.vars.exito!=None:
		exito=int(request.vars.exito)
	else:
		exito=2	

	#print request.vars.mov_id,type(request.vars.mov_id)
	mov_id=request.vars.mov_id
	
	#print rw
	#ahora tengo que busca las entradas y salidas de este mov_id en mv_caja_detalle
	rw=db( db[tabla2].mv_caja_id == mov_id ).select()
	entradas=0.00
	salidas=0.00
	for rec in rw:
		entradas+=rec.entrada
		salidas+=rec.salida

	rw=db( db[tabla].id == mov_id ).select().first()
	if rw:
		form = SQLFORM.factory(			
        	Field('Fecha_Caja', type='date',requires=IS_NOT_EMPTY(), default=rw.fecha ),
        	Field('Monto_Apertura', type='float',default=rw.monto_apertura, writable=False),
        	Field('Entradas', type='float',default=entradas, writable=False),
        	Field('Salidas', type='float',default=salidas, writable=False),
        	Field('Monto_Retiro', type='float',default=0.00),
        	Field('Monto_Cierre', type='float',default=entradas-salidas, writable=False),
        	hidden=dict(mv_id=mov_id,monto_cierre=entradas-salidas,entradas=entradas,salidas=salidas),      	
        	formstyle='bootstrap')		
		if form.process(onvalidation=cierre_finvalidate).accepted:			
		#aunque exito viene del redirect del onvalidate
			exito=1					
		elif form.errors:
			exito=0

	if exito==0:		
		msg="Ha ocurido un error, la caja ya esta cerrada!"
	elif exito==1:
		msg="Caja cerrada exitosamente"
		#olvido las variables de sesion de caja
		response.cookies['caja_id'] = None
		response.cookies['caja_id']['expires'] = -10000
		response.cookies['caja_id']['path'] = '/'			
		
	url=URL('mov_caja','imprimir',vars=dict(mv_id=mov_id))

	#con esta busco los detalles
	return dict(exito=exito,form=form,msg=msg,url=url)	

def cierre_finvalidate(form):	
	#Recibo los datos	
	mov_id=request.vars.mv_id
	monto_cierre=request.vars.monto_cierre
	monto_retiro=request.vars.Monto_Retiro
	descripcion="Caja Cerrada."
	tabla='mv_caja'
	tabla2='mv_caja_det'	
	msg=""
	#valido que la caja no haya sido ya cerrada y evitar duplicidad de registros
	#entonces selecciono la caja id respectiva y que este abierta, si esta cerrada
	# ya no puedo proseguir
	rw=db( (db[tabla].id == mov_id) & (db[tabla].cierre == None ) ).select().first()
	if rw:
		#actualizo el registro mov_id con monto cierre, fecha_cierre=now, descripcion
		row= db(db[tabla].id == mov_id).update(descripcion=descripcion, monto_cierre=monto_cierre,cierre=datetime.datetime.now())
		
		#inserto movimiento de salida por el monto del retiro
		if row > 0:
			record2=db[tabla2].insert(fecha=datetime.datetime.now(),
									concepto='Movimiento de Cierre de caja (retiro para deposito)',
									salida=monto_retiro,
									mv_caja_id=mov_id,
									usuario_id=session.auth.user.id
										)
			#si todo esta ok redirijo a movimientos de caja con este mv_id
			if record2>0:
				redirect(URL('control_caja','cierre_fin',vars=dict(exito=1,mov_id=mov_id)))
			else:				
				redirect(URL('control_caja','cierre_fin',vars=dict(exito=0,mov_id=mov_id)))
	else:
		redirect(URL('control_caja','cierre_fin',vars=dict(exito=0,mov_id=mov_id)))	
	#sino vuelvo a cierre_fin con mensage de error


def error():
    return dict()

def imprimir():
# Let's import the wrapper
	import os
	import pdf
	from pdf.theme import colors, DefaultTheme

	# and define a constant
	TABLE_WIDTH = 540 # this you cannot do in rLab which is why I wrote the helper initially

    # then let's extend the Default theme. I need more space so I redefine the margins
    # also I don't want tables, etc to break across pages (allowSplitting = False)
    # see http://www.reportlab.com/docs/reportlab-userguide.pdf
	class MyTheme(DefaultTheme):
		doc = {
            'leftMargin': 25,
            'rightMargin': 25,
            'topMargin': 20,
            'bottomMargin': 25,
            'allowSplitting': False
            }
            
    # let's create the doc and specify title and author
	doc = pdf.Pdf('Listado de Cajas', 'wuelfhis asuaje')

    # now we apply our theme
	doc.set_theme(MyTheme)

    # time to add the logo at the top right
	#logo_path = os.path.join(request.folder,'static/images','facebook.png')   
	#doc.add_image(logo_path, 67, 67, pdf.LEFT)
	logo=pdf.Image(os.path.join(request.folder,'static/images','facebook.png')   )
	address = pdf.Paragraph("<para align=left> We are please%s </para>" % "Hola",MyTheme.paragraph)
	LIST_STYLE = [(
			'LINEABOVE', (0,0), (-1,0), 2, colors.grey),
			('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
			('LINEBELOW', (0,0), (-1,-1), 2, colors.grey),
			('ALIGN', (0,0), (0,0),'LEFT'),			
			
			]
			
	
	doc.add(pdf.Table([[logo,address,"","","",""]],style=LIST_STYLE ))

    # give me some space
	doc.add_spacer()
    
    # this header defaults to H1
	doc.add_header('Listado de cajas')

    # here's how to add a paragraph
	#doc.add_paragraph("We are pleased to confirm your reservation with ...")
	doc.add_spacer()	

	# let's move on to the divers table

	diver_table = [['Id', 'Codigo', 'Nombre']] # this is the header row 

	for row in db(db.cf_caja.id>0).select() :   
		diver_table.append([row.id, row.codigo, row.nombre]) # these are the other rows

	doc.add_table(diver_table, TABLE_WIDTH)
	
	response.headers['Content-Type']='application/pdf'
	
	return doc.render()
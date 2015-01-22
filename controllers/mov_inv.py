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
	tabla='in_mov'	
	msg="Cargando..."
	url=""
	if request.vars.exito!=None:
		exito=int(request.vars.exito)
	else:
		exito=3
	if exito==1:
		msg="Movimiento insertado correctamente !"
	elif exito==0:
		msg="No se inserto movimiento!"
	elif exito==2:
		msg="Registro eliminado con exito!"
		
	#seleccion data de caja abierta	
	url=URL('mov_inv','imprimir')
	#mv_id=rw.id	
	qryprod=db(db.in_producto.inventario == 'S' ).select()
	vals=[]
	lbls=[]
	for i in qryprod:
		vals.append(i.id)
		lbls.append(i.codigo+' - '+i.nombre)
	#print db._lastsql
	#form con concepto
	form = SQLFORM.factory(						
				Field('Tipo','string',requires=IS_IN_SET(['I','M']),label=T('Tipo Mov.')),	
				Field('Producto','integer',requires=IS_IN_SET(vals, lbls ),label=T('Producto')),	
				Field('Documento', type='string',requires=IS_NOT_EMPTY()),
        		Field('Descripcion', type='string',requires=IS_NOT_EMPTY()),
        		Field('Cant_Entra', type='integer',default='0', requires=IS_NOT_EMPTY()),
        		Field('Costo', type='string',default='0.00',requires=IS_NOT_EMPTY()),
        		Field('Cant_Sale', type='integer',default='0', requires=IS_NOT_EMPTY()),
        		Field('Precio', type='string',default='0.00',requires=IS_NOT_EMPTY()),
        		formstyle='table3cols')
	if form.process(onvalidation=validate).accepted:			
	#aunque exito viene del redirect del onvalidate este es para que no de errror
		exito=1					
	elif form.errors:
		exito=0

	hoy=datetime.datetime.now().date()
	#row=db( db.in_mov.fecha == hoy ).select('id','fecha','tipo','documento','descripcion','entrada','salida')	
	row=db( (db.in_mov.fecha == hoy) & (db.in_mov.producto_id == db.in_producto.id) & (db.in_mov.usuario_id == db.auth_user.id) ).select()
	#print db._lastsql
	#print row
	entradas=0.00
	salidas=0.00
	totales=0.00
	for x in row:
		entradas+=x.in_mov.entrada
		salidas+=x.in_mov.salida
	totales=entradas-salidas
	#print entradas,salidas,totales

	prueba="""
	<table id="mitabla" style=".selected{color:red;}" class="table table-striped table-bordered table-hover" cellspacing="0" width="100%">
        <thead>
            <tr>            	
            	<th>Id</th> 
            	<th>Producto</th>   
                <th>Documento</th>   
                <th>Concepto</th>   
                <th>Entrada</th>            
                <th>Salida</th>                
            </tr>
        </thead>
        <tfoot>
            <tr>
            	<th></th>                
            	<th></th>   
                <th></th> 
                <th></th>      
                <th>_E_</th>                
                <th>_S_</th>
            </tr>
            <tr>
            	<th></th>   
            	<th></th>                
            	<th></th>                
                <th>Totales</th>                
                <th></th>                
                <th>_T_</th>
            </tr>
        </tfoot>
        <tbody>
        """ 
	prueba=prueba.replace('_E_',str(entradas))
	prueba=prueba.replace('_S_',str(salidas))
	prueba=prueba.replace('_T_',str(totales))		
		

	lista=["<tr><td>"+str(row.in_mov.id)+"</td>"+\
			"<td>"+row.in_producto.nombre+"</td>"+\
			"<td>"+row.in_mov.documento+"</td>"+\
			"<td>"+row.in_mov.descripcion+"</td>"+\
			"<td>"+str(row.in_mov.entrada)+"</td>"+\
			"<td>"+str(row.in_mov.salida)+"</td>"+\
			"</tr>" for row in row] 	
	prueba+="".join(lista)
	prueba+="</tbody></table>"

	        	
	if len(prueba)>0:
		mytabla=XML(prueba)
	else:		
		mytabla=T("No existen registros")


	return dict(mytabla=mytabla,exito=exito,msg=msg,form=form,url=url)

def validate(form):

	Tipo=form.vars.Tipo
	Producto=form.vars.Producto
	Documento=form.vars.Documento
	Descripcion=form.vars.Descripcion
	Cant_Entra=form.vars.Cant_Entra
	Costo=form.vars.Costo
	Cant_Sale=form.vars.Cant_Sale
	Precio=form.vars.Precio

	inv=Inventario()
	record2=inv.insertar(Tipo,Producto,Documento,Descripcion,Cant_Entra,Costo,Cant_Sale,Precio)	
	
	if record2:			
		redirect(URL('mov_inv','index',vars=dict(exito=1)))	
	else:			
		redirect(URL('mov_inv','index',vars=dict(exito=0)))


def eliminar():
	if len(request.args) > 0:
		id = request.args[0]
		a=Inventario()
		row=a.eliminar(id)		
		if row:					
			redirect(URL('mov_inv','index',vars=dict(exito=2) ) ) 
		elif row==None:			
			redirect(URL('mov_inv','index',vars=dict(exito=2) ) ) 
	return



def error():
    return dict()

def imprimir():
# Let's import the wrapper
	import os
	import pdf
	from pdf.theme import colors, DefaultTheme

	mov_id=request.vars.mv_id
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
	doc = pdf.Pdf('Caja a la fecha:', 'wuelfhis asuaje')

    # now we apply our theme
	doc.set_theme(MyTheme)

    # time to add the logo at the top right
	#logo_path = os.path.join(request.folder,'static/images','facebook.png')   
	#doc.add_image(logo_path, 67, 67, pdf.LEFT)
	logo=pdf.Image(os.path.join(request.folder,'static/images','facebook.png')   )
	address = pdf.Paragraph("<para align=left> %s </para>" % settings.title,MyTheme.paragraph)
	address2 = pdf.Paragraph("<para align=left>%s </para>" % settings.subtitle,MyTheme.paragraph)
	LIST_STYLE = [(
			'LINEABOVE', (0,0), (-1,0), 2, colors.grey),
			('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
			('LINEBELOW', (0,0), (-1,-1), 2, colors.grey),
			('LEFTPADDING', (0,0), (-1,-1), 0),  
        	('RIGHTPADDING', (0,0), (-1,-1), 0),
			('ALIGN', (0,0), (0,0),'LEFT'),
			('COLWIDTH', (0,0), (0,0),10),
			('ALIGN', (-1,-1), (-1,0),'RIGHT'),
			]
		
	HEAD_STYLE = [
	 	('ALIGN', (0,0), (-1,-1),'CENTER'),
	]
	
	tablelogo=pdf.Table([[logo,[address,address2]]],style=LIST_STYLE )
	tablelogo._argW[0]=40
	doc.add(tablelogo)
	
    # give me some space
	doc.add_spacer()
    
    # this header defaults to H1
	hoy=datetime.datetime.now().date()	
		
	titulo = pdf.Paragraph("<para align=center> <b>Movimientos de Inventario al %s </b></para>" % hoy,MyTheme.paragraph)	
	tableheader=pdf.Table([[titulo]],style=HEAD_STYLE )
	doc.add(tableheader)
	#doc.add_header( "al: %s" % rx.fecha)

    # here's how to add a paragraph
	#doc.add_paragraph("We are pleased to confirm your reservation with ...")
	doc.add_spacer()	

	# let's move on to the divers table

	diver_table = [['Producto','Documento' ,'Concepto','Cnt.Ent','Costo','Cnt.Sal','Precio','Usuario']] # this is the header row 
	entradas=0
	salidas=0
	costo=0.00
	precio=0.00
	total=0.00
	row=db( (db.in_mov.fecha == hoy) & (db.in_mov.producto_id == db.in_producto.id) & (db.in_mov.usuario_id == db.auth_user.id) ).select()
	for row in row:   
		diver_table.append([row.in_producto.nombre, row.in_mov.documento, row.in_mov.descripcion, row.in_mov.entrada,row.in_mov.costo,row.in_mov.salida,row.in_mov.precio,row.auth_user.first_name+' '+row.auth_user.last_name]) # these are the other rows
		entradas+=row.in_mov.entrada
		salidas+=row.in_mov.entrada
		costo+=row.in_mov.costo
		precio+=row.in_mov.precio
	total=entradas-salidas
	diver_table.append(["", "","",""])
	diver_table.append(['Totales', "","",entradas, costo,salidas,precio])
	diver_table.append(['General', "","",total,""])

	
	doc.add_table(diver_table, TABLE_WIDTH)
	
	response.headers['Content-Type']='application/pdf'
	
	return doc.render()
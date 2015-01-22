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
	tabla='mv_caja_det'
	tabla2='mv_caja'
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
	rw=db( (db[tabla2].cierre == None ) ).select().first()
	#print db._lastsql
	if rw:
		url=URL('mov_caja','imprimir',vars=dict(mv_id=rw.id))
		mv_id=rw.id
		row=db(db[tabla].mv_caja_id == mv_id).select()
		#form con concepto
		form = SQLFORM.factory(							
	        		Field('Concepto', type='string',length='200',requires=IS_NOT_EMPTY()),
	        		Field('Entrada', type='string',default='0.00', requires=IS_NOT_EMPTY()),
	        		Field('Salida', type='string',default='0.00',requires=IS_NOT_EMPTY()),
	        		hidden=dict(elid=rw.id),
	        		formstyle='bootstrap')
		if form.process(onvalidation=validate).accepted:			
		#aunque exito viene del redirect del onvalidate este es para que no de errror
			exito=1					
		elif form.errors:
			exito=0

		entradas=0.00
		salidas=0.00
		totales=0.00
		for x in row:
			entradas+=x.entrada
			salidas+=x.salida
		totales=entradas-salidas
		#print entradas,salidas,totales

		prueba="""
		<table id="mitabla" style=".selected{color:red;}" class="table table-striped table-bordered table-hover" cellspacing="0" width="100%">
	        <thead>
	            <tr>
	            	<th>Id</th>                
	                <th>Concepto</th>                
	                <th>Entrada</th>            
	                <th>Salida</th>                
	            </tr>
	        </thead>
	        <tfoot>
	            <tr>
	            	<th></th>                
	                <th></th>                
	                <th>_E_</th>                
	                <th>_S_</th>
	            </tr>
	            <tr>
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
		

		lista=["<tr><td>"+str(row.id)+"</td>"+\
				"<td>"+row.concepto+"</td>"+\
				"<td>"+str(row.entrada)+"</td>"+\
				"<td>"+str(row.salida)+"</td>"+\
				"</tr>" for row in row] 	
		prueba+="".join(lista)
		prueba+="</tbody></table>"

	        	
		if len(prueba)>0:
			mytabla=XML(prueba)
		else:		
			mytabla=T("No existen registros")
	else:
		msg="No hay una caja abierta !"
		exito=0
		mytabla=T("No existen registros")
		form=""

	return dict(mytabla=mytabla,exito=exito,msg=msg,form=form,url=url)

def validate(form):
	tabla='mv_caja_det'
	#print form.vars
	elid=request.vars.elid
	record2=db[tabla].insert(fecha=datetime.datetime.now(),
							concepto=form.vars.Concepto,
							entrada=form.vars.Entrada,
							salida=form.vars.Salida,
							mv_caja_id=elid,
							usuario_id=session.auth.user.id
									)
	#print db._lastsql
	if record2:			
		redirect(URL('mov_caja','index',vars=dict(exito=1)))	
	else:			
		redirect(URL('mov_caja','index',vars=dict(exito=0)))



def eliminar():
	tabla='mv_caja_det'
	if len(request.args) > 0:
		id = request.args[0]
		row=db(db[tabla].id == id).delete()		
		if row:					
			redirect(URL('mov_caja','index',vars=dict(exito=2) ) ) 
		elif row==None:			
			redirect(URL('mov_caja','index',vars=dict(exito=2) ) ) 
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
	rx = db(db.mv_caja.id==mov_id).select().first()	
	titulo = pdf.Paragraph("<para align=center> <b>Movimientos de Caja al %s </b></para>" % rx.fecha,MyTheme.paragraph)	
	tableheader=pdf.Table([[titulo]],style=HEAD_STYLE )
	doc.add(tableheader)
	#doc.add_header( "al: %s" % rx.fecha)

    # here's how to add a paragraph
	#doc.add_paragraph("We are pleased to confirm your reservation with ...")
	doc.add_spacer()	

	# let's move on to the divers table

	diver_table = [['Fecha', 'Concepto', 'Entradas','Salidas','Usuario']] # this is the header row 
	entradas=0.00
	salidas=0.00
	total=0.00
	for row in db(db.mv_caja_det.mv_caja_id==mov_id).select() :   
		diver_table.append([row.fecha, row.concepto, row.entrada, row.salida,row.usuario_id]) # these are the other rows
		entradas+=row.entrada
		salidas+=row.salida
	total=entradas-salidas
	diver_table.append(["", "","",""])
	diver_table.append(['Totales', "",entradas, salidas])
	diver_table.append(['General', "",total,""])

	
	doc.add_table(diver_table, TABLE_WIDTH)
	
	response.headers['Content-Type']='application/pdf'
	
	return doc.render()
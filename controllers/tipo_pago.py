# -*- coding: utf-8 -*-
### required - do no delete
import json
import math 

def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call(): return service()
### end requires
@auth.requires_login()
def index():	
	tabla='fc_forma_pago'
	row=db(db[tabla].id > 0).select()
	exito=request.vars.exito	
	prueba="""
	<table id="mitabla" style=".selected{color:red;}" class="table table-striped table-bordered table-hover" cellspacing="0" width="100%">
        <thead>
            <tr>
            	<th>Id</th>
                <th>Codigo</th>
                <th>Nombre</th>                
            </tr>
        </thead>
        <tfoot>
            <tr>
            	<th>Id</th>
                <th>Codigo</th>
                <th>Nombre</th>                
            </tr>
        </tfoot>
 
        <tbody>
        """
	lista=["<tr><td>"+str(row.id)+"</td><td>"+row.codigo+"</td><td>"+row.nombre+"</td></tr>" for row in row] 	
	prueba+="".join(lista)
	prueba+="</tbody></table>"

        	
	if len(prueba)>0:
		mytabla=XML(prueba)
	else:		
		mytabla=T("No existen registros")

	return dict(mytabla=mytabla,exito=exito)

def handle():
	exito=request.vars.exito	
	tabla='fc_forma_pago'	
	if len(request.args) > 0:
		id = request.args[0]
		row=db(db[tabla].id == id).select().first()
		registro=row.id
	else:
		registro = 0
	form = SQLFORM(db[tabla], registro, deletable=True,  submit_button='Enviar' ,    delete_label='Click para borrar:',  next=URL(c='tipo_pago',  f='handle'), \
			message=T("Operacion Exitosa !"),  upload=URL('download'))	
	if form.accepts(request.vars, session):			
			redirect(URL('tipo_pago','index',vars=dict(exito=1) ) ) 
	elif form.errors:			
			exito=0
	return dict(myform=form,exito=exito)	

def eliminar():
	tabla='fc_forma_pago'	
	if len(request.args) > 0:
		id = request.args[0]
		row=db(db[tabla].id == id).delete()		
		if row:					
			redirect(URL('tipo_pago','index',vars=dict(exito=1) ) ) 
		elif row==None:			
			redirect(URL('tipo_pago','index',vars=dict(exito=2) ) ) 
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
	doc = pdf.Pdf('Tipos de Pago:', 'wuelfhis asuaje')

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
	
	titulo = pdf.Paragraph("<para align=center> <b>Tipos de Pago %s</b></para>" % "Registrados",MyTheme.paragraph)	
	tableheader=pdf.Table([[titulo]],style=HEAD_STYLE )
	doc.add(tableheader)
	#doc.add_header( "al: %s" % rx.fecha)

    # here's how to add a paragraph
	#doc.add_paragraph("We are pleased to confirm your reservation with ...")
	doc.add_spacer()	

	# let's move on to the divers table

	diver_table = [['Codigo', 'Nombre']] # this is the header row 
	
	for row in db(db.fc_forma_pago.id>0).select() :   
		diver_table.append([row.codigo, row.nombre]) # these are the other rows		
	
	
	doc.add_table(diver_table, TABLE_WIDTH)
	
	response.headers['Content-Type']='application/pdf'
	
	return doc.render()
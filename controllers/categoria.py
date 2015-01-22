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
	tabla='in_categoria'
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
	tabla='in_categoria'	
	if len(request.args) > 0:
		id = request.args[0]
		row=db(db[tabla].id == id).select().first()
		registro=row.id
	else:
		registro = 0
	form = SQLFORM(db[tabla], registro, deletable=True,  submit_button='Enviar' ,    delete_label='Click para borrar:',  next=URL(c='categoria',  f='handle'), \
			message=T("Operacion Exitosa !"),  upload=URL('download'))	
	if form.accepts(request.vars, session):			
			redirect(URL('categoria','index',vars=dict(exito=1) ) ) 
	elif form.errors:			
			exito=0
	return dict(myform=form,exito=exito)	

def eliminar():
	tabla='in_categoria'	
	if len(request.args) > 0:
		id = request.args[0]
		row=db(db[tabla].id == id).delete()		
		if row:					
			redirect(URL('categoria','index',vars=dict(exito=1) ) ) 
		elif row==None:			
			redirect(URL('categoria','index',vars=dict(exito=2) ) ) 
	return



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
	doc = pdf.Pdf('Categorias de Producto', 'wuelfhis asuaje')

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
	doc.add_header('Categorias de producto')

    # here's how to add a paragraph
	#doc.add_paragraph("We are pleased to confirm your reservation with ...")
	doc.add_spacer()	

	# let's move on to the divers table

	diver_table = [['Id', 'Codigo', 'Nombre']] # this is the header row 

	for row in db(db.in_categoria.id>0).select() :   
		diver_table.append([row.id, row.codigo, row.nombre]) # these are the other rows

	doc.add_table(diver_table, TABLE_WIDTH)
	
	response.headers['Content-Type']='application/pdf'
	
	return doc.render()
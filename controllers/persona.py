# -*- coding: utf-8 -*-
### required - do no delete
import json
import math 

def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call(): return service()
### end requires
def index():	
	tabla='cf_persona'
	row=db(db[tabla].id > 0).select()
	exito=request.vars.exito	
	prueba="""
	<table id="mitabla" style=".selected{color:red;}" class="table table-striped table-bordered table-hover" cellspacing="0" width="100%">
        <thead>
            <tr>
            	<th>Id</th>
                <th>Cedula</th>
                <th>Nombres</th> 
                <th>Apellidos</th> 
                <th>Foto</th> 
            </tr>
        </thead>
        <tfoot>
            <tr>
            	<th>Id</th>
                <th>Cedula</th>
                <th>Nombres</th> 
                <th>Apellidos</th> 
                <th>Foto</th> 
            </tr>
        </tfoot>
 
        <tbody>
        """
        #IMG(_src=URL('uploads',row.ruta_foto))
	lista=["<tr><td>"+str(row.id)+"</td>"\
		   "<td>"+row.cedula+"</td>"\
		   "<td>"+row.nombres+"</td>"\
		   "<td>"+row.apellidos+"</td>"\
		   "<td><img src='%s' width='80', height='80'></td></tr>" % URL('default', 'download',args=row.ruta_foto)\
			for row in row] 	
	
	prueba+="".join(lista)
	prueba+="</tbody></table>"

        	
	if len(prueba)>0:
		mytabla=XML(prueba)
	else:		
		mytabla=T("No existen registros")

	return dict(mytabla=mytabla,exito=exito)

def handle():
	tabla='cf_persona'	
	exito=request.vars.exito	
	if len(request.args) > 0:
		id = request.args[0]
		row=db(db[tabla].id == id).select().first()
		registro=row.id
	else:
		registro = 0
	form = SQLFORM(db[tabla], registro, deletable=True,  submit_button='Enviar' ,    delete_label='Click para borrar:',  next=URL(c='persona',  f='handle'), \
			message=T("Operacion Exitosa !"),  upload=URL('download'))	
	if form.accepts(request.vars, session):			
			redirect(URL('persona','index',vars=dict(exito=1) ) ) 
	elif form.errors:			
			exito=0
			#redirect(URL('persona','index',vars=dict(exito=0) ) ) 

	return dict(myform=form,exito=exito)	

def eliminar():
	tabla='cf_persona'	
	if len(request.args) > 0:
		id = request.args[0]
		row=db(db[tabla].id == id).delete()		
		if row:					
			redirect(URL('persona','index',vars=dict(exito=1) ) ) 
		elif row==None:			
			redirect(URL('persona','index',vars=dict(exito=2) ) ) 
	return



def error():
    return dict()

def imprimir():
# Let's import the wrapper
	import os
	import pdf
	from pdf.theme import colors, DefaultTheme

	# and define a constant
	TABLE_WIDTH = 560 # this you cannot do in rLab which is why I wrote the helper initially

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
	doc = pdf.Pdf('Personal actual', 'wuelfhis asuaje')

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
	doc.add_header('Personal actual')

    # here's how to add a paragraph
	#doc.add_paragraph("We are pleased to confirm your reservation with ...")
	doc.add_spacer()	

	# let's move on to the divers table

	diver_table = [['Id','Cedula', 'Nombres', 'Apellidos', 'Sexo' ,'Tlf. Hab', 'Tlf. Cel.','Email']] # this is the header row 

	for row in db(db.cf_persona.id>0).select() :   
		foto=pdf.Image(os.path.join(request.folder,'uploads',row.ruta_foto)   )
		foto.drawHeight = 10
		foto.drawWidth = 10
		diver_table.append([row.id, row.cedula, row.nombres, row.apellidos, row.sexo,row.tlf_hab, row.tlf_cel, row.email ]) # these are the other rows

	doc.add_table(diver_table, TABLE_WIDTH)
	
	response.headers['Content-Type']='application/pdf'
	
	return doc.render()
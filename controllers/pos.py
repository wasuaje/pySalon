# -*- coding: utf-8 -*-
### required - do no delete
#import json
import math 
try:
    import simplejson as json
except (ImportError,):
    import json

def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call(): return service()
### end requires
@auth.requires_login()
def index():	
	
	#
	#seleccion de tipos de pago
	#
	row=db(db.fc_forma_pago.id > 0).select()
	lis_fp=[]
	for row in row:
		lis_fp.append(XML("<button data-target='#myModal' data-toggle='modal' class='btn btn-outline btn-default' onclick='set_fp(this.id)' id=fp_%s type='button'>%s</button>" % (row.id,row.nombre) ) )	
	lis_fp.append(SPAN("                "))
	lis_fp.append(XML("<button class='btn btn-outline btn-danger btn-xs' onclick='del_cobro();' type='button'>Elimina</button>"))
	#
	#Seleccion de categorias de productos para mostrar
	#
	row=db(db.in_categoria.id > 0).select()
	lis_cat=[]
	for row in row:
		#url=A(row.nombre,_href="#",_onclick="get_productos();")
		lis_cat.append(XML("<button onclick='get_productos(this.id);' class='btn btn-outline btn-default' id=%s type='button'>%s</button>" % (row.id,row.nombre) ) )

	 
	#armo los selects para eleccion de clientes y especialistas
	fld_cliente=SELECT(_id='sel-clientes',*[OPTION(s.nombre, _value=s.id) for s in db(db.cf_cliente).select()])
	fld_persona=SELECT(_id='sel-personas',*[OPTION(s.nombres+', '+s.apellidos, _value=s.id) for s in db(db.cf_persona).select()])
	
	#form para agregar rapidamente clientes nuevos escondidos en un modal
	form_cliente=TABLE(TR("RIF.",INPUT(_id='rif', type="text")),
						TR("Nombre:",INPUT(_id='nom_cliente', type="text")),
						TR("Juridico", SELECT(OPTION('S',_value=1),OPTION('N',_value=0),_id='juridico')),
						)

	prueba="""
	<table id="mitabla2" style=".selected{color:red;}" class="table table-striped table-bordered table-hover" cellspacing="0" width="100%">
        <thead>
            <tr>
            	<th>Id</th>
                <th>Producto</th>
                <th>Importe</th>                
            </tr>
        </thead>         
        <tbody>
        </tbody>
        </table>
        """

	mytabla=XML(prueba)


	return dict(mytabla=mytabla,categorias=DIV(lis_cat),tipos_pago=DIV(lis_fp),fld_cliente=fld_cliente,fld_persona=fld_persona,form_cliente=form_cliente)


def get_productos():	
	id=request.vars.id
	tabla='in_producto'	
	row=db(db[tabla].categoria_id == id).select()
	lis_cat=[]
	for row in row:
		#url=A(row.nombre,_href="#",_onclick="get_productos();")
		lis_cat.append(XML("<button onclick='fact_prod(this.id);' class='btn btn-outline btn-default' id=%s type='button'>%s</button>" % (row.id,row.nombre) ) )

	return DIV(lis_cat)


def get_fact_lines(fact_id):		
	exito=request.vars.exito	
	importe=0.00
	iva=settings.impuesto
	mto_iva=0.00	
	total=0.00
	lista=[]
	#Busco lo cobrado pra la factura	
	sum = db.fc_cobro_det.monto.sum()
	cobrado=db(db.fc_cobro_det.factura_id==fact_id).select(sum).first()[sum]	
	if cobrado==None:
		cobrado=0.00

	prueba="""
	<table id="mitabla" style=".selected{color:red;}" class="table" cellspacing="0" width="100%">
        <thead>
            <tr>
            	<th>Id</th>                
                <th>Nombre</th>                
                <th>Importe</th>                
            </tr>
        </thead>
        <tfoot>
            <tr>
            	<th></th>
                <th>Importe</th>
                <th>_IMP_</th>                
            </tr>
            <tr>
            	<th></th>
                <th>Impuesto _IVA_% </th>
                <th>_MTOIVA_</th>                
            </tr>
            <tr>
            	<th></th>
                <th>Cobrado</th>
                <th>_COB_</th>                
            </tr>
            <tr>
            	<th></th>
                <th>Total</th>
                <th>_TOT_</th>                
            </tr>
        </tfoot>
 
        <tbody>
        """
	row=db( (db.fc_factura_det.factura_id==fact_id) & (db.fc_factura_det.producto_id == db.in_producto.id) ).select()
	for r in row:
		importe+=r.fc_factura_det.importe
		lista.append("<tr><td>"+str(r.fc_factura_det.id)+"</td><td>"+r.in_producto.nombre+"</td><td>"+str(r.fc_factura_det.importe)+"</td></tr>")

	mto_iva=importe*(iva/100)
	total=importe+mto_iva-cobrado
	prueba=prueba.replace('_COB_',str(cobrado))
	prueba=prueba.replace('_MTOIVA_',str(mto_iva))
	prueba=prueba.replace('_TOT_',str(total))
	prueba=prueba.replace('_IVA_',str(iva))
	prueba=prueba.replace('_IMP_',str(importe))


   	#lista=["<tr><td>"+str(r.fc_factura_det.id)+"</td><td>"+r.in_producto.nombre+"</td><td>"+str(r.fc_factura_det.importe)+"</td></tr>" for row in row] 
	prueba+="".join(lista)
	prueba+="</tbody></table>"


	if len(prueba)>0:
		mytabla=prueba
	else:		
		mytabla=T("No existen registros")
	
	return mytabla

def get_cb_lines(fact_id):
	exito=request.vars.exito	
	monto=0.00
	total=0.00
	lista=[]	

	prueba="""
	<table id="mitabla2" style=".selected{color:red;}" class="table" cellspacing="0" width="100%">
        <thead>
            <tr>
            	<th>Id</th>                
                <th>Tipo</th>                
                <th>Desc</th>                
                <th>Monto</th>                
            </tr>
        </thead>
        <tfoot>            
        </tfoot>
 
        <tbody>
        """
	row=db( (db.fc_cobro_det.factura_id==fact_id) & (db.fc_cobro_det.forma_pago_id == db.fc_forma_pago.id) ).select()
	for r in row:
		monto+=r.fc_cobro_det.monto
		lista.append("<tr><td>"+str(r.fc_cobro_det.id)+"</td><td>"+ 
					r.fc_forma_pago.nombre+"</td><td>"+r.fc_cobro_det.descripcion+
					"</td><td>"+str(r.fc_cobro_det.monto)+"</td></tr>")

	
	total=monto	
   	
	prueba+="".join(lista)
	prueba+="</tbody></table>"


	if len(prueba)>0:
		mytabla=prueba
	else:		
		mytabla=T("No existen registros")
	
	return mytabla


def fact_prod():
	prodid = request.vars.prodid
	clteid = request.vars.clteid
	perid  = request.vars.perid	
	fact_id = int(request.vars.fact_id)
	#si ya viene el numero de factura, es decir estoy insertando solo detalle 
	if fact_id > 0:		
		facid=fact_id
		ins=Factura()
		ins.insertar_det(facid,prodid,perid)
	else:		#ahora si no viene el numero de factura es un full isnserta fact y det				
		ins=Factura()
		facid=ins.insertar_fact("Factura de venta","",0.00,0.00,clteid,perid,prodid)

	#obtnego la tabla con los datos actualizados
	#print facid
	tabla=get_fact_lines(facid)
	return json.dumps({'fact_id':facid,'tabla':tabla})

def fact_del():
	facid=request.vars.fact_id
	dele=Factura()
	facid=dele.eliminar_fact(facid)
	tabla=get_fact_lines(facid)

	return XML(tabla)
	
def det_del():
	det_id=request.vars.det_id
	row=db(db.fc_factura_det.id == det_id).select()
	facid=row[0].factura_id

	dele=Factura()
	detid=dele.eliminar_det(det_id)
	tabla=get_fact_lines(facid)

	return XML(tabla)

def fact_print():
	import os
	facid=request.vars.fact_id
	#p.mono{font-family:"Courier New", Courier, monospace; font-size:8px;}
	#<p class="serif">
	estilo="font-family:'Courier New', Courier, monospace; font-size:10px; width:300px; text-align:center;"
	estilotbl="font-family:'Courier New', Courier, monospace; font-size:10px; width:300px;"
	algleft="text-align:left;"
	algright="text-align:right;"
	fc=Factura()
	emp=db(db.cf_empresa.id > 0).select().first()
	head=fc.get_head(facid)
	lin=fc.get_lines(facid)	

	headr=[]
	headr.append(DIV(emp.razon_social))
	headr.append(DIV("RIF: %s" % emp.rif))	
	headr.append(DIV(emp.direccion or ""))	
	headr.append(DIV("================================================="))
	headr.append(DIV(TABLE(TR("FACTURA#:",TD("000"+str(head.fc_factura.id) ,_style=algright )),
						  TR(TD("FECHA:"),TD(head.fc_factura.fecha,         _style=algright) ),
						   _style=estilotbl)))
	headr.append(DIV("================================================="))
	headr.append(DIV("DATOS DEL CLIENTE:", _style=algleft ))
	headr.append(DIV(head.cf_cliente.nombre, _style=algleft))
	headr.append(DIV("RIF: %s" % head.cf_cliente.rif , _style=algleft))	
	headr.append(DIV("DIRECCION: %s" % head.cf_cliente.direccion or "" , _style=algleft))	
	headr.append(DIV("================================================="))
	
	#lista para guardar datos de tablas
	bdy=[]
	line=[]
	foot=[]
	total=[]

	#variable para rellenar
	mto=0.00
	tot=0.00
	iva=0.00
	mtoiva=0.00

	line.append(TR("COD","PROD",TD("MONTO",_style=algright)))
	for ln in lin:
		line.append(TR(ln.in_producto.codigo,ln.in_producto.nombre,TD(ln.fc_factura_det.importe,_style=algright)))
		mto+=ln.fc_factura_det.importe
		mtoiva+=ln.fc_factura_det.impuesto

	bdy.append(TABLE(line,_style=estilotbl))

	foot.append(DIV("================================================="))


	total.append(DIV(TABLE(TR("BASE:",TD(mto ,_style=algright )),
						  TR(TD("IVA: %s %%" % head.fc_factura.iva ),TD(mtoiva,_style=algright) ),
						  TR(TD("TOTAL:"),TD(mtoiva+mto,_style=algright) ),
						   _style=estilotbl)))

	html=[]
	html.append(DIV(headr))
	html.append(DIV(bdy))
	html.append(DIV(foot))
	html.append(DIV(total))
	html.append(DIV("================================================="))
	html.append(DIV("gracias por su compra !"))

	#file=os.path.join(request.folder,'static','ticket.txt')  
	#fo=open(file,"w")
	#fo.write(fact)
	#fo.close()

	return DIV(html ,_style=estilo)

def add_cobro():
	fp_id = int(request.vars.id_fp)
	monto_cobro = float(request.vars.monto_cobro)
	fact_id = int(request.vars.fact_id)
	ref= request.vars.ref
	desc= request.vars.desc

	#print type(fp_id),type(monto_cobro),type(fact_id),type(ref),type(desc),
	
	cb=Cobro()
	val=cb.insert(fp_id,fact_id,monto_cobro,ref,desc)	
	if val:
		tabla=get_fact_lines(fact_id)
		tabla2=get_cb_lines(fact_id)

	return json.dumps({'row':val,'tabla':tabla,'tabla2':tabla2})

def del_cobro():
	cob_id = int(request.vars.det_id)
	fact_id = int(request.vars.fact_id)
	cb=Cobro()
	val=cb.delete(cob_id)	
	if val:
		tabla=get_fact_lines(fact_id)
		tabla2=get_cb_lines(fact_id)

	return json.dumps({'row':val,'tabla':tabla,'tabla2':tabla2})



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
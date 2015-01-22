# -*- coding: utf-8 -*-
### required - do no delete
def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call(): return service()
### end requires
def index():	
	tabla='cf_empresa'
	count =db(db[tabla].id > 0).count() 
	row=db(db[tabla].id > 0).select().first()
	exito=2
	if count > 0:
		registro=row.id
	else:
		registro = 0
	form = SQLFORM(db[tabla],registro, _id="myform" ,submit_button='Enviar' , delete_label='Click para borrar:',  \
			next=URL(c='empresa',  f='index'), \
			message=T("Operacion Exitosa !"),  upload=URL('download'))	
	if form.accepts(request.vars, session):
		#return dict(exito=0,msg="Operacion Exitosa")
		redirect(URL('empresa','index'))
		response.flash = 'Operacion exitosa !'			

	elif form.errors:
		response.flash = 'Ha habido un error !'			
	return dict(myform=form,exito=exito)

def eliminar():
	id=request.vars.id
	tabla='cf_empresa'
	db(db[tabla].id==id).delete()
	redirect(URL('empresa','index'))
def error():
    return dict()

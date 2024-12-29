from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from functools import wraps
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from utilidades import formato_dinero,\
  calcular_afp_empleado,\
  calcular_afp_empresa,\
  calcular_ars_empleado,\
  calcular_ars_empresa,\
  calcular_infotep,\
  calcular_isr,\
  calcular_riesgos_laborales,\
  calcular_salario_neto

# Inicializar la aplicación
app = Flask(__name__)

# Configuraciones para la aplicación
app.config['SECRET_KEY'] = 'clave-secreta-de-la-sesion-de-usuarios'

# Registrando funciones como filtros personalizado
app.jinja_env.filters['dinero'] = formato_dinero
app.jinja_env.filters['ars_empresa'] = calcular_ars_empresa
app.jinja_env.filters['ars_empleado'] = calcular_ars_empleado
app.jinja_env.filters['riesgos_laborales'] = calcular_riesgos_laborales
app.jinja_env.filters['infotep'] = calcular_infotep
app.jinja_env.filters['afp_empresa'] = calcular_afp_empresa
app.jinja_env.filters['afp_empleado'] = calcular_afp_empleado
app.jinja_env.filters['isr'] = calcular_isr
app.jinja_env.filters['salario_neto'] = calcular_salario_neto

# Configuraciones de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rrhh.db'
# Inicializar base de datos
db = SQLAlchemy(app)

# Configuraciones de la sesión
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_SQLALCHEMY'] = db
# Inicializar la sesión
Session(app)

# Tablas
class Usuarios(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  usuario = db.Column(db.String(50), nullable=False, unique=True)
  password = db.Column(db.String(500), nullable=False)

class Puestos(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  nombre = db.Column(db.String(100), nullable=False)
  salario_minimo = db.Column(db.Float, nullable=False)
  salario_maximo = db.Column(db.Float, nullable=False)

class Departamentos(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  nombre = db.Column(db.String(100), nullable=False)
  supervisor_id = db.Column(db.Integer, db.ForeignKey('empleados.id'))
  supervisor = db.relationship('Empleados', foreign_keys=[supervisor_id], cascade="all,delete", backref='departamentos', lazy=True)

class Empleados(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  nombre = db.Column(db.String(100), nullable=False)
  apellido = db.Column(db.String(100), nullable=False)
  fecha_nacimiento = db.Column(db.DateTime, nullable=False)
  fecha_contratacion = db.Column(db.DateTime, nullable=False)
  sexo = db.Column(db.String(10), nullable=False)
  puesto_id = db.Column(db.Integer, db.ForeignKey('puestos.id'), nullable=False)
  puesto = db.relationship('Puestos', backref='empleados', lazy=True)
  departamento_id = db.Column(db.Integer, db.ForeignKey('departamentos.id'), nullable=False)
  departamento = db.relationship('Departamentos', foreign_keys=[departamento_id], backref='empleados', lazy=True)
  salario = db.Column(db.Float, nullable=False)

# Decorador para requerir inicio de sesión evitando repetir el mismo código
def login_requerido(f):
  @wraps(f)
  def validar_sesion(*args, **kwargs):
    if 'usuario_id' not in session:
      return redirect(url_for('login'))
    return f(*args, **kwargs)
  return validar_sesion

# Index
@app.route('/')
def index():
  if 'usuario_id' in session:
    return redirect(url_for('dashboard'))
  return redirect(url_for('login'))

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    usuario = request.form['usuario']
    password = request.form['password']
    usuario_db = Usuarios.query.filter_by(usuario=usuario).first()
    if usuario_db and check_password_hash(usuario_db.password, password):
      session['usuario_id'] = usuario_db.id
      return redirect(url_for('dashboard'))
    else:
      flash('Credenciales incorrectas', 'error')
  return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
  session.pop('usuario_id', None)
  return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@login_requerido
def dashboard():
  # costo total de la nómina de los empleados
  costo_total = db.session.query(db.func.sum(Empleados.salario)).scalar()
  
  # cantidad de empleados contratados
  cantidad_empleados = Empleados.query.count()

  # cantidad de departamentos
  cantidad_departamentos = Departamentos.query.count()

  # cantidad de puestos de trabajo
  cantidad_puestos = Puestos.query.count()

  # los tres departamentos con mayor nómina
  departamentos_con_mayor_nomina = db.session.query(Departamentos.nombre, db.func.sum(Empleados.salario).label('costo'))\
    .join(Empleados, Departamentos.id == Empleados.departamento_id)\
    .group_by(Departamentos.id)\
    .order_by(db.func.sum(Empleados.salario).desc())\
    .limit(3)\
    .all()

  # puesto de trabajo con más empleados
  puesto_con_mas_empleados = db.session.query(Puestos.nombre, db.func.count(Empleados.id).label('num_employees'))\
    .join(Empleados)\
    .group_by(Puestos.id)\
    .order_by(db.func.count(Empleados.id).desc())\
    .first()

  return render_template(
    'dashboard.html',
    costo_total=costo_total or 0,
    cantidad_empleados=cantidad_empleados,
    cantidad_departamentos=cantidad_departamentos,
    cantidad_puestos=cantidad_puestos,
    departamentos_con_mayor_nomina=departamentos_con_mayor_nomina,
    puesto_con_mas_empleados=puesto_con_mas_empleados
  )

# CRUD Usuarios
@app.route('/usuarios')
@login_requerido
def usuarios():
  usuarios = Usuarios.query.all()
  return render_template('usuarios.html', usuarios=usuarios)

@app.route('/usuarios/crear', methods=['GET', 'POST'])
@login_requerido
def crear_usuario():
  if request.method == 'POST':
    nuevo_usuario = Usuarios(
      usuario=request.form['usuario'],
      password=generate_password_hash(request.form['password'])
    )
    db.session.add(nuevo_usuario)
    db.session.commit()
    flash('Usuario creado', 'exito')
    return redirect(url_for('usuarios'))
  return render_template('crear_usuario.html')

@app.route('/usuarios/actualizar/<int:id>', methods=['GET', 'POST'])
@login_requerido
def actualizar_usuario(id):
  usuario = Usuarios.query.get_or_404(id)
  if request.method == 'POST':
    usuario.usuario = request.form['usuario']
    password = request.form['password']
    if password:
      usuario.password = generate_password_hash(request.form['password'])
    db.session.commit()
    flash('Usuario actualizado', 'exito')
    return redirect(url_for('usuarios'))
  return render_template('actualizar_usuario.html', usuario=usuario)

@app.route('/usuarios/eliminar/<int:id>', methods=['GET'])
@login_requerido
def eliminar_usuario(id):
  usuario = Usuarios.query.get_or_404(id)
  db.session.delete(usuario)
  db.session.commit()
  flash('Usuario eliminado', 'exito')
  return redirect(url_for('usuarios'))

# CRUD Puestos
@app.route('/puestos')
@login_requerido
def puestos():
  puestos = Puestos.query.all()
  return render_template('puestos.html', puestos=puestos)

@app.route('/puestos/crear', methods=['GET', 'POST'])
@login_requerido
def crear_puesto():
  if request.method == 'POST':
    nuevo_puesto = Puestos(
      nombre=request.form['nombre'],
      salario_minimo=request.form['salario_minimo'],
      salario_maximo=request.form['salario_maximo']
    )
    db.session.add(nuevo_puesto)
    db.session.commit()
    flash('Puesto creado', 'exito')
    return redirect(url_for('puestos'))
  return render_template('crear_puesto.html')

@app.route('/puestos/actualizar/<int:id>', methods=['GET', 'POST'])
@login_requerido
def actualizar_puesto(id):
  puesto = Puestos.query.get_or_404(id)
  if request.method == 'POST':
    puesto.nombre = request.form['nombre']
    puesto.salario_minimo = request.form['salario_minimo']
    puesto.salario_maximo = request.form['salario_maximo']
    db.session.commit()
    flash('Puesto actualizado', 'exito')
    return redirect(url_for('puestos'))
  return render_template('actualizar_puesto.html', puesto=puesto)

@app.route('/puestos/eliminar/<int:id>', methods=['GET'])
@login_requerido
def eliminar_puesto(id):
  puesto = Puestos.query.get_or_404(id)
  Empleados.query.filter_by(puesto_id=id).delete()
  db.session.delete(puesto)
  flash('Puesto eliminado', 'exito')
  return redirect(url_for('puestos'))

# CRUD Departamentos
@app.route('/departamentos')
@login_requerido
def departamentos():
  departamentos = Departamentos.query.all()
  return render_template('departamentos.html', departamentos=departamentos)

@app.route('/departamentos/crear', methods=['GET', 'POST'])
@login_requerido
def crear_departamento():
  if request.method == 'POST':
    nuevo_departamento = Departamentos(
      nombre=request.form['nombre'],
      supervisor_id=request.form['supervisor_id']
    )
    db.session.add(nuevo_departamento)
    db.session.commit()
    flash('Departamento creado', 'exito')
    return redirect(url_for('departamentos'))
  empleados = Empleados.query.all()
  return render_template('crear_departamento.html', empleados=empleados)

@app.route('/departamentos/actualizar/<int:id>', methods=['GET', 'POST'])
@login_requerido
def actualizar_departamento(id):
  departamento = Departamentos.query.get_or_404(id)
  if request.method == 'POST':
    departamento.nombre = request.form['nombre']
    departamento.supervisor_id = request.form['supervisor_id']
    db.session.commit()
    flash('Departamento actualizado', 'exito')
    return redirect(url_for('departamentos'))
  empleados = Empleados.query.all()
  return render_template('actualizar_departamento.html', departamento=departamento, empleados=empleados)

@app.route('/departamentos/eliminar/<int:id>', methods=['GET'])
@login_requerido
def eliminar_departamento(id):
  departamento = Departamentos.query.get_or_404(id)
  Empleados.query.filter_by(departamento_id=id).delete()
  db.session.delete(departamento)
  db.session.commit()
  flash('Departamento eliminado', 'exito')
  return redirect(url_for('departamentos'))

# CRUD Empleados
@app.route('/empleados')
@login_requerido
def empleados():
  empleados = Empleados.query.all()
  return render_template('empleados.html', empleados=empleados)

@app.route('/empleados/crear', methods=['GET', 'POST'])
@login_requerido
def crear_empleado():
  if request.method == 'POST':
    new_empleado = Empleados(
      nombre=request.form['nombre'],
      apellido=request.form['apellido'],
      fecha_nacimiento=datetime.strptime(request.form['fecha_nacimiento'], '%Y-%m-%d'),
      fecha_contratacion=datetime.strptime(request.form['fecha_contratacion'], '%Y-%m-%d'),
      sexo=request.form['sexo'],
      puesto_id=request.form['puesto_id'],
      departamento_id=request.form['departamento_id'],
      salario=request.form['salario']
    )
    db.session.add(new_empleado)
    db.session.commit()
    flash('Empleado creado', 'exito')
    return redirect(url_for('empleados'))
  puestos = Puestos.query.all()
  departamentos = Departamentos.query.all()
  return render_template('crear_empleado.html', puestos=puestos, departamentos=departamentos)

@app.route('/empleados/actualizar/<int:id>', methods=['GET', 'POST'])
@login_requerido
def actualizar_empleado(id):
  empleado = Empleados.query.get_or_404(id)
  if request.method == 'POST':
    empleado.nombre = request.form['nombre']
    empleado.apellido = request.form['apellido']
    empleado.fecha_nacimiento = datetime.strptime(request.form['fecha_nacimiento'], '%Y-%m-%d')
    empleado.fecha_contratacion = datetime.strptime(request.form['fecha_contratacion'], '%Y-%m-%d')
    empleado.sexo = request.form['sexo']
    empleado.puesto_id = request.form['puesto_id']
    empleado.departamento_id = request.form['departamento_id']
    empleado.salario = request.form['salario']
    db.session.commit()
    flash('Empleado actualizado', 'exito')
    return redirect(url_for('empleados'))
  puestos = Puestos.query.all()
  departamentos = Departamentos.query.all()
  return render_template('actualizar_empleado.html', empleado=empleado, puestos=puestos, departamentos=departamentos)

@app.route('/empleados/eliminar/<int:id>', methods=['GET'])
@login_requerido
def eliminar_empleado(id):
  empleado = Empleados.query.get_or_404(id)
  db.session.delete(empleado)
  db.session.commit()
  flash('Empleado eliminado', 'exito')
  return redirect(url_for('empleados'))

# Nomina
@app.route('/nomina', methods=['GET'])
@login_requerido
def nomina():
  empleados = Empleados.query.all()
  return render_template('nomina.html', empleados=empleados)

# Función para insertar en la base de datos los usuarios iniciales
def seed():
  if Usuarios.query.count() == 0:
    db.session.add(Usuarios(
      usuario='admin',
      password=generate_password_hash('1234'),
    ))
    db.session.add(Usuarios(
      usuario='luis_joel',
      password=generate_password_hash('100058777'),
    ))
    db.session.commit()

# Crear las tablas y correr el seeder
with app.app_context():
  db.create_all()
  seed()

# Función principal para ejecutar la aplicación
if __name__ == '__main__':
  app.run(debug=True)

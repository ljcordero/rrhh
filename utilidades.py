import locale

locale.setlocale(locale.LC_ALL, 'es_DO.UTF-8')

def formato_dinero(valor):
  return locale.currency(valor, grouping=True).replace('$', 'RD$')

def calcular_isr(salario):
  salario_imponible = salario - calcular_afp_empleado(salario) - calcular_ars_empleado(salario)
  if salario_imponible <= 34685:
    return 0
  elif salario_imponible <= 52027.42:
    return (salario_imponible - 34685) * 0.15
  elif salario_imponible <= 72260.25:
    return 2601.33 + ((salario_imponible - 52027.42) * 0.2)
  else:
    return 6648 + ((salario_imponible - 72260.25) * 0.25)

def calcular_afp_empresa(salario):
  return salario * 0.0710

def calcular_afp_empleado(salario):
  return salario * 0.0287

def calcular_ars_empresa(salario):
  return salario * 0.0709

def calcular_ars_empleado(salario):
  return salario * 0.0304

def calcular_riesgos_laborales(salario):
  return salario * 0.011

def calcular_infotep(salario):
  return salario * 0.01

def calcular_salario_neto(salario):
  return salario - calcular_afp_empleado(salario) - calcular_ars_empleado(salario) - calcular_isr(salario)

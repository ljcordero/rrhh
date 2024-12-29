const fechaNacimientoInput = document.querySelector(
  'input[name="fecha_nacimiento"]'
);

const fechaContratacionInput = document.querySelector(
  'input[name="fecha_contratacion"]'
);

if (fechaNacimientoInput) {
  const valorMaximo = new Date();
  valorMaximo.setFullYear(valorMaximo.getFullYear() - 18);
  valorMaximo.setDate(valorMaximo.getDate() - 1);

  fechaNacimientoInput.setAttribute(
    "max",
    valorMaximo.toISOString().split("T")[0]
  );
}

if (fechaContratacionInput) {
  const valorMinimo = new Date();
  valorMinimo.setFullYear(valorMinimo.getFullYear() - 1);

  fechaContratacionInput.setAttribute(
    "min",
    valorMinimo.toISOString().split("T")[0]
  );
}

const salario = document.getElementById("salario");
const puesto = document.getElementById("puesto");

function establecerRangoSalarial() {
  const opcionSeleccionada = puesto.querySelector(
    `option[value="${puesto.value}"]`
  );

  if (opcionSeleccionada) {
    const salarioMinimo = opcionSeleccionada.getAttribute(
      "data-salario-minimo"
    );
    const salarioMaximo = opcionSeleccionada.getAttribute(
      "data-salario-maximo"
    );

    salario.setAttribute("min", salarioMinimo);
    salario.setAttribute("max", salarioMaximo);
  }
}

establecerRangoSalarial();
document
  .getElementById("puesto")
  .addEventListener("change", establecerRangoSalarial);

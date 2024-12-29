const meses = [
  "Enero",
  "Febrero",
  "Marzo",
  "Abril",
  "Mayo",
  "Junio",
  "Julio",
  "Agosto",
  "Septiembre",
  "Octubre",
  "Noviembre",
  "Diciembre",
];

const titulo = document.getElementById("titulo");

if (titulo) {
  const hoy = new Date();
  titulo.textContent = `Nómina de ${
    meses[hoy.getMonth()]
  } ${hoy.getFullYear()}`;
}

function imprimir() {
  const contenido = document.getElementById("contenido");

  if (contenido) {
    const original = document.body.innerHTML;

    document.body.innerHTML = contenido.outerHTML;

    window.print();

    document.body.innerHTML = original;
  }
}

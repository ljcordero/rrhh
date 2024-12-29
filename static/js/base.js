document
  .getElementById("navbar-toggle")
  ?.addEventListener("click", function () {
    const navbarLinks = document.querySelector(".navbar-links");
    navbarLinks.classList.toggle("active");
  });

document.querySelectorAll(".navbar-links a").forEach((link) => {
  if (window.location.pathname.includes(link.getAttribute("href"))) {
    link.classList.add("active");
  }
});

setTimeout(() => {
  for (const alerta of document.getElementsByClassName("alerta")) {
    alerta.remove();
  }
}, 5000);

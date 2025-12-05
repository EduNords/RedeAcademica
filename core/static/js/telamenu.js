const corpo = document.body;
const botaoTema = document.getElementById("botao-tema");
const overlayTema = document.getElementById("overlay-tema");
const cardTemas = document.querySelectorAll(".card-tema");
const botaoFechar = document.querySelector(".modal-fechar");

// abre o modal ao clicar no botão sol/lua
botaoTema.addEventListener("click", () => {
  overlayTema.classList.add("visivel");
  atualizarSelecaoCards();
});

// fecha ao clicar no X
botaoFechar.addEventListener("click", () => {
  overlayTema.classList.remove("visivel");
});

// fecha clicando fora do modal
overlayTema.addEventListener("click", (e) => {
  if (e.target === overlayTema) {
    overlayTema.classList.remove("visivel");
  }
});

// clique nos cartões de tema
cardTemas.forEach((card) => {
  card.addEventListener("click", () => {
    const tema = card.getAttribute("data-tema-card");
    aplicarTema(tema);
    overlayTema.classList.remove("visivel");
  });
});

function aplicarTema(tema) {
  corpo.setAttribute("data-tema", tema);
  atualizarSelecaoCards();
}

function atualizarSelecaoCards() {
  const temaAtual = corpo.getAttribute("data-tema");
  cardTemas.forEach((card) => {
    card.classList.toggle(
      "ativo",
      card.getAttribute("data-tema-card") === temaAtual
    );
  });
}

// tema inicial
aplicarTema("claro");

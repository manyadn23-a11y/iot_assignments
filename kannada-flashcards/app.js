let cards = [...allCards];
let index = 0;
let known = 0;
let review = 0;
let isFlipped = false;

function showCard() {
  if (index >= cards.length) { showResult(); return; }

  const c = cards[index];
  document.getElementById("card-english").textContent = c.english;
  document.getElementById("card-kannada").textContent = c.kannada;
  document.getElementById("card-pronoun").textContent = c.pronoun;
  document.getElementById("card-counter").textContent =
    "Card " + (index + 1) + " of " + cards.length;
  document.getElementById("progress-fill").style.width =
    Math.round((index / cards.length) * 100) + "%";

  updateStats();

  // Reset flip
  document.getElementById("card-inner").classList.remove("flipped");
  isFlipped = false;
}

function flipCard() {
  isFlipped = !isFlipped;
  document.getElementById("card-inner").classList.toggle("flipped", isFlipped);
}

function markCard(type) {
  if (type === "know") known++;
  else review++;
  index++;
  showCard();
}

function nextCard() {
  index++;
  showCard();
}

function updateStats() {
  document.getElementById("known-count").textContent = known;
  document.getElementById("review-count").textContent = review;
  document.getElementById("remaining-count").textContent = cards.length - index;
}

function showResult() {
  document.getElementById("result-panel").style.display = "block";
  const pct = Math.round((known / cards.length) * 100);
  document.getElementById("result-emoji").textContent = pct >= 80 ? "🎉" : "📚";
  document.getElementById("result-title").textContent =
    pct >= 80 ? "Excellent!" : "Keep practicing!";
  document.getElementById("result-sub").textContent =
    "You knew " + known + " out of " + cards.length + " words (" + pct + "%)";
}

function restart() {
  index = 0; known = 0; review = 0;
  document.getElementById("result-panel").style.display = "none";
  showCard();
}

showCard();
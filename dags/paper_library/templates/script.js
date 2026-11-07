const searchInput = document.getElementById("q");
const categorySelect = document.getElementById("cat");
const count = document.getElementById("count");
const cards = [...document.querySelectorAll(".paper-card")];

function applyFilters() {
  /**
   * Filter function that shows/hides cards based on the search input and selected category. 
   * It also updates the count of shown papers.
   */
  const term = searchInput.value.trim().toLowerCase();
  const category = categorySelect.value;
  let shown = 0;

  for (const card of cards) {
    const matches =
      (!category || card.dataset.category === category) &&
      (!term || card.dataset.search.includes(term));
    card.hidden = !matches;
    if (matches) shown++;
  }
  count.textContent = `${shown} of ${cards.length} papers`;
}

searchInput.addEventListener("input", applyFilters);
categorySelect.addEventListener("change", applyFilters);
applyFilters();

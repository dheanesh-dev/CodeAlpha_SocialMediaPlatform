document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-counter-input]").forEach((input) => {
    const form = input.closest("form");
    const counter = form ? form.querySelector("[data-counter]") : null;
    if (!counter) return;

    const limit = Number(counter.dataset.limit || input.maxLength || 0);
    const updateCounter = () => {
      const length = input.value.length;
      counter.textContent = length + " / " + limit;
      counter.classList.toggle("near-limit", limit > 0 && length >= limit * 0.85);
      counter.classList.toggle("at-limit", limit > 0 && length >= limit);
    };

    input.addEventListener("input", updateCounter);
    updateCounter();
  });

  document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      const message = form.dataset.confirm || "Are you sure?";
      if (!window.confirm(message)) event.preventDefault();
    });
  });
});

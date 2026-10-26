document.addEventListener("DOMContentLoaded", () => {
  document.documentElement.classList.add("sprig-ready");

  document.querySelectorAll("form[data-loading-form]").forEach((form) => {
    form.addEventListener("submit", () => {
      const button = form.querySelector("[data-loading-button]");
      if (!button) {
        return;
      }
      button.dataset.originalText = button.innerHTML;
      button.disabled = true;
      button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>Processing...';
    });
  });

  document.querySelectorAll("input[type='file'][data-image-preview]").forEach((input) => {
    input.addEventListener("change", () => {
      const preview = document.querySelector(input.dataset.imagePreview);
      const emptyText = input.closest("form")?.querySelector("[data-preview-empty]");
      const file = input.files && input.files[0];
      if (!preview || !file) {
        return;
      }
      preview.src = URL.createObjectURL(file);
      preview.classList.remove("d-none");
      if (emptyText) {
        emptyText.classList.add("d-none");
      }
    });
  });

  const moduleChart = document.querySelector("canvas[data-chart='module']");
  if (moduleChart && window.Chart) {
    const labels = moduleChart.dataset.labels ? moduleChart.dataset.labels.split(",") : [];
    const values = moduleChart.dataset.values ? moduleChart.dataset.values.split(",").map(Number) : [];
    new Chart(moduleChart, {
      type: "doughnut",
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: ["#1f7a4d", "#f2b84b", "#2f7ca8", "#6aa84f"],
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { position: "bottom" } },
      },
    });
  }

  const trendChart = document.querySelector("canvas[data-chart='trend']");
  if (trendChart && window.Chart) {
    const daysNode = document.getElementById("trend-days");
    const seriesNode = document.getElementById("trend-series");
    const days = daysNode ? JSON.parse(daysNode.textContent) : [];
    const series = seriesNode ? JSON.parse(seriesNode.textContent) : {};
    const colors = ["#1f7a4d", "#f2b84b", "#2f7ca8", "#6aa84f"];
    new Chart(trendChart, {
      type: "line",
      data: {
        labels: days,
        datasets: Object.keys(series).map((label, index) => ({
          label,
          data: series[label],
          borderColor: colors[index % colors.length],
          backgroundColor: colors[index % colors.length],
          tension: 0.35,
        })),
      },
      options: {
        responsive: true,
        plugins: { legend: { position: "bottom" } },
        scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
      },
    });
  }
});

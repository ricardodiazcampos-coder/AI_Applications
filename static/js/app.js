(function () {
  const categorySelect = document.getElementById("unexpected-category");
  const customGroup = document.getElementById("custom-name-group");
  const customInput = document.getElementById("custom-name");

  function toggleCustomName() {
    if (!categorySelect || !customGroup) return;
    const isOther = categorySelect.value === window.OTHER_UNEXPECTED_LABEL;
    customGroup.classList.toggle("d-none", !isOther);
    if (customInput) {
      customInput.required = isOther;
      if (!isOther) customInput.value = "";
    }
  }

  if (categorySelect) {
    categorySelect.addEventListener("change", toggleCustomName);
    toggleCustomName();
  }

  if (window.ACTIVE_TAB) {
    const trigger = document.querySelector(`[data-bs-target="#tab-${window.ACTIVE_TAB}"]`);
    if (trigger && window.bootstrap) {
      bootstrap.Tab.getOrCreateInstance(trigger).show();
    }
  }

  const data = window.FINANCE_CHART_DATA;
  if (!data || !data.has_data || typeof Chart === "undefined") return;

  const pieCtx = document.getElementById("pieChart");
  if (pieCtx && data.pie.values.length) {
    new Chart(pieCtx, {
      type: "pie",
      data: {
        labels: data.pie.labels,
        datasets: [{
          data: data.pie.values,
          backgroundColor: ["#ef4444", "#f97316", "#3b82f6", "#a855f7"],
        }],
      },
      options: {
        plugins: { title: { display: true, text: "Distribución del ingreso" } },
      },
    });
  }

  const barCtx = document.getElementById("barChart");
  if (barCtx) {
    new Chart(barCtx, {
      type: "bar",
      data: {
        labels: data.bar.labels,
        datasets: [{
          label: "Monto",
          data: data.bar.values,
          backgroundColor: ["#22c55e", "#ef4444", "#f97316", "#3b82f6", "#a855f7"],
        }],
      },
      options: {
        plugins: { title: { display: true, text: "Comparación mensual" }, legend: { display: false } },
        scales: { y: { beginAtZero: true } },
      },
    });
  }
})();

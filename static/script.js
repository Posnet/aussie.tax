document.addEventListener("DOMContentLoaded", () => {
  generateTables();
  updateTax();
});

function generateTables() {
  const resultsContainer = document.getElementById("resultsContainer");
  resultsContainer.innerHTML = "";

  SCHEMES.forEach((scheme, index) => {
    const table = document.createElement("table");
    table.id = `resultsTable${index + 1}`;
    table.classList.add("flex-item");

    const thead = `
            <thead>
                <tr>
                    <th colspan="2">${scheme.name}</th>
                </tr>
                <tr>
                    <th>Band</th>
                    <th>Tax Payable</th>
                </tr>
            </thead>
        `;

    const tbody = document.createElement("tbody");
    tbody.id = `resultsBody${index + 1}`;

    table.innerHTML = thead;
    table.appendChild(tbody);
    resultsContainer.appendChild(table);
  });
}

function updateTax() {
  const income = parseFloat(document.getElementById("income").value);
  const isValidIncome = !isNaN(income) && income > 0;

  const totalsBody = document.getElementById("totalsBody");
  totalsBody.innerHTML = "";

  const currentSchemeTotal = isValidIncome
    ? calculateTotalTax(income, SCHEMES[0].bands)
    : 0;

  SCHEMES.forEach((scheme, index) => {
    const taxDetails = isValidIncome
      ? calculateTax(income, scheme.bands)
      : initializeZeroTax(scheme.bands);

    const totalTax = taxDetails.reduce(
      (total, band) => total + (band ? band.taxPayable : 0),
      0,
    );
    const resultsBody = document.getElementById(`resultsBody${index + 1}`);
    resultsBody.innerHTML = "";

    taxDetails.forEach((band, bandIndex) => {
      const row = document.createElement("tr");
      if (band) {
        const bandCell = document.createElement("td");
        const taxCell = document.createElement("td");

        const cents =
          band.rate <= 0 ? "(Tax Free)" : ` (${(band.rate * 100).toFixed(1)}¢)`;

        let startSpan = document.createElement("span");
        let endSpan = document.createElement("span");
        let rateSpan = document.createElement("span");

        startSpan.innerText = formatCurrency(band.start);
        endSpan.innerText =
          band.end === Infinity ? "and above" : formatCurrency(band.end);
        rateSpan.innerText = cents;

        // Highlight differences
        if (index > 0) {
          const currentBand = calculateTax(income, SCHEMES[0].bands)[bandIndex];
          if (band.start !== currentBand.start) {
            startSpan.style.color =
              band.start > currentBand.start ? "red" : "green";
          }
          if (band.end !== currentBand.end) {
            endSpan.style.color = band.end > currentBand.end ? "red" : "green";
          }
          if (band.rate !== currentBand.rate) {
            rateSpan.style.color =
              band.rate > currentBand.rate ? "red" : "green";
          }
        }

        bandCell.appendChild(startSpan);
        bandCell.appendChild(document.createTextNode(" - "));
        bandCell.appendChild(endSpan);
        taxCell.appendChild(rateSpan);

        row.appendChild(bandCell);
        row.appendChild(taxCell);
      } else {
        row.innerHTML = "<td></td><td></td>";
      }
      resultsBody.appendChild(row);
    });

    const difference = totalTax - currentSchemeTotal;
    const differenceText =
      difference > 0
        ? ` (+${formatCurrency(difference)})`
        : difference < 0
          ? ` (${formatCurrency(difference)})`
          : "";
    const differenceClass =
      difference > 0
        ? "difference-positive"
        : difference < 0
          ? "difference-negative"
          : "";

    const totalRow = document.createElement("tr");
    totalRow.innerHTML = `
            <td>${scheme.name}</td>
            <td>${formatCurrency(totalTax)}<span class="${differenceClass}">${differenceText}</span></td>
        `;
    totalsBody.appendChild(totalRow);
  });
}

function calculateTax(income, bands) {
  let totalTax = 0;
  return bands.map((band) => {
    if (band.length === 0) return null;
    const [start, end, rate] = band;
    if (income < start) return createTaxDetail(start, end, 0, rate);

    const taxableIncome = Math.min(income, end) - start + 1;
    const taxPayable = taxableIncome * rate;
    totalTax += taxPayable;
    return createTaxDetail(start, end, taxPayable, rate);
  });
}

function calculateTotalTax(income, bands) {
  return bands.reduce((total, band) => {
    if (band.length === 0) return total;
    const [start, end, rate] = band;
    if (income > start) {
      const taxableIncome = Math.min(income, end) - start + 1;
      return total + taxableIncome * rate;
    }
    return total;
  }, 0);
}

function createTaxDetail(start, end, taxPayable, rate) {
  return {
    range: `${formatCurrency(start)} - ${end === Infinity ? "and above" : formatCurrency(end)}`,
    taxPayable,
    rate,
  };
}

function initializeZeroTax(bands) {
  return bands.map((band) =>
    band.length === 0 ? null : createTaxDetail(band[0], band[1], 0, band[2]),
  );
}
function formatCurrency(amount) {
  return `$${amount.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, "$&,")}`;
}

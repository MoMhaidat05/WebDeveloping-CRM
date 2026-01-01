const monthsAbbr = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
];

let recapText = document.getElementById("recap-text");
let recapSecondaryText = document.getElementById("recap-secondary-text");
let totalClients = document.getElementById("total-clients");
let totalServices = document.getElementById("total-services");
let totalEarnings = document.getElementById("total-earnings");
const prevBtn = document.getElementById("prev-btn");
const nextBtn = document.getElementById("next-btn");

document.addEventListener("DOMContentLoaded", function () {
  nextBtn.addEventListener("click", function increaseMonth() {
    currentMonth = monthsAbbr.indexOf(currentMonth);
    if (currentMonth === 11) {
      currentMonth = 0;
      currentYear++;
      currentMonth = monthsAbbr[currentMonth];
    } else {
      currentMonth++;
      currentMonth = monthsAbbr[currentMonth];
    }
    updateRecap();
  });

  prevBtn.addEventListener("click", function decreaseMonth() {
    currentMonth = monthsAbbr.indexOf(currentMonth);
    if (currentMonth === 0) {
      currentMonth = 11;
      currentYear--;
      currentMonth = monthsAbbr[currentMonth];
    } else {
      currentMonth--;
      currentMonth = monthsAbbr[currentMonth];
    }
    updateRecap();
  });
});

async function updateRecap() {
  try {
    let response = await fetch(`/api/get_recap`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ month: currentMonth, year: currentYear }),
    });
    let data = await response.json();
    if (response.status === 200) {
      recapText.innerText = data.month + ", " + data.year + " Recap";
      recapSecondaryText.innerText = data.month;
      totalClients.innerText = data.clients;
      totalServices.innerText = data.services;
      totalEarnings.innerText = "$" + data.sum_of_earnings + " JOD";
    } else {
      console.error("Failed to fetch recap data:", data.error);
    }
  } catch (error) {
    console.error("Error fetching recap data:", error);
  }
}

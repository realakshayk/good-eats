const API_URL = '/api/v1/meals/find';
const goals = [
  { key: 'muscle_gain', label: 'Muscle Gain', desc: 'High protein, 2500–3500 cal', icon: '💪' },
  { key: 'weight_loss', label: 'Weight Loss', desc: '1500–2000 cal, low carbs', icon: '🏃' },
  { key: 'keto', label: 'Keto', desc: '5–10% carbs, 70–80% fat', icon: '🥑' },
  { key: 'balanced', label: 'Balanced', desc: '2000–2500 cal, 30/40/30', icon: '⚖️' },
  { key: 'athletic_endurance', label: 'Endurance', desc: '3000–4000 cal, high carbs', icon: '🚴' },
  { key: 'vegan_protein', label: 'Vegan Protein', desc: '2000–2400 cal, plant protein', icon: '🌱' }
];

// State
let selectedGoal = localStorage.getItem('goal') || 'muscle_gain';
let radius = localStorage.getItem('radius') || 3;
let minProtein = localStorage.getItem('minProtein') || '';
let maxProtein = localStorage.getItem('maxProtein') || '';
let excludeIngredients = localStorage.getItem('excludeIngredients') || '';
let location = JSON.parse(sessionStorage.getItem('location') || 'null');

// DOM refs
const goalCards = document.getElementById('goalCards');
const radiusSlider = document.getElementById('radiusSlider');
const radiusVal = document.getElementById('radiusVal');
const minProteinInput = document.getElementById('minProtein');
const maxProteinInput = document.getElementById('maxProtein');
const excludeInput = document.getElementById('excludeIngredients');
const findBtn = document.getElementById('findBtn');
const resultsDiv = document.getElementById('results');

// Render goal cards
function renderGoals() {
  goalCards.innerHTML = '';
  goals.forEach(g => {
    const card = document.createElement('div');
    card.className = `p-3 rounded shadow cursor-pointer border ${selectedGoal === g.key ? 'border-green-600 bg-green-50' : 'border-gray-200 bg-white'}`;
    card.innerHTML = `<div class="text-2xl">${g.icon}</div><div class="font-bold">${g.label}</div><div class="text-xs text-gray-600">${g.desc}</div>`;
    card.onclick = () => {
      selectedGoal = g.key;
      localStorage.setItem('goal', selectedGoal);
      renderGoals();
    };
    goalCards.appendChild(card);
  });
}
renderGoals();

// Restore UI state
radiusSlider.value = radius;
radiusVal.textContent = radius;
minProteinInput.value = minProtein;
maxProteinInput.value = maxProtein;
excludeInput.value = excludeIngredients;

radiusSlider.oninput = e => {
  radiusVal.textContent = e.target.value;
  localStorage.setItem('radius', e.target.value);
};
minProteinInput.onchange = e => localStorage.setItem('minProtein', e.target.value);
maxProteinInput.onchange = e => localStorage.setItem('maxProtein', e.target.value);
excludeInput.onchange = e => localStorage.setItem('excludeIngredients', e.target.value);

// Geolocation
if (!location) {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(pos => {
      location = { lat: pos.coords.latitude, lon: pos.coords.longitude };
      sessionStorage.setItem('location', JSON.stringify(location));
    }, () => {
      // fallback to NYC
      location = { lat: 40.7128, lon: -74.0060 };
      sessionStorage.setItem('location', JSON.stringify(location));
    });
  } else {
    location = { lat: 40.7128, lon: -74.0060 };
    sessionStorage.setItem('location', JSON.stringify(location));
  }
}

// Debounce helper
function debounce(fn, ms) {
  let timer;
  return function(...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), ms);
  };
}

// Loader
function showLoader() {
  resultsDiv.innerHTML = '<div class="animate-pulse text-center p-8">Loading...</div>';
}

// Render results
function renderResults(meals) {
  if (!meals.length) {
    resultsDiv.innerHTML = '<div class="text-center text-gray-500">No meals found.</div>';
    return;
  }
  resultsDiv.innerHTML = '';
  meals.forEach(meal => {
    const card = document.createElement('div');
    card.className = 'bg-white rounded shadow p-4 flex flex-col gap-2';
    card.innerHTML = `
      <div class="font-bold text-lg">${meal.name}</div>
      <div class="text-xs text-gray-600">${meal.description || ''}</div>
      <div class="text-green-700 font-bold">${meal.price || ''}</div>
      <div class="flex gap-1 flex-wrap">${(meal.tags || []).map(t => `<span class='bg-green-100 text-green-800 px-2 py-0.5 rounded text-xs'>${t}</span>`).join('')}</div>
      <div class="flex gap-2 text-xs">
        <span>Score: <b>${(meal.relevance_score || 0).toFixed(2)}</b></span>
        <span>Confidence: <b>${meal.confidence_level || ''}</b></span>
      </div>
      <div class="flex gap-2 text-xs">
        <span>Calories: ${meal.nutrition?.calories || '?'}</span>
        <span>Protein: ${meal.nutrition?.protein || '?'}</span>
        <span>Carbs: ${meal.nutrition?.carbs || '?'}</span>
        <span>Fat: ${meal.nutrition?.fat || '?'}</span>
      </div>
    `;
    resultsDiv.appendChild(card);
  });
}

// Fetch meals
const fetchMeals = debounce(() => {
  if (!location) return;
  showLoader();
  const payload = {
    location,
    goal: selectedGoal,
    radius: parseFloat(radiusSlider.value),
    override_macros: {
      min_protein: minProteinInput.value ? parseFloat(minProteinInput.value) : undefined,
      max_protein: maxProteinInput.value ? parseFloat(maxProteinInput.value) : undefined
    },
    exclude_ingredients: excludeInput.value.split(',').map(x => x.trim()).filter(Boolean)
  };
  fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-API-Key': 'test-free-key' },
    body: JSON.stringify(payload)
  })
    .then(r => r.json())
    .then(data => {
      if (data && data.meals) {
        sessionStorage.setItem('lastResults', JSON.stringify(data.meals));
        renderResults(data.meals);
      } else {
        resultsDiv.innerHTML = '<div class="text-center text-red-500">Error fetching meals.</div>';
      }
    })
    .catch(() => {
      resultsDiv.innerHTML = '<div class="text-center text-red-500">Error fetching meals.</div>';
    });
}, 500);

findBtn.onclick = fetchMeals;

// Restore last results
const lastResults = sessionStorage.getItem('lastResults');
if (lastResults) {
  renderResults(JSON.parse(lastResults));
} 
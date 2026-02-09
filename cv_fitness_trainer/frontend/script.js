const API_BASE = "http://localhost:5000";

let repCount = 0;
let sessionData = {
  angles: [],
  symmetryScores: [],
  romValues: []
};

const themeToggle = document.getElementById('theme-toggle');
const currentTheme = localStorage.getItem('theme') || 'light';

if (currentTheme === 'dark') {
  document.documentElement.setAttribute('data-theme', 'dark');
  themeToggle.textContent = '☀️';
}

themeToggle.addEventListener('click', () => {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  if (currentTheme === 'dark') {
    document.documentElement.setAttribute('data-theme', 'light');
    themeToggle.textContent = '🌙';
    localStorage.setItem('theme', 'light');
  } else {
    document.documentElement.setAttribute('data-theme', 'dark');
    themeToggle.textContent = '☀️';
    localStorage.setItem('theme', 'dark');
  }
});

function updateUI(metrics) {
  document.getElementById('rep-count').textContent = metrics.rep_count || 0;
  document.getElementById('state').textContent = metrics.state || 'REST';
  
  const angle = metrics.current_angle;
  if (angle !== null && angle !== undefined) {
    document.getElementById('angle').textContent = `${Math.round(angle)}°`;
  } else {
    document.getElementById('angle').textContent = '---';
  }
  
  const symmetry = metrics.symmetry_score || 0;
  document.getElementById('symmetry').textContent = `${Math.round(symmetry)}%`;
  
  const rom = metrics.rom || 0;
  if (rom > 0) {
    document.getElementById('rom').textContent = `${Math.round(rom)}°`;
  } else {
    document.getElementById('rom').textContent = '---';
  }
  
  const statusEl = document.getElementById('status');
  if (angle !== null && angle !== undefined) {
    statusEl.textContent = '● DETECTING';
    statusEl.className = 'status-indicator detecting';
  } else {
    statusEl.textContent = '● NO POSE';
    statusEl.className = 'status-indicator error';
  }
  
  const stateEl = document.getElementById('state');
  if (metrics.state === 'REP_DONE') {
    stateEl.style.color = '#00ff88';
    stateEl.style.textShadow = '0 0 10px #00ff88';
    setTimeout(() => {
      stateEl.style.color = '';
      stateEl.style.textShadow = '';
    }, 500);
  }
}

async function fetchMetrics() {
  try {
    const response = await fetch(`${API_BASE}/metrics`);
    const metrics = await response.json();
    updateUI(metrics);
    
    if (metrics.rep_count !== repCount) {
      repCount = metrics.rep_count;
      const repEl = document.getElementById('rep-count');
      repEl.style.transform = 'scale(1.3)';
      repEl.style.color = '#00ff88';
      setTimeout(() => {
        repEl.style.transform = '';
        repEl.style.color = '';
      }, 300);
    }
    
    if (metrics.current_angle !== null && metrics.current_angle !== undefined) {
      sessionData.angles.push(metrics.current_angle);
    }
    if (metrics.symmetry_score) {
      sessionData.symmetryScores.push(metrics.symmetry_score);
    }
    if (metrics.rom) {
      sessionData.romValues.push(metrics.rom);
    }
  } catch (error) {
    console.error('Error fetching metrics:', error);
    document.getElementById('status').textContent = '● ERROR';
    document.getElementById('status').className = 'status-indicator error';
  }
}

document.getElementById('reset-btn').addEventListener('click', async () => {
  try {
    await fetch(`${API_BASE}/reset`, { method: 'POST' });
    sessionData = { angles: [], symmetryScores: [], romValues: [] };
    repCount = 0;
    updateUI({ rep_count: 0, state: 'REST', current_angle: null, symmetry_score: 0, rom: 0 });
  } catch (error) {
    console.error('Error resetting:', error);
  }
});

document.getElementById('end-session').addEventListener('click', async () => {
  const avgSymmetry = sessionData.symmetryScores.length > 0
    ? sessionData.symmetryScores.reduce((a, b) => a + b, 0) / sessionData.symmetryScores.length
    : 0;
  
  const maxROM = sessionData.romValues.length > 0
    ? Math.max(...sessionData.romValues)
    : 0;
  
  const currentMetrics = await fetch(`${API_BASE}/metrics`).then(r => r.json());
  
  const metrics = {
    timestamp: new Date().toISOString(),
    exercise: "exercise",
    valid_reps: currentMetrics.rep_count || 0,
    symmetry_score: Math.round(avgSymmetry),
    rom: Math.round(maxROM),
    tempo_up: null,
    tempo_down: null
  };

  try {
    const res = await fetch(`${API_BASE}/analytics`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(metrics)
    });

    if (res.ok) {
      alert("Session saved successfully!");
      document.getElementById('reset-btn').click();
    } else {
      alert("Failed to save session.");
    }
  } catch (error) {
    console.error('Error saving session:', error);
    alert("Error saving session: " + error.message);
  }
});

setInterval(fetchMetrics, 150);
fetchMetrics();

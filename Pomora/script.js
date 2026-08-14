// ===============================
// Pomora Advanced Dashboard Script
// ===============================

// ----- Timer Settings -----
const FOCUS_TIME = 25 * 60;
const BREAK_TIME = 5 * 60;

let timeLeft = FOCUS_TIME;
let timerInterval = null;
let isRunning = false;
let isBreak = false;

// ----- Elements -----
const timerDisplay = document.getElementById('timer');
const sessionLabel = document.getElementById('sessionLabel');

const startBtn = document.getElementById('startBtn');
const pauseBtn = document.getElementById('pauseBtn');
const resetBtn = document.getElementById('resetBtn');

const goalCount = document.getElementById('goalCount');
const focusHours = document.getElementById('focusHours');
const streakCount = document.getElementById('streakCount');

const themeToggle = document.getElementById('themeToggle');

// ----- Load Saved Data -----
let completedSessions =
  parseInt(localStorage.getItem('pomoraSessions')) || 0;

let totalFocusMinutes =
  parseInt(localStorage.getItem('pomoraFocusMinutes')) || 0;

let streak =
  parseInt(localStorage.getItem('pomoraStreak')) || 0;

// ----- Update Dashboard -----
function updateStats() {
  goalCount.textContent = completedSessions;

  const hours = (totalFocusMinutes / 60).toFixed(1);
  focusHours.textContent = `${hours}h`;

  streakCount.textContent = `${streak} days`;
}

updateStats();

// ----- Timer Display -----
function updateDisplay() {
  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;

  timerDisplay.textContent =
    `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

updateDisplay();

// ----- Save Data -----
function saveData() {
  localStorage.setItem('pomoraSessions', completedSessions);
  localStorage.setItem('pomoraFocusMinutes', totalFocusMinutes);
  localStorage.setItem('pomoraStreak', streak);
}

// ----- Notification Sound -----
function playNotification() {
  const audio = new Audio(
    'https://actions.google.com/sounds/v1/alarms/alarm_clock.ogg'
  );

  audio.play();
}

// ----- Start Timer -----
function startTimer() {
  if (isRunning) return;

  isRunning = true;

  startBtn.innerHTML =
    '<i class="fa-solid fa-spinner fa-spin"></i> Running';

  timerInterval = setInterval(() => {
    timeLeft--;
    updateDisplay();

    if (timeLeft <= 0) {
      clearInterval(timerInterval);
      isRunning = false;

      startBtn.innerHTML =
        '<i class="fa-solid fa-play"></i> Start';

      playNotification();

      // ----- Focus finished -----
      if (!isBreak) {
        completedSessions++;
        totalFocusMinutes += 25;

        // Simple streak update
        streak = Math.max(streak, 1);

        saveData();
        updateStats();

        isBreak = true;
        timeLeft = BREAK_TIME;
        sessionLabel.textContent = 'Break Time ☕';

        alert('🎉 Great job! Time for a 5-minute break.');
      }

      // ----- Break finished -----
      else {
        isBreak = false;
        timeLeft = FOCUS_TIME;
        sessionLabel.textContent = 'Focus Time 🎯';

        alert('🚀 Break over! Back to focus.');
      }

      updateDisplay();
    }
  }, 1000);
}

// ----- Pause Timer -----
function pauseTimer() {
  clearInterval(timerInterval);
  isRunning = false;

  startBtn.innerHTML =
    '<i class="fa-solid fa-play"></i> Resume';
}

// ----- Reset Timer -----
function resetTimer() {
  clearInterval(timerInterval);

  isRunning = false;
  isBreak = false;
  timeLeft = FOCUS_TIME;

  sessionLabel.textContent = 'Focus Time 🎯';

  startBtn.innerHTML =
    '<i class="fa-solid fa-play"></i> Start';

  updateDisplay();
}

// ----- Theme Toggle -----
function loadTheme() {
  const savedTheme = localStorage.getItem('pomoraTheme');

  if (savedTheme === 'light') {
    document.body.classList.add('light-theme');
    themeToggle.textContent = '☀️';
  }
}

loadTheme();

themeToggle.addEventListener('click', () => {
  document.body.classList.toggle('light-theme');

  const isLight =
    document.body.classList.contains('light-theme');

  if (isLight) {
    localStorage.setItem('pomoraTheme', 'light');
    themeToggle.textContent = '☀️';
  } else {
    localStorage.setItem('pomoraTheme', 'dark');
    themeToggle.textContent = '🌙';
  }
});

// ----- Button Events -----
startBtn.addEventListener('click', startTimer);
pauseBtn.addEventListener('click', pauseTimer);
resetBtn.addEventListener('click', resetTimer);

// ----- Task Persistence -----
const taskList = document.getElementById('taskList');

function saveTasks() {
  localStorage.setItem('pomoraTasks', taskList.innerHTML);
}

const savedTasks = localStorage.getItem('pomoraTasks');

if (savedTasks) {
  taskList.innerHTML = savedTasks;
}

taskList.addEventListener('change', saveTasks);

// ----- Initial UI -----
updateDisplay();
updateStats();

console.log('🍅 Pomora loaded successfully!');
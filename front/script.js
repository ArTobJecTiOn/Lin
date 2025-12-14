// ============================================
// API Configuration
// ============================================
const API_BASE = 'http://localhost:8000/api/v1';

// Auth state
let currentUser = null;
let authToken = localStorage.getItem('authToken');

// ============================================
// API Helpers
// ============================================
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };
  
  if (authToken && !options.skipAuth) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers
    });

    if (response.status === 401) {
      // Token expired
      logout();
      return null;
    }

    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || 'Request failed');
    }

    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

// ============================================
// Authentication Functions
// ============================================
async function login(username, password) {
  try {
    const data = await apiRequest('/auth/login', {
      method: 'POST',
      skipAuth: true,
      body: JSON.stringify({ username, password })
    });

    if (data && data.access_token) {
      authToken = data.access_token;
      localStorage.setItem('authToken', authToken);
      await loadCurrentUser();
      return true;
    }
    return false;
  } catch (error) {
    throw error;
  }
}

async function register(username, email, password, displayName = null) {
  try {
    const data = await apiRequest('/auth/register', {
      method: 'POST',
      skipAuth: true,
      body: JSON.stringify({ 
        username, 
        email, 
        password,
        display_name: displayName 
      })
    });

    if (data && data.access_token) {
      authToken = data.access_token;
      localStorage.setItem('authToken', authToken);
      await loadCurrentUser();
      return true;
    }
    return false;
  } catch (error) {
    throw error;
  }
}

function logout() {
  authToken = null;
  currentUser = null;
  localStorage.removeItem('authToken');
  updateUIForAuth();
  showPage('home');
}

async function loadCurrentUser() {
  if (!authToken) {
    console.log('No auth token, showing login button');
    updateUIForAuth();
    return;
  }

  try {
    console.log('Loading current user...');
    const data = await apiRequest('/auth/me');
    currentUser = data;
    console.log('User loaded:', currentUser);
    updateUIForAuth();
  } catch (error) {
    console.error('Failed to load user:', error);
    logout();
  }
}

function updateUIForAuth() {
  const profileBtn = document.getElementById('headerProfileBtn');
  const profileName = profileBtn.querySelector('.profile-name');
  const headerAvatar = profileBtn.querySelector('.header-avatar');

  if (currentUser) {
    // Пользователь вошел - показываем имя
    profileName.textContent = currentUser.display_name || currentUser.username;
    profileBtn.style.cursor = 'pointer';
    profileBtn.title = 'Мой профиль';
    
    if (currentUser.avatar_url) {
      headerAvatar.style.backgroundImage = `url(${currentUser.avatar_url})`;
      headerAvatar.style.backgroundSize = 'cover';
      headerAvatar.style.backgroundPosition = 'center';
    } else {
      // Показываем аватар по умолчанию с первой буквой имени
      headerAvatar.style.backgroundImage = '';
      headerAvatar.style.backgroundColor = '#ff2e4c';
      headerAvatar.textContent = (currentUser.username || 'U')[0].toUpperCase();
      headerAvatar.style.display = 'flex';
      headerAvatar.style.alignItems = 'center';
      headerAvatar.style.justifyContent = 'center';
      headerAvatar.style.fontWeight = '600';
      headerAvatar.style.fontSize = '14px';
    }
  } else {
    // Пользователь не вошел - показываем кнопку "Войти"
    profileName.textContent = 'Войти';
    profileBtn.style.cursor = 'pointer';
    profileBtn.title = 'Войти в аккаунт';
    headerAvatar.style.backgroundImage = '';
    headerAvatar.style.backgroundColor = '#1a1f2a';
    headerAvatar.textContent = '';
  }
}

// ============================================
// Video/Post API Functions
// ============================================
async function loadVideos(filters = {}) {
  try {
    // В реальном приложении можно фильтровать по agent_id, map_id
    const videos = await apiRequest('/videos/');
    return videos || [];
  } catch (error) {
    console.error('Failed to load videos:', error);
    return [];
  }
}

async function loadUserVideos(userId) {
  try {
    const videos = await apiRequest(`/videos/user/${userId}`);
    return videos || [];
  } catch (error) {
    console.error('Failed to load user videos:', error);
    return [];
  }
}

async function likeVideo(videoId) {
  try {
    await apiRequest(`/videos/${videoId}/like`, { method: 'POST' });
  } catch (error) {
    console.error('Failed to like video:', error);
  }
}

async function dislikeVideo(videoId) {
  try {
    await apiRequest(`/videos/${videoId}/dislike`, { method: 'POST' });
  } catch (error) {
    console.error('Failed to dislike video:', error);
  }
}

// ============================================
// UI Functions
// ============================================
function renderVideoCard(video) {
  const card = document.createElement('article');
  card.className = 'card';
  card.dataset.agent = video.agent?.name || 'Unknown';
  card.dataset.side = video.side || 'Unknown';
  card.dataset.owner = video.owner?.username || 'Anonymous';

  const tagText = video.side === 'Attack' ? 'АТАКА' : 
                  video.side === 'Defense' ? 'ОБОРОНА' : 'ФРАГМЕНТ';

  card.innerHTML = `
    <div class="thumb" style="${video.thumbnail_url ? `background-image:url(${video.thumbnail_url}); background-size:cover;` : ''}"></div>
    <span class="tag">${tagText}</span>
    <h3>${video.title}</h3>
    <p>${video.map?.name || 'Unknown'} • ${video.side || 'N/A'} • ${video.owner?.username || 'Anonymous'}</p>
    <div class="card-footer">
      <span>${video.views || 0} просмотров • ${formatDate(video.created_at)}</span>
      <span>👍 ${video.likes || 0} 👎 ${video.dislikes || 0}</span>
    </div>
  `;

  return card;
}

function formatDate(dateString) {
  const date = new Date(dateString);
  const now = new Date();
  const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) return 'сегодня';
  if (diffDays === 1) return 'вчера';
  if (diffDays < 7) return `${diffDays} дней назад`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} недель назад`;
  return date.toLocaleDateString('ru-RU');
}

async function renderHomeGrid() {
  const grid = document.getElementById('homeGrid');
  grid.innerHTML = '<p style="color:#b4b7c4; text-align:center; grid-column: 1/-1;">Загрузка...</p>';
  
  const videos = await loadVideos();
  grid.innerHTML = '';

  if (videos.length === 0) {
    grid.innerHTML = '<p style="color:#b4b7c4; text-align:center; grid-column: 1/-1;">Нет видео</p>';
    return;
  }

  videos.forEach(video => {
    grid.appendChild(renderVideoCard(video));
  });
}

async function renderProfileGrid() {
  if (!currentUser) {
    showPage('home');
    return;
  }

  const grid = document.getElementById('profileGrid');
  const profileName = document.getElementById('profileName');
  
  profileName.textContent = `Профиль — ${currentUser.username}`;
  grid.innerHTML = '<p style="color:#b4b7c4; text-align:center; grid-column: 1/-1;">Загрузка...</p>';

  const videos = await loadUserVideos(currentUser.id);
  grid.innerHTML = '';

  if (videos.length === 0) {
    grid.innerHTML = '<p style="color:#b4b7c4; text-align:center; grid-column: 1/-1;">У вас пока нет видео</p>';
    return;
  }

  videos.forEach(video => {
    grid.appendChild(renderVideoCard(video));
  });
}

// ============================================
// Navigation
// ============================================
function showPage(pageName) {
  // Hide all pages
  document.getElementById('homeGrid').style.display = 'none';
  document.getElementById('profileSection').style.display = 'none';
  document.getElementById('profileEdit').style.display = 'none';

  // Show requested page
  if (pageName === 'home') {
    document.getElementById('homeGrid').style.display = 'grid';
    renderHomeGrid();
  } else if (pageName === 'profile') {
    if (!currentUser) {
      openAuthModal();
      return;
    }
    document.getElementById('profileSection').style.display = 'block';
    renderProfileGrid();
  } else if (pageName === 'profileEdit') {
    if (!currentUser) {
      openAuthModal();
      return;
    }
    document.getElementById('profileEdit').style.display = 'block';
    loadProfileEditData();
  }

  // Update nav active state
  document.querySelectorAll('.nav a').forEach(link => {
    link.classList.remove('active');
  });
}

function loadProfileEditData() {
  if (!currentUser) return;

  document.getElementById('inputUsername').value = currentUser.username || '';
  document.getElementById('inputEmail').value = currentUser.email || '';
  
  const avatarPreview = document.getElementById('avatarPreview');
  if (currentUser.avatar_url) {
    avatarPreview.style.backgroundImage = `url(${currentUser.avatar_url})`;
  }
}

// ============================================
// Modal Functions
// ============================================
function openAuthModal() {
  document.getElementById('authModal').style.display = 'flex';
}

function closeAuthModal() {
  document.getElementById('authModal').style.display = 'none';
  document.getElementById('loginMessage').textContent = '';
  document.getElementById('registerMessage').textContent = '';
}

// ============================================
// Event Listeners - Init
// ============================================
document.addEventListener('DOMContentLoaded', async () => {
  // Load current user if token exists
  await loadCurrentUser();
  
  // Show home page
  showPage('home');

  // ========== HEADER NAV ==========
  document.querySelectorAll('.nav a').forEach(link => {
    link.addEventListener('click', (e) => {
      const page = e.target.dataset.link;
      
      document.querySelectorAll('.nav a').forEach(a => a.classList.remove('active'));
      e.target.classList.add('active');

      if (page === 'home') {
        showPage('home');
      } else if (page === 'strategies') {
        showPage('home'); // For now
      } else if (page === 'gallery') {
        showPage('home'); // For now
      } else if (page === 'forum') {
        showPage('home'); // For now
      }
    });
  });

  // ========== PROFILE BUTTON ==========
  document.getElementById('headerProfileBtn').addEventListener('click', () => {
    console.log('Profile button clicked, currentUser:', currentUser);
    if (currentUser && currentUser.id) {
      // Пользователь вошел - показываем профиль
      showPage('profile');
    } else {
      // Пользователь не вошел - показываем форму входа
      openAuthModal();
    }
  });

  // ========== AUTH MODAL ==========
  document.getElementById('authClose').addEventListener('click', closeAuthModal);
  
  document.getElementById('tabLogin').addEventListener('click', () => {
    document.getElementById('loginForm').style.display = 'block';
    document.getElementById('registerForm').style.display = 'none';
    document.getElementById('tabLogin').classList.add('active');
    document.getElementById('tabRegister').classList.remove('active');
  });

  document.getElementById('tabRegister').addEventListener('click', () => {
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('registerForm').style.display = 'block';
    document.getElementById('tabLogin').classList.remove('active');
    document.getElementById('tabRegister').classList.add('active');
  });

  document.getElementById('openRegisterFromLogin').addEventListener('click', () => {
    document.getElementById('tabRegister').click();
  });

  document.getElementById('openLoginFromRegister').addEventListener('click', () => {
    document.getElementById('tabLogin').click();
  });

  // ========== LOGIN FORM ==========
  document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const messageEl = document.getElementById('loginMessage');

    try {
      messageEl.textContent = 'Вход...';
      messageEl.style.color = '#b4b7c4';
      
      await login(username, password);
      
      messageEl.textContent = 'Успешный вход!';
      messageEl.style.color = '#4ade80';
      
      setTimeout(() => {
        closeAuthModal();
        showPage('home');
      }, 500);
    } catch (error) {
      messageEl.textContent = `Ошибка: ${error.message}`;
      messageEl.style.color = '#ff2e4c';
    }
  });

  // ========== REGISTER FORM ==========
  document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('regUsername').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    const messageEl = document.getElementById('registerMessage');

    try {
      messageEl.textContent = 'Регистрация...';
      messageEl.style.color = '#b4b7c4';
      
      await register(username, email, password);
      
      messageEl.textContent = 'Регистрация успешна!';
      messageEl.style.color = '#4ade80';
      
      setTimeout(() => {
        closeAuthModal();
        showPage('home');
      }, 500);
    } catch (error) {
      messageEl.textContent = `Ошибка: ${error.message}`;
      messageEl.style.color = '#ff2e4c';
    }
  });

  // ========== PROFILE EDIT ==========
  document.getElementById('saveProfile').addEventListener('click', async () => {
    // TODO: Implement profile update
    alert('Обновление профиля (в разработке)');
  });

  document.getElementById('cancelEdit').addEventListener('click', () => {
    showPage('profile');
  });

  document.getElementById('toggleShowPassword').addEventListener('click', () => {
    const input = document.getElementById('inputPassword');
    const btn = document.getElementById('toggleShowPassword');
    
    if (input.type === 'password') {
      input.type = 'text';
      btn.textContent = 'Скрыть';
    } else {
      input.type = 'password';
      btn.textContent = 'Показать';
    }
  });

  // ========== FILTERS ==========
  document.querySelectorAll('.filter-tab').forEach(tab => {
    tab.addEventListener('click', (e) => {
      const targetTab = e.target.dataset.tab;
      
      document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
      e.target.classList.add('active');

      document.querySelectorAll('.filter-group').forEach(g => g.classList.remove('active'));
      document.getElementById(targetTab).classList.add('active');
    });
  });

  document.querySelectorAll('.filter-chip').forEach(chip => {
    chip.addEventListener('click', (e) => {
      const group = e.target.closest('.filter-group');
      group.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
      e.target.classList.add('active');
    });
  });

  document.getElementById('resetFilters').addEventListener('click', () => {
    document.querySelectorAll('.filter-chip').forEach((chip, index) => {
      chip.classList.remove('active');
      if (index === 0) chip.classList.add('active');
    });
  });

  document.getElementById('applyFilters').addEventListener('click', () => {
    // TODO: Apply filters to video grid
    alert('Фильтры применены (в разработке)');
  });
});

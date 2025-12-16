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

    // Только если это авторизованный запрос (не login/register)
    if (response.status === 401 && !options.skipAuth) {
      // Token expired - разлогиниваем пользователя
      logout();
      throw new Error('Сессия истекла. Войдите снова');
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

// ============================================
// Settings Functions
// ============================================
async function updateUserProfile(displayName, newPassword, confirmPassword, currentPassword) {
  try {
    const updates = {};
    
    // Update display name if provided
    if (displayName && displayName !== currentUser.display_name) {
      updates.display_name = displayName;
    }
    
    // Handle password change
    if (newPassword) {
      if (newPassword !== confirmPassword) {
        throw new Error('Пароли не совпадают');
      }
      if (newPassword.length < 6) {
        throw new Error('Пароль должен быть не менее 6 символов');
      }
      if (!currentPassword) {
        throw new Error('Введите текущий пароль для подтверждения');
      }
      updates.new_password = newPassword;
      updates.current_password = currentPassword;
    }

    if (Object.keys(updates).length === 0) {
      throw new Error('Нет изменений для сохранения');
    }

    // Call API to update profile
    const data = await apiRequest(`/users/${currentUser.id}`, {
      method: 'PUT',
      body: JSON.stringify(updates)
    });

    return data;
  } catch (error) {
    throw error;
  }
}

async function uploadAvatar(file) {
  try {
    // Create FormData for file upload
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/users/${currentUser.id}/avatar`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`
      },
      body: formData
    });

    if (response.status === 401) {
      logout();
      throw new Error('Сессия истекла');
    }

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to upload avatar');
    }

    return data;
  } catch (error) {
    throw error;
  }
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
    const response = await apiRequest(`/videos/user/${userId}`);
    console.log('User videos response:', response);
    // API возвращает {videos: [...], count: ...}
    if (response && response.videos) {
      return response.videos;
    }
    return [];
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
  card.style.cursor = 'pointer';

  const tagText = video.side === 'Attack' ? 'АТАКА' : 
                  video.side === 'Defense' ? 'ОБОРОНА' : 'ФРАГМЕНТ';

  card.innerHTML = `
    <div class="thumb" style="${video.video_url ? `background-image:linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url(${video.thumbnail_url || video.video_url}); background-size:cover;` : ''} display:flex; align-items:center; justify-content:center;">
      <span style="font-size: 48px;">▶️</span>
    </div>
    <span class="tag">${tagText}</span>
    <h3>${video.title}</h3>
    <p>${video.map?.name || 'Unknown'} • ${video.side || 'N/A'} • ${video.owner?.username || 'Anonymous'}</p>
    <div class="card-footer">
      <span>${video.views || 0} просмотров • ${formatDate(video.created_at)}</span>
      <span>👍 ${video.likes || 0} 👎 ${video.dislikes || 0}</span>
    </div>
  `;

  // Add click handler to open video player
  card.addEventListener('click', () => {
    openVideoPlayer(video);
  });

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
  console.log('Home videos:', videos);
  grid.innerHTML = '';

  if (!videos || videos.length === 0) {
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

  console.log('Loading user videos for user:', currentUser.id);
  const videos = await loadUserVideos(currentUser.id);
  console.log('Loaded videos type:', typeof videos, 'is array:', Array.isArray(videos), 'videos:', videos);
  grid.innerHTML = '';

  if (!videos || !Array.isArray(videos) || videos.length === 0) {
    grid.innerHTML = '<p style="color:#b4b7c4; text-align:center; grid-column: 1/-1;">У вас пока нет видео</p>';
    return;
  }

  videos.forEach(video => {
    grid.appendChild(renderVideoCard(video));
  });

  // Reinitialize upload button when profile is shown
  initializeUploadButton();
}

// ============================================
// Navigation
// ============================================
function showPage(pageName) {
  // Hide all pages
  document.getElementById('homeGrid').style.display = 'none';
  document.getElementById('profileSection').style.display = 'none';
  document.getElementById('profileEdit').style.display = 'none';
  
  // Close dropdown when changing pages
  const profileDropdown = document.getElementById('profileDropdown');
  if (profileDropdown) {
    profileDropdown.style.display = 'none';
  }

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

// Video player functions
let currentVideoId = null;

function openVideoPlayer(video) {
  console.log('[VIDEO PLAYER] Opening video player for:', video);
  currentVideoId = video.id;
  
  const videoPlayer = document.getElementById('videoPlayer');
  const videoPlayerTitle = document.getElementById('videoPlayerTitle');
  const videoPlayerDescription = document.getElementById('videoPlayerDescription');
  const videoPlayerViews = document.getElementById('videoPlayerViews');
  const videoPlayerLikes = document.getElementById('videoPlayerLikes');
  const closeBtn = document.getElementById('videoPlayerClose');
  
  videoPlayer.src = video.video_url || '';
  videoPlayerTitle.textContent = video.title || 'Видео';
  videoPlayerDescription.textContent = video.description || 'Нет описания';
  videoPlayerViews.textContent = `👁️ ${video.views || 0} просмотров`;
  videoPlayerLikes.textContent = `👍 ${video.likes || 0} | 👎 ${video.dislikes || 0}`;
  
  // Wire close button
  closeBtn.onclick = closeVideoPlayer;
  
  document.getElementById('videoPlayerModal').style.display = 'flex';
  videoPlayer.play();
}

function closeVideoPlayer() {
  const videoPlayer = document.getElementById('videoPlayer');
  videoPlayer.pause();
  document.getElementById('videoPlayerModal').style.display = 'none';
}

// Video upload functions
function openUploadVideoModal() {
  console.log('[VIDEO UPLOAD] Opening upload modal');
  const uploadModal = document.getElementById('uploadVideoModal');
  if (!uploadModal) {
    console.error('[VIDEO UPLOAD] Upload modal not found!');
    return;
  }
  document.getElementById('uploadTitle').value = '';
  document.getElementById('uploadDescription').value = '';
  document.getElementById('uploadAgent').value = '';
  document.getElementById('uploadSide').value = '';
  document.getElementById('uploadVideoFile').value = '';
  document.getElementById('uploadMessage').textContent = '';
  document.getElementById('uploadProgress').style.display = 'none';
  uploadModal.style.display = 'flex';
  console.log('[VIDEO UPLOAD] Upload modal opened');
}

function closeUploadVideoModal() {
  document.getElementById('uploadVideoModal').style.display = 'none';
}

// Initialize upload button
function initializeUploadButton() {
  console.log('[VIDEO UPLOAD] Initializing upload button');
  const uploadBtn = document.getElementById('uploadVideoBtn');
  if (uploadBtn) {
    console.log('[VIDEO UPLOAD] Upload button found, adding click listener');
    // Remove old listeners by cloning
    const newBtn = uploadBtn.cloneNode(true);
    uploadBtn.parentNode.replaceChild(newBtn, uploadBtn);
    
    newBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      console.log('[VIDEO UPLOAD] Upload button clicked!');
      if (!currentUser) {
        console.log('[VIDEO UPLOAD] No current user, opening auth modal');
        openAuthModal();
        return;
      }
      console.log('[VIDEO UPLOAD] Opening upload modal');
      openUploadVideoModal();
    });
  } else {
    console.error('[VIDEO UPLOAD] Upload button not found!');
  }
}

// ============================================
// Event Listeners - Init
// ============================================
document.addEventListener('DOMContentLoaded', async () => {
  // Load current user if token exists
  await loadCurrentUser();
  
  // Initialize upload button
  initializeUploadButton();
  
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

  // ========== PROFILE BUTTON & DROPDOWN ==========
  const profileDropdown = document.getElementById('profileDropdown');
  const profileBtn = document.getElementById('headerProfileBtn');
  
  profileBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    console.log('Profile button clicked, currentUser:', currentUser);
    
    if (currentUser && currentUser.id) {
      // Пользователь вошел - показываем/скрываем dropdown меню
      console.log('Showing dropdown menu');
      const isVisible = profileDropdown.style.display !== 'none';
      profileDropdown.style.display = isVisible ? 'none' : 'block';
    } else {
      // Пользователь не вошел - показываем форму входа
      console.log('User not logged in, opening auth modal');
      openAuthModal();
    }
  });

  // Закрыть dropdown при клике вне его
  document.addEventListener('click', (e) => {
    console.log('Document clicked, closing dropdown');
    profileDropdown.style.display = 'none';
  });

  // Не закрывать dropdown при клике на кнопке или внутри dropdown
  profileBtn.addEventListener('click', (e) => {
    e.stopPropagation();
  });

  profileDropdown.addEventListener('click', (e) => {
    e.stopPropagation();
  });

  // Переход в профиль
  document.getElementById('profileMenuBtn').addEventListener('click', () => {
    console.log('Profile menu clicked');
    showPage('profile');
    profileDropdown.style.display = 'none';
  });

  // Открытие настроек
  document.getElementById('settingsBtn').addEventListener('click', () => {
    console.log('Settings clicked');
    openSettingsModal();
    profileDropdown.style.display = 'none';
  });

  // Выход из профиля
  document.getElementById('logoutBtn').addEventListener('click', () => {
    console.log('Logout clicked');
    logout();
    profileDropdown.style.display = 'none';
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
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    const messageEl = document.getElementById('loginMessage');

    try {
      messageEl.textContent = 'Вход...';
      messageEl.style.color = '#b4b7c4';
      
      const success = await login(username, password);
      
      if (success) {
        messageEl.textContent = 'Успешный вход!';
        messageEl.style.color = '#4ade80';
        
        setTimeout(() => {
          closeAuthModal();
          showPage('home');
        }, 500);
      } else {
        messageEl.textContent = 'Ошибка: Неверные данные для входа';
        messageEl.style.color = '#ff2e4c';
      }
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
      
      const success = await register(username, email, password);
      
      if (success) {
        messageEl.textContent = 'Регистрация успешна!';
        messageEl.style.color = '#4ade80';
        
        setTimeout(() => {
          closeAuthModal();
          showPage('home');
        }, 500);
      } else {
        messageEl.textContent = 'Ошибка: Не удалось зарегистрироваться';
        messageEl.style.color = '#ff2e4c';
      }
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

  // ========== SETTINGS MODAL ==========
  function openSettingsModal() {
    const settingsModal = document.getElementById('settingsModal');
    const settingsDisplayName = document.getElementById('settingsDisplayName');
    const settingsAvatarPreview = document.getElementById('settingsAvatarPreview');
    
    // Load current user data into form
    if (currentUser) {
      settingsDisplayName.value = currentUser.display_name || '';
      
      // Set avatar preview
      if (currentUser.avatar_url) {
        settingsAvatarPreview.style.backgroundImage = `url(${currentUser.avatar_url})`;
        settingsAvatarPreview.style.backgroundSize = 'cover';
        settingsAvatarPreview.style.backgroundPosition = 'center';
        settingsAvatarPreview.textContent = '';
      } else {
        settingsAvatarPreview.style.backgroundImage = '';
        settingsAvatarPreview.style.backgroundColor = '#ff2e4c';
        settingsAvatarPreview.textContent = (currentUser.username || 'U')[0].toUpperCase();
      }
      
      // Clear password fields
      document.getElementById('settingsCurrentPassword').value = '';
      document.getElementById('settingsNewPassword').value = '';
      document.getElementById('settingsConfirmPassword').value = '';
      document.getElementById('settingsMessage').textContent = '';
    }
    
    settingsModal.style.display = 'flex';
  }

  function closeSettingsModal() {
    document.getElementById('settingsModal').style.display = 'none';
  }

  document.getElementById('settingsClose').addEventListener('click', closeSettingsModal);
  document.getElementById('settingsCancelBtn').addEventListener('click', closeSettingsModal);

  // Close settings modal when clicking outside
  document.getElementById('settingsModal').addEventListener('click', (e) => {
    if (e.target.id === 'settingsModal') {
      closeSettingsModal();
    }
  });

  // Avatar file upload button
  document.getElementById('settingsAvatarBtn').addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('settingsAvatarInput').click();
  });

  // Preview avatar when file is selected
  document.getElementById('settingsAvatarInput').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const preview = document.getElementById('settingsAvatarPreview');
        preview.style.backgroundImage = `url(${event.target.result})`;
        preview.style.backgroundSize = 'cover';
        preview.style.backgroundPosition = 'center';
        preview.textContent = '';
      };
      reader.readAsDataURL(file);
    }
  });

  // Settings form submission
  document.getElementById('settingsForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const displayName = document.getElementById('settingsDisplayName').value.trim();
    const currentPassword = document.getElementById('settingsCurrentPassword').value;
    const newPassword = document.getElementById('settingsNewPassword').value;
    const confirmPassword = document.getElementById('settingsConfirmPassword').value;
    const avatarFile = document.getElementById('settingsAvatarInput').files[0];
    const messageEl = document.getElementById('settingsMessage');

    try {
      messageEl.textContent = 'Сохранение...';
      messageEl.style.color = '#b4b7c4';

      // Update profile (display name and/or password)
      if (displayName || newPassword) {
        await updateUserProfile(displayName, newPassword, confirmPassword, currentPassword);
      }

      // Upload avatar if selected
      if (avatarFile) {
        await uploadAvatar(avatarFile);
      }

      // Reload user data
      await loadCurrentUser();

      messageEl.textContent = 'Профиль успешно обновлен!';
      messageEl.style.color = '#4ade80';

      setTimeout(() => {
        closeSettingsModal();
      }, 1500);
    } catch (error) {
      messageEl.textContent = `Ошибка: ${error.message}`;
      messageEl.style.color = '#ff2e4c';
    }
  });

  // ========== VIDEO UPLOAD ==========
  // Attach event listeners for upload modal controls
  document.getElementById('uploadVideoClose').addEventListener('click', closeUploadVideoModal);
  document.getElementById('uploadCancelBtn').addEventListener('click', closeUploadVideoModal);

  // Close upload modal when clicking outside
  document.getElementById('uploadVideoModal').addEventListener('click', (e) => {
    if (e.target.id === 'uploadVideoModal') {
      closeUploadVideoModal();
    }
  });

  // Upload video form submission
  const uploadForm = document.getElementById('uploadVideoForm');
  if (uploadForm) {
    uploadForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      console.log('[VIDEO UPLOAD] Form submitted');
      
      const title = document.getElementById('uploadTitle').value.trim();
      const description = document.getElementById('uploadDescription').value.trim();
      const agent = document.getElementById('uploadAgent').value;
      const side = document.getElementById('uploadSide').value;
      const videoFile = document.getElementById('uploadVideoFile').files[0];
      const messageEl = document.getElementById('uploadMessage');
      const progressEl = document.getElementById('uploadProgress');
      const progressBar = document.getElementById('uploadProgressBar');
      const progressText = document.getElementById('uploadProgressText');

      console.log('[VIDEO UPLOAD] Form data:', { title, agent, side, videoFile: videoFile?.name });

      if (!title || !agent || !side || !videoFile) {
        messageEl.textContent = 'Заполните все обязательные поля';
        messageEl.style.color = '#ff2e4c';
        console.error('[VIDEO UPLOAD] Missing fields');
        return;
      }

    if (videoFile.size > 500 * 1024 * 1024) { // 500 MB limit
      messageEl.textContent = 'Размер видео не должен превышать 500 MB';
      messageEl.style.color = '#ff2e4c';
      return;
    }

    try {
      messageEl.textContent = '';
      progressEl.style.display = 'block';
      progressBar.style.width = '0%';
      
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('title', title);
      formData.append('description', description);
      formData.append('agent', agent);
      formData.append('side', side);
      formData.append('file', videoFile);

      // Upload with progress tracking
      const xhr = new XMLHttpRequest();
      
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const percentComplete = (e.loaded / e.total) * 100;
          progressBar.style.width = percentComplete + '%';
          progressText.textContent = `Загруженно: ${Math.round(percentComplete)}%`;
        }
      });

      xhr.addEventListener('load', async () => {
        console.log('[VIDEO UPLOAD] XHR load event, status:', xhr.status);
        if (xhr.status === 200 || xhr.status === 201) {
          try {
            const data = JSON.parse(xhr.responseText);
            console.log('[VIDEO UPLOAD] Upload successful, data:', data);
            progressText.textContent = 'Видео загружено!';
            messageEl.textContent = 'Видео успешно загружено!';
            messageEl.style.color = '#4ade80';
            
            setTimeout(() => {
              closeUploadVideoModal();
              renderProfileGrid();
            }, 1500);
          } catch (e) {
            console.error('[VIDEO UPLOAD] Error parsing response:', e);
            messageEl.textContent = 'Ошибка обработки ответа';
            messageEl.style.color = '#ff2e4c';
          }
        } else {
          console.error('[VIDEO UPLOAD] Upload failed with status:', xhr.status);
          console.error('[VIDEO UPLOAD] Response text:', xhr.responseText);
          try {
            const error = JSON.parse(xhr.responseText);
            console.error('[VIDEO UPLOAD] Error details:', error);
            if (error.detail) {
              if (Array.isArray(error.detail)) {
                // Validation errors
                messageEl.textContent = `Ошибка: ${error.detail.map(e => e.msg).join(', ')}`;
              } else {
                messageEl.textContent = `Ошибка: ${error.detail}`;
              }
            } else {
              messageEl.textContent = 'Ошибка загрузки';
            }
          } catch (e) {
            messageEl.textContent = `Ошибка: ${xhr.statusText}`;
          }
          messageEl.style.color = '#ff2e4c';
          progressEl.style.display = 'none';
        }
      });

      xhr.addEventListener('error', () => {
        console.error('[VIDEO UPLOAD] XHR error event');
        messageEl.textContent = 'Ошибка при загрузке видео';
        messageEl.style.color = '#ff2e4c';
        progressEl.style.display = 'none';
      });

      console.log('[VIDEO UPLOAD] Sending request to:', `${API_BASE}/videos/upload`);
      xhr.open('POST', `${API_BASE}/videos/upload`);
      xhr.setRequestHeader('Authorization', `Bearer ${authToken}`);
      xhr.send(formData);

    } catch (error) {
      console.error('[VIDEO UPLOAD] Exception:', error);
      messageEl.textContent = `Ошибка: ${error.message}`;
      messageEl.style.color = '#ff2e4c';
      progressEl.style.display = 'none';
    }
    });
  } else {
    console.error('[VIDEO UPLOAD] Upload form not found!');
  }
});

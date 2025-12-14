# Обработка ошибок и примеры использования API

## 📝 HTTP статусы ошибок

| Статус | Описание | Пример |
|--------|---------|--------|
| 400 | Bad Request | Невалидные данные |
| 401 | Unauthorized | Отсутствует/истёк токен |
| 403 | Forbidden | Доступ запрещен |
| 404 | Not Found | Ресурс не найден |
| 500 | Server Error | Ошибка сервера |

## 🔴 Примеры ошибок API

```json
// 401 - Неавторизован
{
  "detail": "Not authenticated"
}

// 400 - Неверные данные
{
  "detail": "Username already exists"
}

// 404 - Не найдено
{
  "detail": "Post not found"
}

// 500 - Ошибка сервера
{
  "detail": "Internal server error"
}
```

## 💻 Примеры JavaScript с обработкой ошибок

### React Hook для API запросов

```javascript
import { useState } from 'react';

export const useApi = (baseURL = 'http://localhost:8000/api/v1') => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const request = async (endpoint, options = {}) => {
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
      };

      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }

      const response = await fetch(`${baseURL}${endpoint}`, {
        ...options,
        headers,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'API Error');
      }

      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { request, loading, error };
};

// Использование
function MyComponent() {
  const { request, loading, error } = useApi();

  const handleLogin = async (username, password) => {
    try {
      const data = await request('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ username, password })
      });
      localStorage.setItem('token', data.access_token);
    } catch (err) {
      console.error('Login failed:', err.message);
    }
  };

  return (
    <div>
      {error && <p style={{color: 'red'}}>{error}</p>}
      {loading && <p>Loading...</p>}
      <button onClick={() => handleLogin('user', 'pass')}>
        Login
      </button>
    </div>
  );
}
```

### Axios с обработкой ошибок

```javascript
import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
});

// Интерцептор для добавления токена
API.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

// Интерцептор для обработки ошибок
API.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Токен истёк или отсутствует
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Использование
async function createPost(title, slug, content) {
  try {
    const response = await API.post('/posts/', {
      owner_id: 'user-uuid',
      title,
      slug,
      content,
    });
    return response.data;
  } catch (error) {
    if (error.response?.status === 400) {
      console.error('Validation error:', error.response.data.detail);
    } else if (error.response?.status === 404) {
      console.error('User not found');
    } else {
      console.error('Unknown error:', error.message);
    }
    throw error;
  }
}
```

### Vue 3 с Composable

```javascript
// useApi.js
import { ref } from 'vue';

export function useApi(baseURL = 'http://localhost:8000/api/v1') {
  const loading = ref(false);
  const error = ref(null);

  const request = async (endpoint, options = {}) => {
    loading.value = true;
    error.value = null;

    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
      };

      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }

      const response = await fetch(`${baseURL}${endpoint}`, {
        ...options,
        headers,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'API Error');
      }

      return data;
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return { request, loading, error };
}

// Component.vue
<template>
  <div>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="loading" class="spinner">Loading...</div>
    <button @click="handleRegister">Register</button>
  </div>
</template>

<script setup>
import { useApi } from './useApi';

const { request, loading, error } = useApi();

async function handleRegister() {
  try {
    const data = await request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        username: 'newuser',
        email: 'user@example.com',
        password: 'password123',
      }),
    });
    localStorage.setItem('token', data.access_token);
  } catch (err) {
    console.error('Registration failed:', err);
  }
}
</script>
```

## 🛡️ Безопасность

### ✅ Делать:
- Хранить токен в `localStorage` или `sessionStorage`
- Отправлять токен в заголовке `Authorization: Bearer <token>`
- Обновлять страницу при 401 ошибке
- Валидировать данные на фронтенде

### ❌ Не делать:
- Хранить пароль в localStorage
- Отправлять токен в URL
- Игнорировать ошибки 401
- Доверять данным только фронтенду

## 📱 Мобильные приложения

### React Native / Expo

```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = 'http://your-server:8000/api/v1';

async function login(username, password) {
  try {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    await AsyncStorage.setItem('token', data.access_token);
    
    return data;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}

async function apiCall(endpoint, options = {}) {
  const token = await AsyncStorage.getItem('token');
  
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (response.status === 401) {
    await AsyncStorage.removeItem('token');
    // Перенаправить на логин
  }

  return response.json();
}
```

## ✅ Чек-лист для фронтенда

- [ ] Сохранение токена после входа
- [ ] Отправка токена во всех авторизованных запросах
- [ ] Обработка 401 ошибок (выход из системы)
- [ ] Показ сообщений об ошибках пользователю
- [ ] Валидация формы перед отправкой
- [ ] Загрузка данных при монтировании компонента
- [ ] Обработка состояния loading
- [ ] Переадресация на /login при отсутствии токена

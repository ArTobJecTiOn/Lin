#!/bin/bash
# API Testing Examples with cURL
# Запуск: bash api_examples.sh

BASE_URL="http://localhost:8000/api/v1"

echo "🚀 Linap2 API Examples"
echo "====================="

# ============================================
# AUTHENTICATION
# ============================================

echo ""
echo "📝 1. Registration (Регистрация)"
echo "================================"

curl -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password123",
    "display_name": "John Doe"
  }' | jq

# Сохраняем токен в переменную (для Unix/Linux/Mac)
# TOKEN=$(curl -s -X POST "$BASE_URL/auth/register" ... | jq -r '.access_token')

echo ""
echo "🔐 2. Login (Вход)"
echo "================="

curl -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure_password123"
  }' | jq

# ============================================
# USERS
# ============================================

echo ""
echo "👤 3. Get Current User (Получить текущего пользователя)"
echo "======================================================"

# Замените TOKEN на ваш реальный токен
TOKEN="your_token_here"

curl -X GET "$BASE_URL/users/me" \
  -H "Authorization: Bearer $TOKEN" | jq

echo ""
echo "👤 4. Get User by ID"
echo "==================="

USER_ID="123e4567-e89b-12d3-a456-426614174000"

curl -X GET "$BASE_URL/users/$USER_ID" \
  -H "Authorization: Bearer $TOKEN" | jq

echo ""
echo "👤 5. Get User by Username"
echo "=========================="

curl -X GET "$BASE_URL/users/username/john_doe" \
  -H "Authorization: Bearer $TOKEN" | jq

echo ""
echo "✏️ 6. Update User Profile"
echo "========================"

curl -X PUT "$BASE_URL/users/$USER_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "John Doe Updated",
    "bio": "Software Developer",
    "locale": "en_US",
    "timezone": "UTC"
  }' | jq

# ============================================
# POSTS
# ============================================

echo ""
echo "📝 7. Create Post (Создать пост)"
echo "==============================="

curl -X POST "$BASE_URL/posts/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "owner_id": "'$USER_ID'",
    "title": "My First Post",
    "slug": "my-first-post",
    "content": "This is my first post content",
    "excerpt": "Short summary of the post"
  }' | jq

echo ""
echo "📖 8. Get Published Posts"
echo "======================="

curl -X GET "$BASE_URL/posts/" | jq

echo ""
echo "📖 9. Get Posts by User"
echo "====================="

curl -X GET "$BASE_URL/posts/user/$USER_ID" \
  -H "Authorization: Bearer $TOKEN" | jq

echo ""
echo "📖 10. Get Post by Slug"
echo "====================="

curl -X GET "$BASE_URL/posts/slug/my-first-post" \
  -H "Authorization: Bearer $TOKEN" | jq

echo ""
echo "✏️ 11. Update Post"
echo "================="

POST_ID="123e4567-e89b-12d3-a456-426614174111"

curl -X PUT "$BASE_URL/posts/$POST_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title",
    "content": "Updated content"
  }' | jq

echo ""
echo "📤 12. Publish Post"
echo "=================="

curl -X PUT "$BASE_URL/posts/$POST_ID/publish" \
  -H "Authorization: Bearer $TOKEN" | jq

echo ""
echo "❌ 13. Delete Post"
echo "================="

curl -X DELETE "$BASE_URL/posts/$POST_ID" \
  -H "Authorization: Bearer $TOKEN" | jq

# ============================================
# VIDEOS
# ============================================

echo ""
echo "🎥 14. Create Video"
echo "=================="

curl -X POST "$BASE_URL/videos/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "owner_id": "'$USER_ID'",
    "title": "My Video",
    "video_url": "https://example.com/video.mp4",
    "description": "Video description",
    "thumb_url": "https://example.com/thumb.jpg",
    "agent": "Agent Phoenix",
    "side": "defending"
  }' | jq

echo ""
echo "🎥 15. Get Videos by Agent"
echo "========================="

curl -X GET "$BASE_URL/videos/agent/Agent%20Phoenix" | jq

echo ""
echo "👍 16. Like Video"
echo "================"

VIDEO_ID="123e4567-e89b-12d3-a456-426614174222"

curl -X POST "$BASE_URL/videos/$VIDEO_ID/like" \
  -H "Authorization: Bearer $TOKEN" | jq

echo ""
echo "👎 17. Dislike Video"
echo "==================="

curl -X POST "$BASE_URL/videos/$VIDEO_ID/dislike" \
  -H "Authorization: Bearer $TOKEN" | jq

# ============================================
# TAGS
# ============================================

echo ""
echo "🏷️ 18. Create Tag"
echo "================"

curl -X POST "$BASE_URL/tags/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Python",
    "slug": "python"
  }' | jq

echo ""
echo "🏷️ 19. Get All Tags"
echo "=================="

curl -X GET "$BASE_URL/tags/" | jq

# ============================================
# LIKES
# ============================================

echo ""
echo "❤️ 20. Like Post"
echo "==============="

curl -X POST "$BASE_URL/likes/post/$POST_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "'$USER_ID'"
  }' | jq

echo ""
echo "❤️ 21. Get Post Likes"
echo "==================="

curl -X GET "$BASE_URL/likes/post/$POST_ID" | jq

# ============================================
# COMMENTS
# ============================================

echo ""
echo "💬 22. Create Comment"
echo "==================="

curl -X POST "$BASE_URL/comments/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "post_id": "'$POST_ID'",
    "author_id": "'$USER_ID'",
    "content": "Great post!"
  }' | jq

echo ""
echo "💬 23. Get Post Comments"
echo "======================"

curl -X GET "$BASE_URL/comments/post/$POST_ID" | jq

# ============================================
# ERROR HANDLING
# ============================================

echo ""
echo "❌ 24. Test Error - Unauthorized"
echo "==============================="

curl -X GET "$BASE_URL/users/me" | jq

echo ""
echo "❌ 25. Test Error - Not Found"
echo "============================"

curl -X GET "$BASE_URL/posts/nonexistent" | jq

echo ""
echo "✅ Done! Все примеры выполнены."

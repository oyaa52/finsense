<template>
  <div class="community-container">
    <!-- Create Post Section -->
    <div class="create-post">
      <textarea
        v-model="newPostContent"
        placeholder="무슨 일이 일어나고 있나요?"
        rows="3"
      ></textarea>
      <div class="post-actions">
        <input
          type="file"
          ref="fileInput"
          @change="handleFileSelect"
          accept="image/*"
          style="display: none"
        />
        <button @click="$refs.fileInput.click()" class="image-btn">
          <i class="fas fa-image"></i>
        </button>
        <button @click="createPost" :disabled="!newPostContent.trim()">
          게시하기
        </button>
      </div>
      <img v-if="selectedImage" :src="imagePreview" class="image-preview" />
    </div>

    <!-- Posts Feed -->
    <div class="posts-feed">
      <div v-if="loading" class="loading">로딩 중...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else class="posts">
        <div v-for="post in posts" :key="post.id" class="post-card">
          <div class="post-header">
            <img :src="post.user.profile_image || '/default-avatar.png'" class="avatar" />
            <div class="user-info">
              <span class="username">{{ post.user.username }}</span>
              <span class="timestamp">{{ formatDate(post.created_at) }}</span>
            </div>
            <button 
              v-if="post.user.id !== currentUserId" 
              class="follow-btn" 
              :class="{ 'following': post.user.is_following }"
              @click="post.user.is_following ? unfollowUser(post.user.id) : followUser(post.user.id)"
            >
              {{ post.user.is_following ? '언팔로우' : '팔로우' }}
            </button>
          </div>
          
          <div class="post-content">
            <p>{{ post.content }}</p>
            <img v-if="post.image" :src="post.image" class="post-image" />
          </div>

          <div class="post-actions">
            <button @click="likePost(post.id)" :class="{ liked: post.is_liked }">
              <i :class="post.is_liked ? 'fas fa-heart' : 'far fa-heart'"></i>
              <span>좋아요 {{ post.likes_count }}</span>
            </button>
            <button @click="toggleComments(post)">
              <i class="far fa-comment"></i>
              <span>댓글 {{ post.comments.length }}</span>
            </button>
          </div>

          <!-- Comments Section -->
          <div v-if="post.showComments" class="comments-section">
            <div class="comment-input">
              <input
                v-model="newComments[post.id]"
                placeholder="댓글을 작성하세요..."
                @keyup.enter="createComment(post.id)"
              />
              <button @click="createComment(post.id)">댓글</button>
            </div>
            <div class="comments-list">
              <div v-for="comment in post.comments" :key="comment.id" class="comment">
                <img :src="comment.user.profile_image || '/default-avatar.png'" class="avatar" />
                <div class="comment-content">
                  <span class="username">{{ comment.user.username }}</span>
                  <p>{{ comment.content }}</p>
                  <span class="timestamp">{{ formatDate(comment.created_at) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useCommunityStore } from '@/stores/community'
import { useAuthStore } from '@/stores/authStore'
import { formatDistanceToNow } from 'date-fns'
import { ko } from 'date-fns/locale'

const store = useCommunityStore()
const authStore = useAuthStore()
const currentUserId = computed(() => authStore.getUserProfile?.id)
const newPostContent = ref('')
const selectedImage = ref(null)
const imagePreview = ref(null)
const newComments = ref({})

const loading = ref(false)
const error = ref(null)
const posts = ref([])

onMounted(async () => {
  await fetchPosts()
})

async function fetchPosts() {
  loading.value = true
  try {
    await store.fetchPosts()
    posts.value = store.posts
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

function handleFileSelect(event) {
  const file = event.target.files[0]
  if (file) {
    selectedImage.value = file
    imagePreview.value = URL.createObjectURL(file)
  }
}

async function createPost() {
  if (!newPostContent.value.trim()) return
  
  try {
    await store.createPost(newPostContent.value, selectedImage.value)
    newPostContent.value = ''
    selectedImage.value = null
    imagePreview.value = null
    await fetchPosts()
  } catch (err) {
    error.value = err.message
  }
}

async function likePost(postId) {
  try {
    await store.likePost(postId)
  } catch (err) {
    error.value = err.message
  }
}

function toggleComments(post) {
  post.showComments = !post.showComments
}

async function createComment(postId) {
  const content = newComments.value[postId]
  if (!content?.trim()) return

  try {
    await store.createComment(postId, content)
    newComments.value[postId] = ''
  } catch (err) {
    error.value = err.message
  }
}

async function followUser(userId) {
  try {
    await store.followUser(userId)
    await fetchPosts()
  } catch (err) {
    error.value = err.message
  }
}

async function unfollowUser(userId) {
  try {
    await store.unfollowUser(userId)
    await fetchPosts()
  } catch (err) {
    error.value = err.message
  }
}

function formatDate(date) {
  return formatDistanceToNow(new Date(date), { addSuffix: true, locale: ko })
}
</script>

<style scoped>
.community-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.create-post {
  background: white;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

textarea {
  width: 100%;
  border: none;
  resize: none;
  padding: 10px;
  margin-bottom: 10px;
  font-size: 16px;
}

.post-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.image-btn {
  background: none;
  border: none;
  color: #1da1f2;
  cursor: pointer;
  font-size: 20px;
}

button {
  background: #1da1f2;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.image-preview {
  max-width: 100%;
  max-height: 300px;
  margin-top: 10px;
  border-radius: 10px;
}

.post-card {
  background: white;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.post-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 10px;
}

.user-info {
  flex-grow: 1;
}

.username {
  font-weight: bold;
  display: block;
}

.timestamp {
  color: #657786;
  font-size: 14px;
}

.post-content {
  margin-bottom: 15px;
}

.post-image {
  max-width: 100%;
  border-radius: 10px;
  margin-top: 10px;
}

.post-actions {
  display: flex;
  gap: 20px;
  padding: 10px 0;
  border-top: 1px solid #eee;
  border-bottom: 1px solid #eee;
}

.post-actions button {
  background: none;
  color: #657786;
  padding: 5px 10px;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.2s ease;
}

.post-actions button:hover {
  color: #1da1f2;
}

.post-actions button.liked {
  color: #e0245e;
}

.post-actions button.liked:hover {
  color: #c01e4f;
}

.post-actions i {
  font-size: 1.1em;
}

.comments-section {
  margin-top: 15px;
  border-top: 1px solid #eee;
  padding-top: 15px;
}

.comment-input {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.comment-input input {
  flex-grow: 1;
  padding: 8px;
  border: 1px solid #eee;
  border-radius: 20px;
}

.comment {
  display: flex;
  margin-bottom: 10px;
}

.comment-content {
  flex-grow: 1;
  background: #f5f8fa;
  padding: 10px;
  border-radius: 10px;
}

.loading, .error {
  text-align: center;
  padding: 20px;
  color: #657786;
}

.error {
  color: #e0245e;
}

.follow-btn {
  background: #1da1f2;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.follow-btn.following {
  background: #dc3545;
}

.follow-btn:hover {
  opacity: 0.9;
}
</style> 
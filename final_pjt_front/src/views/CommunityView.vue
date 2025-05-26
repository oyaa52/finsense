<template>
  <div class="community-container">
    <!-- Create Post Section -->
    <div class="create-post">
      <textarea v-model="newPostContent" placeholder="무슨 일이 일어나고 있나요?" rows="3"></textarea>
      <div class="post-actions">
        <input type="file" ref="fileInput" @change="handleFileSelect" accept="image/*" style="display: none" />
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
            <router-link :to="{ name: 'userProfile', params: { username: post.user.username } }" class="profile-link">
              <img :src="post.user.profile_image || defaultProfileImageUrl" class="avatar" />
            </router-link>
            <div class="user-info">
              <router-link :to="{ name: 'userProfile', params: { username: post.user.username } }" class="username-link">
                <span class="username">{{ post.user.username }}</span>
              </router-link>
              <span class="timestamp">{{ formatDate(post.created_at) }}</span>
            </div>
            <button v-if="post.user.id !== currentUserId" class="follow-btn"
              :class="{ 'following': post.user.is_following }"
              @click="post.user.is_following ? unfollowUser(post.user.id) : followUser(post.user.id)">
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
            <div
              v-if="replyingToCommentId && post.comments.some(c => c.id === replyingToCommentId || (c.replies && c.replies.some(r => r.id === replyingToCommentId)))"
              class="replying-to-info">
              <span>@{{ replyingToUsername }}님에게 답글 남기는 중...</span>
              <button @click="replyingToCommentId = null; replyingToUsername = ''" class="cancel-reply-btn">취소</button>
            </div>
            <div class="comment-input">
              <input v-model="newComments[post.id]" :placeholder="commentPlaceholder"
                @keyup.enter="createComment(post.id)" :ref="el => commentInputRefs[`post-${post.id}`] = el" />
              <button @click="createComment(post.id)">{{ replyingToCommentId ? '답글 게시' : '댓글 게시' }}</button>
            </div>
            <div class="comments-list">
              <div v-for="comment in post.comments" :key="comment.id" class="comment-item">
                <div class="comment">
                  <img :src="comment.user.profile_image || defaultProfileImageUrl" class="avatar comment-avatar" />
                  <div class="comment-body">
                    <div class="comment-header">
                      <span class="username">{{ comment.user.username }}</span>
                      <span class="timestamp">{{ formatDate(comment.created_at) }}</span>
                    </div>
                    <p class="comment-text">{{ comment.content }}</p>
                    <button @click="setReplyingTo(comment, post)" class="reply-btn">답글</button>
                  </div>
                </div>

                <div v-if="comment.replies && comment.replies.length > 0" class="replies-list">
                  <div v-for="reply in comment.replies" :key="reply.id" class="comment-item reply-item">
                    <div class="comment">
                      <img :src="reply.user.profile_image || defaultProfileImageUrl" class="avatar comment-avatar" />
                      <div class="comment-body">
                        <div class="comment-header">
                          <span class="username">{{ reply.user.username }}</span>
                          <span class="timestamp">{{ formatDate(reply.created_at) }}</span>
                        </div>
                        <p class="comment-text">
                          <span v-if="reply.parent_comment_author_username" class="reply-target">
                            @{{ reply.parent_comment_author_username }}
                          </span>
                          {{ reply.content }}
                        </p>
                        <button @click="setReplyingTo(reply, post)" class="reply-btn">답글</button>
                      </div>
                    </div>
                  </div>
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
import { ref, onMounted, computed, nextTick } from 'vue'
import { useCommunityStore } from '@/stores/community'
import { useAuthStore } from '@/stores/authStore'
import { formatDistanceToNow } from 'date-fns'
import { ko } from 'date-fns/locale'

const defaultProfileImageUrl = new URL('@/assets/default_profile.png', import.meta.url).href
const store = useCommunityStore()
const authStore = useAuthStore()
const currentUserId = computed(() => authStore.getUserProfile?.id)
const newPostContent = ref('')
const selectedImage = ref(null)
const imagePreview = ref(null)
const newComments = ref({})
const replyingToCommentId = ref(null)
const replyingToUsername = ref('')
const commentInputRefs = ref({})

const loading = ref(false)
const error = ref(null)
const posts = ref([])

// Helper function to find a comment (and its parent array and index if it's a reply)
// This will be used to add replies correctly.
function findCommentInPost(post, commentId) {
  if (!post || !post.comments) return null;

  for (let i = 0; i < post.comments.length; i++) {
    const comment = post.comments[i];
    if (comment.id === commentId) {
      return comment; // Found top-level comment
    }
    if (comment.replies) {
      for (let j = 0; j < comment.replies.length; j++) {
        const reply = comment.replies[j];
        if (reply.id === commentId) {
          return reply; // Found reply
        }
      }
    }
  }
  return null;
}

onMounted(async () => {
  await fetchPosts()
})

async function fetchPosts() {
  loading.value = true
  try {
    await store.fetchPosts()
    posts.value = store.posts.map(p => ({
      ...p,
      showComments: p.showComments || false
    }))
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
  const content = newComments.value[postId];
  if (!content?.trim()) return;

  // console.log('Creating comment:', { 
  //   postId, 
  //   content, 
  //   replyingToCommentId: replyingToCommentId.value 
  // });

  try {
    const newCommentData = await store.createComment(postId, content, replyingToCommentId.value);

    // Find the post in the local 'posts' ref
    const targetPost = posts.value.find(p => p.id === postId);

    if (targetPost) {
      if (replyingToCommentId.value) { // It's a reply
        const parentComment = findCommentInPost(targetPost, replyingToCommentId.value);
        if (parentComment) {
          if (!parentComment.replies) {
            parentComment.replies = [];
          }
          parentComment.replies.push(newCommentData);
        } else {
          // Fallback or error: parent comment not found, add as a top-level comment for now
          // This case should ideally not happen if replyingToCommentId is correctly set.
          console.warn('Parent comment not found for reply. Adding as top-level comment.');
          targetPost.comments.push(newCommentData);
        }
      } else { // It's a new top-level comment
        if (!targetPost.comments) {
          targetPost.comments = [];
        }
        targetPost.comments.push(newCommentData);
      }
    }

    newComments.value[postId] = '';
    replyingToCommentId.value = null;
    replyingToUsername.value = '';
    // await fetchPosts(); // No longer calling fetchPosts, local state is updated
  } catch (err) {
    console.error('Error creating comment:', err);
    error.value = err.message;
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

const commentPlaceholder = computed(() => {
  if (replyingToUsername.value) {
    return `@${replyingToUsername.value}님에게 답글 작성...`;
  }
  return '댓글을 작성하세요...';
})

function setReplyingTo(comment, post) {
  console.log('Setting reply to:', { commentId: comment.id, username: comment.user.username });
  replyingToCommentId.value = comment.id;
  replyingToUsername.value = comment.user.username;
  nextTick(() => {
    const inputEl = commentInputRefs.value[`post-${post.id}`];
    if (inputEl) {
      inputEl.focus();
    }
  });
}
</script>

<style scoped>
.community-container {
  max-width: 800px;
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

.posts-feed {
  margin-top: 1.5rem;
}

.posts {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  align-items: start;
}

.post-card {
  background-color: #ffffff;
  border: 1px solid #dbdbdb;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  padding: 1rem;
  padding-bottom: 0.5rem;
}

.post-header {
  display: flex;
  align-items: center;
  padding-bottom: 0.75rem;
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
  padding-top: 0.75rem;
  padding-bottom: 0.75rem;
  flex-grow: 1;
}

.post-image {
  max-width: 100%;
  border-radius: 8px;
  margin-top: 0.75rem;
}

.post-actions {
  display: flex;
  gap: 1rem;
  margin-top: auto;
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
  border-top: 1px solid #eee;
  padding-top: 1rem;
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

.comment-item {
  margin-bottom: 0.75rem;
}

.comment {
  display: flex;
  align-items: flex-start;
}

.comment-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  margin-right: 8px;
}

.comment-body {
  flex-grow: 1;
  background: #f0f2f5;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  font-size: 0.9rem;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.comment-header .username {
  font-weight: 600;
}

.comment-header .timestamp {
  font-size: 0.75rem;
  color: #657786;
}

.comment-text {
  margin: 0;
  line-height: 1.4;
  word-wrap: break-word;
}

.reply-btn {
  background: none !important;
  border: none !important;
  color: #657786 !important;
  padding: 0.25rem 0.5rem !important;
  font-size: 0.8rem !important;
  margin-top: 0.25rem;
  cursor: pointer;
}

.reply-btn:hover {
  text-decoration: underline;
  color: #1da1f2 !important;
}

.replies-list {
  margin-left: 40px;
  margin-top: 0.5rem;
  border-left: 2px solid #e0e0e0;
  padding-left: 0.75rem;
}

.reply-item {
  /* 대댓글 자체에 특별한 스타일이 필요하면 여기에 추가 */
  /* 예: 약간 다른 배경색 등 */
}

.replying-to-info {
  font-size: 0.85rem;
  color: #657786;
  margin-bottom: 0.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.25rem 0.5rem;
  background-color: #e9ecef;
  border-radius: 4px;
}

.cancel-reply-btn {
  font-size: 0.75rem !important;
  color: #6c757d !important;
  background: none !important;
  border: none !important;
  padding: 0.1rem 0.3rem !important;
  cursor: pointer;
}

.cancel-reply-btn:hover {
  text-decoration: underline;
}

.reply-target {
  color: #007bff;
  font-weight: 500;
  margin-right: 0.25em;
}

.comment-input button {
  font-size: 0.9rem;
  padding: 6px 12px !important;
}

.loading,
.error {
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

.profile-link,
.username-link {
  text-decoration: none;
  color: inherit; /* 부모 요소의 색상 상속 */
}

.username-link:hover .username {
  text-decoration: underline; /* 호버 시 밑줄 */
  color: #007bff; /* 호버 시 색상 변경 (선택 사항) */
}

.profile-link:hover .avatar {
  opacity: 0.8; /* 프로필 이미지 호버 효과 (선택 사항) */
}

@media (max-width: 480px) {
  .posts {
    grid-template-columns: 1fr;
  }
}
</style>
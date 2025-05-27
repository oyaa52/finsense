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
        <button @click="createPost" :disabled="!newPostContent.trim() && !selectedImage">
          게시하기
        </button>
      </div>
      <img v-if="imagePreview && selectedImage" :src="imagePreview" class="image-preview" />
    </div>

    <!-- Posts Feed -->
    <div class="posts-feed" ref="feedContainer">
      <div v-if="store.loading && posts.length === 0" class="loading">로딩 중...</div>
      <div v-else-if="store.error && posts.length === 0" class="error">{{ store.error }}</div>
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


            <!-- More Options Menu for Posts -->
            <div v-if="currentUserId && post.user.id === currentUserId" class="post-options-container">
              <button @click.stop="togglePostOptionsMenu(post.id)" class="more-options-btn">
                <i class="fas fa-ellipsis-h"></i>
              </button>
              <div v-if="openPostOptionsMenu === post.id" class="options-menu post-options-menu">
                <button v-if="currentUserId && post.user.id === currentUserId"
                        @click="handleDeletePost(post.id)" class="menu-item delete-item">
                  <i class="fas fa-trash-alt"></i> 삭제
                </button>
              </div>
            </div>
            <!-- End More Options Menu for Posts -->
          </div>

          <div class="post-content">
            <p>{{ post.content }}</p>
            <img v-if="post.image" :src="post.image" class="post-image" />
          </div>

          <div class="post-actions">
            <button @click="likePost(post.id)" :class="{ liked: post.is_liked }">
              <i :class="post.is_liked ? 'fas fa-heart' : 'far fa-heart'"></i>
              <span> {{ post.likes_count }}</span>
            </button>
            <button @click="toggleComments(post)">
              <i class="far fa-comment"></i>
              <span> {{ post.comments ? post.comments.length : 0 }}</span>
            </button>
          </div>

          <!-- Comments Section -->
          <div v-if="post.showComments" class="comments-section">
            <div
              v-if="replyingToCommentId && activePostForReply && activePostForReply.id === post.id" 
              class="replying-to-info">
              <span>@{{ replyingToUsername }}님에게 답글 남기는 중...</span>
              <button @click="cancelReply" class="cancel-reply-btn">취소</button>
            </div>
            <form class="comment-input" @submit.prevent="handleCommentSubmit(post.id)">
              <input v-model="newComments[post.id]" 
                     :placeholder="commentPlaceholder(post.id)" 
                     :ref="el => commentInputRefs[`post-${post.id}`] = el" />
              <button type="submit" 
                      class="submit-comment-btn" 
                      :aria-label="replyingToCommentId && activePostForReply && activePostForReply.id === post.id ? '답글 게시' : '댓글 게시'"
                      :title="replyingToCommentId && activePostForReply && activePostForReply.id === post.id ? '답글 게시' : '댓글 게시'">
                <i class="far fa-note-sticky"></i>
              </button>
            </form>
            <div class="comments-list">
              <comment-item 
                v-for="comment in post.comments"
                :key="comment.id"
                :comment="comment"
                :post="post"
                :depth="0"
                :defaultProfileImageUrl="defaultProfileImageUrl"
                :formatDateFunction="formatDate"
                @initiate-reply="handleInitiateReply"
              />
            </div>
          </div>
        </div>
      </div>
      <div v-if="store.isLoadingMore" class="loading">
        <i class="fas fa-spinner fa-spin"></i> 더 많은 게시글을 불러오는 중...
      </div>
      <div v-if="!store.hasMorePosts && posts.length > 0 && !store.loading && !store.isLoadingMore" class="no-more-posts">
        모든 게시글을 불러왔습니다.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useCommunityStore } from '@/stores/community'
import { useAuthStore } from '@/stores/authStore'
import { useAlertStore } from '@/stores/alertStore'
import { formatDistanceToNow } from 'date-fns'
import { ko } from 'date-fns/locale'
import { useRouter } from 'vue-router'
import CommentItem from '@/components/CommentItem.vue'

const defaultProfileImageUrl = new URL('@/assets/default_profile.png', import.meta.url).href
const store = useCommunityStore()
const authStore = useAuthStore()
const router = useRouter()
const alertStore = useAlertStore()

const currentUserId = computed(() => {
  const id = authStore.user?.pk;
  return id;
})

const posts = computed(() => {
  return store.posts
})

const newPostContent = ref('')
const selectedImage = ref(null)
const imagePreview = ref(null)
const newComments = ref({})
const replyingToCommentId = ref(null)
const replyingToUsername = ref('')
const activePostForReply = ref(null)
const commentInputRefs = ref({})
const openPostOptionsMenu = ref(null); // New state for post options menu

const feedContainer = ref(null)
const scrollableContainer = ref(null)

const formatDate = (dateString) => {
  if (!dateString) return ''
  return formatDistanceToNow(new Date(dateString), { addSuffix: true, locale: ko })
}

const handleScroll = async () => {
  if (!scrollableContainer.value) {
    return;
  }
  const target = scrollableContainer.value === window ? document.documentElement : scrollableContainer.value;
  const { scrollTop, clientHeight, scrollHeight } = target;
  const nearBottomOfContainer = clientHeight + scrollTop >= scrollHeight - 150;

  if (nearBottomOfContainer && !store.isLoadingMore && store.hasMorePosts) {
    await store.fetchPosts();
  }
}

onMounted(async () => {
  await nextTick(); 
  let parent = feedContainer.value?.parentElement;
  let attempts = 0;
  while (parent && attempts < 10) { 
    const found = parent.closest('.content-area');
    if (found) {
      scrollableContainer.value = found;
      break;
    }
    parent = parent.parentElement;
    attempts++;
  }

  if (!scrollableContainer.value) {
    scrollableContainer.value = window; 
  }
  
  if (store.posts.length === 0 && store.hasMorePosts) { 
    await store.fetchPosts(true); 
  }

  if (scrollableContainer.value) {
    scrollableContainer.value.addEventListener('scroll', handleScroll);
  }
})

onUnmounted(() => {
  if (scrollableContainer.value) {
    scrollableContainer.value.removeEventListener('scroll', handleScroll);
  }
})

function handleFileSelect(event) {
  const file = event.target.files[0]
  if (file) {
    selectedImage.value = file
    imagePreview.value = URL.createObjectURL(file)
  } else {
    selectedImage.value = null
    imagePreview.value = null
  }
}

async function createPost() {
  if (!newPostContent.value.trim() && !selectedImage.value) {
    alertStore.openAlert({ title: '입력 오류', message: '내용을 입력하거나 이미지를 선택해주세요.', type: 'warning' });
    return
  }
  try {
    await store.createPost(newPostContent.value, selectedImage.value)
    newPostContent.value = ''
    selectedImage.value = null
    imagePreview.value = null

  } catch (err) {

    console.error("Error creating post in view:", err)
  }
}

async function likePost(postId) {
  if (!authStore.isAuthenticated) {
    alertStore.openAlert({
      title: '로그인 필요',
      message: '로그인이 필요한 기능입니다. 로그인 페이지로 이동하시겠습니까?',
      type: 'info',
      showConfirmButton: true,
      onConfirm: () => {
        router.push({ name: 'login' });
      }
    });
    return
  }
  try {
    await store.likePost(postId)

  } catch (err) {

    console.error("Error liking post in view:", err)
  }
}

function toggleComments(post) {
  post.showComments = !post.showComments
  if (!post.showComments) {
    if (activePostForReply.value && activePostForReply.value.id === post.id) {
        cancelReply();
    }
  }
}

const commentPlaceholder = (postId) => {
  if (replyingToCommentId.value && activePostForReply.value && activePostForReply.value.id === postId) {
    return `@${replyingToUsername.value}님에게 답글 남기기`;
  }
  return '댓글을 입력하세요...';
}

function handleInitiateReply({ comment, post }) {
  replyingToCommentId.value = comment.id;
  replyingToUsername.value = comment.user.username;
  activePostForReply.value = post; 

  nextTick(() => {
    const inputRefKey = `post-${post.id}`;
    const inputRef = commentInputRefs.value[inputRefKey];
    if (inputRef) {
      inputRef.focus();
    }
  });
}

function cancelReply() {
  replyingToCommentId.value = null;
  replyingToUsername.value = '';
  activePostForReply.value = null;
}

function handleCommentSubmit(postId) {

  createComment(postId);
}

async function createComment(postId) {
  if (!authStore.isAuthenticated) {
    alertStore.openAlert({ title: '로그인 필요', message: '로그인이 필요한 기능입니다.', type: 'info' });
    router.push({ name: 'login' });
    return;
  }

  const content = newComments.value[postId];

  if (!content?.trim()) {
    alertStore.openAlert({ title: '입력 오류', message: '댓글 내용을 입력해주세요.', type: 'warning' });
    return;
  }

  const finalContent = content.trim();

  try {
    await store.createComment(postId, finalContent, replyingToCommentId.value);
    
    if (newComments.value.hasOwnProperty(postId)) {
        newComments.value[postId] = ''; 
    }
    
    cancelReply();

  } catch (err) {
    const errorMessage = store.error || '댓글 작성 중 오류가 발생했습니다.';
    alert(errorMessage);
    console.error('[View] Error creating comment:', err);
  }
}

const togglePostOptionsMenu = (postId) => {
  if (openPostOptionsMenu.value === postId) {
    openPostOptionsMenu.value = null; // Close if already open
  } else {
    openPostOptionsMenu.value = postId; // Open for this post
  }
};

const handleDeletePost = async (postId) => { // 함수 이름이 handleDeletePost 였습니다.
  alertStore.openAlert({
    title: '게시글 삭제 확인',
    message: '정말로 이 게시글을 삭제하시겠습니까?',
    type: 'warning',
    showConfirmButton: true,
    onConfirm: async () => {
      try {
        await store.deletePost(postId); // communityStore의 deletePost 액션 호출
        // 성공 알림은 store.deletePost 내부에서 처리 (posts 목록 업데이트는 store의 getter나 watch로 처리되도록 권장)
        // posts.value = posts.value.filter(post => post.id !== postId); // 직접적인 목록 조작은 스토어에 위임하는 것이 좋음
      } catch (error) {
        console.error('Error deleting post in view:', error);
        // 실패 알림은 store.deletePost 내부에서 처리
      }
    }
  });
};
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

.create-post .post-actions {
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

.create-post .post-actions button:not(.image-btn) {
  background: #1da1f2;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
}

.create-post .post-actions button:disabled {
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
  position: relative;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 10px;
  object-fit: cover;
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

.post-content p { 
  margin-bottom: 10px; 
  white-space: pre-wrap; 
  word-break: break-word; 
}

.post-image {
  max-width: 100%;
  border-radius: 8px;
  margin-top: 0.75rem;
}

.post-card .post-actions {
  display: flex;
  gap: 1rem; 
  margin-top: auto; 
}

.post-card .post-actions button {
  background: none;
  color: #657786; 
  padding: 5px 10px;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.2s ease; 
  border: none; 
  cursor: pointer; 
  font-size: 0.9em; 
}

.post-card .post-actions button:hover {
  color: #1da1f2; 
}

.post-card .post-actions button.liked { 
  color: #e0245e; 
}
.post-card .post-actions button.liked i.fas { 
  color: #e0245e;
}

.post-card .post-actions button.liked:hover {
  color: #c01e4f; 
}

.post-card .post-actions i {
  font-size: 1.1em;
  margin: 0;
}

.post-card .post-actions button.liked i.fas {
  color: #e0245e;
}

.comments-section { 
  border-top: 1px solid #eee; 
  padding-top: 1rem; 
  margin-top: 15px; 
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

.comment-input button { 
  padding: 6px 12px !important; 
  background-color: transparent;
  color: #1da1f2;
  border: none; 
  border-radius: 20px; 
  cursor: pointer;
  font-size: 1.2rem;
}

.comment-input button:hover {
  color: #0c85d0;
}

.comments-list { 

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

.replying-to-info span { 
  margin-right: 8px;
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

.loading,
.error {
  text-align: center;
  padding: 20px; 
  color: #657786; 
}

.error {
  color: #e0245e; 
}

.posts-feed > .loading { 
  text-align: center;
  padding: 20px;
  color: #666; 
}
.posts-feed > .loading i { 
  margin-right: 8px;
}

.no-more-posts { 
  text-align: center;
  padding: 20px;
  color: #666; 
}

.follow-btn {
  padding: 8px 16px; 
  font-size: 0.9em; 
  border-radius: 20px; 
  cursor: pointer;
  border: 1px solid #1da1f2; 
  background-color: #1da1f2; 
  color: white; 
  transition: all 0.2s ease; 
}

.follow-btn.following {
  background: #dc3545; 
  border-color: #dc3545; 
}

.follow-btn:hover {
  opacity: 0.9; 
}

.profile-link,
.username-link {
  text-decoration: none;
  color: inherit; 
}

.username-link:hover .username {
  text-decoration: underline; 
  color: #007bff; 
}

.profile-link:hover .avatar {
  opacity: 0.8; 
}

/* Styles for More Options Menu */
.post-options-container {
  margin-left: auto;
  position: relative;
}

.more-options-btn {
  background: none;
  border: none;
  color: #657786;
  cursor: pointer;
  padding: 8px;
  font-size: 1.2em;
  line-height: 1;
}

.more-options-btn:hover {
  color: #1da1f2;
}

.options-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: white;
  border: 1px solid #dbdbdb;
  border-radius: 6px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  z-index: 10;
  min-width: 120px; 
  padding: 5px 0;
}

.options-menu .menu-item {
  display: block;
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  padding: 8px 12px;
  font-size: 0.9em;
  cursor: pointer;
}

.options-menu .menu-item:hover {
  background-color: #f5f5f5;
}

.options-menu .menu-item.delete-item {
  color: #e74c3c; /* Red color for delete */
}

.options-menu .menu-item.delete-item i {
  margin-right: 8px;
}
/* End Styles for More Options Menu */

@media (max-width: 480px) {
  .posts {
    grid-template-columns: 1fr;
  }
}
</style>
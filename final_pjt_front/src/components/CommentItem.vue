<template>
  <div class_name="comment-display-item" :style="{ 'margin-left': depth * 20 + 'px' }">
    <div class="comment">
      <img :src="comment.user.profile_image || defaultProfileImageUrl" class="avatar comment-avatar" />
      <div class="comment-body">
        <div class="comment-header">
          <span class="username">{{ comment.user.username }}</span>
          <span class="timestamp">{{ formatDateFunction(comment.created_at) }}</span>
        </div>
        <p class="comment-text">
          <span v-if="comment.parent_comment_author_username" class="reply-target">
            @{{ comment.parent_comment_author_username }}
          </span>
          {{ comment.content }}
        </p>
        <button @click="initiateReply" class="reply-btn">
          답글 ({{ comment.replies ? comment.replies.length : 0 }})
        </button>
        <!-- More Options Menu for Comments -->
        <div v-if="authStore.user && authStore.user.pk === comment.user.id" class="comment-options-container">
          <button @click.stop="toggleCommentOptionsMenu(comment.id)" class="more-options-btn">
            <i class="fas fa-ellipsis-h"></i>
          </button>
          <div v-if="openCommentOptionsMenu === comment.id" class="options-menu comment-options-menu">
            <button @click="handleDeleteComment(comment.id)" class="menu-item delete-item">
              <i class="fas fa-trash-alt"></i> 삭제
            </button>
          </div>
        </div>
        <!-- End More Options Menu for Comments -->
      </div>
    </div>

    <div v-if="comment.replies && comment.replies.length > 0" class="replies-list">
      <comment-item
        v-for="reply in comment.replies"
        :key="reply.id"
        :comment="reply"
        :post="post"
        :depth="depth + 1"
        :defaultProfileImageUrl="defaultProfileImageUrl"
        :formatDateFunction="formatDateFunction"
        @initiate-reply="$emit('initiate-reply', $event)" 
      />
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, computed, ref } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { useCommunityStore } from '@/stores/community'
import { useAlertStore } from '@/stores/alertStore'

const props = defineProps({
  comment: {
    type: Object,
    required: true
  },
  post: { // post is needed to associate the reply with the correct post
    type: Object,
    required: true
  },
  depth: {
    type: Number,
    default: 0
  },
  defaultProfileImageUrl: {
    type: String,
    required: true
  },
  formatDateFunction: {
    type: Function,
    required: true
  }
})

const emit = defineEmits(['initiate-reply'])
const authStore = useAuthStore()
const communityStore = useCommunityStore()
const alertStore = useAlertStore()
const openCommentOptionsMenu = ref(null); // New state for comment options menu

const initiateReply = () => {
  emit('initiate-reply', { comment: props.comment, post: props.post });
}

const toggleCommentOptionsMenu = (commentId) => {
  if (openCommentOptionsMenu.value === commentId) {
    openCommentOptionsMenu.value = null; // Close if already open
  } else {
    openCommentOptionsMenu.value = commentId; // Open for this comment
  }
};

async function handleDeleteComment() { // Removed commentId parameter, will use props.comment.id
  openCommentOptionsMenu.value = null; // Close the menu
  alertStore.openAlert({
    title: '댓글 삭제 확인',
    message: '정말로 이 댓글을 삭제하시겠습니까?',
    type: 'warning',
    showConfirmButton: true,
    onConfirm: async () => {
      try {
        await communityStore.deleteComment(props.post.id, props.comment.id);
        // 성공 알림은 communityStore.deleteComment 내부에서 처리한다고 가정
      } catch (error) {
        // 실패 알림은 communityStore.deleteComment 내부에서 처리한다고 가정
        // console.error('Error deleting comment in item:', error); 
        // alertStore.openAlert({ title: '오류', message: communityStore.error || '댓글 삭제 중 오류가 발생했습니다.', type: 'error' });
      }
    }
  });
}

async function handleFollowUser(targetUser) {
  openCommentOptionsMenu.value = null; // Close the menu
  if (!authStore.isAuthenticated) {
    alertStore.openAlert({
        title: '로그인 필요',
        message: '로그인이 필요한 기능입니다.',
        type: 'info'
        // router.push는 여기서 직접 사용하기 어려우므로, 필요시 이벤트 emit 또는 다른 방식 고려
    });
    return;
  }
  try {
    await communityStore.toggleFollowUser(targetUser.id);
    // 성공 알림 및 UI 업데이트는 communityStore 또는 부모 컴포넌트에서 처리
    // props.comment.user.is_following = true; // 직접적인 prop 변경은 피하는 것이 좋음
  } catch (error) {
    console.error('Error following user:', error);
    // 실패 알림은 communityStore.toggleFollowUser 내부에서 처리한다고 가정
    // alertStore.openAlert({ title: '오류', message: communityStore.error || '팔로우 처리 중 오류가 발생했습니다.', type: 'error' });
  }
}

async function handleUnfollowUser(targetUser) {
  openCommentOptionsMenu.value = null; // Close the menu
   if (!authStore.isAuthenticated) {
    alertStore.openAlert({
        title: '로그인 필요',
        message: '로그인이 필요한 기능입니다.',
        type: 'info'
    });
    return;
  }
  try {
    await communityStore.toggleFollowUser(targetUser.id); // toggleFollowUser가 팔로우/언팔로우 모두 처리
    // 성공 알림 및 UI 업데이트는 communityStore 또는 부모 컴포넌트에서 처리
    // props.comment.user.is_following = false; // 직접적인 prop 변경은 피하는 것이 좋음
  } catch (error) {
    console.error('Error unfollowing user:', error);
    // 실패 알림은 communityStore.toggleFollowUser 내부에서 처리한다고 가정
    // alertStore.openAlert({ title: '오류', message: communityStore.error || '언팔로우 처리 중 오류가 발생했습니다.', type: 'error' });
  }
}
</script>

<script>
// Recursive components need a name option if they are self-referencing in script,
// or if used with <component :is="...">. For SFC <template> self-reference, it's often automatic.
// Explicitly naming it here for clarity and robustness.
export default {
  name: 'CommentItem'
}
</script>

<style scoped>
.comment-display-item {
  /* Styles for each comment item, including recursive ones */
  /* margin-bottom: 0.75rem;  Moved from CommunityView's .comment-item */
}

.comment {
  display: flex;
  align-items: flex-start;
  margin-bottom: 0.5rem; /* Spacing between a comment and its direct replies block */
}

.avatar { /* Copied from CommunityView and potentially slightly adjusted */
  width: 32px;
  height: 32px;
  border-radius: 50%;
  margin-right: 8px;
  object-fit: cover;
}

.comment-avatar {
  /* Specific styles for comment avatars if different from post avatars */
}

.comment-body { /* Copied from CommunityView */
  flex-grow: 1;
  background: #f0f2f5;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  font-size: 0.9rem;
}

.comment-header { /* Copied from CommunityView */
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.comment-header .username { /* Copied from CommunityView */
  font-weight: 600;
  font-size: 0.9em;
}

.comment-header .timestamp { /* Copied from CommunityView */
  font-size: 0.75rem;
  color: #657786;
  margin-left: 8px;
}

.comment-text { /* Copied from CommunityView */
  margin: 0;
  line-height: 1.4;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.reply-target { /* Copied from CommunityView */
  color: #007bff;
  font-weight: 500;
  margin-right: 0.25em;
}

.reply-btn { /* Copied from CommunityView */
  background: none !important;
  border: none !important;
  color: #657786 !important;
  padding: 0.25rem 0.5rem !important;
  font-size: 0.8rem !important;
  margin-top: 0.25rem;
  cursor: pointer;
}

.reply-btn:hover { /* Copied from CommunityView */
  text-decoration: underline;
  color: #1da1f2 !important;
}

.delete-btn {
  background: none !important;
  border: none !important;
  color: #e74c3c !important;
  padding: 0.25rem 0.5rem !important;
  font-size: 0.8rem !important;
  margin-top: 0.25rem;
  margin-left: 8px;
  cursor: pointer;
}

.delete-btn:hover {
  text-decoration: underline;
  color: #c0392b !important;
}

.replies-list { /* Copied from CommunityView, for the container of child CommentItems */
  /* margin-left: 40px; /* Handled by depth prop now */
  /* margin-top: 0.5rem; */ /* Adjusted spacing */
  /* border-left: 2px solid #e0e0e0; /* This might look odd with margin-left, consider removing or adjusting */
  padding-left: 0.75rem; /* Original padding for replies list */
  display: flex;
  flex-direction: column;
  gap: 10px; /* Original gap for replies list */
}

/* Style for the direct child .comment-item inside .replies-list if needed, but direct styling in CommentItem.vue is better */
.replies-list > .comment-display-item {
   /* margin-bottom: 0.5rem; */ /* Add some space between replies in a list */
}

/* If a border-left was desired for child replies, it's better applied based on depth > 0 */
.comment-display-item[style*="margin-left"]:not([style*="margin-left: 0px"]) { /* Crude way to check if it's a reply */
  /* border-left: 2px solid #eee; */
  /* padding-left: 10px; */ /* If border is added, add padding too */
}

/* 댓글 삭제 버튼 스타일 */
.comment-delete-btn {
  background: none !important;
  border: none !important;
  color: #e74c3c !important; /* Red color for delete */
  padding: 0.25rem 0.5rem !important; 
  font-size: 0.8rem !important; 
  margin-top: 0.25rem;
  margin-left: 8px; /* Space from reply button */
  cursor: pointer;
}

.comment-delete-btn:hover {
  text-decoration: underline;
  color: #c0392b !important; /* Darker red on hover */
}

/* Styles for More Options Menu in Comments (similar to CommunityView) */
.comment-options-container {
  margin-left: auto; /* Pushes the button to the right of the reply button */
  position: relative;
  display: inline-block; /* To sit next to the reply button nicely */
}

.more-options-btn {
  background: none;
  border: none;
  color: #657786;
  cursor: pointer;
  padding: 0.25rem 0.5rem; /* Match reply-btn padding */
  font-size: 1em; /* Adjust icon size if needed, relative to text */
  line-height: 1; 
  vertical-align: middle; /* Align with text buttons */
}

.more-options-btn:hover {
  color: #1da1f2;
}

.options-menu {
  position: absolute;
  top: 100%; /* Position below the button */
  right: 0; 
  background-color: white;
  border: 1px solid #dbdbdb;
  border-radius: 6px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  z-index: 10;
  min-width: 120px;
  padding: 5px 0;
}

.comment-options-menu { /* Specific adjustments if needed */
  /* Example: Make it slightly smaller if comments are dense */
  /* min-width: 100px; */ 
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
  color: #e74c3c;
}

.options-menu .menu-item.delete-item i {
  margin-right: 8px;
}
/* End Styles for More Options Menu in Comments */

</style> 
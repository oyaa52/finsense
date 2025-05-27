import { defineStore } from 'pinia'
import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

const POSTS_PER_PAGE = 10; // 페이지 당 게시글 수 (API와 일치시켜야 함)

export const useCommunityStore = defineStore('community', {
  state: () => ({
    posts: [],
    currentPost: null,
    userProfileData: null,
    loading: false, // 초기 전체 로딩 상태
    error: null,
    followers: [],
    following: [],
    // --- 무한 스크롤을 위한 상태 추가 ---
    currentPage: 1,
    postsPerPage: POSTS_PER_PAGE,
    isLoadingMore: false, // 추가 데이터 로딩 상태
    hasMorePosts: true,   // 더 불러올 게시물이 있는지 여부
    // ---------------------------------
  }),

  actions: {
    async fetchPosts(isInitialFetch = false) {
      console.log(`[Store] fetchPosts called. Initial: ${isInitialFetch}, CurrentPage: ${this.currentPage}, HasMore: ${this.hasMorePosts}, IsLoadingMore: ${this.isLoadingMore}`);

      if (isInitialFetch) {
        this.currentPage = 1;
        this.posts = [];
        this.hasMorePosts = true;
        this.loading = true; // 초기 로딩 시작
        this.error = null;
      } else {
        if (this.isLoadingMore || !this.hasMorePosts) {
          console.log('[Store] fetchPosts skipped. LoadingMore: ' + this.isLoadingMore + ', HasMore: ' + this.hasMorePosts);
          return;
        }
        this.isLoadingMore = true; // 추가 로딩 시작
      }

      try {
        const authStore = useAuthStore();
        if (!authStore.accessToken) {
          // console.warn('[Store] Access token is missing. Proceeding without auth for public posts if applicable.');
        }

        console.log(`[Store] Requesting API: /api/v1/community/posts/?page=${this.currentPage}&page_size=${this.postsPerPage}`);
        const response = await axios.get('/api/v1/community/posts/', {
          params: {
            page: this.currentPage,
            page_size: this.postsPerPage
          }
        });

        console.log('[Store] API Response received:', JSON.parse(JSON.stringify(response.data)));

        if (response.data && response.data.results) {
          const fetchedPosts = response.data.results;
          console.log(`[Store] Fetched ${fetchedPosts.length} posts.`);
          if (fetchedPosts.length > 0) {
            this.posts = isInitialFetch ? fetchedPosts : [...this.posts, ...fetchedPosts];
            this.currentPage++;
            console.log(`[Store] Posts updated. New post count: ${this.posts.length}, Next page will be: ${this.currentPage}`);
          }

          const willHaveMorePosts = !(!response.data.next || fetchedPosts.length < this.postsPerPage);
          console.log(`[Store] Checking hasMorePosts. Next URL: ${response.data.next}, Fetched count: ${fetchedPosts.length}, PostsPerPage: ${this.postsPerPage}. Will have more: ${willHaveMorePosts}`);
          this.hasMorePosts = willHaveMorePosts;

        } else if (response.data && Array.isArray(response.data)) {
          const fetchedPosts = response.data;
          console.log(`[Store] Fetched ${fetchedPosts.length} posts (non-paginated).`);
          if (isInitialFetch) {
            this.posts = fetchedPosts;
          } else {
            this.posts = [...this.posts, ...fetchedPosts];
          }
          this.hasMorePosts = false;
          console.log('[Store] Non-paginated response. Posts updated, hasMorePosts set to false.');
        } else {
          this.hasMorePosts = false;
          console.warn('[Store] Unexpected API response structure for posts. Setting hasMorePosts to false. Response:', response.data);
        }

      } catch (error) {
        console.error('[Store] Error fetching posts:', error.response?.data || error.message);
        this.error = error.response?.data?.detail || error.message;
        this.hasMorePosts = false;
      } finally {
        if (isInitialFetch) {
          this.loading = false;
        }
        this.isLoadingMore = false;
        console.log(`[Store] fetchPosts finished. Loading: ${this.loading}, IsLoadingMore: ${this.isLoadingMore}, HasMore: ${this.hasMorePosts}`);
      }
    },

    async createPost(content, image = null) {
      this.loading = true
      try {
        const authStore = useAuthStore()
        if (!authStore.accessToken) {
          throw new Error('로그인이 필요합니다.')
        }
        const formData = new FormData()
        formData.append('content', content)
        if (image) {
          formData.append('image', image)
        }

        const response = await axios.post('/api/v1/community/posts/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Token ${authStore.accessToken}`
          }
        })
        await this.fetchPosts(true);
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async likePost(postId) {
      try {
        const authStore = useAuthStore()
        if (!authStore.accessToken) {
          throw new Error('로그인이 필요합니다.')
        }
        await axios.post(`/api/v1/community/posts/${postId}/like/`, {}, {
          headers: {
            'Authorization': `Token ${authStore.accessToken}`
          }
        })
        const post = this.posts.find(p => p.id === postId)
        if (post) {
          post.is_liked = !post.is_liked
          post.likes_count += post.is_liked ? 1 : -1
        }
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      }
    },

    async createComment(postId, content, parentCommentId = null) {
      const authStore = useAuthStore();
      if (!authStore.isAuthenticated || !authStore.accessToken) { // isAuthenticated와 accessToken 모두 확인
        this.error = '로그인이 필요합니다.';
        console.error('[Store] Create comment failed: User not authenticated or no access token.');
        throw new Error('로그인이 필요합니다.');
      }
      try {
        const payload = { content };
        if (parentCommentId) {
          payload.parent = parentCommentId;
        }

        console.log('[Store] Creating comment/reply. PostID:', postId, 'Payload:', JSON.parse(JSON.stringify(payload)));

        const response = await axios.post(
          `/api/v1/community/posts/${postId}/comments/`,
          payload,
          {
            headers: {
              // Django Rest Framework Token Authentication은 보통 'Token <token>' 형식을 사용합니다.
              // JWT를 사용한다면 'Bearer <token>'일 수 있습니다. authStore의 토큰 형식에 맞춰야 합니다.
              'Authorization': `Token ${authStore.accessToken}`
            }
          }
        );

        const newCommentData = response.data;
        console.log('[Store] Comment created successfully. Response data:', JSON.parse(JSON.stringify(newCommentData)));

        // Ensure the new comment data has a 'replies' array for future nested replies
        if (!newCommentData.replies) {
          newCommentData.replies = [];
        }
        // If the backend response doesn't include a parent ID, but we sent one, use the one from the request.
        // This is crucial if the backend returns the created comment object without explicitly setting its 'parent' field
        // to the ID of the comment it's replying to.
        const effectiveParentId = newCommentData.parent || parentCommentId;

        const targetPostIndex = this.posts.findIndex(p => p.id === postId);
        if (targetPostIndex !== -1) {
          const targetPost = this.posts[targetPostIndex];

          if (!targetPost.comments) {
            targetPost.comments = [];
          }

          if (effectiveParentId) {
            let parentFound = false;
            const findAndAddReply = (commentsArray) => {
              for (let i = 0; i < commentsArray.length; i++) {
                if (commentsArray[i].id === effectiveParentId) {
                  if (!commentsArray[i].replies) {
                    commentsArray[i].replies = [];
                  }
                  commentsArray[i].replies.push(newCommentData);
                  parentFound = true;
                  return true;
                }
                if (commentsArray[i].replies && findAndAddReply(commentsArray[i].replies)) {
                  parentFound = true;
                  return true;
                }
              }
              return false;
            };

            findAndAddReply(targetPost.comments);

            if (!parentFound) {
              console.warn(`[Store] Parent comment with id ${effectiveParentId} not found for reply. Appending to top-level comments for post ${postId}.`);
              targetPost.comments.push(newCommentData);
            }
          } else {
            targetPost.comments.push(newCommentData);
          }
          this.posts.splice(targetPostIndex, 1, { ...targetPost });

        } else {
          console.warn(`[Store] Target post with id ${postId} not found for comment update.`);
        }

        return newCommentData;

      } catch (error) {
        console.error('[Store] Error creating comment:', error.response?.data || error.message, error.response?.status);
        const errorMessage = error.response?.data?.detail || error.response?.data?.message || '댓글 작성 중 오류가 발생했습니다.';
        this.error = errorMessage;
        throw new Error(errorMessage);
      }
    },

    async fetchUserProfileByUsername(username) {
      this.loading = true
      this.error = null
      try {
        const authStore = useAuthStore();
        const headers = {};
        if (authStore.accessToken) {
          headers['Authorization'] = `Token ${authStore.accessToken}`;
        }
        const response = await axios.get(`/api/v1/accounts/profile/${username}/`, { headers })
        this.userProfileData = response.data
        return response.data
      } catch (error) {
        console.error('Error fetching user profile by username:', error)
        this.error = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async toggleFollowUser(targetUserId, followIdForCurrentUser) {
      const authStore = useAuthStore()
      if (!authStore.accessToken) {
        this.error = '로그인이 필요합니다.';
        throw new Error('로그인이 필요합니다.')
      }
      this.error = null;
      let targetUsername = null;
      if (this.userProfileData && this.userProfileData.id === targetUserId) {
        targetUsername = this.userProfileData.username;
      }

      try {
        if (followIdForCurrentUser) {
          await axios.delete(`/api/v1/community/follows/${followIdForCurrentUser}/`, {
            headers: { 'Authorization': `Token ${authStore.accessToken}` }
          });
          if (targetUsername) {
            await this.fetchUserProfileByUsername(targetUsername);
          } else if (this.userProfileData && this.userProfileData.id === targetUserId) {
            this.userProfileData.is_following = false;
            this.userProfileData.followers_count = Math.max(0, (this.userProfileData.followers_count || 0) - 1);
            this.userProfileData.follow_id_for_current_user = null;
          }
          return { followed: false };
        } else {
          const response = await axios.post('/api/v1/community/follows/', {
            following_id: targetUserId
          }, {
            headers: {
              'Authorization': `Token ${authStore.accessToken}`
            }
          });
          if (targetUsername) {
            await this.fetchUserProfileByUsername(targetUsername);
          } else if (this.userProfileData && this.userProfileData.id === targetUserId) {
            this.userProfileData.is_following = true;
            this.userProfileData.followers_count = (this.userProfileData.followers_count || 0) + 1;
            this.userProfileData.follow_id_for_current_user = response.data.id;
          }
          return { followed: true, followData: response.data };
        }
      } catch (error) {
        console.error('Error toggling follow status:', error.response?.data || error.message);
        if (error.response && error.response.data && Array.isArray(error.response.data) && error.response.data.length > 0) {
          this.error = error.response.data.join(', ');
        } else if (error.response && error.response.data && error.response.data.detail) {
          this.error = error.response.data.detail;
        } else {
          this.error = error.message || '팔로우 처리 중 오류가 발생했습니다.';
        }
        throw error;
      }
    },

    async fetchUserFollowers(userId) {
      this.error = null; // 에러 상태 초기화
      try {
        const authStore = useAuthStore();
        if (!authStore.accessToken) {
          this.error = '로그인이 필요합니다.';
          throw new Error('로그인이 필요합니다.');
        }
        // 수정된 URL: /api/v1/community/follows/user/{userId}/followers/
        const response = await axios.get(`/api/v1/community/follows/user/${userId}/followers/`, {
          headers: { 'Authorization': `Token ${authStore.accessToken}` } // 인증 헤더 추가
        });
        this.followers = response.data;
        return response.data;
      } catch (error) {
        console.error('Error fetching user followers:', error.response?.data || error.message);
        this.error = error.response?.data?.detail || error.message || '팔로워 목록 로드 실패';
        throw error;
      }
    },

    async fetchUserFollowing(userId) {
      this.error = null; // 에러 상태 초기화
      try {
        const authStore = useAuthStore();
        if (!authStore.accessToken) {
          this.error = '로그인이 필요합니다.';
          throw new Error('로그인이 필요합니다.');
        }
        // 수정된 URL: /api/v1/community/follows/user/{userId}/following/
        const response = await axios.get(`/api/v1/community/follows/user/${userId}/following/`, {
          headers: { 'Authorization': `Token ${authStore.accessToken}` } // 인증 헤더 추가
        });
        this.following = response.data;
        return response.data;
      } catch (error) {
        console.error('Error fetching user following:', error.response?.data || error.message);
        this.error = error.response?.data?.detail || error.message || '팔로잉 목록 로드 실패';
        throw error;
      }
    },

    async deletePost(postId) {
      const authStore = useAuthStore();
      if (!authStore.isAuthenticated) {
        throw new Error('로그인이 필요합니다.');
      }
      this.loading = true;
      this.error = null;
      try {
        await axios.delete(`/api/v1/community/posts/${postId}/`, {
          headers: { 'Authorization': `Token ${authStore.accessToken}` }
        });
        this.posts = this.posts.filter(p => p.id !== postId);
        console.log(`[Store] Post ${postId} deleted successfully.`);
      } catch (error) {
        console.error('[Store] Error deleting post:', error.response?.data || error.message);
        this.error = error.response?.data?.detail || '게시글 삭제 중 오류가 발생했습니다.';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async deleteComment(postId, commentId) {
      const authStore = useAuthStore();
      if (!authStore.isAuthenticated) {
        throw new Error('로그인이 필요합니다.');
      }
      // No global loading for comment deletion to avoid UI flicker for the whole page
      // this.loading = true; 
      this.error = null;
      try {
        // Assuming nested URL for comment deletion. Adjust if your API is different.
        // e.g., /api/v1/community/comments/${commentId}/
        await axios.delete(`/api/v1/community/posts/${postId}/comments/${commentId}/`, {
          headers: { 'Authorization': `Token ${authStore.accessToken}` }
        });

        const postIndex = this.posts.findIndex(p => p.id === postId);
        if (postIndex !== -1) {
          const post = this.posts[postIndex];

          const removeCommentRecursively = (comments, targetId) => {
            for (let i = 0; i < comments.length; i++) {
              if (comments[i].id === targetId) {
                comments.splice(i, 1);
                return true; // Found and removed
              }
              if (comments[i].replies && comments[i].replies.length > 0) {
                if (removeCommentRecursively(comments[i].replies, targetId)) {
                  return true; // Found and removed in nested replies
                }
              }
            }
            return false; // Not found at this level
          };

          if (removeCommentRecursively(post.comments || [], commentId)) {
            // To ensure reactivity, especially if just modifying nested array, re-assigning the post or the posts array might be safer.
            // For simplicity here, we trust Pinia's reactivity on array mutations. If issues, consider this.posts.splice(postIndex, 1, { ...post });
            console.log(`[Store] Comment ${commentId} from post ${postId} deleted successfully from local state.`);
          } else {
            console.warn(`[Store] Comment ${commentId} not found in post ${postId} for local removal after deletion.`);
          }
        } else {
          console.warn(`[Store] Post ${postId} not found for comment ${commentId} deletion.`);
        }

      } catch (error) {
        console.error('[Store] Error deleting comment:', error.response?.data || error.message);
        this.error = error.response?.data?.detail || '댓글 삭제 중 오류가 발생했습니다.';
        // Potentially re-throw or handle more gracefully
        throw error;
      } finally {
        // this.loading = false;
      }
    }
  }
})
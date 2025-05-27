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
      if (isInitialFetch) {
        this.currentPage = 1;
        this.posts = [];
        this.hasMorePosts = true;
        this.loading = true; // 초기 로딩 시작
        this.error = null;
      } else {
        if (this.isLoadingMore || !this.hasMorePosts) {
          return;
        }
        this.isLoadingMore = true; // 추가 로딩 시작
      }

      try {
        const authStore = useAuthStore();
        // authStore.accessToken 없어도 공개 게시글은 조회 가능하도록 처리 (필요시 주석 해제)
        // if (!authStore.accessToken) { }

        const response = await axios.get('/api/v1/community/posts/', {
          params: {
            page: this.currentPage,
            page_size: this.postsPerPage
          }
        });

        if (response.data && response.data.results) {
          const fetchedPosts = response.data.results;
          if (fetchedPosts.length > 0) {
            this.posts = isInitialFetch ? fetchedPosts : [...this.posts, ...fetchedPosts];
            this.currentPage++;
          }
          // 다음 페이지 존재 여부 판단 (next url 또는 가져온 게시글 수 기준)
          this.hasMorePosts = !(!response.data.next || fetchedPosts.length < this.postsPerPage);
        } else if (response.data && Array.isArray(response.data)) { // 페이지네이션 없는 응답 처리
          const fetchedPosts = response.data;
          this.posts = isInitialFetch ? fetchedPosts : [...this.posts, ...fetchedPosts];
          this.hasMorePosts = false;
        } else {
          this.hasMorePosts = false; // 예상치 못한 응답 구조
        }
      } catch (error) {
        this.error = error.response?.data?.detail || error.message || '게시글 로드 실패';
        this.hasMorePosts = false;
      } finally {
        if (isInitialFetch) {
          this.loading = false;
        }
        this.isLoadingMore = false;
      }
    },

    async createPost(content, image = null) {
      this.loading = true
      this.error = null;
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
        await this.fetchPosts(true); // 새 글 작성 후 목록 새로고침
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.message || '게시글 작성 실패';
        throw error
      } finally {
        this.loading = false
      }
    },

    async likePost(postId) {
      this.error = null;
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
          post.is_liked = !post.is_liked // 좋아요 상태 토글
          post.likes_count += post.is_liked ? 1 : -1 // 좋아요 수 업데이트
        }
      } catch (error) {
        this.error = error.response?.data?.detail || error.message || '좋아요 처리 실패';
        throw error
      }
    },

    async createComment(postId, content, parentCommentId = null) {
      const authStore = useAuthStore();
      if (!authStore.isAuthenticated || !authStore.accessToken) {
        this.error = '로그인이 필요합니다.';
        throw new Error('로그인이 필요합니다.');
      }
      this.error = null;
      try {
        const payload = { content };
        if (parentCommentId) {
          payload.parent = parentCommentId; // 대댓글인 경우 부모 ID 포함
        }

        const response = await axios.post(
          `/api/v1/community/posts/${postId}/comments/`,
          payload,
          {
            headers: {
              'Authorization': `Token ${authStore.accessToken}` // 인증 토큰 사용
            }
          }
        );

        const newCommentData = response.data;
        // 새 댓글에 replies 배열이 없으면 추가 (중첩 대댓글용)
        if (!newCommentData.replies) {
          newCommentData.replies = [];
        }
        // 백엔드 응답에 parent ID가 명시적으로 없더라도, 요청 시 사용한 parentCommentId를 활용
        const effectiveParentId = newCommentData.parent || parentCommentId;

        const targetPostIndex = this.posts.findIndex(p => p.id === postId);
        if (targetPostIndex !== -1) {
          const targetPost = this.posts[targetPostIndex];

          if (!targetPost.comments) {
            targetPost.comments = []; // 댓글 배열 초기화
          }

          if (effectiveParentId) { // 대댓글인 경우
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
            findAndAddReply(targetPost.comments); // 재귀적으로 부모 댓글 찾아 추가

            if (!parentFound) { // 부모 댓글 못 찾으면 최상위 댓글로 추가
              targetPost.comments.push(newCommentData);
            }
          } else { // 일반 댓글인 경우
            targetPost.comments.push(newCommentData);
          }
          // 반응성을 위해 게시글 객체 교체 (필요시)
          this.posts.splice(targetPostIndex, 1, { ...targetPost });
        } else {
          // 대상 게시글을 찾지 못한 경우 (일반적으로 발생하지 않음)
        }
        return newCommentData;
      } catch (error) {
        const errorMessage = error.response?.data?.detail || error.response?.data?.message || '댓글 작성 실패';
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
        this.error = error.response?.data?.detail || error.message || '사용자 프로필 로드 실패';
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
      // 현재 로드된 프로필 데이터와 대상 유저 ID가 일치하면 사용자명 확보 (API 재호출 방지용)
      if (this.userProfileData && this.userProfileData.id === targetUserId) {
        targetUsername = this.userProfileData.username;
      }

      try {
        if (followIdForCurrentUser) { // 이미 팔로우 중이면 언팔로우
          await axios.delete(`/api/v1/community/follows/${followIdForCurrentUser}/`, {
            headers: { 'Authorization': `Token ${authStore.accessToken}` }
          });
          // 프로필 데이터 즉시 업데이트 로직
          if (targetUsername) { // 사용자명이 있으면 프로필 다시 로드
            await this.fetchUserProfileByUsername(targetUsername);
          } else if (this.userProfileData && this.userProfileData.id === targetUserId) {
            this.userProfileData.is_following = false;
            this.userProfileData.followers_count = Math.max(0, (this.userProfileData.followers_count || 0) - 1);
            this.userProfileData.follow_id_for_current_user = null;
          }
          return { followed: false };
        } else { // 팔로우하고 있지 않으면 팔로우
          const response = await axios.post('/api/v1/community/follows/', {
            following_id: targetUserId
          }, {
            headers: {
              'Authorization': `Token ${authStore.accessToken}`
            }
          });
          // 프로필 데이터 즉시 업데이트 로직
          if (targetUsername) { // 사용자명이 있으면 프로필 다시 로드
            await this.fetchUserProfileByUsername(targetUsername);
          } else if (this.userProfileData && this.userProfileData.id === targetUserId) {
            this.userProfileData.is_following = true;
            this.userProfileData.followers_count = (this.userProfileData.followers_count || 0) + 1;
            this.userProfileData.follow_id_for_current_user = response.data.id;
          }
          return { followed: true, followData: response.data };
        }
      } catch (error) {
        this.error = error.response?.data?.detail || error.message || '팔로우 처리 실패';
        if (error.response && error.response.data && Array.isArray(error.response.data) && error.response.data.length > 0) {
          this.error = error.response.data.join(', '); // 배열 형태의 에러 메시지 처리
        }
        throw error;
      }
    },

    async fetchUserFollowers(userId) {
      this.error = null;
      try {
        const authStore = useAuthStore();
        if (!authStore.accessToken) {
          this.error = '로그인이 필요합니다.';
          throw new Error('로그인이 필요합니다.');
        }
        const response = await axios.get(`/api/v1/community/follows/user/${userId}/followers/`, {
          headers: { 'Authorization': `Token ${authStore.accessToken}` }
        });
        this.followers = response.data;
        return response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || error.message || '팔로워 목록 로드 실패';
        throw error;
      }
    },

    async fetchUserFollowing(userId) {
      this.error = null;
      try {
        const authStore = useAuthStore();
        if (!authStore.accessToken) {
          this.error = '로그인이 필요합니다.';
          throw new Error('로그인이 필요합니다.');
        }
        const response = await axios.get(`/api/v1/community/follows/user/${userId}/following/`, {
          headers: { 'Authorization': `Token ${authStore.accessToken}` }
        });
        this.following = response.data;
        return response.data;
      } catch (error) {
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
        this.posts = this.posts.filter(p => p.id !== postId); // 로컬 상태에서 게시글 제거
      } catch (error) {
        this.error = error.response?.data?.detail || '게시글 삭제 실패';
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
      this.error = null;
      try {
        // API 엔드포인트는 프로젝트에 맞게 조정 (예: /api/v1/community/comments/${commentId}/)
        await axios.delete(`/api/v1/community/posts/${postId}/comments/${commentId}/`, {
          headers: { 'Authorization': `Token ${authStore.accessToken}` }
        });

        const postIndex = this.posts.findIndex(p => p.id === postId);
        if (postIndex !== -1) {
          const post = this.posts[postIndex];
          // 재귀적으로 댓글 찾아 삭제하는 함수
          const removeCommentRecursively = (comments, targetId) => {
            for (let i = 0; i < comments.length; i++) {
              if (comments[i].id === targetId) {
                comments.splice(i, 1); // 댓글 제거
                return true; // 찾아서 제거함
              }
              if (comments[i].replies && comments[i].replies.length > 0) {
                if (removeCommentRecursively(comments[i].replies, targetId)) {
                  return true; // 중첩된 대댓글에서 찾아 제거함
                }
              }
            }
            return false; // 현재 레벨에서 못 찾음
          };

          if (removeCommentRecursively(post.comments || [], commentId)) {
            // 로컬 상태에서 댓글 제거 성공 (Pinia 반응성 활용)
          } else {
            // 로컬에서 댓글 못 찾음 (일반적이지 않음)
          }
        } else {
          // 게시글 못 찾음
        }
      } catch (error) {
        this.error = error.response?.data?.detail || '댓글 삭제 실패';
        throw error;
      } finally {
        // 댓글 삭제 시 전체 로딩은 불필요
      }
    }
  }
})
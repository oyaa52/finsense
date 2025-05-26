import { defineStore } from 'pinia'
import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

export const useCommunityStore = defineStore('community', {
  state: () => ({
    posts: [],
    currentPost: null,
    loading: false,
    error: null,
    followers: [],
    following: []
  }),

  actions: {
    async fetchPosts() {
      this.loading = true
      try {
        const authStore = useAuthStore()
        if (!authStore.accessToken) {
          throw new Error('로그인이 필요합니다.')
        }
        const response = await axios.get('/api/v1/community/posts/')
        console.log('API Response for /api/v1/community/posts/:', JSON.stringify(response.data, null, 2));
        this.posts = response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading = false
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
            'Content-Type': 'multipart/form-data'
          }
        })
        this.posts.unshift(response.data)
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
        await axios.post(`/api/v1/community/posts/${postId}/like/`)
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
      const token = localStorage.getItem('accessToken');
      if (!token) throw new Error('Authentication required.');
      try {
        const payload = { content };
        if (parentCommentId) {
          payload.parent = parentCommentId;
        }

        console.log('Requesting POST /api/v1/community/posts/' + postId + '/comments/ with payload:', JSON.stringify(payload, null, 2));

        const response = await axios.post(
          `/api/v1/community/posts/${postId}/comments/`,
          payload,
          { headers: { Authorization: `Token ${token}` } }
        );
        return response.data;
      } catch (error) {
        console.error('Error creating comment:', error);
        throw error;
      }
    },

    async followUser(userId) {
      try {
        const authStore = useAuthStore()
        if (!authStore.accessToken) {
          throw new Error('로그인이 필요합니다.')
        }
        await axios.post('/api/v1/community/follows/', {
          following_id: userId
        })
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      }
    },

    async unfollowUser(userId) {
      try {
        const authStore = useAuthStore()
        if (!authStore.accessToken) {
          throw new Error('로그인이 필요합니다.')
        }
        // 현재 사용자의 팔로우 목록에서 해당 사용자를 찾아 삭제
        const follow = this.following.find(f => f.following.id === userId)
        if (follow) {
          await axios.delete(`/api/v1/community/follows/${follow.id}/`)
        }
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      }
    },

    async fetchUserFollowers(userId) {
      try {
        const authStore = useAuthStore()
        if (!authStore.accessToken) {
          throw new Error('로그인이 필요합니다.')
        }
        const response = await axios.get(`/api/v1/community/follows/${userId}/user_followers/`)
        this.followers = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      }
    },

    async fetchUserFollowing(userId) {
      try {
        const authStore = useAuthStore()
        if (!authStore.accessToken) {
          throw new Error('로그인이 필요합니다.')
        }
        const response = await axios.get(`/api/v1/community/follows/${userId}/user_following/`)
        this.following = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      }
    }
  }
}) 
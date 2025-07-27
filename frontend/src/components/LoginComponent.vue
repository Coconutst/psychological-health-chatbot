<template>
  <div :class="isModal ? '' : 'min-h-screen flex items-center justify-center bg-gray-900 py-12 px-4 sm:px-6 lg:px-8'">
    <div :class="isModal ? 'w-full space-y-4' : 'max-w-md w-full space-y-8'">
      <!-- Logo和标题 - 模态框模式下紧凑显示 -->
      <div v-if="!isModal" class="text-center">
        <div class="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-indigo-600">
          <font-awesome-icon :icon="['fas', 'brain']" class="h-6 w-6 text-white" />
        </div>
        <h2 class="mt-6 text-3xl font-extrabold text-white">
          心理健康聊天机器人
        </h2>
        <p class="mt-2 text-sm text-gray-400">
          {{ isLogin ? '登录您的账户' : '创建新账户' }}
        </p>
      </div>
      
      <!-- 登录/注册切换 - 超紧凑版 -->
      <div class="flex rounded-md bg-gray-800 p-0.5">
        <button
          @click="isLogin = true"
          :class="[
            isModal ? 'flex-1 py-1 px-2 text-xs font-medium rounded transition-colors duration-200' : 'flex-1 py-2 px-4 text-sm font-medium rounded-md transition-colors duration-200',
            isLogin
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'text-gray-400 hover:text-white'
          ]"
        >
          登录
        </button>
        <button
          @click="isLogin = false"
          :class="[
            isModal ? 'flex-1 py-1 px-2 text-xs font-medium rounded transition-colors duration-200' : 'flex-1 py-2 px-4 text-sm font-medium rounded-md transition-colors duration-200',
            !isLogin
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'text-gray-400 hover:text-white'
          ]"
        >
          注册
        </button>
      </div>

      <!-- 登录表单 - 超紧凑版 -->
      <form v-if="isLogin" @submit.prevent="handleLogin" :class="isModal ? 'mt-2 space-y-2' : 'mt-8 space-y-6'">
        <div :class="isModal ? 'space-y-2' : 'space-y-4'">
          <div>
            <label for="email" :class="isModal ? 'block text-xs font-medium text-gray-300' : 'block text-sm font-medium text-gray-300'">
              邮箱地址
            </label>
            <div :class="isModal ? 'mt-0.5 relative' : 'mt-1 relative'">
              <input
                id="email"
                v-model="loginForm.email"
                type="email"
                required
                :class="[
                  'appearance-none relative block w-full border border-gray-600 placeholder-gray-400 text-white bg-gray-700 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10',
                  isModal ? 'px-2 py-1.5 pl-8 text-xs' : 'px-3 py-2 pl-10 sm:text-sm'
                ]"
                placeholder="请输入邮箱"
              />
              <div class="absolute inset-y-0 left-0 flex items-center pointer-events-none" :class="isModal ? 'pl-2' : 'pl-3'">
                <font-awesome-icon :icon="['fas', 'envelope']" :class="isModal ? 'h-3 w-3' : 'h-4 w-4'" class="text-gray-400" />
              </div>
            </div>
          </div>
          <div>
            <label for="password" :class="isModal ? 'block text-xs font-medium text-gray-300' : 'block text-sm font-medium text-gray-300'">
              密码
            </label>
            <div :class="isModal ? 'mt-0.5 relative' : 'mt-1 relative'">
              <input
                id="password"
                v-model="loginForm.password"
                :type="showPassword ? 'text' : 'password'"
                required
                :class="[
                  'appearance-none relative block w-full border border-gray-600 placeholder-gray-400 text-white bg-gray-700 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10',
                  isModal ? 'px-2 py-1.5 pl-8 pr-8 text-xs' : 'px-3 py-2 pl-10 pr-10 sm:text-sm'
                ]"
                placeholder="请输入密码"
              />
              <div class="absolute inset-y-0 left-0 flex items-center pointer-events-none" :class="isModal ? 'pl-2' : 'pl-3'">
                <font-awesome-icon :icon="['fas', 'lock']" :class="isModal ? 'h-3 w-3' : 'h-4 w-4'" class="text-gray-400" />
              </div>
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 flex items-center"
                :class="isModal ? 'pr-2' : 'pr-3'"
              >
                <font-awesome-icon 
                  :icon="['fas', showPassword ? 'eye-slash' : 'eye']" 
                  :class="isModal ? 'h-3 w-3' : 'h-4 w-4'" 
                  class="text-gray-400 hover:text-gray-300" 
                />
              </button>
            </div>
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="isLoading"
            :class="[
              'group relative w-full flex justify-center border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200',
              isModal ? 'py-1.5 px-3' : 'py-2 px-4'
            ]"
          >
            <span v-if="isLoading" class="absolute left-0 inset-y-0 flex items-center pl-3">
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            </span>
            {{ isLoading ? '登录中...' : '登录' }}
          </button>
        </div>
      </form>

      <!-- 注册表单 - 超紧凑版 -->
      <form v-else @submit.prevent="handleRegister" :class="isModal ? 'mt-2 space-y-2' : 'mt-8 space-y-6'">
        <div :class="isModal ? 'space-y-2' : 'space-y-4'">
          <div>
            <label for="username" :class="isModal ? 'block text-xs font-medium text-gray-300' : 'block text-sm font-medium text-gray-300'">
              用户名
            </label>
            <div :class="isModal ? 'mt-0.5 relative' : 'mt-1 relative'">
              <input
                id="username"
                v-model="registerForm.username"
                type="text"
                required
                :class="[
                  'appearance-none relative block w-full border border-gray-600 placeholder-gray-400 text-white bg-gray-700 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10',
                  isModal ? 'px-2 py-1.5 pl-8 text-xs' : 'px-3 py-2 pl-10 sm:text-sm'
                ]"
                placeholder="请输入用户名"
              />
              <div class="absolute inset-y-0 left-0 flex items-center pointer-events-none" :class="isModal ? 'pl-2' : 'pl-3'">
                <font-awesome-icon :icon="['fas', 'user']" :class="isModal ? 'h-3 w-3' : 'h-4 w-4'" class="text-gray-400" />
              </div>
            </div>
          </div>
          <div>
            <label for="reg-email" :class="isModal ? 'block text-xs font-medium text-gray-300' : 'block text-sm font-medium text-gray-300'">
              邮箱地址
            </label>
            <div :class="isModal ? 'mt-0.5 relative' : 'mt-1 relative'">
              <input
                id="reg-email"
                v-model="registerForm.email"
                type="email"
                required
                :class="[
                  'appearance-none relative block w-full border border-gray-600 placeholder-gray-400 text-white bg-gray-700 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10',
                  isModal ? 'px-2 py-1.5 pl-8 text-xs' : 'px-3 py-2 pl-10 sm:text-sm'
                ]"
                placeholder="请输入邮箱"
              />
              <div class="absolute inset-y-0 left-0 flex items-center pointer-events-none" :class="isModal ? 'pl-2' : 'pl-3'">
                <font-awesome-icon :icon="['fas', 'envelope']" :class="isModal ? 'h-3 w-3' : 'h-4 w-4'" class="text-gray-400" />
              </div>
            </div>
          </div>
          <div>
            <label for="reg-password" :class="isModal ? 'block text-xs font-medium text-gray-300' : 'block text-sm font-medium text-gray-300'">
              密码
            </label>
            <div :class="isModal ? 'mt-0.5 relative' : 'mt-1 relative'">
              <input
                id="reg-password"
                v-model="registerForm.password"
                :type="showRegPassword ? 'text' : 'password'"
                required
                :class="[
                  'appearance-none relative block w-full border border-gray-600 placeholder-gray-400 text-white bg-gray-700 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10',
                  isModal ? 'px-2 py-1.5 pl-8 pr-8 text-xs' : 'px-3 py-2 pl-10 pr-10 sm:text-sm'
                ]"
                placeholder="请输入密码"
              />
              <div class="absolute inset-y-0 left-0 flex items-center pointer-events-none" :class="isModal ? 'pl-2' : 'pl-3'">
                <font-awesome-icon :icon="['fas', 'lock']" :class="isModal ? 'h-3 w-3' : 'h-4 w-4'" class="text-gray-400" />
              </div>
              <button
                type="button"
                @click="showRegPassword = !showRegPassword"
                class="absolute inset-y-0 right-0 flex items-center"
                :class="isModal ? 'pr-2' : 'pr-3'"
              >
                <font-awesome-icon 
                  :icon="['fas', showRegPassword ? 'eye-slash' : 'eye']" 
                  :class="isModal ? 'h-3 w-3' : 'h-4 w-4'" 
                  class="text-gray-400 hover:text-gray-300" 
                />
              </button>
            </div>
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="isLoading"
            :class="[
              'group relative w-full flex justify-center border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200',
              isModal ? 'py-1.5 px-3' : 'py-2 px-4'
            ]"
          >
            <span v-if="isLoading" class="absolute left-0 inset-y-0 flex items-center pl-3">
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            </span>
            {{ isLoading ? '注册中...' : '创建账户' }}
          </button>
        </div>
      </form>

      <!-- 错误信息 - 紧凑版 -->
      <div v-if="error" :class="[
        'rounded-md bg-red-900 border border-red-700',
        isModal ? 'p-3' : 'p-4'
      ]">
        <div class="flex">
          <div class="flex-shrink-0">
            <font-awesome-icon :icon="['fas', 'exclamation-circle']" :class="isModal ? 'h-4 w-4' : 'h-5 w-5'" class="text-red-400" />
          </div>
          <div :class="isModal ? 'ml-2' : 'ml-3'">
            <p :class="isModal ? 'text-xs' : 'text-sm'" class="text-red-300">{{ error }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import api from '../api/index.js'
import { setCookie } from '../utils/cookie.js'

export default {
  name: 'LoginComponent',
  props: {
    isModal: {
      type: Boolean,
      default: false
    }
  },
  emits: ['login-success'],
  setup(props, { emit }) {
    const isLogin = ref(true)
    const showPassword = ref(false)
    const isLoading = ref(false)
    const error = ref('')
    
    const loginForm = ref({
      email: 'user@example.com',
      password: 'password123'
    })
    
    const registerForm = ref({
      username: '',
      email: '',
      password: ''
    })
    
    const handleLogin = async () => {
      if (!loginForm.value.email || !loginForm.value.password) {
        error.value = '请填写完整的登录信息'
        return
      }
      
      isLoading.value = true
      error.value = ''
      
      try {
        const response = await api.login(loginForm.value.email, loginForm.value.password)
        console.log('🎉 [Login] 登录成功:', response.data)
        
        // 保存token和用户信息
        setCookie('token', response.data.access_token, 7)
        setCookie('userInfo', JSON.stringify(response.data.user), 7)
        
        // 通知父组件登录成功
        emit('login-success', response.data.user)
      } catch (err) {
        console.error('❌ [Login] 登录失败:', err)
        error.value = err.response?.data?.detail || '登录失败，请检查邮箱和密码'
      } finally {
        isLoading.value = false
      }
    }
    
    const handleRegister = async () => {
      if (!registerForm.value.username || !registerForm.value.email || !registerForm.value.password) {
        error.value = '请填写完整的注册信息'
        return
      }
      
      isLoading.value = true
      error.value = ''
      
      try {
        const response = await api.register(
          registerForm.value.username,
          registerForm.value.email,
          registerForm.value.password
        )
        console.log('🎉 [Register] 注册成功:', response.data)
        
        // 注册成功后自动登录
        await handleLogin()
      } catch (err) {
        console.error('❌ [Register] 注册失败:', err)
        error.value = err.response?.data?.detail || '注册失败，请稍后重试'
      } finally {
        isLoading.value = false
      }
    }
    
    return {
      isLogin,
      showPassword,
      isLoading,
      error,
      loginForm,
      registerForm,
      handleLogin,
      handleRegister
    }
  }
}
</script>
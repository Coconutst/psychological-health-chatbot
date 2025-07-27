<template>
  <div id="app" class="min-h-screen bg-gray-900 text-white">
    <!-- 主界面 -->
    <div class="flex min-h-screen">
      <!-- 顶部导航栏 - 融合版 -->
      <div class="fixed top-0 left-0 right-0 z-50 bg-gray-800 border-b border-gray-700">
        <div class="flex items-center justify-between px-4 py-3">
          <!-- 左侧区域：折叠按钮 + Logo + 聊天信息 -->
          <div class="flex items-center space-x-3">
            <!-- 侧边栏折叠按钮 - 桌面端 -->
            <button 
              @click="toggleSidebar"
              class="p-1.5 text-gray-400 hover:text-white transition-colors hidden md:block"
              title="折叠侧边栏"
            >
              <font-awesome-icon :icon="sidebarCollapsed ? 'chevron-right' : 'chevron-left'" class="text-sm" />
            </button>
            
            <!-- Logo和应用标题 -->
            <div class="flex items-center space-x-2">
              <div class="w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded flex items-center justify-center">
                <font-awesome-icon icon="brain" class="text-white text-sm" />
              </div>
              <h1 class="text-lg font-semibold text-white">心理咨询机器人</h1>
            </div>
            
            <!-- 分隔线 -->
            <div class="h-6 w-px bg-gray-600 hidden md:block"></div>
            
            <!-- 当前聊天信息 -->
            <div class="flex items-center space-x-2 hidden md:flex">
              <div class="w-5 h-5 bg-indigo-600 rounded-full flex items-center justify-center">
                <font-awesome-icon icon="robot" class="text-white text-xs" />
              </div>
              <div>
                <h2 class="text-sm font-medium text-white">
                  {{ getCurrentConversationTitle() }}
                </h2>
                <p class="text-xs text-gray-400">
                  {{ isLoading ? '正在输入...' : '在线 · 随时为您提供帮助' }}
                </p>
              </div>
            </div>
          </div>
          
          <!-- 右侧区域：聊天操作 + 用户操作 -->
          <div class="flex items-center space-x-2">
            <!-- 聊天操作按钮 -->
            <div class="flex items-center space-x-1 mr-2">
              <button
                @click="clearCurrentChat"
                class="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors duration-200"
                title="清空对话"
              >
                <font-awesome-icon icon="broom" class="h-3 w-3" />
              </button>
              <button
                @click="exportCurrentChat"
                class="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors duration-200"
                title="导出对话"
              >
                <font-awesome-icon icon="download" class="h-3 w-3" />
              </button>
            </div>
            
            <!-- 移动端菜单按钮 -->
            <button 
              @click="showMobileSidebar = true"
              class="p-1.5 text-gray-400 hover:text-white transition-colors md:hidden"
              title="菜单"
            >
              <font-awesome-icon icon="bars" class="text-sm" />
            </button>
            
            <!-- 用户区域 -->
            <div v-if="isLoggedIn" class="flex items-center space-x-1">
              <span class="text-gray-300 text-sm hidden sm:block">{{ userInfo?.username || userInfo?.email }}</span>
              <button 
                @click="showProfile = true"
                class="p-1.5 text-gray-400 hover:text-white transition-colors"
                title="用户资料"
              >
                <font-awesome-icon icon="user" class="text-sm" />
              </button>
              <button 
                @click="showSettings = true"
                class="p-1.5 text-gray-400 hover:text-white transition-colors"
                title="设置"
              >
                <font-awesome-icon icon="cog" class="text-sm" />
              </button>
              <button 
                @click="handleLogout"
                class="p-1.5 text-gray-400 hover:text-white transition-colors"
                title="退出登录"
              >
                <font-awesome-icon icon="sign-out-alt" class="text-sm" />
              </button>
            </div>
            <div v-else>
              <button 
                @click="showLogin = true"
                class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm transition-colors"
              >
                登录
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 主内容区域 - 紧凑版 -->
      <div class="flex w-full pt-16">
        <!-- 侧边栏 - 响应式，参考GPT官网比例，固定定位 -->
        <div 
          class="fixed left-0 top-16 bottom-0 z-30 flex-shrink-0 hidden md:block transition-all duration-300 ease-in-out bg-gray-800"
          :class="sidebarCollapsed ? 'w-0' : 'w-60'"
        >
          <div 
            class="h-full overflow-hidden transition-all duration-300 ease-in-out"
            :class="sidebarCollapsed ? 'w-0 opacity-0' : 'w-60 opacity-100'"
          >
            <Sidebar 
              :conversations="conversations"
              :current-conversation-id="currentConversationId"
              :is-logged-in="isLoggedIn"
              :is-collapsed="sidebarCollapsed"
              @new-conversation="createNewConversation"
              @select-conversation="selectConversation"
              @delete-conversation="deleteConversation"
              @title-updated="handleTitleUpdated"
            />
          </div>
        </div>
        
        <!-- 移动端侧边栏 -->
        <div v-if="showMobileSidebar" class="fixed inset-0 z-50 md:hidden">
          <div class="fixed inset-0 bg-black bg-opacity-50" @click="showMobileSidebar = false"></div>
          <div class="fixed left-0 top-0 bottom-0 w-60 bg-gray-900 pt-16">
            <Sidebar 
              :conversations="conversations"
              :current-conversation-id="currentConversationId"
              :is-logged-in="isLoggedIn"
              @new-conversation="createNewConversation"
              @select-conversation="selectConversation"
              @delete-conversation="deleteConversation"
              @title-updated="handleTitleUpdated"
            />
          </div>
        </div>
        
        <!-- 聊天区域 - 响应式，适应固定侧边栏 -->
        <div 
          class="flex-1 w-full md:w-auto transition-all duration-300 ease-in-out"
          :class="sidebarCollapsed ? 'md:ml-0' : 'md:ml-60'"
        >
          <ChatArea 
            :conversation-id="currentConversationId"
            :messages="currentMessages"
            :is-loading="isLoading"
            :is-logged-in="isLoggedIn"
            :sidebar-collapsed="sidebarCollapsed"
            @send-message="sendMessage"
            @clear-chat="clearCurrentChat"
            @export-chat="exportCurrentChat"
            @feedback-updated="handleFeedbackUpdated"
          />
        </div>
      </div>
    </div>
    
    <!-- 登录模态框 - 响应式紧凑版 -->
     <div v-if="showLogin" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-2">
       <div class="bg-gray-800 rounded-lg p-2 w-full max-w-xs mx-auto max-h-[80vh] overflow-y-auto">
         <div class="flex justify-between items-center mb-1">
           <h2 class="text-base font-semibold text-white">登录</h2>
           <button @click="showLogin = false" class="text-gray-400 hover:text-white transition-colors">
             <font-awesome-icon icon="times" class="w-3 h-3" />
           </button>
         </div>
         <LoginComponent :isModal="true" @login-success="handleLoginSuccess" />
       </div>
     </div>
    
    <!-- 用户资料模态框 -->
    <UserProfile v-if="showProfile" :user-info="userInfo" @close="showProfile = false" />
    
    <!-- 设置模态框 - 响应式 -->
    <div v-if="showSettings" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-2">
      <div class="bg-gray-800 rounded-lg p-3 w-full max-w-xs mx-auto max-h-[80vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-2">
          <h2 class="text-lg font-semibold text-white">设置</h2>
          <button @click="showSettings = false" class="text-gray-400 hover:text-white transition-colors">
            <font-awesome-icon icon="times" class="w-4 h-4" />
          </button>
        </div>
        <Settings @close="showSettings = false" />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, nextTick } from 'vue'
import api from './api/index.js'
import { getCookie, setCookie, removeCookie } from './utils/cookie.js'
import LoginComponent from './components/LoginComponent.vue'
import Sidebar from './components/Sidebar.vue'
import ChatArea from './components/ChatArea.vue'
import UserProfile from './components/UserProfile.vue'
import Settings from './components/Settings.vue'

export default {
  name: 'App',
  components: {
    LoginComponent,
    Sidebar,
    ChatArea,
    UserProfile,
    Settings
  },
  setup() {
    // 响应式数据
    const isLoggedIn = ref(false)
    const userInfo = ref(null)
    const conversations = ref([])
    const currentConversationId = ref(null)
    const currentMessages = ref([])
    const isLoading = ref(false)
    const showProfile = ref(false)
    const showSettings = ref(false)
    const showLogin = ref(false)
    const showMobileSidebar = ref(false)
    const sidebarCollapsed = ref(false)
    
    // 检查登录状态
    const checkLoginStatus = async () => {
      const token = getCookie('token')
      const userInfoCookie = getCookie('userInfo')
      
      if (token && userInfoCookie && userInfoCookie !== 'undefined') {
        try {
          userInfo.value = JSON.parse(userInfoCookie)
          isLoggedIn.value = true
          await loadConversations()
        } catch (error) {
          console.error('检查登录状态失败:', error)
          handleLogout()
        }
      }
    }

    // 处理登录成功
    const handleLoginSuccess = async (userData) => {
      userInfo.value = userData
      isLoggedIn.value = true
      showLogin.value = false
      await loadConversations()
    }

    // 处理退出登录
    const handleLogout = () => {
      removeCookie('token')
      removeCookie('userInfo')
      isLoggedIn.value = false
      userInfo.value = null
      conversations.value = []
      currentConversationId.value = null
      currentMessages.value = []
    }

    // 加载对话列表
    const loadConversations = async () => {
      try {
        const response = await api.getConversations()
        if (response.success) {
          conversations.value = response.data
          if (response.data.length > 0) {
            currentConversationId.value = response.data[0].conversation_id
            await loadMessages(response.data[0].conversation_id)
          }
        }
      } catch (error) {
        console.error('加载对话列表失败:', error)
      }
    }

    // 加载消息
    const loadMessages = async (conversationId) => {
      // 如果是临时ID，不需要加载消息
      if (conversationId?.startsWith('temp_')) {
        currentMessages.value = []
        return
      }
      
      try {
        isLoading.value = true
        const response = await api.getMessages(conversationId)
        if (response.success) {
          currentMessages.value = response.data
        }
      } catch (error) {
        console.error('加载消息失败:', error)
      } finally {
        isLoading.value = false
      }
    }

    // 创建新对话
    const createNewConversation = async () => {
      try {
        const response = await api.createConversation()
        if (response.success) {
          conversations.value.unshift(response.data)
          currentConversationId.value = response.data.conversation_id
          currentMessages.value = []
        }
      } catch (error) {
        console.error('创建新对话失败:', error)
      }
    }

    // 选择对话
    const selectConversation = async (conversationId) => {
      currentConversationId.value = conversationId
      await loadMessages(conversationId)
    }

    // 删除对话
    const deleteConversation = async (conversationId) => {
      try {
        const response = await api.deleteConversation(conversationId)
        if (response.success) {
          conversations.value = conversations.value.filter(c => c.conversation_id !== conversationId)
          if (currentConversationId.value === conversationId) {
            if (conversations.value.length > 0) {
              currentConversationId.value = conversations.value[0].conversation_id
              await loadMessages(conversations.value[0].conversation_id)
            } else {
              currentConversationId.value = null
              currentMessages.value = []
            }
          }
        }
      } catch (error) {
        console.error('删除对话失败:', error)
      }
    }

    // 发送消息
    const sendMessage = async (content) => {
      // 如果未登录，创建临时对话
      if (!isLoggedIn.value) {
        // 创建临时消息
        const userMessage = {
          id: Date.now(),
          role: 'user',
          content: content,
          timestamp: new Date().toISOString()
        }
        
        const aiMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: '您好！我是心理咨询机器人，很高兴为您提供帮助。请注意，未登录状态下的对话不会被保存。如需保存对话记录，请先登录。\n\n请告诉我您遇到的问题，我会尽力为您提供专业的心理咨询建议。',
          timestamp: new Date().toISOString()
        }
        
        currentMessages.value.push(userMessage, aiMessage)
        return
      }
      
      if (!currentConversationId.value) {
        await createNewConversation()
      }
      
      try {
        isLoading.value = true
        
        // 添加用户消息到界面
        const userMessage = {
          id: Date.now(),
          role: 'user',
          content: content,
          timestamp: new Date().toISOString()
        }
        currentMessages.value.push(userMessage)
        
        // 准备AI消息容器
        const aiMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: '',
          timestamp: new Date().toISOString()
        }
        currentMessages.value.push(aiMessage)
        
        // 确定conversation_id（如果是临时ID则传null让后端创建新对话）
        const conversationId = currentConversationId.value?.startsWith('temp_') ? null : currentConversationId.value
        
        // 调用流式聊天
        await api.streamChat(
          content,
          conversationId,
          (data) => {
            // 处理流式响应
            if (data.content) {
              aiMessage.content += data.content
            }
            if (data.conversation_id && currentConversationId.value?.startsWith('temp_')) {
              // 更新真实的conversation_id
              currentConversationId.value = data.conversation_id
              // 重新加载对话列表以获取最新的对话信息
              loadConversations()
            }
          },
          () => {
            // 完成回调
            console.log('消息发送完成')
          },
          (error) => {
            // 错误回调
            console.error('发送消息失败:', error)
            aiMessage.content = '抱歉，发送消息时出现错误，请稍后重试。'
          }
        )
      } catch (error) {
        console.error('发送消息失败:', error)
      } finally {
        isLoading.value = false
      }
    }

    // 清空当前聊天（仅清空界面显示，不删除服务器记录）
    const clearCurrentChat = () => {
      currentMessages.value = []
    }

    // 导出当前聊天
    const exportCurrentChat = () => {
      if (currentMessages.value.length === 0) return
      
      const content = currentMessages.value
        .map(msg => `${msg.role === 'user' ? '用户' : 'AI'}: ${msg.content}`)
        .join('\n\n')
      
      const blob = new Blob([content], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `chat-${new Date().toISOString().slice(0, 10)}.txt`
      a.click()
      URL.revokeObjectURL(url)
    }

    // 切换侧边栏折叠状态
    const toggleSidebar = () => {
      sidebarCollapsed.value = !sidebarCollapsed.value
    }

    // 获取当前对话标题
    const getCurrentConversationTitle = () => {
      if (!currentConversationId.value) {
        return '心理健康助手'
      }
      
      const currentConversation = conversations.value.find(
        conv => conv.conversation_id === currentConversationId.value
      )
      
      return currentConversation?.title || '心理健康助手'
    }

    // 处理消息反馈更新
    const handleFeedbackUpdated = async (messageId, feedback) => {
      console.log('处理反馈更新:', messageId, feedback)
      // 重新加载当前对话的消息以获取最新的反馈状态
      if (currentConversationId.value && !currentConversationId.value.startsWith('temp_')) {
        await loadMessages(currentConversationId.value)
      }
    }

    // 处理对话标题更新
    const handleTitleUpdated = async (event) => {
      console.log('🔄 处理标题更新事件:', event)
      try {
        // 重新加载对话列表以获取最新的标题
        await loadConversations()
        console.log('✅ 对话列表已刷新')
      } catch (error) {
        console.error('❌ 刷新对话列表失败:', error)
      }
    }

    // 组件挂载时检查登录状态
    onMounted(() => {
      checkLoginStatus()
    })

    return {
      isLoggedIn,
      userInfo,
      conversations,
      currentConversationId,
      currentMessages,
      isLoading,
      showProfile,
      showSettings,
      showLogin,
      showMobileSidebar,
      sidebarCollapsed,
      handleLoginSuccess,
      handleLogout,
      createNewConversation,
      selectConversation,
      deleteConversation,
      sendMessage,
      clearCurrentChat,
      exportCurrentChat,
      toggleSidebar,
      getCurrentConversationTitle,
      handleFeedbackUpdated,
      handleTitleUpdated
    }
  }
}
</script>

<style scoped>
.auth-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 30px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.auth-container h1 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.auth-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
}

.auth-tabs .btn {
  flex: 1;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-info span {
  color: #666;
}
</style>
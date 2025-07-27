import { reactive, watch } from 'vue'

// 从localStorage读取初始状态
const getInitialState = () => {
  try {
    return {
      // 用户相关
      isLoggedIn: JSON.parse(localStorage.getItem('isLoggedIn')) || false,
      userInfo: JSON.parse(localStorage.getItem('userInfo')) || null,
      
      // 对话相关
      conversations: JSON.parse(localStorage.getItem('conversations')) || [],
      currentConversationId: JSON.parse(localStorage.getItem('currentConversationId')) || null,
      currentMessages: JSON.parse(localStorage.getItem('currentMessages')) || [],
      
      // UI状态
      isLoading: false,
      showProfile: false,
      showSettings: false,
      showLogin: false,
      showMobileSidebar: false,
      sidebarCollapsed: false
    }
  } catch (error) {
    console.error('读取localStorage失败:', error)
    return {
      isLoggedIn: false,
      userInfo: null,
      conversations: [],
      currentConversationId: null,
      currentMessages: [],
      isLoading: false,
      showProfile: false,
      showSettings: false,
      showLogin: false,
      showMobileSidebar: false,
      sidebarCollapsed: false
    }
  }
}

// 创建响应式状态
const state = reactive(getInitialState())

// 监听状态变化并保存到localStorage
watch(
  () => state.isLoggedIn,
  (newVal) => localStorage.setItem('isLoggedIn', JSON.stringify(newVal))
)

watch(
  () => state.userInfo,
  (newVal) => localStorage.setItem('userInfo', JSON.stringify(newVal))
)

watch(
  () => state.conversations,
  (newVal) => localStorage.setItem('conversations', JSON.stringify(newVal)),
  { deep: true }
)

watch(
  () => state.currentConversationId,
  (newVal) => localStorage.setItem('currentConversationId', JSON.stringify(newVal))
)

watch(
  () => state.currentMessages,
  (newVal) => localStorage.setItem('currentMessages', JSON.stringify(newVal)),
  { deep: true }
)

// 状态操作方法
export const useAppState = () => {
  // 登录成功
  const loginSuccess = (userData) => {
    state.userInfo = userData
    state.isLoggedIn = true
  }

  // 登出
  const logout = () => {
    state.isLoggedIn = false
    state.userInfo = null
    state.conversations = []
    state.currentConversationId = null
    state.currentMessages = []
    
    // 清除localStorage
    localStorage.removeItem('isLoggedIn')
    localStorage.removeItem('userInfo')
    localStorage.removeItem('conversations')
    localStorage.removeItem('currentConversationId')
    localStorage.removeItem('currentMessages')
  }

  // 设置对话列表
  const setConversations = (conversations) => {
    state.conversations = conversations
  }

  // 设置当前对话ID
  const setCurrentConversationId = (id) => {
    state.currentConversationId = id
  }

  // 设置当前消息列表
  const setCurrentMessages = (messages) => {
    state.currentMessages = messages
  }

  // 添加消息
  const addMessage = (message) => {
    state.currentMessages.push(message)
  }

  // 更新消息内容
  const updateMessageContent = (messageId, content, replace = false) => {
    const message = state.currentMessages.find(msg => msg.id === messageId)
    if (message) {
      if (replace) {
        message.content = content
      } else {
        message.content += content
      }
    }
  }

  // 更新消息状态
  const updateMessageStatus = (messageId, status) => {
    const message = state.currentMessages.find(msg => msg.id === messageId)
    if (message) {
      message.status = status
    }
  }

  // 更新消息思考过程
  const updateMessageThinking = (messageId, thinking) => {
    const message = state.currentMessages.find(msg => msg.id === messageId)
    if (message) {
      message.thinking = thinking
    }
  }

  // 更新消息流式状态
  const updateMessageStreaming = (messageId, isStreaming) => {
    const message = state.currentMessages.find(msg => msg.id === messageId)
    if (message) {
      message.isStreaming = isStreaming
    }
  }

  // 更新消息反馈
  const updateMessageFeedback = (messageId, feedback) => {
    const message = state.currentMessages.find(msg => msg.id === messageId)
    if (message) {
      message.feedback = feedback
    }
  }

  // 设置加载状态
  const setLoading = (loading) => {
    state.isLoading = loading
  }

  // 设置UI状态
  const setShowProfile = (show) => {
    state.showProfile = show
  }

  const setShowSettings = (show) => {
    state.showSettings = show
  }

  const setShowLogin = (show) => {
    state.showLogin = show
  }

  const setShowMobileSidebar = (show) => {
    state.showMobileSidebar = show
  }

  const setSidebarCollapsed = (collapsed) => {
    state.sidebarCollapsed = collapsed
  }

  return {
    // 状态
    state,
    
    // 方法
    loginSuccess,
    logout,
    setConversations,
    setCurrentConversationId,
    setCurrentMessages,
    addMessage,
    updateMessageContent,
    updateMessageStatus,
    updateMessageThinking,
    updateMessageStreaming,
    updateMessageFeedback,
    setLoading,
    setShowProfile,
    setShowSettings,
    setShowLogin,
    setShowMobileSidebar,
    setSidebarCollapsed
  }
}

export default useAppState
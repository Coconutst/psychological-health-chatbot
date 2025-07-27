import axios from 'axios'
import { getCookie, removeCookie } from '../utils/cookie.js'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8002/api',
  timeout: 30000, // 增加超时时间以支持流式响应
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加token
api.interceptors.request.use(
  config => {
    console.log('🚀 [API] 发送请求:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      baseURL: config.baseURL,
      data: config.data,
      params: config.params
    })
    
    const token = getCookie('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log('🔑 [API] 已添加认证Token')
    } else {
      console.log('⚠️ [API] 未找到认证Token')
    }
    return config
  },
  error => {
    console.error('💥 [API] 请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器 - 统一处理响应
api.interceptors.response.use(
  response => {
    console.log('✅ [API] 响应成功:', {
      status: response.status,
      statusText: response.statusText,
      url: response.config.url,
      data: response.data
    })
    // 统一包装成功响应格式
    return {
      success: true,
      data: response.data,
      message: 'success'
    }
  },
  error => {
    console.error('❌ [API] 响应错误:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      message: error.message,
      data: error.response?.data
    })
    
    if (error.response) {
      // 服务器返回错误状态码
      const { status, data } = error.response
      
      if (status === 401) {
        console.log('🔒 [API] Token过期，清除登录状态')
        // token过期或无效，清除本地存储
        removeCookie('token')
        removeCookie('userInfo')
        window.location.reload()
      }
      
      return Promise.reject({
        success: false,
        message: data.detail || data.message || '请求失败',
        status
      })
    } else if (error.request) {
      // 网络错误
      return Promise.reject({
        success: false,
        message: '网络连接失败，请检查网络设置'
      })
    } else {
      // 其他错误
      return Promise.reject({
        success: false,
        message: error.message || '未知错误'
      })
    }
  }
)

// 🔥 流式聊天处理函数 - 版本 2.0 (完美解决SSE解析问题)
const handleStreamResponse = async (response, onMessage, onComplete, onError) => {
  console.log('🚀 [SSE] 使用新版本解析器 v2.0')
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  
  try {
    while (true) {
      const { done, value } = await reader.read()
      
      if (done) {
        if (onComplete) onComplete()
        break
      }
      
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || '' // 保留最后一行（可能不完整）
      
      for (const line of lines) {
        if (line.trim() === '') continue
        
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') {
            if (onComplete) onComplete()
            return
          }
          
          try {
            const parsed = JSON.parse(data)
            
            // 🔥 完美解决方案：根据数据类型精确处理
            switch (parsed.type) {
              case 'content':
                // ✅ 只有content类型才是真正的聊天内容
                if (parsed.content && onMessage) {
                  onMessage({ 
                    content: parsed.content, 
                    conversation_id: parsed.conversation_id 
                  })
                }
                break
                
              case 'status':
              case 'tools_status':
              case 'thinking':
              case 'response_start':
                // ✅ 状态信息：只传递conversation_id，不触发内容更新
                console.log(`🔄 [${parsed.type}]`, parsed.message || parsed.content || '处理中...')
                if (parsed.conversation_id && onMessage) {
                  onMessage({ conversation_id: parsed.conversation_id })
                }
                break
                
              default:
                // ✅ 兼容其他格式，但不会误解析状态信息
                if ((parsed.content || parsed.message) && !parsed.type) {
                  if (onMessage) onMessage({ 
                    content: parsed.content || parsed.message, 
                    conversation_id: parsed.conversation_id 
                  })
                }
                break
            }
          } catch (e) {
            // ✅ 只对真正无法解析的数据显示警告
            if (!data.includes('"type":')) {
              console.warn('⚠️ 解析SSE数据失败:', data)
            }
          }
        }
      }
    }
  } catch (error) {
    console.error('流式响应处理错误:', error)
    if (onError) onError(error)
  }
}

// API方法
export default {
  // 用户注册
  register(username, email, password) {
    console.log('📝 [API] 调用注册接口:', { username, email })
    return api.post('/auth/register', {
      username,
      email,
      password
    })
  },

  // 用户登录
  login(email, password) {
    console.log('🔐 [API] 调用登录接口:', { email })
    return api.post('/auth/login', {
      email,
      password
    })
  },

  // 修改密码
  changePassword(passwordData) {
    console.log('🔑 [API] 调用修改密码接口')
    return api.post('/auth/change-password', passwordData)
  },

  // 刷新token
  refreshToken(refreshToken) {
    console.log('🔄 [API] 调用刷新Token接口')
    return api.post(`/auth/refresh?refresh_token=${refreshToken}`)
  },

  // 验证token
  validateToken() {
    console.log('🔍 [API] 调用Token验证接口')
    return api.post('/auth/validate')
  },

  // 用户登出
  logout() {
    console.log('🚪 [API] 调用登出接口')
    return api.post('/auth/logout')
  },

  // 获取当前用户信息
  getCurrentUser() {
    console.log('👤 [API] 调用获取用户信息接口')
    return api.get('/auth/me')
  },

  // 流式聊天
  async streamChat(message, conversationId = null, onMessage, onComplete, onError) {
    console.log('💬 [API] 调用流式聊天接口:', { message, conversationId })
    
    const token = getCookie('token')
    const response = await fetch('http://localhost:8002/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        model: 'deepseek-chat',
        message: message,
        stream: true,
        conversation_id: conversationId
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return handleStreamResponse(response, onMessage, onComplete, onError)
  },

  // 创建新对话
  async createConversation() {
    console.log('🆕 [API] 创建新对话')
    // 新对话通过发送第一条消息来创建，这里返回一个模拟的对话对象
    // 实际的对话会在第一次发送消息时由后端创建
    const newConversation = {
      conversation_id: `temp_${Date.now()}`, // 临时ID，实际ID会在发送消息后更新
      title: '新对话',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
    return {
      success: true,
      data: newConversation
    }
  },

  // 获取对话列表
  getConversations() {
    console.log('📚 [API] 调用获取对话列表接口')
    return api.get('/conversations/')
  },

  // 获取对话消息
  getMessages(conversationId) {
    console.log('💬 [API] 调用获取消息接口，对话ID:', conversationId)
    return api.get(`/conversations/${conversationId}/messages`)
  },

  // 删除对话
  deleteConversation(conversationId) {
    console.log('🗑️ [API] 调用删除对话接口，对话ID:', conversationId)
    return api.delete(`/conversations/${conversationId}`)
  },

  // 更新对话标题
  updateConversationTitle(conversationId, title) {
    console.log('✏️ [API] 调用更新对话标题接口:', { conversationId, title })
    return api.patch(`/conversations/${conversationId}`, {
      title: title
    })
  },

  // 更新消息反馈
  updateMessageFeedback(messageId, feedback) {
    console.log('👍 [API] 调用更新消息反馈接口:', { messageId, feedback })
    return api.patch(`/conversations/messages/${messageId}/feedback`, {
      feedback: feedback
    })
  },

  // 获取用户情绪画像
  getUserEmotionProfile() {
    console.log('😊 [API] 调用获取用户情绪画像接口')
    return api.get('/user/emotion-profile')
  },

  // 获取用户情绪统计
  getUserEmotionStats() {
    console.log('📊 [API] 调用获取用户情绪统计接口')
    return api.get('/user/emotion-stats')
  }
}
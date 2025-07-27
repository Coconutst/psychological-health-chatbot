<template>
  <div class="flex-1 flex flex-col h-full bg-gray-900 relative">

    <!-- 消息区域 - GPT官网风格 -->
    <div class="flex-1 overflow-y-auto px-4 py-3 pb-32" ref="messagesContainer">
      <div class="max-w-4xl mx-auto">
      <!-- 欢迎消息 - 紧凑版 -->
      <div v-if="messages.length === 0" class="flex flex-col items-center justify-center h-full text-center">
        <div class="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center mb-2">
          <font-awesome-icon :icon="['fas', 'heart']" class="text-white text-sm" />
        </div>
        <h2 class="text-base font-bold text-white mb-1">欢迎使用心理健康助手</h2>
        <p class="text-gray-400 mb-3 max-w-sm text-xs">
          我是您的专业心理健康助手，可以为您提供情感支持、心理咨询建议和日常心理健康指导。请随时与我分享您的想法和感受。
        </p>
        <div v-if="!isLoggedIn" class="mb-3 p-2 bg-yellow-900/30 border border-yellow-600/50 rounded-lg">
          <p class="text-yellow-400 text-xs">
            <font-awesome-icon :icon="['fas', 'info-circle']" class="mr-1" />
            您当前处于未登录状态，对话内容不会被保存。登录后可保存对话记录。
          </p>
        </div>
        
        <!-- 快速开始建议 -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-1.5 max-w-lg">
          <button
            v-for="suggestion in quickSuggestions"
            :key="suggestion.text"
            @click="sendQuickMessage(suggestion.text)"
            class="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg border border-gray-700 hover:border-indigo-500 transition-all duration-200 text-left group"
          >
            <div class="flex items-center space-x-1.5">
              <div class="w-5 h-5 bg-indigo-600 rounded-full flex items-center justify-center group-hover:bg-indigo-500 transition-colors duration-200">
                <font-awesome-icon :icon="suggestion.icon" class="text-white text-xs" />
              </div>
              <div>
                <p class="text-white font-medium text-xs">{{ suggestion.title }}</p>
                <p class="text-gray-400 text-xs">{{ suggestion.description }}</p>
              </div>
            </div>
          </button>
        </div>
      </div>

      <!-- 消息列表 - 紧凑版 -->
      <div v-else class="space-y-3">
        <div
          v-for="(message, index) in messages"
          :key="message.id || index"
          class="flex"
          :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
        >
          <!-- 助手消息 - GPT官网风格 -->
          <div v-if="message.role === 'assistant'" class="flex space-x-3 mb-5">
            <div class="flex-shrink-0">
              <div class="w-7 h-7 bg-green-600 rounded-sm flex items-center justify-center">
                <font-awesome-icon :icon="['fas', 'robot']" class="text-white text-xs" />
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <div class="prose prose-invert max-w-none">
                <div v-html="formatMessage(message.content)" class="text-gray-100 whitespace-pre-wrap text-xs leading-4"></div>
              </div>
              <div class="flex items-center justify-between mt-2">
                <span class="text-xs text-gray-500">{{ formatTime(message.created_at) }}</span>
                <div class="flex items-center space-x-1.5">
                  <button
                    @click="copyMessage(message.content)"
                    class="p-1.5 text-gray-500 hover:text-gray-300 hover:bg-gray-800 rounded transition-colors duration-200"
                    title="复制消息"
                  >
                    <font-awesome-icon :icon="['fas', 'copy']" class="h-3.5 w-3.5" />
                  </button>
                  <button
                    @click="likeMessage(message.message_id, true)"
                    class="p-1.5 text-gray-500 hover:text-green-400 hover:bg-gray-800 rounded transition-colors duration-200"
                    :class="{ 'text-green-400': message.feedback === 1 || message.feedback === 'positive' }"
                    title="有帮助"
                  >
                    <font-awesome-icon :icon="['fas', 'thumbs-up']" class="h-3.5 w-3.5" />
                  </button>
                  <button
                    @click="likeMessage(message.message_id, false)"
                    class="p-1.5 text-gray-500 hover:text-red-400 hover:bg-gray-800 rounded transition-colors duration-200"
                    :class="{ 'text-red-400': message.feedback === -1 || message.feedback === 'negative' }"
                    title="没有帮助"
                  >
                    <font-awesome-icon :icon="['fas', 'thumbs-down']" class="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 用户消息 - 右对齐风格 -->
          <div v-else class="flex space-x-3 mb-5 max-w-2xl ml-auto">
            <div class="text-right">
              <div class="inline-block bg-blue-600 text-white px-3 py-2 rounded-lg max-w-xs lg:max-w-md text-xs leading-4">{{ message.content }}</div>
              <div class="flex justify-end mt-2">
                <span class="text-xs text-gray-500">{{ formatTime(message.created_at) }}</span>
              </div>
            </div>
            <div class="flex-shrink-0">
              <div class="w-7 h-7 bg-blue-600 rounded-full flex items-center justify-center">
                <font-awesome-icon :icon="['fas', 'user']" class="text-white text-xs" />
              </div>
            </div>
          </div>
        </div>

        <!-- 正在输入指示器 - GPT官网风格 -->
        <div v-if="isLoading" class="flex space-x-3 mb-5">
          <div class="flex-shrink-0">
            <div class="w-7 h-7 bg-green-600 rounded-sm flex items-center justify-center">
              <font-awesome-icon :icon="['fas', 'robot']" class="text-white text-xs" />
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center space-x-2">
              <div class="flex space-x-1">
                <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></div>
                <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
              </div>
              <span class="text-gray-400 text-sm">正在思考中...</span>
            </div>
          </div>
        </div>
      </div>
      </div>
    </div>

    <!-- 输入区域 - GPT官网风格 -->
        <div class="fixed bottom-0 left-0 right-0 bg-gray-900 border-t border-gray-700 px-3 py-2 z-40" :class="{ 'md:left-60': !sidebarCollapsed, 'md:left-0': sidebarCollapsed }">
           <div class="max-w-lg mx-auto">
        <form @submit.prevent="handleSendMessage" class="relative">
          <div class="relative flex items-end bg-gray-800 rounded-xl border border-gray-600 focus-within:border-gray-500 transition-colors">
            <textarea
              v-model="inputMessage"
              ref="messageInput"
              @keydown="handleKeyDown"
              placeholder="请输入您的问题或想法..."
              class="flex-1 px-3 py-2.5 bg-transparent text-white placeholder-gray-500 focus:outline-none resize-none text-xs leading-4 transition-all duration-200"
              rows="1"
              :disabled="isLoading"
              style="min-height: 52px; max-height: 200px;"
            ></textarea>
            
            <!-- 发送按钮 -->
            <button
              type="submit"
              :disabled="isLoading || !inputMessage.trim() || inputMessage.length > 2000"
              class="m-1.5 p-1.5 bg-white hover:bg-gray-100 disabled:bg-gray-600 disabled:cursor-not-allowed text-gray-900 disabled:text-gray-400 rounded-lg transition-colors duration-200 flex items-center justify-center"
              title="发送消息"
            >
              <font-awesome-icon 
                :icon="isLoading ? ['fas', 'spinner'] : ['fas', 'arrow-up']" 
                :class="{ 'animate-spin': isLoading }"
                class="h-3.5 w-3.5" 
              />
            </button>
          </div>
          
          <!-- 字符计数 -->
          <div class="absolute -bottom-5 right-0 text-xs text-gray-500" v-if="inputMessage.length > 1800">
            {{ inputMessage.length }}/2000
          </div>
        </form>
        
        <!-- 输入提示 -->
            <div class="mt-2 text-xs text-gray-500 text-center">
              AI 可能会出错。请核查重要信息。
            </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, nextTick, watch } from 'vue'
import MarkdownIt from 'markdown-it'
import api from '../api/index.js'

// 配置markdown-it
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true
})

export default {
  name: 'ChatArea',
  props: {
    currentConversation: {
      type: Object,
      default: null
    },
    messages: {
      type: Array,
      default: () => []
    },
    isLoading: {
      type: Boolean,
      default: false
    },
    isLoggedIn: {
      type: Boolean,
      default: false
    },
    sidebarCollapsed: {
      type: Boolean,
      default: false
    }
  },
  emits: ['sendMessage', 'feedbackUpdated'],
  setup(props, { emit }) {
    const inputMessage = ref('')
    const messagesContainer = ref(null)
    const messageInput = ref(null)
    
    const quickSuggestions = ref([
      {
        icon: ['fas', 'heart'],
        title: '情感支持',
        description: '分享您的感受和情绪',
        text: '我最近感到有些焦虑，能帮我分析一下原因吗？'
      },
      {
        icon: ['fas', 'brain'],
        title: '压力管理',
        description: '学习应对压力的方法',
        text: '我工作压力很大，有什么好的减压方法吗？'
      },
      {
        icon: ['fas', 'moon'],
        title: '睡眠问题',
        description: '改善睡眠质量',
        text: '我最近失眠严重，有什么改善睡眠的建议吗？'
      },
      {
        icon: ['fas', 'users'],
        title: '人际关系',
        description: '处理人际交往困扰',
        text: '我在人际交往中遇到了一些困难，能给我一些建议吗？'
      }
    ])
    
    const handleSendMessage = () => {
      if (!inputMessage.value.trim() || props.isLoading) return
      
      emit('sendMessage', inputMessage.value.trim())
      inputMessage.value = ''
      
      // 重置输入框高度
      nextTick(() => {
        if (messageInput.value) {
          messageInput.value.style.height = '44px'
        }
      })
    }
    
    const sendQuickMessage = (message) => {
      emit('sendMessage', message)
    }
    
    const handleKeyDown = (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault()
        handleSendMessage()
      }
      
      // 自动调整输入框高度
      nextTick(() => {
        const textarea = event.target
        textarea.style.height = '44px'
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px'
      })
    }
    
    const scrollToBottom = () => {
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
        }
      })
    }
    
    const formatMessage = (content) => {
      try {
        // 使用markdown-it渲染
        let html = md.render(content)
        
        // 添加自定义样式类
        html = html
          // 为列表添加样式
          .replace(/<ul>/g, '<ul class="list-disc list-inside space-y-1 ml-4">')
          .replace(/<ol>/g, '<ol class="list-decimal list-inside space-y-1 ml-4">')
          .replace(/<li>/g, '<li class="text-gray-100">')
          // 为标题添加样式
          .replace(/<h1>/g, '<h1 class="text-xl font-bold text-white mb-3 mt-4">')
          .replace(/<h2>/g, '<h2 class="text-lg font-bold text-white mb-2 mt-3">')
          .replace(/<h3>/g, '<h3 class="text-base font-semibold text-white mb-2 mt-2">')
          // 为段落添加样式
          .replace(/<p>/g, '<p class="text-gray-100 mb-2">')
          // 为强调文本添加样式
          .replace(/<strong>/g, '<strong class="font-semibold text-white">')
          .replace(/<em>/g, '<em class="italic text-blue-300">')
          // 为代码块添加样式
          .replace(/<code>/g, '<code class="bg-gray-700 text-green-300 px-1 py-0.5 rounded text-sm">')
          .replace(/<pre>/g, '<pre class="bg-gray-800 p-3 rounded-lg overflow-x-auto my-2">')
          // 为复选框样式（✓）添加特殊处理
          .replace(/✓/g, '<span class="text-green-400 font-bold">✓</span>')
          // 为链接添加样式
          .replace(/<a /g, '<a class="text-blue-400 hover:text-blue-300 underline" target="_blank" ')
        
        return html
      } catch (error) {
        console.error('Markdown渲染错误:', error)
        // 降级到简单渲染
        return content
          .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-white">$1</strong>')
          .replace(/\*(.*?)\*/g, '<em class="italic text-blue-300">$1</em>')
          .replace(/`(.*?)`/g, '<code class="bg-gray-700 text-green-300 px-1 rounded">$1</code>')
          .replace(/\n/g, '<br>')
      }
    }
    
    const formatTime = (timestamp) => {
      if (!timestamp) return ''
      
      const date = new Date(timestamp)
      const now = new Date()
      const diffMs = now - date
      const diffMins = Math.floor(diffMs / 60000)
      
      if (diffMins < 1) return '刚刚'
      if (diffMins < 60) return `${diffMins}分钟前`
      if (diffMins < 1440) return `${Math.floor(diffMins / 60)}小时前`
      
      return date.toLocaleString('zh-CN', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
    
    const copyMessage = async (content) => {
      try {
        await navigator.clipboard.writeText(content)
        // TODO: 显示复制成功提示
        console.log('消息已复制到剪贴板')
      } catch (err) {
        console.error('复制失败:', err)
      }
    }
    
    const likeMessage = async (messageId, isPositive) => {
      try {
        console.log('消息反馈:', messageId, isPositive ? 'positive' : 'negative')
        
        // 调用API更新消息反馈
        const feedback = isPositive ? 1 : -1
        
        // 立即更新本地消息状态，提供即时反馈
        const targetMessage = props.messages.find(msg => msg.message_id === messageId)
        if (targetMessage) {
          targetMessage.feedback = feedback
        }
        
        const response = await api.updateMessageFeedback(messageId, feedback)
        
        if (response.data) {
          console.log('反馈更新成功:', response.data)
          // 确保本地状态与API返回的数据一致
          if (targetMessage && response.data.feedback !== undefined) {
            targetMessage.feedback = response.data.feedback
          }
          // 触发消息列表更新，让父组件重新获取消息
          emit('feedbackUpdated', messageId, feedback)
        }
      } catch (error) {
        console.error('更新消息反馈失败:', error)
        // 如果API调用失败，恢复本地状态
        const targetMessage = props.messages.find(msg => msg.message_id === messageId)
        if (targetMessage) {
          targetMessage.feedback = null
        }
        // TODO: 显示错误提示
      }
    }
    
    const clearChat = () => {
      if (confirm('确定要清空当前对话吗？此操作无法撤销。')) {
        // TODO: 实现清空对话功能
        console.log('清空对话')
      }
    }
    
    const exportChat = () => {
      // TODO: 实现导出对话功能
      console.log('导出对话')
    }
    
    // 监听消息变化，自动滚动到底部
    watch(
      () => [props.messages.length, props.isLoading],
      () => {
        scrollToBottom()
      },
      { flush: 'post' }
    )
    
    return {
      inputMessage,
      messagesContainer,
      messageInput,
      quickSuggestions,
      handleSendMessage,
      sendQuickMessage,
      handleKeyDown,
      formatMessage,
      formatTime,
      copyMessage,
      likeMessage,
      clearChat,
      exportChat
    }
  }
}
</script>

<style scoped>
/* 自定义滚动条样式 */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #374151;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #6B7280;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #9CA3AF;
}

/* Markdown内容样式 */
:deep(.prose) {
  @apply max-w-none;
}

:deep(.prose h1) {
  @apply text-xl font-bold text-white mb-3 mt-4;
}

:deep(.prose h2) {
  @apply text-lg font-bold text-white mb-2 mt-3;
}

:deep(.prose h3) {
  @apply text-base font-semibold text-white mb-2 mt-2;
}

:deep(.prose p) {
  @apply text-gray-100 mb-2 leading-relaxed;
}

:deep(.prose ul) {
  @apply list-disc list-inside space-y-1 ml-4 mb-3;
}

:deep(.prose ol) {
  @apply list-decimal list-inside space-y-1 ml-4 mb-3;
}

:deep(.prose li) {
  @apply text-gray-100 leading-relaxed;
}

:deep(.prose strong) {
  @apply font-semibold text-white;
}

:deep(.prose em) {
  @apply italic text-blue-300;
}

:deep(.prose code) {
  @apply bg-gray-700 text-green-300 px-1 py-0.5 rounded text-sm;
}

:deep(.prose pre) {
  @apply bg-gray-800 p-3 rounded-lg overflow-x-auto my-2;
}

:deep(.prose pre code) {
  @apply bg-transparent p-0;
}

:deep(.prose a) {
  @apply text-blue-400 hover:text-blue-300 underline;
}

:deep(.prose blockquote) {
  @apply border-l-4 border-gray-600 pl-4 italic text-gray-300 my-2;
}

/* 特殊符号样式 */
:deep(.text-green-400) {
  @apply font-bold;
}

/* 输入框样式 */
textarea {
  field-sizing: content;
}
</style>
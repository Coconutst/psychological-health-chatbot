<template>
  <div class="w-full h-full bg-gray-800 border-r border-gray-700 flex flex-col">

    <!-- 新建对话按钮 - 紧凑版 -->
    <div class="p-3 border-b border-gray-700">
      <button
        @click="createNewConversation"
        class="w-full flex items-center justify-center space-x-2 px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded text-sm transition-colors duration-200 font-medium"
        :disabled="!isLoggedIn"
        :class="{ 'opacity-50 cursor-not-allowed': !isLoggedIn }"
      >
        <font-awesome-icon :icon="['fas', 'plus']" class="h-3 w-3" />
        <span>{{ isLoggedIn ? '新建对话' : '登录后可新建对话' }}</span>
      </button>
    </div>

    <!-- 对话列表 - 紧凑版 -->
    <div class="flex-1 overflow-y-auto">
      <div class="p-2">
        <div v-if="conversations.length === 0" class="text-center py-6">
          <font-awesome-icon :icon="['fas', 'comments']" class="h-8 w-8 text-gray-600 mb-2" />
          <p class="text-gray-400 text-xs">{{ isLoggedIn ? '暂无对话记录' : '未登录状态' }}</p>
          <p class="text-gray-500 text-xs mt-1">{{ isLoggedIn ? '点击上方按钮开始新对话' : '可直接在右侧开始临时对话' }}</p>
        </div>
        
        <div v-else class="space-y-1">
          <div
            v-for="conversation in conversations"
            :key="conversation.id"
            @click="selectConversation(conversation)"
            class="group relative p-2 rounded cursor-pointer transition-all duration-200 hover:bg-gray-700"
            :class="{
              'bg-gray-700 border border-indigo-500': currentConversationId === conversation.conversation_id,
              'hover:bg-gray-750': currentConversationId !== conversation.conversation_id
            }"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1 min-w-0">
                <h3 class="text-xs font-medium text-white truncate">
                  {{ conversation.title || '新对话' }}
                </h3>
                <p class="text-xs text-gray-500 mt-0.5">
                  {{ formatDate(conversation.created_at) }}
                </p>
                <div v-if="conversation.last_message" class="text-xs text-gray-500 mt-0.5 truncate">
                  {{ conversation.last_message }}
                </div>
              </div>
              
              <!-- 对话操作按钮 -->
              <div class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                <button
                  @click.stop="editConversationTitle(conversation)"
                  class="p-1 text-gray-400 hover:text-white hover:bg-gray-600 rounded transition-colors duration-200"
                  title="编辑标题"
                >
                  <font-awesome-icon :icon="['fas', 'edit']" class="h-3 w-3" />
                </button>
                <button
                  @click.stop="deleteConversation(conversation.conversation_id)"
                  class="p-1 text-gray-400 hover:text-red-400 hover:bg-gray-600 rounded transition-colors duration-200"
                  title="删除对话"
                >
                  <font-awesome-icon :icon="['fas', 'trash']" class="h-3 w-3" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部状态栏 - 紧凑版 -->
    <div class="p-3 border-t border-gray-700">
      <div class="flex items-center justify-between text-xs text-gray-400">
        <span>{{ conversations.length }} 个对话</span>
        <div class="flex items-center space-x-1">
          <div class="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
          <span>在线</span>
        </div>
      </div>
    </div>


  </div>
</template>

<script>
import { ref } from 'vue'
import api from '../api/index.js'

export default {
  name: 'Sidebar',
  props: {
    conversations: {
      type: Array,
      default: () => []
    },
    currentConversationId: {
      type: String,
      default: null
    },
    isLoggedIn: {
      type: Boolean,
      default: false
    },
    isCollapsed: {
      type: Boolean,
      default: false
    }
  },
  emits: ['select-conversation', 'new-conversation', 'delete-conversation', 'title-updated'],
  setup(props, { emit }) {
    
    const selectConversation = (conversation) => {
      emit('select-conversation', conversation.conversation_id)
    }
    
    const createNewConversation = () => {
      emit('new-conversation')
    }
    
    const deleteConversation = async (conversationId) => {
      try {
        // 使用自定义确认对话框
        const confirmed = await getCustomConfirm('确定要删除这个对话吗？', '此操作无法撤销，请谨慎操作。')
        
        if (confirmed) {
          emit('delete-conversation', conversationId)
        }
      } catch (error) {
        console.error('❌ 删除对话确认失败:', error)
      }
    }
    
    const editConversationTitle = async (conversation) => {
      console.log('✏️ 编辑对话标题:', conversation)
      
      try {
        // 直接使用自定义输入框，避免 prompt() 不支持的问题
        const newTitle = await getCustomInput('请输入新的对话标题:', conversation.title || '新对话')
        
        if (newTitle && newTitle.trim() !== conversation.title) {
          console.log('🔄 开始更新对话标题:', conversation.conversation_id, newTitle)
          
          // 调用API更新对话标题
          const response = await api.updateConversationTitle(conversation.conversation_id, newTitle.trim())
          
          console.log('✅ 对话标题更新成功:', response.data)
          
          // 通知父组件标题已更新，触发对话列表刷新
          emit('title-updated', {
            conversationId: conversation.conversation_id,
            newTitle: newTitle.trim()
          })
        }
      } catch (error) {
        console.error('❌ 编辑对话标题失败:', error)
        alert('操作失败，请稍后重试')
      }
    }
    
    // 自定义输入对话框函数
    const getCustomInput = (message, defaultValue = '') => {
      return new Promise((resolve) => {
        // 创建遮罩层
        const overlay = document.createElement('div')
        overlay.style.cssText = `
          position: fixed;
          top: 0;
          left: 0;
          width: 100vw;
          height: 100vh;
          background: rgba(0, 0, 0, 0.6);
          z-index: 10000;
          display: flex;
          align-items: center;
          justify-content: center;
          backdrop-filter: blur(2px);
        `
        
        // 创建对话框容器
        const dialog = document.createElement('div')
        dialog.style.cssText = `
          background: #1F2937;
          border-radius: 12px;
          padding: 24px;
          box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
          border: 1px solid #374151;
          min-width: 400px;
          max-width: 90vw;
        `
        
        // 创建标题
        const title = document.createElement('h3')
        title.textContent = message
        title.style.cssText = `
          color: #F9FAFB;
          font-size: 16px;
          font-weight: 600;
          margin: 0 0 16px 0;
          text-align: center;
        `
        
        // 创建输入框
        const input = document.createElement('input')
        input.type = 'text'
        input.value = defaultValue
        input.style.cssText = `
          width: 100%;
          padding: 12px 16px;
          border: 2px solid #374151;
          border-radius: 8px;
          background: #111827;
          color: #F9FAFB;
          font-size: 14px;
          outline: none;
          transition: border-color 0.2s;
          box-sizing: border-box;
        `
        
        // 输入框焦点样式
        input.addEventListener('focus', () => {
          input.style.borderColor = '#4F46E5'
        })
        input.addEventListener('blur', () => {
          input.style.borderColor = '#374151'
        })
        
        // 创建按钮容器
        const buttonContainer = document.createElement('div')
        buttonContainer.style.cssText = `
          display: flex;
          gap: 12px;
          margin-top: 20px;
          justify-content: flex-end;
        `
        
        // 创建确定按钮
        const confirmBtn = document.createElement('button')
        confirmBtn.textContent = '确定'
        confirmBtn.style.cssText = `
          padding: 10px 20px;
          background: #4F46E5;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          transition: background-color 0.2s;
        `
        
        // 创建取消按钮
        const cancelBtn = document.createElement('button')
        cancelBtn.textContent = '取消'
        cancelBtn.style.cssText = `
          padding: 10px 20px;
          background: #6B7280;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          transition: background-color 0.2s;
        `
        
        // 按钮悬停效果
        confirmBtn.addEventListener('mouseenter', () => {
          confirmBtn.style.backgroundColor = '#4338CA'
        })
        confirmBtn.addEventListener('mouseleave', () => {
          confirmBtn.style.backgroundColor = '#4F46E5'
        })
        
        cancelBtn.addEventListener('mouseenter', () => {
          cancelBtn.style.backgroundColor = '#5B6470'
        })
        cancelBtn.addEventListener('mouseleave', () => {
          cancelBtn.style.backgroundColor = '#6B7280'
        })
        
        // 组装对话框
        buttonContainer.appendChild(confirmBtn)
        buttonContainer.appendChild(cancelBtn)
        
        dialog.appendChild(title)
        dialog.appendChild(input)
        dialog.appendChild(buttonContainer)
        
        overlay.appendChild(dialog)
        document.body.appendChild(overlay)
        
        // 聚焦输入框并选中文本
        setTimeout(() => {
          input.focus()
          input.select()
        }, 100)
        
        // 清理函数
        const cleanup = () => {
          if (document.body.contains(overlay)) {
            document.body.removeChild(overlay)
          }
        }
        
        // 确定按钮事件
        confirmBtn.onclick = () => {
          const value = input.value.trim()
          resolve(value || null)
          cleanup()
        }
        
        // 取消按钮事件
        cancelBtn.onclick = () => {
          resolve(null)
          cleanup()
        }
        
        // 键盘事件
        input.onkeydown = (e) => {
          if (e.key === 'Enter') {
            e.preventDefault()
            const value = input.value.trim()
            resolve(value || null)
            cleanup()
          } else if (e.key === 'Escape') {
            e.preventDefault()
            resolve(null)
            cleanup()
          }
        }
        
        // 点击遮罩层关闭
        overlay.onclick = (e) => {
          if (e.target === overlay) {
            resolve(null)
            cleanup()
          }
        }
      })
    }
    
    // 自定义确认对话框函数
    const getCustomConfirm = (title, message) => {
      return new Promise((resolve) => {
        // 创建遮罩层
        const overlay = document.createElement('div')
        overlay.style.cssText = `
          position: fixed;
          top: 0;
          left: 0;
          width: 100vw;
          height: 100vh;
          background: rgba(0, 0, 0, 0.6);
          z-index: 10000;
          display: flex;
          align-items: center;
          justify-content: center;
          backdrop-filter: blur(2px);
        `
        
        // 创建对话框容器
        const dialog = document.createElement('div')
        dialog.style.cssText = `
          background: #1F2937;
          border-radius: 12px;
          padding: 24px;
          box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
          border: 1px solid #374151;
          min-width: 400px;
          max-width: 90vw;
        `
        
        // 创建标题
        const titleElement = document.createElement('h3')
        titleElement.textContent = title
        titleElement.style.cssText = `
          color: #F9FAFB;
          font-size: 18px;
          font-weight: 600;
          margin: 0 0 12px 0;
          text-align: center;
        `
        
        // 创建消息内容
        const messageElement = document.createElement('p')
        messageElement.textContent = message
        messageElement.style.cssText = `
          color: #D1D5DB;
          font-size: 14px;
          margin: 0 0 20px 0;
          text-align: center;
          line-height: 1.5;
        `
        
        // 创建按钮容器
        const buttonContainer = document.createElement('div')
        buttonContainer.style.cssText = `
          display: flex;
          gap: 12px;
          justify-content: center;
        `
        
        // 创建确定按钮（删除）
        const confirmBtn = document.createElement('button')
        confirmBtn.textContent = '确定删除'
        confirmBtn.style.cssText = `
          padding: 10px 20px;
          background: #DC2626;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          transition: background-color 0.2s;
        `
        
        // 创建取消按钮
        const cancelBtn = document.createElement('button')
        cancelBtn.textContent = '取消'
        cancelBtn.style.cssText = `
          padding: 10px 20px;
          background: #6B7280;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          transition: background-color 0.2s;
        `
        
        // 按钮悬停效果
        confirmBtn.addEventListener('mouseenter', () => {
          confirmBtn.style.backgroundColor = '#B91C1C'
        })
        confirmBtn.addEventListener('mouseleave', () => {
          confirmBtn.style.backgroundColor = '#DC2626'
        })
        
        cancelBtn.addEventListener('mouseenter', () => {
          cancelBtn.style.backgroundColor = '#5B6470'
        })
        cancelBtn.addEventListener('mouseleave', () => {
          cancelBtn.style.backgroundColor = '#6B7280'
        })
        
        // 组装对话框
        buttonContainer.appendChild(cancelBtn)
        buttonContainer.appendChild(confirmBtn)
        
        dialog.appendChild(titleElement)
        dialog.appendChild(messageElement)
        dialog.appendChild(buttonContainer)
        
        overlay.appendChild(dialog)
        document.body.appendChild(overlay)
        
        // 清理函数
        const cleanup = () => {
          if (document.body.contains(overlay)) {
            document.body.removeChild(overlay)
          }
        }
        
        // 确定按钮事件
        confirmBtn.onclick = () => {
          resolve(true)
          cleanup()
        }
        
        // 取消按钮事件
        cancelBtn.onclick = () => {
          resolve(false)
          cleanup()
        }
        
        // 键盘事件
        document.addEventListener('keydown', function handleKeydown(e) {
          if (e.key === 'Enter') {
            e.preventDefault()
            resolve(true)
            cleanup()
            document.removeEventListener('keydown', handleKeydown)
          } else if (e.key === 'Escape') {
            e.preventDefault()
            resolve(false)
            cleanup()
            document.removeEventListener('keydown', handleKeydown)
          }
        })
        
        // 点击遮罩层关闭
        overlay.onclick = (e) => {
          if (e.target === overlay) {
            resolve(false)
            cleanup()
          }
        }
      })
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return ''
      
      const date = new Date(dateString)
      const now = new Date()
      const diffTime = Math.abs(now - date)
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      
      if (diffDays === 1) {
        return '今天'
      } else if (diffDays === 2) {
        return '昨天'
      } else if (diffDays <= 7) {
        return `${diffDays - 1}天前`
      } else {
        return date.toLocaleDateString('zh-CN', {
          month: 'short',
          day: 'numeric'
        })
      }
    }
    
    return {
      selectConversation,
      createNewConversation,
      deleteConversation,
      editConversationTitle,
      formatDate
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
</style>
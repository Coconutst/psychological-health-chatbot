<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
      <!-- 模态框头部 -->
      <div class="flex items-center justify-between p-6 border-b border-gray-700">
        <h2 class="text-xl font-semibold text-white">设置</h2>
        <button
          @click="$emit('close')"
          class="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-md transition-colors duration-200"
        >
          <font-awesome-icon :icon="['fas', 'times']" class="h-5 w-5" />
        </button>
      </div>

      <!-- 设置内容 -->
      <div class="p-6 space-y-6">
        <!-- 账户设置 -->
        <div class="space-y-4">
          <h3 class="text-lg font-medium text-white border-b border-gray-700 pb-2">
            <font-awesome-icon :icon="['fas', 'user-cog']" class="mr-2" />
            账户设置
          </h3>
          
          <!-- 修改密码 -->
          <div class="bg-gray-700 rounded-lg p-4">
            <h4 class="text-white font-medium mb-3">修改密码</h4>
            <div class="space-y-3">
              <div>
                <label class="block text-sm text-gray-300 mb-1">当前密码</label>
                <div class="relative">
                  <input
                    v-model="passwordForm.currentPassword"
                    :type="showCurrentPassword ? 'text' : 'password'"
                    class="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="请输入当前密码"
                  />
                  <button
                    type="button"
                    @click="showCurrentPassword = !showCurrentPassword"
                    class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-white"
                  >
                    <font-awesome-icon :icon="['fas', showCurrentPassword ? 'eye-slash' : 'eye']" />
                  </button>
                </div>
              </div>
              
              <div>
                <label class="block text-sm text-gray-300 mb-1">新密码</label>
                <div class="relative">
                  <input
                    v-model="passwordForm.newPassword"
                    :type="showNewPassword ? 'text' : 'password'"
                    class="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="请输入新密码"
                  />
                  <button
                    type="button"
                    @click="showNewPassword = !showNewPassword"
                    class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-white"
                  >
                    <font-awesome-icon :icon="['fas', showNewPassword ? 'eye-slash' : 'eye']" />
                  </button>
                </div>
              </div>
              
              <div>
                <label class="block text-sm text-gray-300 mb-1">确认新密码</label>
                <div class="relative">
                  <input
                    v-model="passwordForm.confirmPassword"
                    :type="showConfirmPassword ? 'text' : 'password'"
                    class="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="请再次输入新密码"
                  />
                  <button
                    type="button"
                    @click="showConfirmPassword = !showConfirmPassword"
                    class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-white"
                  >
                    <font-awesome-icon :icon="['fas', showConfirmPassword ? 'eye-slash' : 'eye']" />
                  </button>
                </div>
              </div>
              
              <button
                @click="changePassword"
                :disabled="!canChangePassword || isChangingPassword"
                class="w-full px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-md transition-colors duration-200 flex items-center justify-center"
              >
                <font-awesome-icon 
                  v-if="isChangingPassword" 
                  :icon="['fas', 'spinner']" 
                  class="animate-spin mr-2" 
                />
                {{ isChangingPassword ? '修改中...' : '修改密码' }}
              </button>
            </div>
          </div>
        </div>

        <!-- 聊天设置 -->
        <div class="space-y-4">
          <h3 class="text-lg font-medium text-white border-b border-gray-700 pb-2">
            <font-awesome-icon :icon="['fas', 'comments']" class="mr-2" />
            聊天设置
          </h3>
          
          <div class="bg-gray-700 rounded-lg p-4 space-y-4">
            <!-- 自动保存对话 -->
            <div class="flex items-center justify-between">
              <div>
                <label class="text-white font-medium">自动保存对话</label>
                <p class="text-sm text-gray-400">自动保存您的聊天记录</p>
              </div>
              <button
                @click="settings.autoSave = !settings.autoSave"
                :class="[
                  'relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200',
                  settings.autoSave ? 'bg-indigo-600' : 'bg-gray-600'
                ]"
              >
                <span
                  :class="[
                    'inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200',
                    settings.autoSave ? 'translate-x-6' : 'translate-x-1'
                  ]"
                />
              </button>
            </div>
            
            <!-- 发送快捷键 -->
            <div class="flex items-center justify-between">
              <div>
                <label class="text-white font-medium">Enter 发送消息</label>
                <p class="text-sm text-gray-400">按 Enter 键发送消息，Shift+Enter 换行</p>
              </div>
              <button
                @click="settings.enterToSend = !settings.enterToSend"
                :class="[
                  'relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200',
                  settings.enterToSend ? 'bg-indigo-600' : 'bg-gray-600'
                ]"
              >
                <span
                  :class="[
                    'inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200',
                    settings.enterToSend ? 'translate-x-6' : 'translate-x-1'
                  ]"
                />
              </button>
            </div>
            
            <!-- 显示时间戳 -->
            <div class="flex items-center justify-between">
              <div>
                <label class="text-white font-medium">显示时间戳</label>
                <p class="text-sm text-gray-400">在消息旁显示发送时间</p>
              </div>
              <button
                @click="settings.showTimestamp = !settings.showTimestamp"
                :class="[
                  'relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200',
                  settings.showTimestamp ? 'bg-indigo-600' : 'bg-gray-600'
                ]"
              >
                <span
                  :class="[
                    'inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200',
                    settings.showTimestamp ? 'translate-x-6' : 'translate-x-1'
                  ]"
                />
              </button>
            </div>
            
            <!-- 字体大小 -->
            <div>
              <label class="block text-white font-medium mb-2">字体大小</label>
              <div class="flex items-center space-x-4">
                <span class="text-sm text-gray-400">小</span>
                <input
                  v-model="settings.fontSize"
                  type="range"
                  min="12"
                  max="20"
                  step="1"
                  class="flex-1 h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer slider"
                />
                <span class="text-sm text-gray-400">大</span>
                <span class="text-white text-sm w-8">{{ settings.fontSize }}px</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 隐私设置 -->
        <div class="space-y-4">
          <h3 class="text-lg font-medium text-white border-b border-gray-700 pb-2">
            <font-awesome-icon :icon="['fas', 'shield-alt']" class="mr-2" />
            隐私设置
          </h3>
          
          <div class="bg-gray-700 rounded-lg p-4 space-y-4">
            <!-- 数据收集 -->
            <div class="flex items-center justify-between">
              <div>
                <label class="text-white font-medium">允许数据分析</label>
                <p class="text-sm text-gray-400">帮助我们改进服务质量</p>
              </div>
              <button
                @click="settings.allowAnalytics = !settings.allowAnalytics"
                :class="[
                  'relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200',
                  settings.allowAnalytics ? 'bg-indigo-600' : 'bg-gray-600'
                ]"
              >
                <span
                  :class="[
                    'inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200',
                    settings.allowAnalytics ? 'translate-x-6' : 'translate-x-1'
                  ]"
                />
              </button>
            </div>
            
            <!-- 情绪分析 -->
            <div class="flex items-center justify-between">
              <div>
                <label class="text-white font-medium">情绪分析</label>
                <p class="text-sm text-gray-400">分析您的情绪状态以提供更好的建议</p>
              </div>
              <button
                @click="settings.emotionAnalysis = !settings.emotionAnalysis"
                :class="[
                  'relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200',
                  settings.emotionAnalysis ? 'bg-indigo-600' : 'bg-gray-600'
                ]"
              >
                <span
                  :class="[
                    'inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200',
                    settings.emotionAnalysis ? 'translate-x-6' : 'translate-x-1'
                  ]"
                />
              </button>
            </div>
          </div>
        </div>

        <!-- 通知设置 -->
        <div class="space-y-4">
          <h3 class="text-lg font-medium text-white border-b border-gray-700 pb-2">
            <font-awesome-icon :icon="['fas', 'bell']" class="mr-2" />
            通知设置
          </h3>
          
          <div class="bg-gray-700 rounded-lg p-4 space-y-4">
            <!-- 浏览器通知 -->
            <div class="flex items-center justify-between">
              <div>
                <label class="text-white font-medium">浏览器通知</label>
                <p class="text-sm text-gray-400">接收重要消息的浏览器通知</p>
              </div>
              <button
                @click="toggleNotifications"
                :class="[
                  'relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200',
                  settings.browserNotifications ? 'bg-indigo-600' : 'bg-gray-600'
                ]"
              >
                <span
                  :class="[
                    'inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200',
                    settings.browserNotifications ? 'translate-x-6' : 'translate-x-1'
                  ]"
                />
              </button>
            </div>
            
            <!-- 声音提醒 -->
            <div class="flex items-center justify-between">
              <div>
                <label class="text-white font-medium">声音提醒</label>
                <p class="text-sm text-gray-400">新消息时播放提示音</p>
              </div>
              <button
                @click="settings.soundNotifications = !settings.soundNotifications"
                :class="[
                  'relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200',
                  settings.soundNotifications ? 'bg-indigo-600' : 'bg-gray-600'
                ]"
              >
                <span
                  :class="[
                    'inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200',
                    settings.soundNotifications ? 'translate-x-6' : 'translate-x-1'
                  ]"
                />
              </button>
            </div>
          </div>
        </div>

        <!-- 数据管理 -->
        <div class="space-y-4">
          <h3 class="text-lg font-medium text-white border-b border-gray-700 pb-2">
            <font-awesome-icon :icon="['fas', 'database']" class="mr-2" />
            数据管理
          </h3>
          
          <div class="bg-gray-700 rounded-lg p-4 space-y-3">
            <button
              @click="exportData"
              class="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors duration-200 flex items-center justify-center"
            >
              <font-awesome-icon :icon="['fas', 'download']" class="mr-2" />
              导出聊天记录
            </button>
            
            <button
              @click="clearAllData"
              class="w-full px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md transition-colors duration-200 flex items-center justify-center"
            >
              <font-awesome-icon :icon="['fas', 'trash']" class="mr-2" />
              清除所有数据
            </button>
          </div>
        </div>
      </div>

      <!-- 底部按钮 -->
      <div class="flex items-center justify-end space-x-3 p-6 border-t border-gray-700">
        <button
          @click="resetSettings"
          class="px-4 py-2 text-gray-400 hover:text-white transition-colors duration-200"
        >
          重置设置
        </button>
        <button
          @click="saveSettings"
          :disabled="isSaving"
          class="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-600 text-white rounded-md transition-colors duration-200 flex items-center"
        >
          <font-awesome-icon 
            v-if="isSaving" 
            :icon="['fas', 'spinner']" 
            class="animate-spin mr-2" 
          />
          {{ isSaving ? '保存中...' : '保存设置' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../api/index.js'

export default {
  name: 'Settings',
  emits: ['close'],
  setup() {
    const passwordForm = ref({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    })
    
    const showCurrentPassword = ref(false)
    const showNewPassword = ref(false)
    const showConfirmPassword = ref(false)
    const isChangingPassword = ref(false)
    const isSaving = ref(false)
    
    const settings = ref({
      autoSave: true,
      enterToSend: true,
      showTimestamp: true,
      fontSize: 14,
      allowAnalytics: true,
      emotionAnalysis: true,
      browserNotifications: false,
      soundNotifications: true
    })
    
    const canChangePassword = computed(() => {
      return passwordForm.value.currentPassword && 
             passwordForm.value.newPassword && 
             passwordForm.value.confirmPassword &&
             passwordForm.value.newPassword === passwordForm.value.confirmPassword &&
             passwordForm.value.newPassword.length >= 6
    })
    
    const loadSettings = () => {
      const savedSettings = localStorage.getItem('chatSettings')
      if (savedSettings) {
        try {
          const parsed = JSON.parse(savedSettings)
          settings.value = { ...settings.value, ...parsed }
        } catch (error) {
          console.error('加载设置失败:', error)
        }
      }
    }
    
    const saveSettings = async () => {
      isSaving.value = true
      try {
        localStorage.setItem('chatSettings', JSON.stringify(settings.value))
        
        // 应用字体大小设置
        document.documentElement.style.setProperty('--chat-font-size', `${settings.value.fontSize}px`)
        
        // 这里可以调用API保存到服务器
        // await api.saveUserSettings(settings.value)
        
        setTimeout(() => {
          isSaving.value = false
        }, 1000)
      } catch (error) {
        console.error('保存设置失败:', error)
        isSaving.value = false
      }
    }
    
    const resetSettings = () => {
      if (confirm('确定要重置所有设置吗？')) {
        settings.value = {
          autoSave: true,
          enterToSend: true,
          showTimestamp: true,
          fontSize: 14,
          allowAnalytics: true,
          emotionAnalysis: true,
          browserNotifications: false,
          soundNotifications: true
        }
        localStorage.removeItem('chatSettings')
      }
    }
    
    const changePassword = async () => {
      if (!canChangePassword.value) return
      
      isChangingPassword.value = true
      try {
        await api.changePassword({
          current_password: passwordForm.value.currentPassword,
          new_password: passwordForm.value.newPassword
        })
        
        // 清空表单
        passwordForm.value = {
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        }
        
        alert('密码修改成功！')
      } catch (error) {
        console.error('修改密码失败:', error)
        alert('修改密码失败：' + (error.response?.data?.message || '未知错误'))
      } finally {
        isChangingPassword.value = false
      }
    }
    
    const toggleNotifications = async () => {
      if (!settings.value.browserNotifications) {
        // 请求通知权限
        if ('Notification' in window) {
          const permission = await Notification.requestPermission()
          if (permission === 'granted') {
            settings.value.browserNotifications = true
          } else {
            alert('需要允许通知权限才能启用此功能')
          }
        } else {
          alert('您的浏览器不支持通知功能')
        }
      } else {
        settings.value.browserNotifications = false
      }
    }
    
    const exportData = async () => {
      try {
        // 这里应该调用API获取用户数据
        const data = {
          conversations: [], // 从API获取
          settings: settings.value,
          exportDate: new Date().toISOString()
        }
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `chat-data-${new Date().toISOString().split('T')[0]}.json`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      } catch (error) {
        console.error('导出数据失败:', error)
        alert('导出数据失败')
      }
    }
    
    const clearAllData = () => {
      if (confirm('确定要清除所有聊天数据吗？此操作不可恢复！')) {
        if (confirm('请再次确认：这将删除所有对话记录和设置！')) {
          // 清除本地存储
          localStorage.clear()
          
          // 这里应该调用API清除服务器数据
          // await api.clearAllUserData()
          
          alert('所有数据已清除')
          location.reload()
        }
      }
    }
    
    onMounted(() => {
      loadSettings()
    })
    
    return {
      passwordForm,
      showCurrentPassword,
      showNewPassword,
      showConfirmPassword,
      isChangingPassword,
      isSaving,
      settings,
      canChangePassword,
      saveSettings,
      resetSettings,
      changePassword,
      toggleNotifications,
      exportData,
      clearAllData
    }
  }
}
</script>

<style scoped>
/* 自定义滑块样式 */
.slider::-webkit-slider-thumb {
  appearance: none;
  height: 16px;
  width: 16px;
  border-radius: 50%;
  background: #6366f1;
  cursor: pointer;
  border: 2px solid #ffffff;
}

.slider::-moz-range-thumb {
  height: 16px;
  width: 16px;
  border-radius: 50%;
  background: #6366f1;
  cursor: pointer;
  border: 2px solid #ffffff;
}
</style>
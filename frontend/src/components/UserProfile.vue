<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="$emit('close')">
    <div class="bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
      <!-- 模态框头部 -->
      <div class="flex items-center justify-between p-6 border-b border-gray-700">
        <h2 class="text-xl font-semibold text-white">个人资料</h2>
        <button
          @click="$emit('close')"
          class="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-md transition-colors duration-200"
        >
          <font-awesome-icon :icon="['fas', 'times']" class="h-5 w-5" />
        </button>
      </div>

      <!-- 用户基本信息 -->
      <div class="p-6 border-b border-gray-700">
        <div class="flex items-center space-x-4">
          <div class="w-16 h-16 bg-indigo-600 rounded-full flex items-center justify-center">
            <font-awesome-icon :icon="['fas', 'user']" class="text-white text-2xl" />
          </div>
          <div class="flex-1">
            <h3 class="text-lg font-medium text-white">{{ currentUserInfo?.username || userInfo?.username || '未知用户' }}</h3>
            <p class="text-gray-400">{{ currentUserInfo?.email || userInfo?.email || '未设置邮箱' }}</p>
            <p class="text-sm text-gray-500 mt-1">
              注册时间: {{ formatDate(currentUserInfo?.created_at || userInfo?.created_at) }}
            </p>
          </div>
          <button
            @click="showChangePassword = true"
            class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md transition-colors duration-200"
          >
            修改密码
          </button>
        </div>
      </div>

      <!-- 使用统计 -->
      <div class="p-6 border-b border-gray-700">
        <h4 class="text-lg font-medium text-white mb-4">使用统计</h4>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="bg-gray-700 rounded-lg p-4 text-center">
            <div class="text-2xl font-bold text-indigo-400">{{ stats.totalConversations }}</div>
            <div class="text-sm text-gray-400 mt-1">总对话数</div>
          </div>
          <div class="bg-gray-700 rounded-lg p-4 text-center">
            <div class="text-2xl font-bold text-green-400">{{ stats.totalMessages }}</div>
            <div class="text-sm text-gray-400 mt-1">消息总数</div>
          </div>
          <div class="bg-gray-700 rounded-lg p-4 text-center">
            <div class="text-2xl font-bold text-blue-400">{{ stats.activeDays }}</div>
            <div class="text-sm text-gray-400 mt-1">活跃天数</div>
          </div>
          <div class="bg-gray-700 rounded-lg p-4 text-center">
            <div class="text-2xl font-bold text-purple-400">{{ stats.avgSessionTime }}</div>
            <div class="text-sm text-gray-400 mt-1">平均会话时长</div>
          </div>
        </div>
      </div>

      <!-- 情绪统计 -->
      <div class="p-6 border-b border-gray-700" v-if="emotionStats">
        <h4 class="text-lg font-medium text-white mb-4">情绪统计</h4>
        <div class="space-y-4">
          <!-- 当前情绪状态 -->
          <div class="bg-gray-700 rounded-lg p-4">
            <h5 class="text-sm font-medium text-gray-300 mb-3">当前情绪状态</h5>
            <div class="flex items-center space-x-3">
              <span class="text-3xl">{{ getEmotionEmoji(emotionStats.current_emotion) }}</span>
              <div>
                <div class="text-white font-medium">{{ getEmotionLabel(emotionStats.current_emotion) }}</div>
                <div class="text-sm text-gray-400">更新时间: {{ formatDate(emotionStats.last_updated) }}</div>
              </div>
            </div>
          </div>

          <!-- 情绪分布 -->
          <div class="bg-gray-700 rounded-lg p-4">
            <h5 class="text-sm font-medium text-gray-300 mb-3">情绪分布统计</h5>
            <div class="space-y-2">
              <div 
                v-for="(count, emotion) in emotionStats.emotion_distribution" 
                :key="emotion"
                class="flex items-center justify-between"
              >
                <div class="flex items-center space-x-2">
                  <span class="text-2xl">{{ getEmotionEmoji(emotion) }}</span>
                  <span class="text-white">{{ getEmotionLabel(emotion) }}</span>
                </div>
                <div class="flex items-center space-x-2">
                  <div class="w-24 bg-gray-600 rounded-full h-2">
                    <div 
                      class="h-2 rounded-full transition-all duration-300"
                      :class="getEmotionColor(emotion)"
                      :style="{ width: `${(count / emotionStats.total_records * 100)}%` }"
                    ></div>
                  </div>
                  <span class="text-sm text-gray-400 w-12 text-right">{{ count }}次</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 最近情绪记录 -->
          <div class="bg-gray-700 rounded-lg p-4" v-if="emotionStats.recent_emotions">
            <h5 class="text-sm font-medium text-gray-300 mb-3">最近情绪记录</h5>
            <div class="space-y-2 max-h-40 overflow-y-auto">
              <div 
                v-for="(record, index) in emotionStats.recent_emotions.slice(0, 5)" 
                :key="index"
                class="flex items-center justify-between p-2 bg-gray-600 rounded"
              >
                <div class="flex items-center space-x-2">
                  <span class="text-lg">{{ getEmotionEmoji(record.emotion) }}</span>
                  <span class="text-white text-sm">{{ getEmotionLabel(record.emotion) }}</span>
                  <span class="text-xs text-gray-400">({{ Math.round(record.confidence * 100) }}%)</span>
                </div>
                <span class="text-xs text-gray-400">{{ formatTime(new Date(record.timestamp)) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 情绪画像 -->
      <div class="p-6 border-b border-gray-700" v-if="emotionProfile">
        <h4 class="text-lg font-medium text-white mb-4">情绪画像</h4>
        <div class="space-y-4">
          <!-- 主要情绪 -->
          <div class="bg-gray-700 rounded-lg p-4">
            <h5 class="text-sm font-medium text-gray-300 mb-3">主要情绪分布</h5>
            <div class="space-y-2">
              <div 
                v-for="emotion in emotionProfile.primary_emotions" 
                :key="emotion.emotion"
                class="flex items-center justify-between"
              >
                <div class="flex items-center space-x-2">
                  <span class="text-2xl">{{ getEmotionEmoji(emotion.emotion) }}</span>
                  <span class="text-white">{{ getEmotionLabel(emotion.emotion) }}</span>
                </div>
                <div class="flex items-center space-x-2">
                  <div class="w-24 bg-gray-600 rounded-full h-2">
                    <div 
                      class="h-2 rounded-full transition-all duration-300"
                      :class="getEmotionColor(emotion.emotion)"
                      :style="{ width: `${emotion.percentage}%` }"
                    ></div>
                  </div>
                  <span class="text-sm text-gray-400 w-12 text-right">{{ emotion.percentage }}%</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 情绪趋势 -->
          <div class="bg-gray-700 rounded-lg p-4">
            <h5 class="text-sm font-medium text-gray-300 mb-3">近期情绪趋势</h5>
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-400">整体情绪状态:</span>
              <span 
                :class="{
                  'text-green-400': emotionProfile.overall_mood === 'positive',
                  'text-yellow-400': emotionProfile.overall_mood === 'neutral',
                  'text-red-400': emotionProfile.overall_mood === 'negative'
                }"
              >
                {{ getMoodLabel(emotionProfile.overall_mood) }}
              </span>
            </div>
            <div class="flex items-center justify-between text-sm mt-2">
              <span class="text-gray-400">情绪稳定性:</span>
              <span class="text-blue-400">{{ emotionProfile.stability_score }}/10</span>
            </div>
          </div>

          <!-- 建议 -->
          <div class="bg-gray-700 rounded-lg p-4" v-if="emotionProfile.recommendations">
            <h5 class="text-sm font-medium text-gray-300 mb-3">个性化建议</h5>
            <ul class="space-y-2">
              <li 
                v-for="(recommendation, index) in emotionProfile.recommendations" 
                :key="index"
                class="flex items-start space-x-2 text-sm text-gray-300"
              >
                <font-awesome-icon :icon="['fas', 'lightbulb']" class="text-yellow-400 mt-0.5 flex-shrink-0" />
                <span>{{ recommendation }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 最近活动 -->
      <div class="p-6">
        <h4 class="text-lg font-medium text-white mb-4">最近活动</h4>
        <div class="space-y-3">
          <div 
            v-for="activity in recentActivities" 
            :key="activity.id"
            class="flex items-center space-x-3 p-3 bg-gray-700 rounded-lg"
          >
            <div class="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center flex-shrink-0">
              <font-awesome-icon :icon="activity.icon" class="text-white text-sm" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-white text-sm font-medium truncate">{{ activity.title }}</p>
              <p class="text-gray-400 text-xs">{{ activity.description }}</p>
            </div>
            <span class="text-xs text-gray-500 flex-shrink-0">{{ formatTime(activity.timestamp) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 修改密码模态框 -->
    <div v-if="showChangePassword" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-white">修改密码</h3>
          <button @click="showChangePassword = false" class="text-gray-400 hover:text-white transition-colors">
            <font-awesome-icon icon="times" class="w-4 h-4" />
          </button>
        </div>
        
        <form @submit.prevent="handleChangePassword" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">当前密码</label>
            <input
              v-model="passwordForm.currentPassword"
              type="password"
              required
              class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="请输入当前密码"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">新密码</label>
            <input
              v-model="passwordForm.newPassword"
              type="password"
              required
              minlength="6"
              class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="请输入新密码（至少6位）"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">确认新密码</label>
            <input
              v-model="passwordForm.confirmPassword"
              type="password"
              required
              class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="请再次输入新密码"
            />
          </div>
          
          <div v-if="passwordError" class="text-red-400 text-sm">{{ passwordError }}</div>
          <div v-if="passwordSuccess" class="text-green-400 text-sm">{{ passwordSuccess }}</div>
          
          <div class="flex space-x-3 pt-4">
            <button
              type="button"
              @click="showChangePassword = false"
              class="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md transition-colors duration-200"
            >
              取消
            </button>
            <button
              type="submit"
              :disabled="isChangingPassword"
              class="flex-1 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-800 disabled:cursor-not-allowed text-white rounded-md transition-colors duration-200"
            >
              {{ isChangingPassword ? '修改中...' : '确认修改' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '../api/index.js'

export default {
  name: 'UserProfile',
  props: {
    userInfo: {
      type: Object,
      required: false,
      default: () => ({})
    }
  },
  emits: ['close'],
  setup(props, { emit }) {
    // 用户信息状态
    const currentUserInfo = ref({})
    const isLoadingUserInfo = ref(false)
    const emotionProfile = ref(null)
    const stats = ref({
      totalConversations: 0,
      totalMessages: 0,
      activeDays: 0,
      avgSessionTime: '0分钟'
    })
    
    const recentActivities = ref([
      {
        id: 1,
        icon: ['fas', 'comments'],
        title: '开始新对话',
        description: '与心理健康助手开始了新的对话',
        timestamp: new Date(Date.now() - 1000 * 60 * 30) // 30分钟前
      },
      {
        id: 2,
        icon: ['fas', 'heart'],
        title: '情绪记录',
        description: '记录了当前的情绪状态',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2) // 2小时前
      },
      {
        id: 3,
        icon: ['fas', 'user-edit'],
        title: '更新资料',
        description: '更新了个人资料信息',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24) // 1天前
      }
    ])
    
    // 修改密码相关状态
    const showChangePassword = ref(false)
    const isChangingPassword = ref(false)
    const passwordError = ref('')
    const passwordSuccess = ref('')
    const passwordForm = ref({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    })

    // 获取用户信息
    const fetchUserInfo = async () => {
      try {
        isLoadingUserInfo.value = true
        const response = await api.getCurrentUser()
        if (response.data) {
          currentUserInfo.value = response.data
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
      } finally {
        isLoadingUserInfo.value = false
      }
    }

    // 组件挂载时获取用户信息
    onMounted(() => {
      fetchUserInfo()
    })

    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return '未知'
      try {
        const date = new Date(dateString)
        return date.toLocaleDateString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit'
        })
      } catch (error) {
        return '未知'
      }
    }
    
    const loadEmotionProfile = async () => {
      try {
        console.log('🔄 开始加载情绪画像数据...')
        const response = await api.getUserEmotionProfile()
        console.log('✅ 情绪画像API响应:', response)
        
        if (response.data && response.data.primary_emotions) {
          emotionProfile.value = response.data
          console.log('✅ 情绪画像数据加载成功:', emotionProfile.value)
        } else {
          console.warn('⚠️ API返回数据为空，使用模拟数据')
          // 使用模拟数据
          emotionProfile.value = {
            primary_emotions: [
              { emotion: 'calm', percentage: 35 },
              { emotion: 'happy', percentage: 25 },
              { emotion: 'anxious', percentage: 20 },
              { emotion: 'sad', percentage: 15 },
              { emotion: 'angry', percentage: 5 }
            ],
            overall_mood: 'neutral',
            stability_score: 7,
            recommendations: [
              '建议保持规律的作息时间',
              '可以尝试一些放松技巧，如深呼吸或冥想',
              '适当的运动有助于改善情绪状态',
              '与朋友或家人分享您的感受'
            ]
          }
        }
      } catch (error) {
        console.error('❌ 加载情绪画像失败:', error)
        // 使用模拟数据
        emotionProfile.value = {
          primary_emotions: [
            { emotion: 'calm', percentage: 35 },
            { emotion: 'happy', percentage: 25 },
            { emotion: 'anxious', percentage: 20 },
            { emotion: 'sad', percentage: 15 },
            { emotion: 'angry', percentage: 5 }
          ],
          overall_mood: 'neutral',
          stability_score: 7,
          recommendations: [
            '建议保持规律的作息时间',
            '可以尝试一些放松技巧，如深呼吸或冥想',
            '适当的运动有助于改善情绪状态',
            '与朋友或家人分享您的感受'
          ]
        }
      }
    }
    
    const emotionStats = ref(null)
    
    const loadUserStats = async () => {
      try {
        console.log('🔄 开始加载情绪统计数据...')
        const response = await api.getUserEmotionStats()
        console.log('✅ 情绪统计API响应:', response)
        
        if (response.data) {
          // 处理情绪统计数据
          emotionStats.value = response.data
          console.log('✅ 情绪统计数据加载成功:', emotionStats.value)
          
          // 更新统计信息
          stats.value = {
            totalConversations: response.data.total_records || 0,
            totalMessages: response.data.recent_emotions?.length || 0,
            activeDays: Math.ceil((response.data.total_records || 0) / 3), // 估算活跃天数
            avgSessionTime: '25分钟' // 暂时使用固定值
          }
          console.log('✅ 统计信息更新成功:', stats.value)
        } else {
          console.warn('⚠️ 情绪统计API返回数据为空')
          // 使用默认值
          stats.value = {
            totalConversations: 0,
            totalMessages: 0,
            activeDays: 0,
            avgSessionTime: '0分钟'
          }
        }
      } catch (error) {
        console.error('❌ 加载用户统计失败:', error)
        // 使用默认值
        stats.value = {
          totalConversations: 0,
          totalMessages: 0,
          activeDays: 0,
          avgSessionTime: '0分钟'
        }
      }
    }
    
    const getEmotionEmoji = (emotion) => {
      const emojiMap = {
        happy: '😊',
        sad: '😢',
        angry: '😠',
        anxious: '😰',
        calm: '😌',
        excited: '🤗',
        confused: '😕',
        grateful: '🙏',
        neutral: '😐'
      }
      return emojiMap[emotion] || '😐'
    }
    
    const getEmotionLabel = (emotion) => {
      const labelMap = {
        happy: '快乐',
        sad: '悲伤',
        angry: '愤怒',
        anxious: '焦虑',
        calm: '平静',
        excited: '兴奋',
        confused: '困惑',
        grateful: '感激',
        neutral: '中性'
      }
      return labelMap[emotion] || emotion
    }
    
    const getEmotionColor = (emotion) => {
      const colorMap = {
        happy: 'bg-yellow-400',
        sad: 'bg-blue-400',
        angry: 'bg-red-400',
        anxious: 'bg-orange-400',
        calm: 'bg-green-400',
        excited: 'bg-purple-400',
        confused: 'bg-gray-400',
        grateful: 'bg-pink-400',
        neutral: 'bg-gray-500'
      }
      return colorMap[emotion] || 'bg-gray-400'
    }
    
    const getMoodLabel = (mood) => {
      const moodMap = {
        positive: '积极',
        neutral: '中性',
        negative: '消极'
      }
      return moodMap[mood] || mood
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
      
      return date.toLocaleDateString('zh-CN')
    }
    
    const handleChangePassword = async () => {
      passwordError.value = ''
      passwordSuccess.value = ''
      
      // 验证密码
      if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
        passwordError.value = '新密码和确认密码不一致'
        return
      }
      
      if (passwordForm.value.newPassword.length < 6) {
        passwordError.value = '新密码长度至少为6位'
        return
      }
      
      isChangingPassword.value = true
      
      try {
        const response = await api.changePassword({
          current_password: passwordForm.value.currentPassword,
          new_password: passwordForm.value.newPassword
        })
        
        if (response.data.success) {
          passwordSuccess.value = '密码修改成功！'
          // 清空表单
          passwordForm.value = {
            currentPassword: '',
            newPassword: '',
            confirmPassword: ''
          }
          // 2秒后关闭模态框
          setTimeout(() => {
            showChangePassword.value = false
            passwordSuccess.value = ''
          }, 2000)
        } else {
          passwordError.value = response.data.message || '密码修改失败'
        }
      } catch (error) {
        console.error('修改密码失败:', error)
        passwordError.value = error.response?.data?.message || '修改密码失败，请重试'
      } finally {
        isChangingPassword.value = false
      }
    }
    
    onMounted(() => {
      fetchUserInfo()
      loadEmotionProfile()
      loadUserStats()
    })
    
    return {
      currentUserInfo,
      isLoadingUserInfo,
      emotionProfile,
      emotionStats,
      stats,
      recentActivities,
      showChangePassword,
      isChangingPassword,
      passwordError,
      passwordSuccess,
      passwordForm,
      getEmotionEmoji,
      getEmotionLabel,
      getEmotionColor,
      getMoodLabel,
      formatDate,
      formatTime,
      handleChangePassword,
      fetchUserInfo,
      close: () => emit('close')
    }
  }
}
</script>
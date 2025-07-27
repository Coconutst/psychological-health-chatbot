import { createApp } from 'vue'
import App from './App.vue'
import './style.css'

// FontAwesome配置
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import {
  faUser,
  faLock,
  faEnvelope,
  faPaperPlane,
  faPlus,
  faTrash,
  faEdit,
  faCog,
  faSignOutAlt,
  faBars,
  faTimes,
  faComments,
  faHeart,
  faChartLine,
  faRobot,
  faMoon,
  faSun,
  faThumbsUp,
  faThumbsDown,
  faCopy,
  faRefresh,
  faBrain,
  faEye,
  faEyeSlash,
  faInfoCircle,
  faUserSlash,
  faEllipsisVertical,
  faUserCircle,
  faBroom,
  faDownload,
  faSpinner,
  faUsers,
  faChevronLeft,
  faChevronRight,
  faArrowUp,
  faDatabase,
  faBell,
  faShieldAlt,
  faUserCog,
  faLightbulb,
  faUserEdit
} from '@fortawesome/free-solid-svg-icons'
import { 
  faUser as faUserRegular,
  faComments as faCommentsRegular 
} from '@fortawesome/free-regular-svg-icons'

// 添加图标到库
library.add(
  faUser,
  faLock,
  faEnvelope,
  faPaperPlane,
  faPlus,
  faTrash,
  faEdit,
  faCog,
  faSignOutAlt,
  faBars,
  faTimes,
  faComments,
  faHeart,
  faChartLine,
  faRobot,
  faMoon,
  faSun,
  faThumbsUp,
  faThumbsDown,
  faCopy,
  faRefresh,
  faBrain,
  faEye,
  faEyeSlash,
  faInfoCircle,
  faUserSlash,
  faEllipsisVertical,
  faUserCircle,
  faBroom,
  faDownload,
  faSpinner,
  faUsers,
  faChevronLeft,
  faChevronRight,
  faArrowUp,
  faDatabase,
  faBell,
  faShieldAlt,
  faUserCog,
  faLightbulb,
  faUserEdit,
  faUserRegular,
  faCommentsRegular
)

console.log('🎯 [MAIN] 开始创建Vue应用')
console.log('📦 [MAIN] Vue版本:', createApp.version || 'Unknown')
console.log('🌍 [MAIN] 环境模式:', import.meta.env.MODE)
console.log('🔗 [MAIN] API基础URL:', import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000')

const app = createApp(App)
app.component('font-awesome-icon', FontAwesomeIcon)
console.log('✅ [MAIN] Vue应用创建成功')

app.mount('#app')
console.log('🚀 [MAIN] Vue应用已挂载到#app')

// 全局错误处理
app.config.errorHandler = (err, vm, info) => {
  console.error('💥 [ERROR] Vue全局错误:', err)
  console.error('📍 [ERROR] 错误信息:', info)
  console.error('🔍 [ERROR] 组件实例:', vm)
}

// 全局警告处理
app.config.warnHandler = (msg, vm, trace) => {
  console.warn('⚠️ [WARN] Vue警告:', msg)
  console.warn('📍 [WARN] 组件追踪:', trace)
}

console.log('🎉 [MAIN] 应用启动完成！')
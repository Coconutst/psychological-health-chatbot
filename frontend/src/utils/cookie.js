// Cookie 工具函数

/**
 * 设置 Cookie
 * @param {string} name - Cookie 名称
 * @param {string} value - Cookie 值
 * @param {number} days - 过期天数
 */
export function setCookie(name, value, days = 7) {
  console.log('🍪 [COOKIE] 设置Cookie:', { name, value: name === 'token' ? '[HIDDEN]' : value, days })
  const expires = new Date()
  expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000))
  
  document.cookie = `${name}=${encodeURIComponent(value)};expires=${expires.toUTCString()};path=/`
  console.log('✅ [COOKIE] Cookie设置完成')
}

/**
 * 获取 Cookie
 * @param {string} name - Cookie 名称
 * @returns {string|null} Cookie 值
 */
export function getCookie(name) {
  console.log('🔍 [COOKIE] 获取Cookie:', name)
  const nameEQ = name + '='
  const ca = document.cookie.split(';')
  
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i]
    while (c.charAt(0) === ' ') {
      c = c.substring(1, c.length)
    }
    if (c.indexOf(nameEQ) === 0) {
      const value = decodeURIComponent(c.substring(nameEQ.length, c.length))
      console.log('✅ [COOKIE] Cookie找到:', name, name === 'token' ? '[HIDDEN]' : value)
      return value
    }
  }
  
  console.log('❌ [COOKIE] Cookie未找到:', name)
  return null
}

/**
 * 删除 Cookie
 * @param {string} name - Cookie 名称
 */
export function removeCookie(name) {
  console.log('🗑️ [COOKIE] 删除Cookie:', name)
  document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/`
  console.log('✅ [COOKIE] Cookie删除完成')
}

/**
 * 检查 Cookie 是否存在
 * @param {string} name - Cookie 名称
 * @returns {boolean} 是否存在
 */
export function hasCookie(name) {
  const exists = getCookie(name) !== null
  console.log('🔍 [COOKIE] 检查Cookie存在性:', name, exists ? '存在' : '不存在')
  return exists
}
import request from '../utils/request'

// AI 聊天（POST /api/ai/chat）
// AI 是两轮 LLM 调用 + 工具执行，耗时较长，单独设 60 秒超时（覆盖默认 15 秒）
export function chat(message) {
  return request.post('/ai/chat', { message }, { timeout: 60000 })
}

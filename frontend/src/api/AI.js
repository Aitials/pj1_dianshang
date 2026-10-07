import request from '../utils/request'

// AI 聊天（POST /api/ai/chat）
// AI 是两轮 LLM 调用 + 工具执行，耗时较长，单独设 60 秒超时（覆盖默认 15 秒）
//
// threadId 是会话标识，必须由调用方保存并逐轮回传：
//   - 首次传 null/undefined → 不发送 thread_id 字段，后端自己生成一个并在响应里返回
//   - 之后每轮都要把上一轮响应里的 thread_id 原样传回
//   - 否则后端每次都会当成新会话，Agent 的 Memory（上下文）就串不起来
export function chat(message, threadId) {
  const body = { message }
  if (threadId) {
    body.thread_id = threadId
  }
  return request.post('/ai/chat', body, { timeout: 60000 })
}

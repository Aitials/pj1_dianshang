// AI 对话的本地持久化层（localStorage）
// ============================================================================
// 为什么放前端：
//   后端目前没有"会话"这个概念 —— ai_analysis 表只存问答流水、没有 thread 归属，
//   Memory 用的 InMemorySaver 是进程内存，也没有"列出会话"的接口。
//   所以会话列表先存在浏览器里，每个会话各自绑定一个后端返回的 thread_id。
//
// ⚠️ 这一层是刻意隔离出来的：将来后端支持会话管理后，只要把这个文件改成调接口，
//    上层 AIChat.vue 基本不用动。
//
// 已知限制（不是 bug，是本方案的边界）：
//   1. 换浏览器 / 清缓存就没了 —— 它只是浏览器本地数据，不是服务端数据
//   2. 后端进程重启后 InMemorySaver 清空，旧 thread_id 会退化成"新会话"
//      （后端不会报错，只是没有历史记忆；前端表现是"它不记得之前聊过什么"）
// ============================================================================

const KEY = 'ai_conversations'
const VERSION = 1

// 容量上限：localStorage 总共约 5MB，AI 回答往往很长，必须设上限防止写爆
const MAX_CONVERSATIONS = 50
const MAX_MESSAGES = 200

// 会话开场白：新建会话时的第一条 assistant 消息（messages.length === 1 时页面显示示例问题）
export const WELCOME =
  '你好，我是 AI 运营助手。我可以帮你分析平台的销售趋势、订单、库存预警、客户复购、物流履约等情况，也可以联网查询当前的电商政策与行业动态。'

// 本地会话 id。注意：这是【浏览器侧】的会话标识，和【后端返回的 thread_id】是两回事，
// 别混用 —— 后端要的是 threadId，不是这个 id。
function makeId() {
  const rand = Math.random().toString(36).slice(2, 8)
  return `c_${Date.now()}_${rand}`
}

// 用第一条用户消息当会话标题，超长截断
function makeTitle(text) {
  const t = (text || '').trim().replace(/\s+/g, ' ')
  if (!t) return '新对话'
  return t.length > 20 ? t.slice(0, 20) + '…' : t
}

function makeWelcomeMessage() {
  return { id: Date.now(), role: 'assistant', content: WELCOME }
}

// 新建一个空会话对象（只造对象，不入库）
export function createConversation() {
  const now = Date.now()
  return {
    id: makeId(),
    threadId: null, // 首轮为 null：不传 thread_id，由后端生成并返回
    title: '新对话',
    createdAt: now,
    updatedAt: now,
    messages: [makeWelcomeMessage()],
  }
}

// 读取本地状态。任何异常（JSON 坏了、结构不对）都降级成空状态，不让页面崩
export function loadState() {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return { version: VERSION, activeId: null, items: [] }

    const parsed = JSON.parse(raw)
    if (!parsed || !Array.isArray(parsed.items)) {
      return { version: VERSION, activeId: null, items: [] }
    }

    // 逐条做一次结构兜底，避免历史脏数据把渲染搞崩
    const items = parsed.items
      .filter((c) => c && typeof c.id === 'string' && Array.isArray(c.messages))
      .map((c) => ({
        id: c.id,
        threadId: typeof c.threadId === 'string' ? c.threadId : null,
        title: typeof c.title === 'string' && c.title ? c.title : '新对话',
        createdAt: Number(c.createdAt) || Date.now(),
        updatedAt: Number(c.updatedAt) || Date.now(),
        messages: c.messages
          .filter((m) => m && typeof m.content === 'string')
          .map((m) => ({
            id: Number(m.id) || Date.now(),
            role: m.role === 'user' ? 'user' : 'assistant',
            content: m.content,
          })),
      }))

    const activeId = items.some((c) => c.id === parsed.activeId) ? parsed.activeId : null
    return { version: VERSION, activeId, items }
  } catch (e) {
    return { version: VERSION, activeId: null, items: [] }
  }
}

// 写入本地。超容量被浏览器拒绝时只告警，不影响本次对话继续用
export function saveState(state) {
  try {
    const trimmed = {
      version: VERSION,
      activeId: state.activeId,
      // 按更新时间倒序保留最近的 N 个会话
      items: [...state.items]
        .sort((a, b) => b.updatedAt - a.updatedAt)
        .slice(0, MAX_CONVERSATIONS)
        .map((c) => ({
          ...c,
          // 单个会话只保留最近 N 条消息（至少保留开场白）
          messages: c.messages.slice(-MAX_MESSAGES),
        })),
    }
    localStorage.setItem(KEY, JSON.stringify(trimmed))
  } catch (e) {
    // 超配额（QuotaExceededError）或隐私模式禁用 localStorage
    console.warn('[aiChatStorage] 本地会话写入失败，本次会话仍在内存中可用：', e)
  }
}

// 用第一条用户消息命名会话（只在标题还是默认值时改，不覆盖用户已有标题）
export function autoTitle(conversation, text) {
  if (!conversation) return
  if (conversation.title && conversation.title !== '新对话') return
  conversation.title = makeTitle(text)
}

// 供组件用的时间格式化（今天显示时分，否则显示月-日）
export function formatTime(ts) {
  const d = new Date(Number(ts) || Date.now())
  const now = new Date()
  const sameDay =
    d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth() && d.getDate() === now.getDate()
  const pad = (n) => String(n).padStart(2, '0')
  if (sameDay) return `${pad(d.getHours())}:${pad(d.getMinutes())}`
  return `${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

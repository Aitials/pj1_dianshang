<template>
  <div class="ai-layout">
    <!-- 左：会话列表（会话数据保存在浏览器 localStorage，见 utils/aiChatStorage.js） -->
    <aside class="conv-sidebar">
      <div class="conv-head">
        <span class="conv-head-title">对话</span>
        <el-button size="small" type="primary" :disabled="loading" @click="newConversation">
          <el-icon><Plus /></el-icon>
          新对话
        </el-button>
      </div>

      <div class="conv-list" v-if="sortedConversations.length">
        <div
          v-for="c in sortedConversations"
          :key="c.id"
          class="conv-item"
          :class="{ active: c.id === activeId }"
          @click="selectConversation(c.id)"
        >
          <div class="conv-main">
            <div class="conv-title" :title="c.title">{{ c.title }}</div>
            <div class="conv-time">{{ formatTime(c.updatedAt) }}</div>
          </div>
          <el-icon class="conv-del" title="删除对话" @click.stop="removeConversation(c.id)">
            <Delete />
          </el-icon>
        </div>
      </div>
      <div class="conv-empty" v-else>还没有对话</div>
    </aside>

    <!-- 右：对话区 -->
    <div class="chat-wrap">
      <!-- 消息区 -->
      <div class="chat-messages" ref="messagesRef">
        <div class="empty" v-if="messages.length === 1">
          <div class="empty-icon">
            <el-icon :size="40"><ChatDotRound /></el-icon>
          </div>
          <div class="empty-title">AI 运营助手</div>
          <div class="empty-tips">可以问我销售、订单、库存、客户、物流等经营问题</div>
          <div class="example-questions">
            <div class="example-tag" v-for="q in examples" :key="q" @click="askExample(q)">{{ q }}</div>
          </div>
        </div>

        <div v-for="msg in messages" :key="msg.id" :class="['message', msg.role]">
          <div class="avatar" v-if="msg.role === 'assistant'">
            <el-icon :size="18"><ChatDotRound /></el-icon>
          </div>
          <div class="bubble md" v-if="msg.role === 'assistant'" v-html="renderMarkdown(msg.content)"></div>
          <div class="bubble" v-else>{{ msg.content }}</div>
        </div>

        <!-- "正在思考中"只显示在【发起请求的那个会话】里，避免切走之后跑到别的会话上 -->
        <div class="message assistant" v-if="loadingConvId === activeId">
          <div class="avatar">
            <el-icon :size="18"><ChatDotRound /></el-icon>
          </div>
          <div class="bubble thinking-box">
            <span class="thinking-text">正在思考中</span>
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="chat-input">
        <el-input
          v-model="input"
          placeholder="输入你的问题，回车发送"
          :disabled="loading"
          clearable
          @keyup.enter="send"
        />
        <el-button type="primary" :loading="loading" @click="send">发送</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { chat } from '../api/AI'
import { autoTitle, createConversation, formatTime, loadState, saveState } from '../utils/aiChatStorage'

// AI 回复是 Markdown 格式，渲染成 HTML（表格/加粗/列表正常显示）
// 回复内容里可能夹带联网检索到的外部内容，属于不可信输入，
// 交给 v-html 前必须消毒，过滤 <script>、on* 事件、javascript: 等
function renderMarkdown(text) {
  const html = marked.parse(text || '')
  return DOMPurify.sanitize(html, { USE_PROFILES: { html: true } })
}

// ---- 会话状态 ----
// 会话列表存在 localStorage（见 utils/aiChatStorage.js），每个会话各自绑定一个
// 后端返回的 thread_id。切换会话时用的是各自那个 id，绝不在发送时新建 UUID。
const messagesRef = ref(null)
const conversations = ref([])
const activeId = ref(null)

// 当前会话的消息列表。用 computed 从会话对象派生，而不是另外再存一份 ref，
// 避免"侧边栏会话里的消息"和"当前显示的消息"两份数据不同步。
const activeConversation = computed(
  () => conversations.value.find((c) => c.id === activeId.value) || null
)
const messages = computed(() => activeConversation.value?.messages || [])

// 侧边栏按最近更新倒序（和常见对话产品一致）
const sortedConversations = computed(() =>
  [...conversations.value].sort((a, b) => b.updatedAt - a.updatedAt)
)

const examples = ['最近销售趋势怎么样？', '哪些商品库存不足？', '整体复购率是多少？', '物流准时率如何？']

const input = ref('')
// 记录"正在等回复的那个会话 id"，而不是一个布尔量：
// 这样中途切到别的会话时，"正在思考中"不会显示在错误的会话里
const loadingConvId = ref(null)
const loading = computed(() => loadingConvId.value !== null)

function persist() {
  saveState({ activeId: activeId.value, items: conversations.value })
}

// 初始化：从本地恢复；一个会话都没有就自动建一个，避免出现空态
function initConversations() {
  const state = loadState()
  conversations.value = state.items
  activeId.value = state.activeId

  if (!conversations.value.length) {
    const c = createConversation()
    conversations.value.push(c)
    activeId.value = c.id
  } else if (!activeId.value) {
    // activeId 失效（例如它指向的会话已被删掉）→ 落到最近更新的那个
    activeId.value = sortedConversations.value[0].id
  }
  persist()
}
initConversations()

function newConversation() {
  if (loading.value) return
  const c = createConversation()
  conversations.value.unshift(c)
  activeId.value = c.id
  input.value = ''
  persist()
  scrollToBottom()
}

function selectConversation(id) {
  if (id === activeId.value) return
  activeId.value = id
  persist()
  scrollToBottom()
}

async function removeConversation(id) {
  if (loadingConvId.value === id) {
    ElMessage.warning('该对话正在生成回复，请稍候再删除')
    return
  }
  const target = conversations.value.find((c) => c.id === id)
  try {
    await ElMessageBox.confirm(`删除对话「${target?.title || '新对话'}」？删除后不可恢复。`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch (e) {
    return // 用户点了取消
  }

  conversations.value = conversations.value.filter((c) => c.id !== id)
  if (activeId.value === id) {
    if (conversations.value.length) {
      activeId.value = sortedConversations.value[0].id
    } else {
      // 全部删完就补一个新的，避免出现"没有当前会话"的空态
      const c = createConversation()
      conversations.value.push(c)
      activeId.value = c.id
    }
  }
  persist()
}

async function send() {
  const text = input.value.trim()
  if (!text || loading.value) return

  const conv = activeConversation.value
  if (!conv) return

  conv.messages.push({ id: Date.now(), role: 'user', content: text })
  autoTitle(conv, text) // 用第一条用户消息给会话命名
  conv.updatedAt = Date.now()
  input.value = ''
  loadingConvId.value = conv.id
  persist()
  scrollToBottom()

  try {
    // 关键：传这个会话自己的 threadId。首轮是 null（后端生成并返回），之后原样回传。
    const res = await chat(text, conv.threadId)
    if (res && res.thread_id) {
      conv.threadId = res.thread_id
    }
    conv.messages.push({ id: Date.now(), role: 'assistant', content: res.answer || '（无返回内容）' })
  } catch (e) {
    conv.messages.push({ id: Date.now(), role: 'assistant', content: '抱歉，请求失败了，请稍后重试。' })
  } finally {
    conv.updatedAt = Date.now()
    loadingConvId.value = null
    persist()
    scrollToBottom()
  }
}

function askExample(q) {
  input.value = q
  send()
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}
</script>

<style scoped>
/* 两栏布局：左侧会话列表 + 右侧对话区 */
.ai-layout {
  height: calc(100vh - 130px);
  display: flex;
  gap: 16px;
}

/* ---- 会话侧边栏 ---- */
.conv-sidebar {
  width: 240px;
  flex-shrink: 0;
  background: #fff;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.conv-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 12px 14px;
  border-bottom: 1px solid #e2e8f0;
}
.conv-head-title {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
}
.conv-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}
.conv-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
}
.conv-item:hover {
  background: #f1f5f9;
}
.conv-item.active {
  background: #eff6ff;
}
.conv-main {
  flex: 1;
  /* min-width:0 是让下面 .conv-title 能正常出现省略号的关键（flex 子项默认不收缩） */
  min-width: 0;
}
.conv-title {
  font-size: 13px;
  color: #334155;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.conv-item.active .conv-title {
  color: #2563eb;
  font-weight: 600;
}
.conv-time {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 2px;
}
/* 删除按钮平时隐藏，hover 会话项时才出现，避免列表太吵 */
.conv-del {
  flex-shrink: 0;
  color: #cbd5e1;
  opacity: 0;
  transition: opacity 0.15s, color 0.15s;
}
.conv-item:hover .conv-del {
  opacity: 1;
}
.conv-del:hover {
  color: #ef4444;
}
.conv-empty {
  padding: 24px 0;
  text-align: center;
  color: #94a3b8;
  font-size: 13px;
}

/* 右侧对话区：高度由 .ai-layout 统一控制 */
.chat-wrap {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
}

/* 消息区 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: #f8fafc;
}
.empty {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #64748b;
}
.empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  background: #eff6ff;
  color: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}
.empty-title {
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 8px;
}
.empty-tips {
  font-size: 13px;
  margin-bottom: 20px;
}
.example-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}
.example-tag {
  padding: 8px 14px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  font-size: 13px;
  color: #334155;
  cursor: pointer;
  transition: all 0.2s;
}
.example-tag:hover {
  border-color: #2563eb;
  color: #2563eb;
  background: #eff6ff;
}

/* 消息 */
.message {
  display: flex;
  margin-bottom: 16px;
  align-items: flex-start;
}
.message.user {
  justify-content: flex-end;
}
.message.assistant {
  justify-content: flex-start;
}
.avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: #2563eb;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-right: 10px;
}
.message.user .avatar {
  display: none;
}
.bubble {
  max-width: 72%;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}
.message.user .bubble {
  background: #2563eb;
  color: #fff;
  border-top-right-radius: 4px;
}
.message.assistant .bubble {
  background: #fff;
  color: #334155;
  border: 1px solid #e2e8f0;
  border-top-left-radius: 4px;
  max-width: 85%;
}

/* Markdown 渲染样式（AI 回复） */
.bubble.md {
  white-space: normal;
}
.bubble.md :deep(p) {
  margin: 0 0 8px;
}
.bubble.md :deep(p:last-child) {
  margin-bottom: 0;
}
.bubble.md :deep(table) {
  border-collapse: collapse;
  margin: 8px 0;
  font-size: 13px;
  display: block;
  overflow-x: auto;
}
.bubble.md :deep(th),
.bubble.md :deep(td) {
  border: 1px solid #e2e8f0;
  padding: 6px 12px;
  text-align: left;
}
.bubble.md :deep(th) {
  background: #f1f5f9;
  font-weight: 600;
  color: #0f172a;
}
.bubble.md :deep(tr:nth-child(even) td) {
  background: #f8fafc;
}
.bubble.md :deep(ul),
.bubble.md :deep(ol) {
  margin: 8px 0;
  padding-left: 20px;
}
.bubble.md :deep(li) {
  margin: 4px 0;
}
.bubble.md :deep(code) {
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  color: #2563eb;
}
.bubble.md :deep(strong) {
  color: #0f172a;
}

/* 思考中动画 */
.thinking-box {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #64748b;
}
.thinking-text {
  font-size: 13px;
  margin-right: 2px;
}
.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #94a3b8;
  animation: blink 1.2s infinite;
}
.dot:nth-child(3) {
  animation-delay: 0.2s;
}
.dot:nth-child(4) {
  animation-delay: 0.4s;
}
@keyframes blink {
  0%,
  80%,
  100% {
    opacity: 0.3;
  }
  40% {
    opacity: 1;
  }
}

/* 输入区 */
.chat-input {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #e2e8f0;
  background: #fff;
}
</style>

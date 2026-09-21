<template>
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

      <div class="message assistant" v-if="loading">
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
</template>

<script setup>
import { nextTick, ref } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { chat } from '../api/AI'

// AI 回复是 Markdown 格式，渲染成 HTML（表格/加粗/列表正常显示）
// 回复内容里可能夹带联网检索到的外部内容，属于不可信输入，
// 交给 v-html 前必须消毒，过滤 <script>、on* 事件、javascript: 等
function renderMarkdown(text) {
  const html = marked.parse(text || '')
  return DOMPurify.sanitize(html, { USE_PROFILES: { html: true } })
}

const messagesRef = ref(null)
const messages = ref([
  {
    id: 1,
    role: 'assistant',
    content: '你好，我是 AI 运营助手。我可以帮你分析平台的销售趋势、订单、库存预警、客户复购、物流履约等情况，也可以联网查询当前的电商政策与行业动态。',
  },
])

const examples = ['最近销售趋势怎么样？', '哪些商品库存不足？', '整体复购率是多少？', '物流准时率如何？']

const input = ref('')
const loading = ref(false)

async function send() {
  const text = input.value.trim()
  if (!text || loading.value) return

  messages.value.push({ id: Date.now(), role: 'user', content: text })
  input.value = ''
  loading.value = true
  scrollToBottom()

  try {
    const res = await chat(text)
    messages.value.push({ id: Date.now(), role: 'assistant', content: res.answer || '（无返回内容）' })
  } catch (e) {
    messages.value.push({ id: Date.now(), role: 'assistant', content: '抱歉，请求失败了，请稍后重试。' })
  } finally {
    loading.value = false
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
.chat-wrap {
  height: calc(100vh - 130px);
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

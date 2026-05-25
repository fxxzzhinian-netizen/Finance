<template>
  <div class="page">
    <div class="card">
      <div class="brand-bar">
        <img :src="logoImg" alt="LOGO" class="brand-logo" />
        <div class="brand-text">
          <div class="brand-title">德工智能资产管理平台</div>
          <div class="brand-sub">Supply Public View</div>
        </div>
      </div>

      <div v-if="loading" class="state-box">
        <div class="spinner" aria-hidden="true"></div>
        <div class="state-text">正在加载物资信息...</div>
      </div>

      <div v-else-if="error" class="state-box error">
        <svg viewBox="0 0 24 24" width="40" height="40" aria-hidden="true">
          <path
            fill="#c44545"
            d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"
          />
        </svg>
        <div class="state-text">{{ error }}</div>
        <div class="state-hint">请联系管理员核对二维码或链接。</div>
      </div>

      <div v-else-if="record" class="supply">
        <div class="banner">
          <div class="supply-code mono">{{ record.serial_number }}</div>
          <div class="supply-title">
            {{ record.receiver }} 领取 {{ record.item_name }} x{{ record.quantity }}
          </div>
        </div>

        <div class="section">
          <div class="section-head">
            <span class="section-name">领取信息</span>
          </div>
          <div class="info-grid">
            <div class="info-item" v-for="item in baseItems" :key="item.label">
              <div class="ii-label">{{ item.label }}</div>
              <div class="ii-value" :class="{ mono: item.mono }">
                {{ item.value || '-' }}
              </div>
            </div>
          </div>
        </div>

        <div class="tip-bar">
          <svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true">
            <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
          </svg>
          <span>本页面为只读扫码视图。</span>
        </div>
      </div>
    </div>

    <div class="footer">Asset Management &copy; {{ new Date().getFullYear() }}</div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getPublicSupply } from '../api/supplies'
import logoImg from '../img/logo.png'

const route = useRoute()
const loading = ref(true)
const error = ref('')
const record = ref(null)

const baseItems = computed(() => {
  const r = record.value
  if (!r) return []
  return [
    { label: '序列号', value: r.serial_number, mono: true },
    { label: '领取人', value: r.receiver },
    { label: '物品名称', value: r.item_name },
    { label: '数量', value: String(r.quantity), mono: true },
    { label: '记录时间', value: fmtFullTime(r.created_at), mono: true },
  ]
})

function fmtFullTime(value) {
  if (!value) return ''
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return ''
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    record.value = await getPublicSupply(route.params.serialNumber)
  } catch (e) {
    error.value = e?.response?.data?.detail || '物资记录不存在或链接已失效'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.page {
  min-height: 100vh;
  min-height: 100dvh;
  padding: 32px 16px 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: transparent;
  color: #2f2f33;
  font-family: 'HarmonyOS Sans SC', 'Noto Sans SC', 'PingFang SC',
    'Microsoft YaHei UI', 'Microsoft YaHei', -apple-system,
    BlinkMacSystemFont, 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
}

.card {
  width: 100%;
  max-width: 520px;
  padding: 22px 22px 18px;
  background: #fff;
  border: 1px solid rgba(var(--theme-primary-rgb), 0.18);
  border-radius: 18px;
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 1) inset,
    0 18px 50px rgba(94, 74, 46, 0.18);
}

.brand-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 8px;
  margin-bottom: 12px;
}

.brand-logo {
  width: auto;
  height: 40px;
  max-width: 160px;
  object-fit: contain;
}

.brand-title {
  color: #2f2f33;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 1px;
}

.brand-sub {
  color: var(--theme-text-muted, #b9a78a);
  font-size: 11px;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.state-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 48px 16px;
  color: var(--theme-primary-deep, #8a7355);
  text-align: center;
}

.state-text {
  color: var(--theme-text-hover, #5e4a2e);
  font-size: 14px;
  font-weight: 600;
}

.state-hint {
  color: var(--theme-text-muted, #b9a78a);
  font-size: 12.5px;
}

.state-box.error .state-text {
  color: #c44545;
}

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid rgba(var(--theme-primary-rgb), 0.25);
  border-top-color: #c9a063;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.banner {
  padding: 14px 16px;
  margin-bottom: 18px;
  background: linear-gradient(135deg, #fbf3e3 0%, #f5e6c8 100%);
  border: 1px solid rgba(var(--theme-primary-rgb), 0.3);
  border-radius: 12px;
}

.supply-code {
  margin-bottom: 4px;
  color: var(--theme-primary-deep, #8a7355);
  font-size: 13px;
  font-weight: 600;
}

.supply-title {
  color: #2f2f33;
  font-size: 16px;
  font-weight: 700;
  line-height: 1.4;
}

.section {
  margin-top: 14px;
}

.section-head {
  margin-bottom: 10px;
}

.section-name {
  color: var(--theme-text-hover, #5e4a2e);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 1px;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px 16px;
}

.info-item:last-child {
  grid-column: 1 / -1;
}

.ii-label {
  margin-bottom: 2px;
  color: var(--theme-primary-deep, #8a7355);
  font-size: 11.5px;
}

.ii-value {
  color: #2f2f33;
  font-size: 13.5px;
  font-weight: 500;
  line-height: 1.4;
  word-break: break-all;
}

.mono {
  font-family: 'SF Mono', Menlo, Consolas, monospace;
}

.tip-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 18px;
  padding-top: 12px;
  color: var(--theme-text-muted, #b9a78a);
  border-top: 1px dashed rgba(var(--theme-primary-rgb), 0.3);
  font-size: 11.5px;
}

.tip-bar svg {
  color: #c9a063;
}

.footer {
  margin-top: 18px;
  color: var(--theme-text-muted, #b9a78a);
  font-size: 11.5px;
  letter-spacing: 1px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 479px) {
  .page {
    padding: 16px 10px 36px;
  }

  .card {
    padding: 16px 14px 12px;
    border-radius: 12px;
  }

  .brand-logo {
    height: 32px;
    max-width: 120px;
  }

  .brand-title {
    font-size: 14px;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>

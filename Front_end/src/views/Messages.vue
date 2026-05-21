<template>
  <div class="messages-page">
    <!-- 顶部工具条 -->
    <div class="msg-toolbar">
      <div class="toolbar-left">
        <label class="mine-switch">
          <span class="mine-switch-label">仅我的</span>
          <el-switch
            v-model="mineOnly"
            aria-label="仅显示我的日志"
          />
        </label>

        <div
          class="type-select-control"
          :style="typeSelectStyle"
        >
          <el-select
            v-model="selectedActionFilter"
            class="type-select"
            popper-class="messages-type-select-popper"
            :popper-style="typeSelectPopperStyle"
            aria-label="日志类型筛选"
          >
            <el-option
              v-for="opt in actionOptions"
              :key="opt.value || 'all'"
              :label="opt.label"
              :value="opt.value || TYPE_FILTER_ALL"
            />
          </el-select>
        </div>
      </div>

      <div class="toolbar-right">
        <div class="form-control ai-search-control" :class="{ 'is-filled': !!keyword, 'is-loading': aiSearching }">
          <input
            type="text"
            required
            v-model="keyword"
            :disabled="aiSearching"
            @keyup.enter="onAiSearch"
          />
          <label aria-hidden="true">
            <span
              v-for="(ch, i) in keywordLabel"
              :key="i"
              :style="{ transitionDelay: `${i * 50}ms` }"
            >{{ ch }}</span>
          </label>
          <span v-if="aiSearching" class="ai-search-spinner" aria-hidden="true"></span>
        </div>
        <el-tooltip :content="aiSearching ? 'AI 解析中…' : 'AI 搜索'" placement="top">
          <button
            type="button"
            class="svg-icon-btn search-btn"
            :class="{ 'is-ai-loading': aiSearching }"
            :disabled="aiSearching"
            @click="onAiSearch"
            aria-label="AI 搜索"
          >
            <svg viewBox="0 0 1024 1024" width="21" height="21" aria-hidden="true">
              <path d="M469.333333 0c259.2 0 469.333333 210.133333 469.333334 469.333333 0 114.218667-40.832 218.922667-108.629334 300.330667l161.664 161.706667a42.666667 42.666667 0 1 1-60.373333 60.330666l-161.706667-161.706666A467.413333 467.413333 0 0 1 469.333333 938.666667c-259.2 0-469.333333-210.133333-469.333333-469.333334s210.133333-469.333333 469.333333-469.333333z m0 85.333333a384 384 0 1 0 0 768 384 384 0 0 0 0-768z"/>
              <path d="M469.333333 170.666667c102.528 0 195.669333 57.088 250.026667 148.906666a42.666667 42.666667 0 1 1-73.386667 43.52c-39.552-66.773333-105.344-107.093333-176.64-107.093333a42.666667 42.666667 0 0 1 0-85.333333z"/>
              <path d="M725.333333 469.333333m-42.666666 0a42.666667 42.666667 0 1 0 85.333333 0 42.666667 42.666667 0 1 0-85.333333 0Z"/>
            </svg>
          </button>
        </el-tooltip>

        <el-tooltip content="重置" placement="top">
          <button
            type="button"
            class="svg-icon-btn reset-btn"
            @click="onReset"
            aria-label="重置"
          >
            <svg viewBox="0 0 1024 1024" width="24" height="24" aria-hidden="true">
              <path d="M377.856 856.576l-19.456 71.68c23.04 8.704 46.08 14.848 70.656 19.456l20.992-71.68c-25.088-4.096-49.152-10.752-72.192-19.456z m318.976-714.752V363.52h74.24v-115.712c68.096 67.072 111.104 160.256 111.104 263.68 0 204.8-165.376 370.176-370.176 370.176V955.904c244.736 0 443.904-199.168 443.904-443.904 0-113.664-43.52-217.6-114.688-295.936h77.312V141.824H696.832z m-101.376-65.536l-20.992 71.68c24.576 4.096 48.64 10.752 71.68 19.456l19.456-71.68c-23.04-8.704-46.08-14.848-70.144-19.456z m-83.456-8.192c-244.736 0-443.904 199.168-443.904 443.904 0 113.664 43.008 217.6 113.152 295.936h-76.288v74.24H326.656V660.48h-74.24v115.712c-68.096-67.072-111.104-160.256-111.104-263.68 0-204.8 165.376-370.176 370.176-370.176v-74.24z"/>
            </svg>
          </button>
        </el-tooltip>
        <button
          type="button"
          class="btn-secondary"
          :disabled="unread === 0"
          @click="onMarkAllRead"
        >
          全部已读
          <span v-if="unread > 0" class="unread-pill">{{ unread > 99 ? '99+' : unread }}</span>
        </button>
      </div>
    </div>

    <!-- 时间线 -->
    <div
      class="msg-timeline"
      :class="{ empty: !loading && items.length === 0, 'first-load': playToken <= 1 }"
      :key="`timeline-${playToken}`"
    >
      <template v-if="items.length > 0">
        <section v-if="showTypeRatio" class="type-ratio-card">
          <div class="ratio-title-row">
            <div class="ratio-heading">
              <span class="ratio-title">日志类型占比</span>
              <span class="ratio-total">{{ typeRatioTotal }} 条日志</span>
            </div>
            <span class="ratio-title-line"></span>
          </div>
          <div class="ratio-metrics">
            <div
              v-for="stat in typeRatioStats"
              :key="stat.value"
              class="ratio-metric"
              :style="{
                '--ratio-color': stat.color,
                '--ratio-angle': `${Math.min(100, Math.max(0, stat.percent)) * 3.6}deg`,
              }"
            >
              <div class="ratio-copy">
                <span class="ratio-label">
                  <span class="ratio-dot"></span>
                  <span class="ratio-name">{{ stat.label }}</span>
                </span>
                <span class="ratio-percent">{{ stat.percent.toFixed(1) }}%</span>
              </div>
              <div class="ratio-ring" aria-hidden="true">
                <div class="ratio-ring-core">
                  <span v-html="actionIcon(stat.value)"></span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <div
          v-for="group in grouped"
          :key="group.date"
          class="day-group"
          :class="{ collapsed: isGroupCollapsed(group.date) }"
        >
          <div class="day-label">
            <svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true">
              <path fill="currentColor" d="M7 2h2v2h6V2h2v2h3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2L2.01 6A2 2 0 0 1 4 4h3V2zm13 8H4v10h16V10zM4 8h16V6H4v2z"/>
            </svg>
            <span class="day-text">{{ group.label }}</span>
            <span class="day-count">{{ group.items.length }} 条日志</span>
            <span class="day-line"></span>
            <button
              type="button"
              class="day-toggle"
              :class="{ collapsed: isGroupCollapsed(group.date) }"
              :aria-expanded="!isGroupCollapsed(group.date)"
              :aria-label="isGroupCollapsed(group.date) ? '展开当日日志' : '折叠当日日志'"
              @click="toggleGroup(group.date)"
            >
              <svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true">
                <path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M6 9l6 6 6-6"/>
              </svg>
            </button>
          </div>
          <div
            v-for="row in group.items"
            :key="row.id"
            v-show="!isGroupCollapsed(group.date)"
            class="msg-card"
            :class="[
              `act-${row.action.split('.')[0]}`,
              `act-${row.action.replace(/\./g, '-')}`,
              { unread: !row.is_read },
            ]"
            @click="onCardClick(row)"
          >
            <span v-if="!row.is_read" class="unread-badge">
              <span class="unread-light"></span>
              未读
            </span>
            <div class="msg-icon">
              <img
                v-if="actionImage(row.action)"
                :src="actionImage(row.action)"
                :alt="actionLabel(row.action)"
                class="msg-icon-img"
              />
              <span v-else v-html="actionIcon(row.action)"></span>
            </div>
            <div class="msg-body">
              <div class="msg-head">
                <span class="action-tag" :class="`tag-${row.action.replace('.', '-')}`">
                  {{ actionLabel(row.action) }}
                </span>
                <div class="msg-summary">{{ row.summary }}</div>
              </div>
              <div class="msg-foot">
                <span class="meta-time">{{ fmtTime(row.created_at) }}</span>
                <div v-if="row.ip" class="meta-ip">
                  <svg viewBox="0 0 24 24" width="11" height="11" aria-hidden="true">
                    <path fill="currentColor" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5a2.5 2.5 0 0 1 0-5 2.5 2.5 0 0 1 0 5z"/>
                  </svg>
                  {{ row.ip }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- 空状态 -->
      <div v-else-if="!loading" class="empty-state">
        <svg viewBox="0 0 1024 1024" width="64" height="64" aria-hidden="true">
          <path
            fill="var(--theme-primary-light-3, #d4b89a)"
            d="M512 64a448 448 0 1 0 0 896 448 448 0 0 0 0-896zm0 832a384 384 0 1 1 0-768 384 384 0 0 1 0 768zm-32-256h64v64h-64v-64zm0-320h64v256h-64V320z"
          />
        </svg>
        <div class="empty-title">暂无日志</div>
        <div class="empty-sub">所有的资产新增、修改、删除等操作都会同步记录在这里</div>
      </div>

      <!-- 骨架/Loading -->
      <div v-if="loading && items.length === 0" class="loading">加载中…</div>
    </div>

    <!-- 分页 -->
    <div v-if="total > pageSize" class="msg-pager">
      <el-pagination
        :current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next, jumper, total"
        background
        @update:current-page="page = $event"
        @current-change="reload(false)"
      />
    </div>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailOpen"
      :show-close="true"
      width="760px"
      align-center
      append-to-body
      class="log-detail-dialog"
      destroy-on-close
    >
      <template #header>
        <div class="dlg-header" v-if="detailRow">
          <div class="dlg-icon">
            <img
              v-if="actionImage(detailRow.action)"
              :src="actionImage(detailRow.action)"
              :alt="actionLabel(detailRow.action)"
            />
            <span v-else v-html="actionIcon(detailRow.action)"></span>
          </div>
          <div class="dlg-title-wrap">
            <div class="dlg-title-line">
              <span
                class="action-tag"
                :class="`tag-${detailRow.action.replace('.', '-')}`"
              >{{ actionLabel(detailRow.action) }}</span>
              <span class="dlg-actor">{{ detailRow.actor || '系统' }}</span>
            </div>
            <div class="dlg-summary">{{ detailRow.summary }}</div>
          </div>
        </div>
      </template>

      <div v-if="detailRow" class="dlg-body">
        <div class="dlg-meta-row">
          <div class="dlg-meta-item">
            <span class="dlg-meta-label">时间</span>
            <span class="dlg-meta-value">{{ fmtFullTime(detailRow.created_at) }}</span>
          </div>
          <div v-if="detailRow.ip" class="dlg-meta-item">
            <span class="dlg-meta-label">来源 IP</span>
            <span class="dlg-meta-value mono">{{ detailRow.ip }}</span>
          </div>
          <div v-if="detailRow.target_label" class="dlg-meta-item">
            <span class="dlg-meta-label">对象</span>
            <span class="dlg-meta-value mono">{{ detailRow.target_label }}</span>
          </div>
        </div>

        <template v-if="detailRow.changes && detailRow.changes.length > 0">
          <div class="dlg-section-title">
            字段变更
            <span class="dlg-section-count">{{ detailRow.changes.length }}</span>
          </div>
          <div class="dlg-changes">
            <div class="dlg-change-head" aria-hidden="true">
              <span>字段名称</span>
              <span>变更前</span>
              <span></span>
              <span>变更后</span>
            </div>
            <div
              v-for="(c, i) in detailRow.changes"
              :key="i"
              class="dlg-change-row"
            >
              <div class="dlg-change-label">{{ c.label }}</div>
              <div class="dlg-change-flow">
                <span class="dlg-ch-before">{{ c.before ?? '空' }}</span>
                <svg viewBox="0 0 24 24" width="14" height="14" class="dlg-ch-arrow" aria-hidden="true">
                  <path fill="currentColor" d="M16.01 11H4v2h12.01v3L20 12l-3.99-4z"/>
                </svg>
                <span class="dlg-ch-after">{{ c.after || '空' }}</span>
              </div>
            </div>
          </div>
        </template>

        <div v-else class="dlg-empty">该操作没有字段级变更记录</div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { listLogs, markLogsRead, getLogTypeStats } from '../api/logs'
import { aiParseSearch } from '../api/ai'
import { toast } from '../utils/toast'

import imgAssetCreate from '../img/新增资产.png'
import imgAssetUpdate from '../img/修改资产.png'
import imgAssetDelete from '../img/删除资产.png'
import imgAssetImport from '../img/批量上传.png'
import imgQrRegen from '../img/二维码刷新.png'
import imgFileUpload from '../img/上传文件.png'
import imgFileDelete from '../img/删除文件.png'
import imgLogin from '../img/登入.png'
import imgLogout from '../img/登出.png'

const ACTION_IMAGE_MAP = {
  'asset.create': imgAssetCreate,
  'asset.update': imgAssetUpdate,
  'asset.delete': imgAssetDelete,
  'asset.import': imgAssetImport,
  'asset.qr.regen': imgQrRegen,
  'file.upload': imgFileUpload,
  'file.delete': imgFileDelete,
  login: imgLogin,
  logout: imgLogout,
}

function actionImage(a) {
  return ACTION_IMAGE_MAP[a] || ''
}

const scope = ref('all')
const actionFilter = ref('')
const keyword = ref('')
const keywordLabel = computed(() => Array.from('AI Search'))
const aiSearching = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const unread = ref(0)
const items = ref([])
const loading = ref(false)

const actionOptions = [
  { value: '', label: '全部类型' },
  { value: 'asset.create', label: '新增资产' },
  { value: 'asset.update', label: '修改资产' },
  { value: 'asset.delete', label: '删除资产' },
  { value: 'asset.import', label: '批量导入' },
  { value: 'asset.qr.regen', label: '二维码刷新' },
  { value: 'file.upload', label: '上传附件' },
  { value: 'file.delete', label: '删除附件' },
  { value: 'login', label: '登录' },
  { value: 'logout', label: '登出' },
]

const TYPE_FILTER_ALL = '__all__'
const TYPE_RATIO_COLORS = [
  '#5bc487',
  '#538fe2',
  '#9c66d0',
  '#f0cf59',
  '#99a4b5',
  '#ada395',
  '#38a6c7',
  '#d8874d',
  '#c75e7f',
]

const mineOnly = computed({
  get: () => scope.value === 'mine',
  set: (value) => onScopeChange(value ? 'mine' : 'all'),
})

const selectedActionFilter = computed({
  get: () => actionFilter.value || TYPE_FILTER_ALL,
  set: (value) => onActionChange(value === TYPE_FILTER_ALL ? '' : value),
})

const selectedActionLabel = computed(() => (
  actionOptions.find((opt) => opt.value === actionFilter.value)?.label || '全部类型'
))
const longestActionLabel = computed(() => (
  actionOptions.reduce((longest, opt) => (
    Array.from(opt.label).length > Array.from(longest).length ? opt.label : longest
  ), '全部类型')
))
const typeSelectStyle = computed(() => ({
  '--type-select-width': `${Math.max(Array.from(selectedActionLabel.value).length, 4)}em`,
}))
const typeSelectPopperStyle = computed(() => ({
  width: `calc(${Math.max(Array.from(longestActionLabel.value).length, 4)}em + 56px)`,
  minWidth: '108px',
}))

const showTypeRatio = computed(() => !actionFilter.value)
const typeRatioRaw = ref({ total: 0, items: [] })
const typeRatioTotal = computed(() => typeRatioRaw.value.total || 0)
const typeRatioStats = computed(() => {
  const total = typeRatioTotal.value
  const counts = new Map()
  for (const row of typeRatioRaw.value.items || []) {
    counts.set(row.action, (counts.get(row.action) || 0) + (row.count || 0))
  }

  const knownStats = actionOptions
    .filter((opt) => opt.value && counts.has(opt.value))
    .map((opt) => {
      const count = counts.get(opt.value)
      return {
        value: opt.value,
        label: opt.label,
        count,
        percent: total > 0 ? (count / total) * 100 : 0,
      }
    })

  const knownValues = new Set(knownStats.map((stat) => stat.value))
  const unknownStats = Array.from(counts.entries())
    .filter(([value]) => !knownValues.has(value))
    .map(([value, count]) => ({
      value,
      label: actionLabel(value),
      count,
      percent: total > 0 ? (count / total) * 100 : 0,
    }))

  return [...knownStats, ...unknownStats]
    .sort((a, b) => b.count - a.count)
    .map((stat, index) => ({
      ...stat,
      color: TYPE_RATIO_COLORS[index % TYPE_RATIO_COLORS.length],
    }))
})

async function reloadTypeStats() {
  if (!showTypeRatio.value) {
    typeRatioRaw.value = { total: 0, items: [] }
    return
  }
  try {
    const data = await getLogTypeStats({
      scope: scope.value,
      keyword: keyword.value || undefined,
    })
    typeRatioRaw.value = {
      total: data?.total || 0,
      items: Array.isArray(data?.items) ? data.items : [],
    }
  } catch {
    /* 已由拦截器提示 */
  }
}

const ACTION_LABEL_MAP = Object.fromEntries(
  actionOptions.filter((o) => o.value).map((o) => [o.value, o.label]),
)

function actionLabel(a) {
  return ACTION_LABEL_MAP[a] || a
}

// 每个动作配一个单层、线条风格的语义化图标（参考 lucide / heroicons）
const ACTION_ICON_MAP = {
  // 新增资产：方框 + 加号（plus-square）
  'asset.create':
    '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      '<rect x="3" y="3" width="18" height="18" rx="4"/>' +
      '<path d="M12 8v8M8 12h8"/>' +
    '</svg>',
  // 修改资产：铅笔（pencil / edit）
  'asset.update':
    '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      '<path d="M12 20h9"/>' +
      '<path d="M16.5 3.5a2.121 2.121 0 1 1 3 3L7 19l-4 1 1-4 12.5-12.5z"/>' +
    '</svg>',
  // 删除资产：垃圾桶（trash）
  'asset.delete':
    '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      '<path d="M3 6h18"/>' +
      '<path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>' +
      '<path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>' +
      '<path d="M10 11v6M14 11v6"/>' +
    '</svg>',
  // 批量导入：向下托盘（download / import）
  'asset.import':
    '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>' +
      '<path d="M7 10l5 5 5-5"/>' +
      '<path d="M12 15V3"/>' +
    '</svg>',
  // 二维码刷新：刷新箭头
  'asset.qr.regen':
    '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      '<path d="M21 12a9 9 0 1 1-3-6.7"/>' +
      '<path d="M21 4v5h-5"/>' +
    '</svg>',
  // 上传附件：云朵向上箭头（cloud-upload）
  'file.upload':
    '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      '<path d="M17.5 19a4.5 4.5 0 1 0-1-8.9A6 6 0 0 0 5 13"/>' +
      '<path d="M12 12v9"/>' +
      '<path d="M8.5 15.5L12 12l3.5 3.5"/>' +
    '</svg>',
  // 删除附件：文件 + ✕
  'file.delete':
    '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>' +
      '<path d="M14 2v6h6"/>' +
      '<path d="M9.5 13.5l5 5M14.5 13.5l-5 5"/>' +
    '</svg>',
  // 登录：log-in
  login:
    '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      '<path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/>' +
      '<path d="M10 17l5-5-5-5"/>' +
      '<path d="M15 12H3"/>' +
    '</svg>',
  // 登出：log-out
  logout:
    '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      '<path d="M9 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h4"/>' +
      '<path d="M16 17l5-5-5-5"/>' +
      '<path d="M21 12H9"/>' +
    '</svg>',
}

function actionIcon(a) {
  return (
    ACTION_ICON_MAP[a] ||
    '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><circle cx="12" cy="12" r="6" fill="currentColor"/></svg>'
  )
}

function fmtTime(t) {
  if (!t) return ''
  const d = new Date(t)
  const now = new Date()
  const diff = (now - d) / 1000
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`
  const sameDay =
    d.getFullYear() === now.getFullYear() &&
    d.getMonth() === now.getMonth() &&
    d.getDate() === now.getDate()
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  if (sameDay) return `${hh}:${mm}`
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${m}-${day} ${hh}:${mm}`
}

function dayLabel(t) {
  const d = new Date(t)
  const now = new Date()
  const startOf = (x) => new Date(x.getFullYear(), x.getMonth(), x.getDate()).getTime()
  const diffDay = Math.round((startOf(now) - startOf(d)) / 86400000)
  if (diffDay === 0) return '今天'
  if (diffDay === 1) return '昨天'
  if (diffDay < 7) return `${diffDay} 天前`
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${m}-${day}`
}

const collapsedGroups = ref(new Set())

function isGroupCollapsed(date) {
  return collapsedGroups.value.has(date)
}

function toggleGroup(date) {
  const next = new Set(collapsedGroups.value)
  if (next.has(date)) {
    next.delete(date)
  } else {
    next.add(date)
  }
  collapsedGroups.value = next
}

const grouped = computed(() => {
  const out = []
  const map = new Map()
  for (const it of items.value) {
    const d = new Date(it.created_at)
    const key = `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`
    if (!map.has(key)) {
      map.set(key, { date: key, label: dayLabel(it.created_at), items: [] })
      out.push(map.get(key))
    }
    map.get(key).items.push(it)
  }
  return out
})

const playToken = ref(0)

async function reload(reset = false) {
  if (reset) page.value = 1
  loading.value = true
  try {
    const tasks = [
      listLogs({
        page: page.value,
        page_size: pageSize.value,
        scope: scope.value,
        action: actionFilter.value || undefined,
        keyword: keyword.value || undefined,
      }),
    ]
    if (reset) tasks.push(reloadTypeStats())
    const [data] = await Promise.all(tasks)
    items.value = data.items || []
    total.value = data.total || 0
    unread.value = data.unread || 0
    playToken.value++
  } finally {
    loading.value = false
  }
}

function onScopeChange(v) {
  if (scope.value === v) return
  scope.value = v
  reload(true)
}

function onActionChange(v) {
  if (actionFilter.value === v) return
  actionFilter.value = v
  reload(true)
}

function clearKeyword() {
  keyword.value = ''
  reload(true)
}

async function onAiSearch() {
  const text = keyword.value?.trim()
  if (!text) {
    reload(true)
    return
  }
  aiSearching.value = true
  try {
    const res = await aiParseSearch(text, 'logs')
    const p = res.params || {}
    keyword.value = p.keyword || ''
    if (p.action) actionFilter.value = p.action
    if (p.scope) scope.value = p.scope
    await reload(true)
  } catch {
    reload(true)
  } finally {
    aiSearching.value = false
  }
}

function onReset() {
  keyword.value = ''
  actionFilter.value = ''
  scope.value = 'all'
  reload(true)
}

async function onMarkOne(row) {
  if (row.is_read) return
  try {
    const res = await markLogsRead([row.id])
    row.is_read = true
    unread.value = res?.unread ?? Math.max(unread.value - 1, 0)
    window.dispatchEvent(new CustomEvent('messages:unread', { detail: unread.value }))
  } catch {
    /* 已由拦截器提示 */
  }
}

const detailOpen = ref(false)
const detailRow = ref(null)

function onCardClick(row) {
  detailRow.value = row
  detailOpen.value = true
  if (!row.is_read) {
    onMarkOne(row)
  }
}

function fmtFullTime(t) {
  if (!t) return ''
  const d = new Date(t)
  const pad = (n) => String(n).padStart(2, '0')
  return (
    `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ` +
    `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
  )
}

async function onMarkAllRead() {
  try {
    const res = await markLogsRead(null)
    items.value.forEach((it) => (it.is_read = true))
    unread.value = res?.unread ?? 0
    window.dispatchEvent(new CustomEvent('messages:unread', { detail: unread.value }))
    toast.success('已全部标记为已读')
  } catch {
    /* 已由拦截器提示 */
  }
}

let pollTimer = null
onMounted(() => {
  reload(true)
  pollTimer = setInterval(() => {
    if (!loading.value) reload(false)
  }, 30000)
})
onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
.messages-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
  min-height: 0;
  font-family: 'HarmonyOS Sans SC', 'Noto Sans SC', 'PingFang SC',
    'Microsoft YaHei UI', 'Microsoft YaHei', -apple-system,
    BlinkMacSystemFont, 'Helvetica Neue', sans-serif;
  letter-spacing: 0.3px;
  -webkit-font-smoothing: antialiased;
  color: var(--text-primary, #2f2f33);
  animation: page-fade-in 0.45s cubic-bezier(0.22, 1, 0.36, 1) both;
}
.messages-page .msg-toolbar {
  animation: section-rise 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
  animation-delay: 0.06s;
}
.messages-page .msg-timeline.first-load {
  animation: section-rise 0.55s cubic-bezier(0.22, 1, 0.36, 1) both;
  animation-delay: 0.16s;
}
@keyframes page-fade-in {
  from { opacity: 0; }
  to   { opacity: 1; }
}
@keyframes section-rise {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ===================== 工具条（扁平、无卡片） ===================== */
.msg-toolbar {
  flex: 0 0 auto;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
  padding: 4px 4px 14px;
  background: transparent;
  border: 0;
  border-radius: 0;
  box-shadow: none;
  margin-bottom: 4px;
}
.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  flex-wrap: wrap;
}
/* 让左侧筛选项与右侧输入框底线大致齐平 */
.mine-switch,
.type-select-control {
  align-self: center;
}
.toolbar-right .btn-secondary,
.toolbar-right .btn-icon {
  margin-bottom: 6px;
}

/* 左侧开关与类型筛选 */
.mine-switch {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  user-select: none;
  align-self: flex-end;
}
.mine-switch-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--theme-primary-deep, #8a7355);
  letter-spacing: 0.5px;
}
.mine-switch :deep(.el-switch__core) {
  min-width: 40px;
  height: 22px;
  border-color: rgba(var(--theme-primary-rgb), 0.18);
  background: rgba(var(--theme-primary-rgb), 0.12);
  box-shadow: inset 0 1px 3px rgba(94, 74, 46, 0.12);
}
.mine-switch :deep(.el-switch__action) {
  width: 18px;
  height: 18px;
  color: #fff;
  box-shadow: 0 2px 6px rgba(94, 74, 46, 0.18);
}
.mine-switch :deep(.el-switch.is-checked .el-switch__core) {
  border-color: var(--theme-primary, #c5a47e);
  background: var(--theme-primary, #c5a47e);
}

/* 一道竖向分隔线，强化 switch 与类型筛选的层级 */
.toolbar-left::before {
  content: none;
}
.mine-switch + .type-select-control {
  position: relative;
  margin-left: 2px;
  padding-left: 18px;
}
.mine-switch + .type-select-control::before {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  transform: translateY(-50%);
  width: 1px;
  height: 14px;
  background: rgba(var(--theme-primary-rgb), 0.35);
}

.type-select-control {
  position: relative;
  width: calc(var(--type-select-width, 4em) + 34px);
  min-width: 108px;
  /* max-width: 180px; */
  transition: width 0.24s ease;
}
.type-select {
  width: 100%;
}
.type-select :deep(.el-select__wrapper) {
  min-height: 44px;
  padding: 14px 0 6px;
  background: transparent !important;
  border-radius: 0;
  border: 0;
  border-bottom: 2px solid var(--theme-input-border, #e0d2b8);
  box-shadow: none !important;
  font-size: 15px;
  color: var(--theme-primary-deep, #8a7355);
  line-height: 1.2;
  transition: border-bottom-color 0.25s ease;
}
.type-select :deep(.el-select__wrapper.is-focused),
.type-select :deep(.el-select__wrapper:hover) {
  border-bottom-color: var(--theme-primary, #c5a47e);
  box-shadow: none !important;
}
.type-select :deep(.el-select__selection),
.type-select :deep(.el-select__selected-item) {
  min-width: 0;
}
.type-select :deep(.el-select__placeholder),
.type-select :deep(.el-select__selected-item span) {
  color: var(--theme-primary-deep, #8a7355);
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.4px;
}
.type-select :deep(.el-select__suffix) {
  color: var(--theme-text-hover, #5e4a2e);
}
.type-select :deep(.el-select__caret) {
  font-size: 15px;
  color: var(--theme-primary-deep, #8a7355);
  transition: color 0.22s ease, transform 0.22s ease;
}
.type-select-control:hover :deep(.el-select__caret),
.type-select :deep(.el-select__wrapper.is-focused .el-select__caret) {
  color: var(--theme-text-hover, #5e4a2e);
}
html.dark .type-select :deep(.el-select__wrapper) {
  background: transparent !important;
  border-bottom-color: var(--theme-primary, #c5a47e) !important;
}
html.dark .type-select :deep(.el-select__wrapper.is-focused),
html.dark .type-select :deep(.el-select__wrapper:hover) {
  border-bottom-color: var(--theme-primary, #c5a47e) !important;
}
html.dark .type-select :deep(.el-select__placeholder),
html.dark .type-select :deep(.el-select__selected-item span),
html.dark .type-select :deep(.el-select__caret) {
  color: var(--theme-primary-deep);
}
html.dark .type-select-control:hover :deep(.el-select__caret),
html.dark .type-select :deep(.el-select__wrapper.is-focused .el-select__caret) {
  color: var(--theme-text-hover);
}

/* 金色浮动 label 输入框（与资产表保持一致） */
.form-control {
  position: relative;
  margin: 0;
  width: 220px;
}
.form-control input {
  background-color: transparent;
  border: 0;
  border-bottom: 2px solid var(--theme-input-border, #e0d2b8);
  display: block;
  width: 100%;
  padding: 14px 0 6px;
  font-size: 15px;
  color: var(--theme-primary-deep, #8a7355);
  font-family: inherit;
  transition: border-bottom-color 0.25s ease;
}
.form-control input:focus,
.form-control input:valid,
.form-control.is-filled input {
  outline: 0;
  border-bottom-color: var(--theme-primary, #c5a47e);
}
.form-control label {
  position: absolute;
  top: 14px;
  left: 0;
  pointer-events: none;
  display: flex;
}
.form-control label span {
  display: inline-block;
  font-size: 15px;
  min-width: 5px;
  color: var(--theme-text-muted, #b9a78a);
  letter-spacing: 1px;
  transition: 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.form-control input:focus + label span,
.form-control input:valid + label span,
.form-control.is-filled label span {
  color: var(--theme-primary-deep, #8a7355);
  transform: translateY(-18px);
  font-size: 11px;
  font-weight: 600;
}

/* ===================== AI 搜索加载状态 ===================== */
.ai-search-control {
  position: relative;
}
.ai-search-control.is-loading input {
  opacity: 0.5;
  pointer-events: none;
}
.ai-search-spinner {
  position: absolute;
  right: 2px;
  bottom: 10px;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(var(--theme-primary-rgb), 0.25);
  border-top-color: var(--theme-primary, #c5a47e);
  border-radius: 50%;
  animation: ai-spin 0.7s linear infinite;
}
@keyframes ai-spin {
  to { transform: rotate(360deg); }
}
.search-btn.is-ai-loading {
  opacity: 0.5;
  pointer-events: none;
}

/* "全部已读" 改为文字按钮（无边框） */
.btn-secondary {
  appearance: none;
  border: 0;
  background: transparent;
  color: var(--theme-primary-deep, #8a7355);
  height: 30px;
  padding: 0 6px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: color 0.2s ease, background-color 0.22s ease,
    transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.btn-secondary:hover:not(:disabled) {
  color: var(--theme-text-hover, #5e4a2e);
  background: rgba(var(--theme-primary-rgb), 0.1);
  transform: translateY(-1px);
}
.btn-secondary:active:not(:disabled) {
  transform: scale(0.96);
  transition-duration: 0.1s;
}
.btn-secondary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.unread-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  padding: 0;
  background: #ef665b;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  line-height: 1;
  border-radius: 50%;
  flex-shrink: 0;
}

/* 刷新按钮：纯图标，悬浮才出现底色 */
.btn-icon {
  appearance: none;
  border: 0;
  background: transparent;
  color: var(--theme-primary-deep, #8a7355);
  width: 30px;
  height: 30px;
  border-radius: 6px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.18s ease;
}
.btn-icon:hover:not(:disabled) {
  background: rgba(var(--theme-primary-rgb), 0.12);
  color: var(--theme-text-hover, #5e4a2e);
}
.btn-icon .spinning {
  animation: spin 0.9s linear infinite;
}

/* ===================== 资产表同款图标按钮（查询 / 重置） ===================== */
.svg-icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  background: transparent;
  border: none;
  cursor: pointer;
  outline: none;
  transition: transform 0.22s cubic-bezier(0.34, 1.56, 0.64, 1), filter 0.18s ease;
  line-height: 0;
}
.svg-icon-btn svg {
  display: block;
  transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1), fill 0.18s ease;
}
.svg-icon-btn:hover {
  transform: scale(1.18);
}
.svg-icon-btn:active {
  transform: scale(0.92);
  transition-duration: 0.1s;
}
.svg-icon-btn:focus-visible {
  outline: 1px dashed rgba(var(--theme-primary-deep-rgb), 0.5);
  outline-offset: 2px;
}
.svg-icon-btn.search-btn,
.svg-icon-btn.reset-btn {
  padding: 6px;
}
.svg-icon-btn.search-btn svg,
.svg-icon-btn.reset-btn svg { fill: var(--theme-primary-deep, #8a7355); }
.svg-icon-btn.search-btn:hover svg,
.svg-icon-btn.reset-btn:hover svg { fill: var(--theme-text-hover, #6e5a40); }
.svg-icon-btn.reset-btn svg { transition: transform 0.45s cubic-bezier(0.22, 1, 0.36, 1); }
.svg-icon-btn.reset-btn:hover svg { transform: rotate(-180deg); }
.svg-icon-btn.search-btn:hover svg { animation: search-bounce 0.5s ease; }
@keyframes search-bounce {
  0%, 100% { transform: translateY(0); }
  40%      { transform: translateY(-3px) scale(1.05); }
  70%      { transform: translateY(0) scale(0.98); }
}
/* 让图标按钮的下沿与输入框底部金线对齐 */
.toolbar-right .svg-icon-btn {
  padding-bottom: 6px;
  margin-bottom: 0;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ===================== 时间线 ===================== */
.msg-timeline {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  gap: 18px;
  max-width: 1280px;
  width: 100%;
  min-height: 0;
  margin: 0 auto;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 4px;
  scrollbar-gutter: stable;
}
/* -------- 日志类型占比卡片：圆环指标组 -------- */
.type-ratio-card {
  position: relative;
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 8px 0 22px;
  background: transparent;
  border: 0;
  border-radius: 0;
  box-shadow: none;
}
.type-ratio-card::before {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 1px;
  pointer-events: none;
  background: linear-gradient(90deg, transparent, rgba(var(--theme-primary-rgb), 0.22), transparent);
}
.ratio-title-row {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
  min-height: 22px;
}
.ratio-heading {
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  gap: 12px;
}
.ratio-title {
  color: var(--theme-primary-deep, #8a7355);
  font-size: 14px;
  font-weight: 800;
  letter-spacing: 0.5px;
}
.ratio-total {
  position: relative;
  color: var(--theme-text-muted, #b9a78a);
  font-size: 12px;
  font-weight: 600;
}
.ratio-total::before {
  content: '';
  display: inline-block;
  width: 4px;
  height: 4px;
  margin: 0 7px 2px 0;
  border-radius: 50%;
  background: var(--theme-primary, #c5a47e);
  box-shadow: 0 0 8px rgba(var(--theme-primary-rgb), 0.55);
}
.ratio-title-line {
  flex: 1 1 auto;
  height: 1px;
  background: linear-gradient(90deg, rgba(var(--theme-primary-rgb), 0.28), transparent);
}
.ratio-metrics {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 40px 12px;
  align-items: center;
}
.ratio-metric {
  --ratio-color: var(--theme-primary, #c5a47e);
  --ratio-angle: 0deg;
  display: grid;
  grid-template-columns: minmax(72px, max-content) 66px;
  align-items: center;
  justify-content: center;
  gap: 35px;
  min-width: 0;
}
.ratio-copy {
  min-width: 0;
}
.ratio-label {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  max-width: 100%;
  color: var(--theme-text-muted, #b9a78a);
  font-size: 12px;
  font-weight: 700;
}
.ratio-dot {
  flex: 0 0 auto;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--ratio-color);
  box-shadow: 0 0 10px var(--ratio-color);
}
.ratio-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ratio-percent {
  display: block;
  margin-top: 8px;
  margin-left: 13px;
  color: var(--ratio-color);
  font-family: 'SF Mono', Menlo, Consolas, monospace;
  font-size: 18px;
  font-weight: 800;
  letter-spacing: 0.3px;
}
.ratio-ring {
  position: relative;
  display: grid;
  place-items: center;
  width: 66px;
  height: 66px;
  border-radius: 50%;
  background:
    conic-gradient(var(--ratio-color) 0deg var(--ratio-angle), rgba(var(--theme-primary-rgb), 0.12) var(--ratio-angle) 360deg);
  box-shadow:
    0 0 18px color-mix(in srgb, var(--ratio-color) 34%, transparent),
    inset 0 0 12px rgba(0, 0, 0, 0.12);
}
.ratio-ring::before {
  content: '';
  position: absolute;
  inset: 6px;
  border-radius: 50%;
  background: var(--bg-card, #fff);
  box-shadow: inset 0 0 0 1px rgba(var(--theme-primary-rgb), 0.12);
}
.ratio-ring::after {
  content: '';
  position: absolute;
  inset: -5px;
  border-radius: 50%;
  border: 1px solid rgba(var(--theme-primary-rgb), 0.12);
  border-top-color: color-mix(in srgb, var(--ratio-color) 55%, transparent);
  opacity: 0.9;
}
.ratio-ring-core {
  position: relative;
  z-index: 1;
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  color: var(--ratio-color);
  border-radius: 50%;
  background: rgba(var(--theme-primary-rgb), 0.08);
}
.ratio-ring-core :deep(svg) {
  width: 22px;
  height: 22px;
  display: block;
  filter: drop-shadow(0 0 6px color-mix(in srgb, var(--ratio-color) 45%, transparent));
}

/* -------- 黑夜模式：保留原本的深色玻璃质感（已迁移到下方非 scoped 块） -------- */
.day-group {
  flex: 0 0 auto;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  justify-content: stretch;
  gap: 16px 18px;
}
.day-label {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 2px -2px;
  color: var(--theme-primary-deep, #8a7355);
  animation: day-label-in 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
}
@keyframes day-label-in {
  from { opacity: 0; transform: translateY(-4px); }
  to   { opacity: 1; transform: translateY(0); }
}
.day-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(
    to right,
    transparent,
    rgba(var(--theme-primary-rgb), 0.35),
    transparent
  );
}
.day-toggle {
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  padding: 0;
  margin-left: 2px;
  color: var(--theme-primary-deep, #8a7355);
  background: transparent;
  border: 1px solid rgba(var(--theme-primary-rgb), 0.28);
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.2s ease, background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}
.day-toggle:hover {
  color: var(--theme-primary, #c5a47e);
  background: rgba(var(--theme-primary-rgb), 0.10);
  border-color: rgba(var(--theme-primary-rgb), 0.5);
}
.day-toggle:focus-visible {
  outline: 2px solid rgba(var(--theme-primary-rgb), 0.45);
  outline-offset: 2px;
}
.day-toggle svg {
  display: block;
  transition: transform 0.25s cubic-bezier(0.22, 1, 0.36, 1);
}
.day-toggle.collapsed svg {
  transform: rotate(-90deg);
}
.day-text {
  font-size: 12px;
  color: var(--theme-primary-deep, #8a7355);
  letter-spacing: 1px;
  font-weight: 600;
}
.day-count {
  font-size: 11px;
  color: var(--theme-text-muted, #b9a78a);
}

.msg-card {
  position: relative;
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr);
  grid-template-rows: minmax(0, 1fr) auto;
  align-items: start;
  gap: 13px 13px;
  min-height: 128px;
  padding: 18px 18px 16px;
  background:
    radial-gradient(circle at 14% 10%, rgba(var(--theme-primary-rgb), 0.24), transparent 36%),
    radial-gradient(circle at 100% 100%, rgba(var(--theme-primary-rgb), 0.16), transparent 36%),
    linear-gradient(145deg, rgba(255, 255, 255, 0.82), rgba(255, 255, 255, 0.48));
  border: 1px solid rgba(var(--theme-primary-rgb), 0.30);
  border-radius: 12px;
  animation: msg-card-rise 0.42s cubic-bezier(0.22, 1, 0.36, 1) both;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.64),
    0 12px 30px rgba(var(--theme-primary-deep-rgb), 0.10);
  backdrop-filter: blur(12px);
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease,
    background 0.18s ease;
  cursor: pointer;
  overflow: hidden;
}
.msg-card::before {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.34), transparent 38%),
    radial-gradient(circle at 100% 100%, rgba(var(--theme-primary-rgb), 0.22), transparent 36%);
  opacity: 0.82;
}
.msg-card::after {
  content: '→';
  position: absolute;
  right: 15px;
  bottom: 13px;
  color: var(--theme-primary-deep, #8a7355);
  font-size: 20px;
  line-height: 1;
  opacity: 0.75;
  transition: transform 0.18s ease, opacity 0.18s ease;
}
.msg-card .msg-body {
  display: contents;
}

.msg-card:hover {
  transform: translateY(-3px);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.62),
    0 14px 36px rgba(var(--theme-primary-deep-rgb), 0.18),
    0 0 22px rgba(var(--theme-primary-rgb), 0.18);
  border-color: rgba(var(--theme-primary-rgb), 0.55);
}
.msg-card:hover::after {
  opacity: 1;
  transform: translateX(3px);
}
.msg-card:active {
  transform: scale(0.995);
  transition-duration: 0.1s;
}
.msg-card.unread {
  background:
    radial-gradient(circle at 14% 10%, rgba(var(--theme-primary-rgb), 0.36), transparent 38%),
    radial-gradient(circle at 100% 100%, rgba(var(--theme-primary-rgb), 0.22), transparent 38%),
    linear-gradient(145deg, rgba(255, 251, 243, 0.90), rgba(255, 255, 255, 0.58));
  border-color: rgba(var(--theme-primary-rgb), 0.72);
  /* box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.76),
    0 14px 34px rgba(var(--theme-primary-deep-rgb), 0.18),
    0 0 26px rgba(var(--theme-primary-rgb), 0.28); */
}
.unread-badge {
  position: absolute;
  top: 15px;
  right: 16px;
  z-index: 2;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  height: 22px;
  padding: 0 8px;
  border: 1px solid rgba(var(--theme-primary-rgb), 0.24);
  border-radius: 999px;
  background: rgba(var(--theme-primary-rgb), 0.12);
  color: var(--theme-primary-deep, #8a7355);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.4px;
}
.unread-light {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #f7bd55;
  box-shadow:
    0 0 0 3px rgba(247, 189, 85, 0.18),
    0 0 10px rgba(247, 189, 85, 0.55);
}
/* 交错入场：限定在前 12 张，避免大列表性能负担 */
.msg-card:nth-child(1)  { animation-delay: 0.02s; }
.msg-card:nth-child(2)  { animation-delay: 0.05s; }
.msg-card:nth-child(3)  { animation-delay: 0.08s; }
.msg-card:nth-child(4)  { animation-delay: 0.11s; }
.msg-card:nth-child(5)  { animation-delay: 0.14s; }
.msg-card:nth-child(6)  { animation-delay: 0.17s; }
.msg-card:nth-child(7)  { animation-delay: 0.20s; }
.msg-card:nth-child(8)  { animation-delay: 0.23s; }
.msg-card:nth-child(9)  { animation-delay: 0.26s; }
.msg-card:nth-child(10) { animation-delay: 0.29s; }
.msg-card:nth-child(11) { animation-delay: 0.32s; }
.msg-card:nth-child(12) { animation-delay: 0.35s; }

@keyframes msg-card-rise {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* 卡片左侧图标：直接展示 PNG，无边框无底色 */
.msg-icon {
  position: relative;
  z-index: 1;
  grid-column: 1;
  grid-row: 1;
  flex-shrink: 0;
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 0;
  border: 1px solid rgba(var(--theme-primary-rgb), 0.34);
  border-radius: 10px;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.42),
    0 8px 18px rgba(var(--theme-primary-deep-rgb), 0.10);
  color: #b08a52;
}
.msg-icon-img {
  width: 29px;
  height: 29px;
  object-fit: contain;
  display: block;
  user-select: none;
  -webkit-user-drag: none;
}

.msg-body {
  flex: 1;
  width: 100%;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.msg-head {
  position: relative;
  z-index: 1;
  grid-column: 2;
  grid-row: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 9px;
  flex-wrap: nowrap;
  min-width: 0;
  padding-right: 62px;
  padding-top: 1px;
}
.actor {
  font-weight: 700;
  font-size: 13px;
  color: var(--text-primary, #2f2f33);
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.action-tag {
  order: -1;
  font-size: 10.5px;
  font-weight: 600;
  padding: 3px 9px;
  border-radius: 4px;
  letter-spacing: 0.5px;
  background: #f0e7d3;
  color: var(--theme-primary-deep, #8a7355);
}
.tag-asset-create { background: #e1f3e8; color: #2c7a5e; }
.tag-asset-update { background: #fff3d9; color: #b08a52; }
.tag-asset-qr-regen { background: #e6f0fb; color: #1f5fa8; }
.tag-file-upload { background: #e6f0fb; color: #1f5fa8; }
.tag-file-delete { background: #fde4e4; color: #c44545; }
.tag-login { background: #f0e7f7; color: #6b3a8a; }
.tag-logout { background: #f0e7f7; color: #6b3a8a; }

.unread-dot {
  width: 7px;
  height: 7px;
  background: #ef665b;
  border-radius: 50%;
  box-shadow: 0 0 0 3px rgba(239, 102, 91, 0.18);
}
.msg-summary {
  width: 100%;
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary, #2f2f33);
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.changes {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-top: 2px;
  padding: 5px 10px;
  background: #f9f5ec;
  border-left: 2px solid rgba(var(--theme-primary-rgb), 0.5);
  border-radius: 0 6px 6px 0;
}
.change-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  flex-wrap: wrap;
}
.ch-field {
  color: var(--theme-primary-deep, #8a7355);
  font-weight: 600;
  min-width: 56px;
}
.ch-before {
  color: #c44545;
  text-decoration: line-through;
  background: rgba(196, 69, 69, 0.08);
  padding: 1px 6px;
  border-radius: 3px;
  max-width: 240px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ch-after {
  color: #2c7a5e;
  background: rgba(44, 122, 94, 0.08);
  padding: 1px 6px;
  border-radius: 3px;
  font-weight: 600;
  max-width: 240px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ch-arrow {
  color: var(--theme-text-muted, #b9a78a);
  flex-shrink: 0;
}

.meta-time {
  margin-left: 0;
  font-size: 12px;
  color: var(--text-muted, #999);
  line-height: 1.2;
}
.msg-foot {
  position: relative;
  z-index: 1;
  grid-column: 1 / -1;
  grid-row: 2;
  align-self: end;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 14px;
  margin-top: auto;
  padding-right: 28px;
}
.msg-foot .msg-summary {
  flex: initial;
  min-width: 0;
}
.meta-ip {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 11px;
  color: var(--theme-text-muted, #b9a78a);
  letter-spacing: 0.3px;
  font-family: 'SF Mono', Menlo, Consolas, monospace;
  line-height: 1.2;
}
.meta-ip svg {
  color: var(--theme-primary-light-3, #d4b89a);
}
/* msg-card 暗色样式已迁移到下方非 scoped 块 */

@media (max-width: 1180px) {
  .ratio-metrics {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
  .day-group {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 860px) {
  .ratio-metrics {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  .day-group {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 560px) {
  .day-group,
  .ratio-metrics {
    grid-template-columns: 1fr;
  }
}

/* 空 / loading */
.msg-timeline.empty {
  min-height: 320px;
}
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 60px 20px;
  color: var(--theme-text-muted, #b9a78a);
  text-align: center;
}
.empty-title {
  font-size: 16px;
  color: var(--theme-primary-deep, #8a7355);
  font-weight: 600;
}
.empty-sub {
  font-size: 12.5px;
}
.loading {
  text-align: center;
  color: var(--theme-text-muted, #b9a78a);
  padding: 40px;
  font-size: 13px;
}

.msg-pager {
  flex: 0 0 auto;
  display: flex;
  justify-content: flex-end;
  padding: 8px 4px 4px;
}

/* 日志类型占比：暗色圆环视觉 */
html.dark .messages-page .type-ratio-card::before {
  background: linear-gradient(90deg, transparent, rgba(var(--theme-primary-rgb), 0.18), transparent);
}
html.dark .messages-page .ratio-total,
html.dark .messages-page .ratio-label {
  color: rgba(232, 234, 242, 0.58);
}
html.dark .messages-page .ratio-title-line {
  background: linear-gradient(90deg, rgba(var(--theme-primary-rgb), 0.24), transparent);
}
html.dark .messages-page .ratio-ring {
  background:
    conic-gradient(var(--ratio-color) 0deg var(--ratio-angle), rgba(255, 255, 255, 0.075) var(--ratio-angle) 360deg);
  box-shadow:
    0 0 20px color-mix(in srgb, var(--ratio-color) 36%, transparent),
    inset 0 0 16px rgba(0, 0, 0, 0.48);
}
html.dark .messages-page .ratio-ring::before {
  background:
    radial-gradient(circle, rgba(255, 255, 255, 0.06), rgba(0, 0, 0, 0.34)),
    rgba(14, 17, 28, 0.96);
  box-shadow:
    inset 0 0 0 1px rgba(255, 255, 255, 0.045),
    inset 0 0 18px rgba(0, 0, 0, 0.58);
}
html.dark .messages-page .ratio-ring::after {
  border-color: rgba(255, 255, 255, 0.08);
  border-top-color: color-mix(in srgb, var(--ratio-color) 68%, transparent);
}
html.dark .messages-page .ratio-ring-core {
  background: rgba(255, 255, 255, 0.045);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

html.dark .messages-page .msg-card::before {
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.08), transparent 38%),
    radial-gradient(circle at 100% 100%, rgba(var(--theme-primary-rgb), 0.18), transparent 38%);
  opacity: 0.9;
}
html.dark .messages-page .msg-icon {
  background:
    linear-gradient(145deg, rgba(255, 255, 255, 0.10), rgba(255, 255, 255, 0.03)) !important;
  border-color: rgba(var(--theme-primary-rgb), 0.34) !important;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.10),
    0 0 18px rgba(var(--theme-primary-rgb), 0.12) !important;
}
html.dark .messages-page .unread-badge {
  border-color: rgba(247, 189, 85, 0.28);
  background: rgba(247, 189, 85, 0.12);
  color: #f6c45f;
}
/* 顶部类型筛选下拉菜单：与资产表单 el-select 行为一致 */
.messages-type-select-popper.el-popper {
  border: 0;
  border-radius: 6px;
}
html[data-mode='light'] .messages-type-select-popper.el-popper,
html:not([data-mode='dark']) .messages-type-select-popper.el-popper {
  background: #fff;
  box-shadow: 0 10px 28px rgba(94, 74, 46, 0.16);
}
.messages-type-select-popper .el-popper__arrow::before {
  border-color: transparent;
  box-shadow: none;
}
html[data-mode='light'] .messages-type-select-popper .el-popper__arrow::before,
html:not([data-mode='dark']) .messages-type-select-popper .el-popper__arrow::before {
  background: #fff;
}
.messages-type-select-popper .el-select-dropdown {
  border-radius: 6px;
}
.messages-type-select-popper .el-select-dropdown__list {
  padding: 14px 0;
}
.messages-type-select-popper .el-select-dropdown__item {
  height: 34px;
  line-height: 34px;
  padding: 0 8px;
  font-size: 15px;
  font-weight: 500;
  letter-spacing: 0.3px;
}
html[data-mode='light'] .messages-type-select-popper .el-select-dropdown__item,
html:not([data-mode='dark']) .messages-type-select-popper .el-select-dropdown__item {
  color: #6f7283;
}
.messages-type-select-popper .el-select-dropdown__item.is-hovering,
.messages-type-select-popper .el-select-dropdown__item:hover {
  background: rgba(var(--theme-primary-rgb), 0.08);
  color: var(--theme-text-hover, #5e4a2e);
}
.messages-type-select-popper .el-select-dropdown__item.is-selected {
  background: transparent;
  color: var(--theme-primary-deep, #8a7355);
  font-weight: 700;
}
html[data-mode='dark'] .messages-type-select-popper.el-popper {
  background: var(--theme-surface);
  box-shadow: 0 14px 32px rgba(0, 0, 0, 0.42);
}
html[data-mode='dark'] .messages-type-select-popper .el-popper__arrow::before {
  background: var(--theme-surface);
}
html[data-mode='dark'] .messages-type-select-popper .el-select-dropdown__item {
  color: var(--text-secondary);
}
html[data-mode='dark'] .messages-type-select-popper .el-select-dropdown__item.is-hovering,
html[data-mode='dark'] .messages-type-select-popper .el-select-dropdown__item:hover {
  background: var(--bg-hover);
  color: var(--theme-text-hover);
}
html[data-mode='dark'] .messages-type-select-popper .el-select-dropdown__item.is-selected {
  background: transparent;
  color: var(--theme-primary-deep);
  font-weight: 700;
}
/* ============================================================
   Messages 页面：dark 模式下根容器使用页面底色
   ============================================================ */
html.dark .messages-page {
  color: var(--text-primary) !important;
}
html.dark .messages-page .form-control input {
  border-bottom-color: var(--theme-primary, #c5a47e) !important;
  color: var(--theme-primary) !important;
}
html.dark .messages-page .form-control input:focus,
html.dark .messages-page .form-control input:valid,
html.dark .messages-page .form-control.is-filled input {
  border-bottom-color: var(--theme-primary) !important;
}
html.dark .messages-page .form-control label span {
  color: rgba(255, 255, 255, 0.55) !important;
}
html.dark .messages-page .form-control input:focus + label span,
html.dark .messages-page .form-control input:valid + label span,
html.dark .messages-page .form-control.is-filled label span {
  color: var(--theme-primary) !important;
}

/* ============================================================
   Messages 列表 / 卡片 / 标签 暗色覆盖
   ============================================================ */
html.dark .messages-page .scope-btn.active,
html.dark .messages-page .actor,
html.dark .messages-page .msg-summary {
  color: var(--text-primary) !important;
}
html.dark .messages-page .meta-time {
  color: var(--text-muted) !important;
}
html.dark .messages-page .msg-card {
  background:
    radial-gradient(circle at 12% 10%, rgba(var(--theme-primary-rgb), 0.20), transparent 36%),
    radial-gradient(circle at 100% 100%, rgba(90, 110, 190, 0.12), transparent 42%),
    linear-gradient(145deg, rgba(31, 33, 48, 0.86), rgba(13, 15, 25, 0.78)) !important;
  border-color: rgba(255, 255, 255, 0.10) !important;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.08),
    0 14px 34px rgba(0, 0, 0, 0.34) !important;
}
html.dark .messages-page .msg-card:hover {
  border-color: rgba(var(--theme-primary-rgb), 0.52) !important;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.12),
    0 18px 42px rgba(0, 0, 0, 0.44),
    0 0 28px rgba(var(--theme-primary-rgb), 0.22) !important;
}
html.dark .messages-page .msg-card.unread {
  background:
    radial-gradient(circle at 12% 10%, rgba(var(--theme-primary-rgb), 0.38), transparent 38%),
    radial-gradient(circle at 100% 100%, rgba(247, 189, 85, 0.14), transparent 40%),
    linear-gradient(145deg, rgba(49, 39, 28, 0.88), rgba(15, 17, 26, 0.78)) !important;
  border-color: rgba(var(--theme-primary-rgb), 0.68) !important;
  /* box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.12),
    0 16px 38px rgba(0, 0, 0, 0.44),
    0 0 32px rgba(var(--theme-primary-rgb), 0.34) !important; */
}
.messages-page .changes {
  background: var(--theme-surface-muted) !important;
  border-left-color: rgba(var(--theme-primary-rgb), 0.6) !important;
}
.messages-page .ch-before {
  color: #ff8a8a !important;
  background: rgba(245, 108, 108, 0.16) !important;
}
.messages-page .ch-after {
  color: #6fd49b !important;
  background: rgba(70, 167, 109, 0.18) !important;
}

/* action-tag：暗色下做反转，色块用半透明带主色，文字用更亮的同色 */
.messages-page .action-tag {
  background: rgba(var(--theme-primary-rgb), 0.18) !important;
  color: var(--theme-primary) !important;
}
.messages-page .tag-asset-create {
  background: rgba(44, 122, 94, 0.22) !important;
  color: #6fd49b !important;
}
.messages-page .tag-asset-update {
  background: rgba(176, 138, 82, 0.22) !important;
  color: #e0b974 !important;
}
.messages-page .tag-asset-delete,
.messages-page .tag-file-delete {
  background: rgba(196, 69, 69, 0.22) !important;
  color: #ff8a8a !important;
}
.messages-page .tag-asset-qr-regen,
.messages-page .tag-file-upload {
  background: rgba(79, 143, 216, 0.22) !important;
  color: #7fb6ee !important;
}
.messages-page .tag-login,
.messages-page .tag-logout {
  background: rgba(155, 110, 200, 0.22) !important;
  color: #c9a8e6 !important;
}

</style>

<!-- 非 scoped：日志详情弹窗（el-dialog 通过 append-to-body 被 teleport 到 body 下，必须用全局样式） -->
<style>
/* ============================================================
   .log-detail-dialog —— 全局样式
   ============================================================ */
.log-detail-dialog.el-dialog {
  position: relative;
  display: flex;
  flex-direction: column;
  max-width: calc(100vw - 32px);
  max-height: calc(100vh - 36px);
  border: 1px solid transparent;
  border-radius: 18px;
  overflow: hidden;
  background: var(--bg-card);
  box-shadow: 0 26px 70px rgba(0, 0, 0, 0.24);
  backdrop-filter: blur(22px) saturate(130%);
  -webkit-backdrop-filter: blur(22px) saturate(130%);
}
/* 一圈渐变描边：左上亮、右下暗，金属质感 */
.log-detail-dialog.el-dialog::before {
  content: '';
  position: absolute;
  pointer-events: none;
  inset: 0;
  border-radius: inherit;
  padding: 1px;
  background:
    linear-gradient(
      135deg,
      color-mix(in srgb, var(--theme-primary, #c5a47e) 95%, #fff5d8) 0%,
      rgba(var(--theme-primary-rgb), 0.65) 22%,
      rgba(var(--theme-primary-rgb), 0.18) 48%,
      rgba(var(--theme-primary-rgb), 0.42) 72%,
      color-mix(in srgb, var(--theme-primary, #c5a47e) 90%, #ffe6a8) 100%
    );
  -webkit-mask:
    linear-gradient(#000 0 0) content-box,
    linear-gradient(#000 0 0);
          mask:
    linear-gradient(#000 0 0) content-box,
    linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
          mask-composite: exclude;
}
.log-detail-dialog .el-dialog__header {
  flex-shrink: 0;
  margin-right: 0;
  background: transparent;
  border-bottom: 0;
}
.log-detail-dialog .el-dialog__body {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}
.log-detail-dialog .el-dialog__headerbtn {
  top: 24px;
  right: 24px;
  width: 34px;
  height: 34px;
}
.log-detail-dialog .el-dialog__close {
  color: var(--text-secondary);
  font-size: 24px;
  transition: color 0.18s ease, transform 0.18s ease;
}
.log-detail-dialog .el-dialog__headerbtn:hover .el-dialog__close {
  color: var(--theme-primary);
  transform: rotate(90deg);
}
.log-detail-dialog .dlg-header {
  display: flex;
  align-items: center;
  gap: 18px;
  padding-right: 36px;
}
.log-detail-dialog .dlg-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 74px;
  height: 74px;
  border: 1px solid rgba(var(--theme-primary-rgb), 0.22);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.025);
}
.log-detail-dialog .dlg-icon img {
  display: block;
  width: 40px;
  height: 40px;
  object-fit: contain;
  filter: none;
}
.log-detail-dialog .dlg-title-wrap {
  flex: 1;
  min-width: 0;
}
.log-detail-dialog .dlg-title-line {
  display: flex;
  align-items: center;
  gap: 11px;
  margin-bottom: 7px;
}
.log-detail-dialog .dlg-actor {
  font-size: 15px;
  font-weight: 700;
  color: var(--theme-primary-deep, #8a7355);
}
.log-detail-dialog .tag-asset-create { background: rgba(44, 122, 94, 0.28); color: #3f9d68; }
.log-detail-dialog .tag-asset-update { background: rgba(176, 138, 82, 0.24); color: #b7833f; }
.log-detail-dialog .tag-asset-delete { background: rgba(196, 69, 69, 0.2); color: #c45a5a; }
.log-detail-dialog .tag-asset-qr-regen { background: rgba(79, 143, 216, 0.22); color: #4f8fd8; }
.log-detail-dialog .tag-file-upload { background: rgba(79, 143, 216, 0.22); color: #4f8fd8; }
.log-detail-dialog .tag-file-delete { background: rgba(196, 69, 69, 0.2); color: #c45a5a; }
.log-detail-dialog .tag-login { background: rgba(155, 110, 200, 0.22); color: #9b6ec8; }
.log-detail-dialog .tag-logout { background: rgba(155, 110, 200, 0.22); color: #9b6ec8; }
.log-detail-dialog .dlg-summary {
  font-size: 18px;
  line-height: 1.25;
  font-weight: 600;
  letter-spacing: 0.3px;
  color: var(--text-primary);
}
.log-detail-dialog .dlg-title-wrap::after {
  content: '这是一次操作日志的详细信息，记录了本次操作涉及的字段变更。';
  display: block;
  margin-top: 8px;
  font-size: 12px;
  line-height: 1.5;
  color: var(--text-secondary);
}
.log-detail-dialog .dlg-body {
  display: flex;
  flex-direction: column;
  min-height: 0;
  max-height: calc(100vh - 224px);
  overflow: hidden;
}
.log-detail-dialog .dlg-meta-row {
  flex-shrink: 0;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin: 8px 0 20px;
}
.log-detail-dialog .dlg-meta-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 9px;
  min-width: 0;
  min-height: 66px;
  padding: 0px 0px 0px 74px;
  font-size: 14px;
  border: 1px solid rgba(var(--theme-primary-rgb), 0.18);
  border-radius: 12px;
}
.log-detail-dialog .dlg-meta-item + .dlg-meta-item {
  border-left: 1px solid rgba(var(--theme-primary-rgb), 0.18);
}
.log-detail-dialog .dlg-meta-label {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--theme-primary-deep, #8a7355);
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.4px;
}
.log-detail-dialog .dlg-meta-label::before {
  position: absolute;
  left: -50px;
  top: 80%;
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  color: var(--theme-primary, #c5a47e);
  font-size: 23px;
  line-height: 1;
  border: 0;
  border-radius: 0;
  background: transparent;
  transform: translateY(-50%);
}
.log-detail-dialog .dlg-meta-item:nth-child(1) .dlg-meta-label::before { content: '◷'; }
.log-detail-dialog .dlg-meta-item:nth-child(2) .dlg-meta-label::before { content: '◉'; }
.log-detail-dialog .dlg-meta-item:nth-child(3) .dlg-meta-label::before { content: '♙'; }
.log-detail-dialog .dlg-meta-value {
  max-width: 100%;
  overflow: hidden;
  color: var(--text-primary);
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
}
.log-detail-dialog .dlg-meta-value.mono {
  font-family: 'SF Mono', Menlo, Consolas, monospace;
  font-size: 13px;
}
.log-detail-dialog .dlg-section-title {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  margin-bottom: 12px;
  padding-bottom: 0;
  color: var(--theme-primary-deep, #8a7355);
  font-size: 14px;
  font-weight: 800;
  border-bottom: 0;
}
.log-detail-dialog .dlg-section-count {
  min-width: 18px;
  padding: 2px 6px;
  color: var(--theme-primary-deep, #8a7355);
  font-size: 12px;
  font-weight: 700;
  text-align: center;
  background: rgba(var(--theme-primary-rgb), 0.16);
  border: 1px solid rgba(var(--theme-primary-rgb), 0.22);
  border-radius: 999px;
}
.log-detail-dialog .dlg-changes {
  flex: 1;
  min-height: 120px;
  max-height: clamp(220px, calc(100vh - 410px), 430px);
  display: flex;
  flex-direction: column;
  gap: 0;
  overflow-y: auto;
  padding: 0;
  border: 1px solid rgba(var(--theme-primary-rgb), 0.18);
  border-radius: 10px;
  background: var(--theme-surface-subtle, rgba(255, 255, 255, 0.78));
}
.log-detail-dialog .dlg-changes::-webkit-scrollbar { width: 7px; }
.log-detail-dialog .dlg-changes::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.04);
  border-radius: 999px;
}
.log-detail-dialog .dlg-changes::-webkit-scrollbar-thumb {
  background: rgba(var(--theme-primary-rgb), 0.45);
  border-radius: 999px;
}
.log-detail-dialog .dlg-changes::-webkit-scrollbar-thumb:hover {
  background: rgba(var(--theme-primary-rgb), 0.66);
}
.log-detail-dialog .dlg-change-head {
  position: sticky;
  top: 0;
  z-index: 1;
  display: grid;
  grid-template-columns: 1.15fr 1fr 42px 1.55fr;
  gap: 14px;
  padding: 13px 20px;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 700;
  background: var(--theme-surface, #fff);
  border-bottom: 1px solid rgba(var(--theme-primary-rgb), 0.14);
}
.log-detail-dialog .dlg-change-head > span {
  justify-self: start;
  text-align: left;
}
.log-detail-dialog .dlg-change-row {
  display: grid;
  grid-template-columns: 1.15fr 1fr 42px 1.55fr;
  align-items: center;
  gap: 14px;
  min-height: 40px;
  padding: 0 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 0;
  background: transparent;
}
.log-detail-dialog .dlg-change-row:last-child { border-bottom: 0; }
.log-detail-dialog .dlg-change-row:hover { background: rgba(var(--theme-primary-rgb), 0.06); }
.log-detail-dialog .dlg-change-label {
  justify-self: start;
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 700;
  text-align: left;
}
.log-detail-dialog .dlg-change-flow {
  display: contents;
  align-items: center;
  font-size: 14px;
}
.log-detail-dialog .dlg-ch-before,
.log-detail-dialog .dlg-ch-after {
  justify-self: start;
  max-width: 100%;
  overflow: hidden;
  padding: 4px 11px;
  font-size: 13px;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
  border-radius: 5px;
}
.log-detail-dialog .dlg-ch-before {
  color: #c45a5a;
  text-decoration: none;
  background: rgba(196, 69, 69, 0.16);
}
.log-detail-dialog .dlg-ch-after {
  color: #3f9d68;
  background: rgba(44, 122, 94, 0.18);
}
.log-detail-dialog .dlg-ch-arrow {
  color: var(--theme-primary-deep, #8a7355);
  flex-shrink: 0;
}
.log-detail-dialog .dlg-empty {
  padding: 30px;
  text-align: center;
  color: var(--text-secondary);
  font-size: 14px;
  background: var(--theme-surface-subtle, rgba(255, 255, 255, 0.78));
  border: 1px solid rgba(var(--theme-primary-rgb), 0.2);
  border-radius: 10px;
}

/* 进入动效 */
.log-detail-dialog {
  animation: log-dialog-pop-in 0.36s cubic-bezier(0.22, 1, 0.36, 1) both;
}
@keyframes log-dialog-pop-in {
  from {
    opacity: 0;
    transform: translate3d(0, 18px, 0) scale(0.96);
  }
  to {
    opacity: 1;
    transform: translate3d(0, 0, 0) scale(1);
  }
}
.el-overlay:has(.log-detail-dialog) {
  animation: log-dialog-overlay-in 0.28s ease both;
  background:
    radial-gradient(circle at 50% 45%, rgba(var(--theme-primary-rgb), 0.10), transparent 36%),
    rgba(0, 0, 0, 0.72);
}
@keyframes log-dialog-overlay-in {
  from { opacity: 0; }
  to   { opacity: 1; }
}

.log-detail-dialog .dlg-change-row {
  animation: change-row-fade 0.32s cubic-bezier(0.22, 1, 0.36, 1) both;
}
.log-detail-dialog .dlg-change-row:nth-child(1) { animation-delay: 0.04s; }
.log-detail-dialog .dlg-change-row:nth-child(2) { animation-delay: 0.08s; }
.log-detail-dialog .dlg-change-row:nth-child(3) { animation-delay: 0.12s; }
.log-detail-dialog .dlg-change-row:nth-child(4) { animation-delay: 0.16s; }
.log-detail-dialog .dlg-change-row:nth-child(5) { animation-delay: 0.20s; }
.log-detail-dialog .dlg-change-row:nth-child(n+6) { animation-delay: 0.24s; }
@keyframes change-row-fade {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ===================== 黑夜模式 ===================== */
html.dark .log-detail-dialog .el-dialog__close {
  color: rgba(245, 240, 230, 0.78);
}
html.dark .log-detail-dialog .el-dialog__headerbtn:hover .el-dialog__close {
  color: var(--theme-primary, #c5a47e);
}
html.dark .log-detail-dialog .dlg-icon {
  border-color: rgba(var(--theme-primary-rgb), 0.22);
  background:
    linear-gradient(145deg, rgba(255, 255, 255, 0.035), rgba(0, 0, 0, 0.12)),
    rgba(255, 255, 255, 0.025);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.08),
    inset 0 -12px 22px rgba(0, 0, 0, 0.22),
    inset 0 0 0 1px rgba(0, 0, 0, 0.24),
    0 1px 0 rgba(255, 255, 255, 0.04),
    0 12px 22px rgba(0, 0, 0, 0.22);
}
html.dark .log-detail-dialog .dlg-icon img {
  filter: none;
}
html.dark .log-detail-dialog .dlg-actor {
  color: rgba(246, 238, 220, 0.9);
}
html.dark .log-detail-dialog .dlg-summary {
  color: #f7f3ea;
}
html.dark .log-detail-dialog .dlg-title-wrap::after {
  color: rgba(244, 238, 226, 0.58);
}
html.dark .log-detail-dialog .action-tag {
  border-color: rgba(var(--theme-primary-rgb), 0.28);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
}
html.dark .log-detail-dialog .dlg-meta-item {
  border-color: rgba(var(--theme-primary-rgb), 0.24);
  background:
    linear-gradient(145deg, rgba(255, 255, 255, 0.095), rgba(255, 255, 255, 0.028)),
    rgba(11, 16, 28, 0.72);
}
html.dark .log-detail-dialog .dlg-meta-item + .dlg-meta-item {
  border-left-color: rgba(var(--theme-primary-rgb), 0.24);
}
html.dark .log-detail-dialog .dlg-meta-label,
html.dark .log-detail-dialog .dlg-section-title,
html.dark .log-detail-dialog .dlg-ch-arrow {
  color: var(--theme-primary, #c5a47e);
}
html.dark .log-detail-dialog .dlg-meta-label::before {
  color: var(--theme-primary, #c5a47e);
  border: 0;
  background: transparent;
  box-shadow: none;
}
html.dark .log-detail-dialog .dlg-meta-value {
  color: #f3efe7;
}
html.dark .log-detail-dialog .dlg-section-count {
  color: #fff6df;
  background: linear-gradient(180deg, rgba(var(--theme-primary-rgb), 0.36), rgba(var(--theme-primary-rgb), 0.18));
  border-color: rgba(var(--theme-primary-rgb), 0.28);
}
html.dark .log-detail-dialog .dlg-changes {
  border-color: rgba(var(--theme-primary-rgb), 0.16);
  background:
    linear-gradient(145deg, rgba(255, 255, 255, 0.065), rgba(255, 255, 255, 0.018)),
    rgba(11, 16, 28, 0.62);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.055),
    inset 0 -18px 36px rgba(0, 0, 0, 0.12),
    0 12px 30px rgba(0, 0, 0, 0.22);
  backdrop-filter: blur(14px) saturate(120%);
  -webkit-backdrop-filter: blur(14px) saturate(120%);
}
html.dark .log-detail-dialog .dlg-change-head {
  color: rgba(244, 238, 226, 0.58);
  background:
    linear-gradient(180deg, rgba(18, 24, 38, 0.72), rgba(12, 17, 28, 0.54));
  border-bottom-color: rgba(var(--theme-primary-rgb), 0.1);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
html.dark .log-detail-dialog .dlg-change-row {
  border-bottom-color: rgba(255, 255, 255, 0.035);
}
html.dark .log-detail-dialog .dlg-change-row:nth-child(odd) {
  background: rgba(255, 255, 255, 0.022);
}
html.dark .log-detail-dialog .dlg-change-row:hover {
  background: rgba(var(--theme-primary-rgb), 0.045);
}
html.dark .log-detail-dialog .dlg-change-label {
  color: rgba(245, 238, 222, 0.84);
}
html.dark .log-detail-dialog .dlg-ch-before {
  color: #ff9e9e;
  background: rgba(196, 69, 69, 0.2);
}
html.dark .log-detail-dialog .dlg-ch-after {
  color: #6ee6a4;
  background: rgba(44, 149, 96, 0.25);
}
html.dark .log-detail-dialog .dlg-changes::-webkit-scrollbar-thumb {
  background: rgba(var(--theme-primary-rgb), 0.58);
}
html.dark .el-overlay:has(.log-detail-dialog) {
  background:
    radial-gradient(circle at 50% 38%, rgba(var(--theme-primary-rgb), 0.12), transparent 34%),
    rgba(0, 0, 0, 0.76);
}

@media (max-width: 760px) {
  .log-detail-dialog.el-dialog {
    max-height: calc(100vh - 20px);
  }
  .log-detail-dialog .el-dialog__header,
  .log-detail-dialog .el-dialog__body {
    padding-left: 22px;
    padding-right: 22px;
  }
  .log-detail-dialog .dlg-header {
    align-items: flex-start;
    gap: 16px;
  }
  .log-detail-dialog .dlg-summary {
    font-size: 18px;
  }
  .log-detail-dialog .dlg-body {
    max-height: calc(100vh - 174px);
  }
  .log-detail-dialog .dlg-meta-row {
    grid-template-columns: 1fr;
    gap: 10px;
    padding: 14px;
  }
  .log-detail-dialog .dlg-meta-item {
    align-items: flex-start;
    padding: 0;
  }
  .log-detail-dialog .dlg-meta-item + .dlg-meta-item {
    border-left: 0;
    border-top: 1px solid rgba(255, 255, 255, 0.07);
    padding-top: 10px;
  }
  .log-detail-dialog .dlg-change-row {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  .log-detail-dialog .dlg-changes {
    max-height: clamp(140px, calc(100vh - 360px), 360px);
    padding: 10px 14px;
  }
}
</style>

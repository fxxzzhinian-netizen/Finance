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
          <div class="ratio-icon-wrap">
            <img :src="imgLogTypeRatio" alt="" class="ratio-icon" />
          </div>
          <div class="ratio-main">
            <div class="ratio-title-row">
              <div>
                <div class="ratio-title">日志类型占比</div>
                <div class="ratio-sub">当前加载日志分布</div>
              </div>
              <span class="ratio-total">{{ typeRatioTotal }} 条日志</span>
            </div>
            <div class="ratio-bar" aria-hidden="true">
              <span
                v-for="stat in typeRatioStats"
                :key="stat.value"
                class="ratio-bar-segment"
                :style="{ width: `${stat.percent}%`, backgroundColor: stat.color }"
              ></span>
            </div>
          </div>
          <div class="ratio-legend">
            <div
              v-for="stat in typeRatioStats"
              :key="stat.value"
              class="ratio-legend-item"
            >
              <span class="ratio-dot" :style="{ backgroundColor: stat.color }"></span>
              <span class="ratio-name">{{ stat.label }}</span>
              <span class="ratio-percent">{{ stat.percent.toFixed(1) }}%</span>
            </div>
          </div>
        </section>

        <div
          v-for="group in grouped"
          :key="group.date"
          class="day-group"
        >
          <div class="day-label">
            <svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true">
              <path fill="currentColor" d="M7 2h2v2h6V2h2v2h3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2L2.01 6A2 2 0 0 1 4 4h3V2zm13 8H4v10h16V10zM4 8h16V6H4v2z"/>
            </svg>
            <span class="day-text">{{ group.label }}</span>
            <span class="day-count">{{ group.items.length }} 条日志</span>
            <span class="day-line"></span>
          </div>
          <div
            v-for="row in group.items"
            :key="row.id"
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
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next, jumper, total"
        background
        @current-change="reload(false)"
      />
    </div>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailOpen"
      :show-close="true"
      width="720px"
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
                <span class="dlg-ch-after">{{ c.after ?? '空' }}</span>
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
import { listLogs, markLogsRead } from '../api/logs'
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
import imgLogTypeRatio from '../img/log_type_ratio_icon.png'

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
  '#426da8',
  '#7f43b8',
  '#f0cf59',
  '#6f7f97',
  '#e6ddd0',
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
const typeRatioTotal = computed(() => items.value.length)
const typeRatioStats = computed(() => {
  const total = typeRatioTotal.value
  const counts = new Map()
  for (const row of items.value) {
    counts.set(row.action, (counts.get(row.action) || 0) + 1)
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
    .map(([value, count], index) => ({
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

const ACTION_LABEL_MAP = Object.fromEntries(
  actionOptions.filter((o) => o.value).map((o) => [o.value, o.label]),
)

function actionLabel(a) {
  return ACTION_LABEL_MAP[a] || a
}

// 每个动作配一个高识别度的语义化图标（双图层：底色块 + 角标）
const ACTION_ICON_MAP = {
  // 新增资产：纸箱 + 加号角标
  'asset.create':
    '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">' +
      '<path fill="currentColor" d="M21 8.5L12 4 3 8.5v7L12 20l9-4.5v-7zM12 6.18L18.18 9 12 12.06 5.82 9 12 6.18zM5 10.62l6 2.97v6.16l-6-3v-6.13zm14 6.13l-6 3v-6.16l6-2.97v6.13z"/>' +
      '<g transform="translate(15.5 14)">' +
        '<circle cx="4" cy="4" r="4.5" fill="#fff"/>' +
        '<path fill="#2c7a5e" d="M4 1.5v5M1.5 4h5" stroke="#2c7a5e" stroke-width="1.5" stroke-linecap="round"/>' +
      '</g>' +
    '</svg>',
  // 修改资产：纸箱 + 铅笔角标
  'asset.update':
    '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">' +
      '<path fill="currentColor" d="M21 8.5L12 4 3 8.5v7L12 20l9-4.5v-7zM12 6.18L18.18 9 12 12.06 5.82 9 12 6.18zM5 10.62l6 2.97v6.16l-6-3v-6.13zm14 6.13l-6 3v-6.16l6-2.97v6.13z"/>' +
      '<g transform="translate(13.5 12)">' +
        '<circle cx="5" cy="5" r="5.2" fill="#fff"/>' +
        '<path fill="#b08a52" d="M2.2 7l.55-1.65L6.4 1.7a.7.7 0 0 1 .98 0l.92.92a.7.7 0 0 1 0 .98L4.65 7.25 3 7.8a.4.4 0 0 1-.5-.5L2.2 7z"/>' +
      '</g>' +
    '</svg>',
  // 删除资产：纸箱 + 红色叉角标
  'asset.delete':
    '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">' +
      '<path fill="currentColor" d="M21 8.5L12 4 3 8.5v7L12 20l9-4.5v-7zM12 6.18L18.18 9 12 12.06 5.82 9 12 6.18zM5 10.62l6 2.97v6.16l-6-3v-6.13zm14 6.13l-6 3v-6.16l6-2.97v6.13z" opacity="0.55"/>' +
      '<g transform="translate(13.5 12)">' +
        '<circle cx="5" cy="5" r="5.2" fill="#fff"/>' +
        '<path stroke="#c44545" stroke-width="1.6" stroke-linecap="round" d="M3 3l4 4M7 3l-4 4"/>' +
      '</g>' +
    '</svg>',
  // 批量导入：纸箱 + 向下箭头角标（表示从外部一次导入很多）
  'asset.import':
    '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">' +
      '<path fill="currentColor" d="M21 8.5L12 4 3 8.5v7L12 20l9-4.5v-7zM12 6.18L18.18 9 12 12.06 5.82 9 12 6.18zM5 10.62l6 2.97v6.16l-6-3v-6.13zm14 6.13l-6 3v-6.16l6-2.97v6.13z" opacity="0.6"/>' +
      '<g transform="translate(13 11.5)">' +
        '<circle cx="5" cy="5" r="5.2" fill="#fff"/>' +
        '<path fill="none" stroke="#5a8dc5" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" d="M5 2v5M2.7 5L5 7.3 7.3 5M2.3 8.3h5.4"/>' +
      '</g>' +
    '</svg>',
  // 二维码刷新：二维码 + 旋转箭头
  'asset.qr.regen':
    '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">' +
      '<path fill="currentColor" d="M3 3h7v7H3V3zm2 2v3h3V5H5zm9-2h7v7h-7V3zm2 2v3h3V5h-3zM3 14h7v7H3v-7zm2 2v3h3v-3H5zm12.5-3.5l1.7 1.7A4 4 0 1 1 14 18v-1.6a2.4 2.4 0 1 0 4-1.8l-1.7 1.7-1.4-1.4 3-3 3 3-1.4 1.4z"/>' +
    '</svg>',
  // 上传附件：云朵向上箭头
  'file.upload':
    '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">' +
      '<path fill="currentColor" d="M19.35 10.04A7.49 7.49 0 0 0 12 4C9.11 4 6.6 5.64 5.35 8.04A5.994 5.994 0 0 0 0 14a6 6 0 0 0 6 6h13a5 5 0 0 0 .35-9.96zM14 13v4h-4v-4H7l5-5 5 5h-3z"/>' +
    '</svg>',
  // 删除附件：文件 + 红色叉
  'file.delete':
    '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">' +
      '<path fill="currentColor" d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6zm4 18H6V4h7v5h5v11z"/>' +
      '<path stroke="#c44545" stroke-width="1.8" stroke-linecap="round" fill="none" d="M9 13l5 5M14 13l-5 5"/>' +
    '</svg>',
  // 登录：门 + 向内箭头
  login:
    '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">' +
      '<path fill="currentColor" d="M11 7L9.6 8.4l2.6 2.6H2v2h10.2l-2.6 2.6L11 17l5-5-5-5z"/>' +
      '<path fill="currentColor" d="M14 3a2 2 0 0 1 2 2v3h-2V5h-2V3h2zm0 18h-2v-2h2v-3h2v3a2 2 0 0 1-2 2zm6-18a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4v-2h4V5h-4V3h4z" opacity="0.55"/>' +
    '</svg>',
  // 登出：门 + 向外箭头
  logout:
    '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">' +
      '<path fill="currentColor" d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5-5-5z"/>' +
      '<path fill="currentColor" d="M4 5h6V3H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h6v-2H4V5z" opacity="0.55"/>' +
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
    const data = await listLogs({
      page: page.value,
      page_size: pageSize.value,
      scope: scope.value,
      action: actionFilter.value || undefined,
      keyword: keyword.value || undefined,
    })
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
    page.value = 1
    await reload(false)
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
  display: flex;
  flex-direction: column;
  gap: 18px;
  max-width: 1280px;
  width: 100%;
  margin: 0 auto;
}
/* -------- 日志类型占比卡片：基础布局（主题无关） -------- */
.type-ratio-card {
  position: relative;
  display: grid;
  grid-template-columns: 78px minmax(0, 1fr) minmax(300px, 0.92fr);
  align-items: center;
  gap: 24px;
  padding: 18px 22px;
  overflow: hidden;
  border-radius: 14px;
}
.type-ratio-card::before {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
}
.ratio-icon-wrap,
.ratio-main,
.ratio-legend {
  position: relative;
  z-index: 1;
}
.ratio-icon-wrap {
  width: 64px;
  height: 64px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}
.ratio-icon {
  width: 54px;
  height: 54px;
  transform-origin: center;
  transform: scale(1.8);
  overflow: hidden;
  object-fit: contain;
  display: block;
}
.ratio-title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 14px;
}
.ratio-title {
  font-size: 15px;
  font-weight: 800;
  letter-spacing: 0.5px;
}
.ratio-sub,
.ratio-total {
  margin-top: 4px;
  font-size: 12px;
}
.ratio-total {
  flex-shrink: 0;
  font-weight: 600;
}
.ratio-bar {
  display: flex;
  width: 100%;
  height: 14px;
  overflow: hidden;
  border-radius: 999px;
}
.ratio-bar-segment {
  min-width: 4px;
  height: 100%;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.22),
    inset 0 -1px 0 rgba(0, 0, 0, 0.12);
}
.ratio-legend {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px 22px;
}
.ratio-legend-item {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  min-width: 0;
  font-size: 12px;
}
.ratio-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  box-shadow: 0 0 10px currentColor;
}
.ratio-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ratio-percent {
  font-family: 'SF Mono', Menlo, Consolas, monospace;
  font-size: 11.5px;
  font-weight: 600;
}

/* -------- 白天模式：参考系统主色（金棕色），与日志卡片风格一致 -------- */
.type-ratio-card {
  border: 1px solid rgba(var(--theme-primary-rgb), 0.28);
  background:
    radial-gradient(circle at 14% 12%, rgba(var(--theme-primary-rgb), 0.22), transparent 38%),
    linear-gradient(135deg, var(--theme-surface) 0%, var(--bg-card) 55%, var(--theme-surface-subtle) 100%);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.55),
    0 10px 28px rgba(var(--theme-primary-deep-rgb), 0.10);
}
.type-ratio-card::before {
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.32), transparent 38%),
    radial-gradient(circle at 100% 100%, rgba(var(--theme-primary-rgb), 0.20), transparent 38%);
  opacity: 0.75;
}
.ratio-icon-wrap {
  background:
    radial-gradient(circle at 32% 28%, rgba(255, 255, 255, 0.85) 0%, rgba(var(--theme-primary-rgb), 0.22) 70%);
  box-shadow:
    inset 0 0 16px rgba(var(--theme-primary-rgb), 0.20),
    inset 0 1px 0 rgba(255, 255, 255, 0.6),
    0 4px 12px rgba(var(--theme-primary-deep-rgb), 0.14);
}
.ratio-icon {
  filter: drop-shadow(0 1px 2px rgba(var(--theme-primary-deep-rgb), 0.25));
}
.ratio-title {
  color: var(--theme-primary-deep, #8a7355);
}
.ratio-sub {
  color: var(--theme-text-muted, #b9a78a);
}
.ratio-total {
  color: var(--theme-text-hover, #6e5a40);
}
.ratio-bar {
  background: rgba(var(--theme-primary-rgb), 0.14);
  box-shadow:
    inset 0 1px 2px rgba(var(--theme-primary-deep-rgb), 0.20),
    inset 0 -1px 0 rgba(255, 255, 255, 0.4);
}
.ratio-legend-item {
  color: var(--text-primary, #2f2f33);
}
.ratio-name {
  color: var(--theme-primary-deep, #8a7355);
}
.ratio-percent {
  color: var(--theme-primary-deep, #8a7355);
}

/* -------- 黑夜模式：保留原本的深色玻璃质感（已迁移到下方非 scoped 块） -------- */
.day-group {
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
.tag-asset-delete { background: #fde4e4; color: #c44545; }
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
  .type-ratio-card {
    grid-template-columns: 70px minmax(0, 1fr);
  }
  .ratio-legend {
    grid-column: 1 / -1;
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  .day-group {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 860px) {
  .type-ratio-card {
    grid-template-columns: 1fr;
  }
  .ratio-icon-wrap {
    display: none;
  }
  .ratio-legend {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .day-group {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 560px) {
  .day-group,
  .ratio-legend {
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
  display: flex;
  justify-content: flex-end;
  padding: 8px 4px 4px;
}
</style>

<!-- 弹窗内部样式：因 el-dialog 通过 teleport 渲染到 body，使用非 scoped -->
<style scoped>
html.dark .messages-page .type-ratio-card {
  border-color: rgba(255, 255, 255, 0.10);
  background:
    radial-gradient(120% 140% at 0% 50%, rgba(var(--theme-primary-rgb), 0.12) 0%, transparent 55%),
    radial-gradient(80% 120% at 100% 50%, rgba(110, 90, 220, 0.12) 0%, transparent 60%),
    linear-gradient(135deg, #1f2233 0%, #181a28 45%, #11131c 100%);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.06),
    0 16px 38px rgba(0, 0, 0, 0.5);
}
html.dark .messages-page .type-ratio-card::before {
  background:
    radial-gradient(circle at 0% 0%, rgba(255, 255, 255, 0.07), transparent 40%),
    radial-gradient(circle at 100% 100%, rgba(0, 0, 0, 0.35), transparent 50%);
  opacity: 1;
}
html.dark .messages-page .ratio-icon-wrap {
  background:
    radial-gradient(circle at 35% 30%, rgba(var(--theme-primary-rgb), 0.18) 0%, rgba(0, 0, 0, 0.55) 70%);
  box-shadow:
    inset 0 0 18px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.05),
    0 0 22px rgba(var(--theme-primary-rgb), 0.18);
}
html.dark .messages-page .ratio-icon {
  filter: drop-shadow(0 0 10px rgba(var(--theme-primary-rgb), 0.42));
}
html.dark .messages-page .ratio-title {
  color: #eef0f7;
}
html.dark .messages-page .ratio-sub {
  color: rgba(232, 234, 242, 0.58);
}
html.dark .messages-page .ratio-total {
  color: rgba(232, 234, 242, 0.78);
}
html.dark .messages-page .ratio-bar {
  background: rgba(0, 0, 0, 0.4);
  box-shadow:
    inset 0 1px 3px rgba(0, 0, 0, 0.55),
    inset 0 -1px 0 rgba(255, 255, 255, 0.04);
}
html.dark .messages-page .ratio-bar-segment {
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.18),
    inset 0 -1px 0 rgba(0, 0, 0, 0.18);
}
html.dark .messages-page .ratio-legend-item {
  color: rgba(232, 234, 242, 0.82);
}
html.dark .messages-page .ratio-name {
  color: #e0b974;
}
html.dark .messages-page .ratio-percent {
  color: #e0b974;
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
.log-detail-dialog .el-dialog {
  position: relative;
  display: flex;
  flex-direction: column;
  max-width: calc(100vw - 32px);
  max-height: calc(100vh - 36px);
  border-radius: 18px;
  overflow: hidden;
  background:
    radial-gradient(circle at 14% 12%, rgba(var(--theme-primary-rgb), 0.22), transparent 34%),
    radial-gradient(circle at 100% 100%, rgba(var(--theme-primary-rgb), 0.16), transparent 36%),
    linear-gradient(145deg, rgba(24, 28, 42, 0.78), rgba(7, 12, 24, 0.84));
  border: 1px solid rgba(var(--theme-primary-rgb), 0.64);
  box-shadow:
    inset 0 0 0 1px rgba(255, 255, 255, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.08),
    0 26px 70px rgba(0, 0, 0, 0.58),
    0 0 0 1px rgba(var(--theme-primary-rgb), 0.12),
    0 0 34px rgba(var(--theme-primary-rgb), 0.22);
  backdrop-filter: blur(22px) saturate(130%);
  -webkit-backdrop-filter: blur(22px) saturate(130%);
}
.log-detail-dialog .el-dialog::before {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  border-radius: inherit;
  background:
    linear-gradient(90deg, transparent 3%, rgba(247, 189, 85, 0.55) 50%, transparent 97%) top / 100% 1px no-repeat,
    linear-gradient(90deg, transparent 3%, rgba(247, 189, 85, 0.45) 50%, transparent 97%) bottom / 100% 1px no-repeat;
  opacity: 0.9;
}
.log-detail-dialog .el-dialog__header {
  flex-shrink: 0;
  padding: 24px 8px 24px;
  margin-right: 0;
  background: transparent;
  border-bottom: 0;
}
.log-detail-dialog .el-dialog__body {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  padding: 0 8px 24px;
}
.log-detail-dialog .el-dialog__headerbtn {
  top: 28px;
  right: 28px;
  width: 34px;
  height: 34px;
}
.log-detail-dialog .el-dialog__close {
  color: rgba(232, 234, 242, 0.78);
  font-size: 24px;
  transition: color 0.18s ease, transform 0.18s ease;
}
.log-detail-dialog .el-dialog__headerbtn:hover .el-dialog__close {
  color: #e7c382;
  transform: rotate(90deg);
}
.log-detail-dialog .dlg-header {
  display: flex;
  align-items: center;
  gap: 24px;
}
.log-detail-dialog .dlg-icon {
  flex-shrink: 0;
  width: 82px;
  height: 82px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 18px;
}
.log-detail-dialog .dlg-icon img {
  width: 76px;
  height: 76px;
  object-fit: contain;
  display: block;
  filter: drop-shadow(0 0 16px rgba(var(--theme-primary-rgb), 0.50));
}
.log-detail-dialog .dlg-title-wrap {
  flex: 1;
  min-width: 0;
}
.log-detail-dialog .dlg-title-line {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}
.log-detail-dialog .dlg-actor {
  font-size: 16px;
  font-weight: 500;
  color: #d7aa62;
}
.log-detail-dialog .action-tag {
  font-size: 15px;
  font-weight: 700;
  padding: 7px 14px;
  border-radius: 999px;
  letter-spacing: 0.5px;
  border: 1px solid rgba(94, 219, 151, 0.35);
  background: rgba(46, 160, 109, 0.24);
  color: #67d69a;
}
.log-detail-dialog .tag-asset-create { background: rgba(44, 122, 94, 0.28); color: #6fd49b; }
.log-detail-dialog .tag-asset-update { background: rgba(176, 138, 82, 0.28); color: #e0b974; }
.log-detail-dialog .tag-asset-delete { background: rgba(196, 69, 69, 0.28); color: #ff8a8a; }
.log-detail-dialog .tag-asset-qr-regen { background: rgba(79, 143, 216, 0.28); color: #7fb6ee; }
.log-detail-dialog .tag-file-upload { background: rgba(79, 143, 216, 0.28); color: #7fb6ee; }
.log-detail-dialog .tag-file-delete { background: rgba(196, 69, 69, 0.28); color: #ff8a8a; }
.log-detail-dialog .tag-login { background: rgba(155, 110, 200, 0.28); color: #c9a8e6; }
.log-detail-dialog .tag-logout { background: rgba(155, 110, 200, 0.28); color: #c9a8e6; }
.log-detail-dialog .dlg-summary {
  font-size: 23px;
  color: #e9edf7;
  line-height: 1.45;
  font-weight: 600;
  letter-spacing: 0.3px;
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
  gap: 0;
  padding: 14px 0;
  background: rgba(12, 18, 31, 0.58);
  border: 1px solid rgba(var(--theme-primary-rgb), 0.34);
  border-radius: 10px;
  margin-bottom: 28px;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.06),
    0 10px 28px rgba(0, 0, 0, 0.20);
}
.log-detail-dialog .dlg-meta-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  min-width: 0;
  padding: 0 22px;
  font-size: 14px;
}
.log-detail-dialog .dlg-meta-item + .dlg-meta-item {
  border-left: 1px solid rgba(255, 255, 255, 0.07);
}
.log-detail-dialog .dlg-meta-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #d7aa62;
  font-weight: 700;
  letter-spacing: 0.4px;
}
.log-detail-dialog .dlg-meta-label::before {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  color: #d7aa62;
  font-size: 14px;
}
.log-detail-dialog .dlg-meta-item:nth-child(1) .dlg-meta-label::before {
  content: '◷';
}
.log-detail-dialog .dlg-meta-item:nth-child(2) .dlg-meta-label::before {
  content: '◉';
}
.log-detail-dialog .dlg-meta-item:nth-child(3) .dlg-meta-label::before {
  content: '♙';
}
.log-detail-dialog .dlg-meta-value {
  max-width: 100%;
  overflow: hidden;
  color: #dfe4ef;
  text-overflow: ellipsis;
  white-space: nowrap;
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
  font-size: 17px;
  font-weight: 800;
  color: #d7aa62;
  margin-bottom: 14px;
  padding-bottom: 0;
  border-bottom: 0;
  width: 100%;
}
.log-detail-dialog .dlg-section-count {
  background: rgba(var(--theme-primary-rgb), 0.22);
  color: #e7c382;
  font-size: 12px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 999px;
  min-width: 18px;
  text-align: center;
}

.log-detail-dialog .dlg-changes {
  flex: 1;
  min-height: 120px;
  display: flex;
  flex-direction: column;
  gap: 0;
  max-height: clamp(140px, calc(100vh - 410px), 430px);
  overflow-y: auto;
  padding: 12px 24px;
  background: rgba(12, 18, 31, 0.52);
  border: 1px solid rgba(var(--theme-primary-rgb), 0.32);
  border-radius: 10px;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.05),
    0 12px 34px rgba(0, 0, 0, 0.24);
}
.log-detail-dialog .dlg-changes::-webkit-scrollbar {
  width: 7px;
}
.log-detail-dialog .dlg-changes::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.04);
  border-radius: 999px;
}
.log-detail-dialog .dlg-changes::-webkit-scrollbar-thumb {
  background: rgba(var(--theme-primary-rgb), 0.45);
  border-radius: 999px;
}
.log-detail-dialog .dlg-changes::-webkit-scrollbar-thumb:hover {
  background: rgba(var(--theme-primary-rgb), 0.66);
}
.log-detail-dialog .dlg-change-row {
  display: grid;
  grid-template-columns: 130px 1fr;
  align-items: center;
  gap: 24px;
  padding: 11px 4px;
  background: transparent;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 0;
}
.log-detail-dialog .dlg-change-row:last-child {
  border-bottom: 0;
}
.log-detail-dialog .dlg-change-row:hover {
  background: rgba(var(--theme-primary-rgb), 0.06);
}
.log-detail-dialog .dlg-change-label {
  font-size: 15px;
  color: #d7c29a;
  font-weight: 700;
}
.log-detail-dialog .dlg-change-flow {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  font-size: 14px;
}
.log-detail-dialog .dlg-ch-before {
  color: #f3a0a0;
  text-decoration: line-through;
  background: rgba(196, 69, 69, 0.22);
  padding: 5px 14px;
  border-radius: 5px;
  max-width: 240px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 700;
}
.log-detail-dialog .dlg-ch-after {
  color: #6fd49b;
  background: rgba(44, 122, 94, 0.24);
  padding: 5px 14px;
  border-radius: 5px;
  font-weight: 600;
  max-width: 280px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.log-detail-dialog .dlg-ch-arrow {
  color: #d7aa62;
  flex-shrink: 0;
}
.log-detail-dialog .dlg-empty {
  padding: 30px;
  text-align: center;
  color: rgba(232, 234, 242, 0.66);
  font-size: 14px;
  background: rgba(12, 18, 31, 0.52);
  border: 1px solid rgba(var(--theme-primary-rgb), 0.28);
  border-radius: 10px;
}

/* ===================== 日志详情弹窗 进入动效 ===================== */
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

/* 字段变更行：进入时上浮淡入 */
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

@media (max-width: 760px) {
  .log-detail-dialog .el-dialog {
    max-height: calc(100vh - 20px);
  }
  .log-detail-dialog .el-dialog__header,
  .log-detail-dialog .el-dialog__body{
    padding-left: 22px;
    padding-right: 22px;
  }
  .log-detail-dialog .dlg-header {
    align-items: flex-start;
    gap: 16px;
  }
  .log-detail-dialog .dlg-icon {
    width: 58px;
    height: 58px;
    border-radius: 14px;
  }
  .log-detail-dialog .dlg-icon img {
    width: 54px;
    height: 54px;
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
</style>

<!-- ============================================================
     从 main.css 迁移过来的 Messages 页面全局样式（暗色模式覆盖等）
     说明：scoped 样式无法用 html.dark .xxx 这种祖先选择器命中
     scoped hash 的元素，因此放在非 scoped 块中。
     ============================================================ -->
<style scoped>
/* ============================================================
   Messages 页面：dark 模式下根容器使用页面底色
   ============================================================ */
html.dark .messages-page {
  background: var(--bg-page) !important;
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
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.12),
    0 16px 38px rgba(0, 0, 0, 0.44),
    0 0 32px rgba(var(--theme-primary-rgb), 0.34) !important;
}
html.dark .messages-page .changes {
  background: var(--theme-surface-muted) !important;
  border-left-color: rgba(var(--theme-primary-rgb), 0.6) !important;
}
html.dark .messages-page .ch-before {
  color: #ff8a8a !important;
  background: rgba(245, 108, 108, 0.16) !important;
}
html.dark .messages-page .ch-after {
  color: #6fd49b !important;
  background: rgba(70, 167, 109, 0.18) !important;
}

/* action-tag：暗色下做反转，色块用半透明带主色，文字用更亮的同色 */
html.dark .messages-page .action-tag,
html.dark .log-detail-dialog .action-tag {
  background: rgba(var(--theme-primary-rgb), 0.18) !important;
  color: var(--theme-primary) !important;
}
html.dark .messages-page .tag-asset-create,
html.dark .log-detail-dialog .tag-asset-create {
  background: rgba(44, 122, 94, 0.22) !important;
  color: #6fd49b !important;
}
html.dark .messages-page .tag-asset-update,
html.dark .log-detail-dialog .tag-asset-update {
  background: rgba(176, 138, 82, 0.22) !important;
  color: #e0b974 !important;
}
html.dark .messages-page .tag-asset-delete,
html.dark .messages-page .tag-file-delete,
html.dark .log-detail-dialog .tag-asset-delete,
html.dark .log-detail-dialog .tag-file-delete {
  background: rgba(196, 69, 69, 0.22) !important;
  color: #ff8a8a !important;
}
html.dark .messages-page .tag-asset-qr-regen,
html.dark .messages-page .tag-file-upload,
html.dark .log-detail-dialog .tag-asset-qr-regen,
html.dark .log-detail-dialog .tag-file-upload {
  background: rgba(79, 143, 216, 0.22) !important;
  color: #7fb6ee !important;
}
html.dark .messages-page .tag-login,
html.dark .messages-page .tag-logout,
html.dark .log-detail-dialog .tag-login,
html.dark .log-detail-dialog .tag-logout {
  background: rgba(155, 110, 200, 0.22) !important;
  color: #c9a8e6 !important;
}

/* ============================================================
   日志详情弹窗 (.log-detail-dialog) 暗色覆盖
   弹窗 teleport 到 body，必须用非 scoped 全局规则
   ============================================================ */
html.dark .log-detail-dialog .el-dialog {
  background:
    radial-gradient(circle at 14% 12%, rgba(var(--theme-primary-rgb), 0.22), transparent 34%),
    radial-gradient(circle at 100% 100%, rgba(var(--theme-primary-rgb), 0.16), transparent 36%),
    linear-gradient(145deg, rgba(24, 28, 42, 0.78), rgba(7, 12, 24, 0.84)) !important;
  border-color: rgba(var(--theme-primary-rgb), 0.64) !important;
  box-shadow:
    inset 0 0 0 1px rgba(255, 255, 255, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.08),
    0 26px 70px rgba(0, 0, 0, 0.58),
    0 0 0 1px rgba(var(--theme-primary-rgb), 0.12),
    0 0 34px rgba(var(--theme-primary-rgb), 0.22) !important;
  backdrop-filter: blur(22px) saturate(130%) !important;
  -webkit-backdrop-filter: blur(22px) saturate(130%) !important;
}
html.dark .log-detail-dialog .el-dialog__header {
  background: transparent !important;
  border-bottom-color: transparent !important;
}
html.dark .log-detail-dialog .dlg-actor {
  color: #d7aa62 !important;
}
html.dark .log-detail-dialog .dlg-summary {
  color: #e9edf7 !important;
}
html.dark .log-detail-dialog .dlg-meta-label,
html.dark .log-detail-dialog .dlg-section-title,
html.dark .log-detail-dialog .dlg-ch-arrow {
  color: #d7aa62 !important;
}
html.dark .log-detail-dialog .dlg-meta-value {
  color: #dfe4ef !important;
}
html.dark .log-detail-dialog .dlg-meta-row,
html.dark .log-detail-dialog .dlg-empty {
  background: rgba(12, 18, 31, 0.58) !important;
  border-color: rgba(var(--theme-primary-rgb), 0.34) !important;
}
html.dark .log-detail-dialog .dlg-change-row {
  background: transparent !important;
}
html.dark .log-detail-dialog .dlg-change-row:hover {
  background: rgba(var(--theme-primary-rgb), 0.06) !important;
}
html.dark .log-detail-dialog .dlg-ch-before {
  color: #f3a0a0 !important;
  background: rgba(196, 69, 69, 0.22) !important;
}
html.dark .log-detail-dialog .dlg-ch-after {
  color: #6fd49b !important;
  background: rgba(44, 122, 94, 0.24) !important;
}
html.dark .log-detail-dialog .meta,
html.dark .log-detail-dialog .json {
  background: var(--theme-surface) !important;
  color: var(--text-primary) !important;
}
</style>

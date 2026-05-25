<template>
  <div class="supplies-page">
    <div class="filter-bar">
      <form class="filter-row" @submit.prevent="onSearch" autocomplete="off">
        <div class="actions-left">
          <el-tooltip content="新增物资记录" placement="top">
            <button
              type="button"
              class="svg-icon-btn add-btn"
              aria-label="新增物资记录"
              @click="openCreate"
            >
              <svg viewBox="0 0 1024 1024" width="22" height="22" aria-hidden="true">
                <path d="M469.332942 469.332942V298.751751a42.623964 42.623964 0 1 1 85.333262 0V469.332942h170.581192a42.623964 42.623964 0 1 1 0 85.333262H554.666204v170.581192a42.623964 42.623964 0 1 1-85.333262 0V554.666204H298.751751a42.623964 42.623964 0 1 1 0-85.333262H469.332942z m477.866269 312.533073a42.666631 42.666631 0 0 1-72.533273-45.055962A424.959646 424.959646 0 0 0 938.665884 511.999573c0-235.647804-191.018507-426.666311-426.666311-426.666311S85.333262 276.35177 85.333262 511.999573s191.018507 426.666311 426.666311 426.666311a424.447646 424.447646 0 0 0 225.578479-64.426613 42.666631 42.666631 0 0 1 45.183962 72.405273A509.780909 509.780909 0 0 1 511.999573 1023.999147C229.247809 1023.999147 0 794.751338 0 511.999573S229.247809 0 511.999573 0s511.999573 229.247809 511.999574 511.999573a510.719574 510.719574 0 0 1-76.799936 269.866442z"/>
              </svg>
            </button>
          </el-tooltip>

          <el-tooltip content="待开放" placement="top">
            <button
              type="button"
              class="svg-icon-btn import-btn log-btn"
              aria-label="待开放"
              @click="showComingSoon"
            >
              <svg viewBox="0 0 1024 1024" width="22" height="22" aria-hidden="true">
                <path d="M928 257c24.3 0 44 19.7 44 44v633c0 24.3-19.7 44-44 44H96c-24.3 0-44-19.7-44-44V301c0-24.3 19.7-44 44-44h832zM767 668H257c-41.421 0-75 33.579-75 75 0 41.007 32.91 74.328 73.76 74.99l1.24 0.01h510c41.421 0 75-33.579 75-75s-33.579-75-75-75z m0-250H467c-41.421 0-75 33.579-75 75 0 41.007 32.91 74.328 73.76 74.99l1.24 0.01h300c41.421 0 75-33.579 75-75s-33.579-75-75-75zM928 47c24.3 0 44 19.7 44 44v62c0 24.3-19.7 44-44 44H96c-24.3 0-44-19.7-44-44V91c0-24.3 19.7-44 44-44h832z"/>
              </svg>
            </button>
          </el-tooltip>
        </div>

        <div class="actions-right">
          <div class="form-control ai-search-control" :class="{ 'is-filled': !!query.keyword }">
            <input
              v-model.trim="query.keyword"
              type="text"
              required
              placeholder=""
              @keyup.enter="onSearch"
            />
            <label aria-hidden="true">
              <span
                v-for="(ch, i) in keywordLabel"
                :key="i"
                :style="{ transitionDelay: `${i * 50}ms` }"
              >{{ ch }}</span>
            </label>
          </div>

          <el-tooltip content="查询" placement="top">
            <button type="button" class="svg-icon-btn search-btn" aria-label="查询" @click="onSearch">
              <svg viewBox="0 0 1024 1024" width="21" height="21" aria-hidden="true">
                <path d="M469.333333 0c259.2 0 469.333333 210.133333 469.333334 469.333333 0 114.218667-40.832 218.922667-108.629334 300.330667l161.664 161.706667a42.666667 42.666667 0 1 1-60.373333 60.330666l-161.706667-161.706666A467.413333 467.413333 0 0 1 469.333333 938.666667c-259.2 0-469.333333-210.133333-469.333333-469.333334s210.133333-469.333333 469.333333-469.333333z m0 85.333333a384 384 0 1 0 0 768 384 384 0 0 0 0-768z"/>
                <path d="M469.333333 170.666667c102.528 0 195.669333 57.088 250.026667 148.906666a42.666667 42.666667 0 1 1-73.386667 43.52c-39.552-66.773333-105.344-107.093333-176.64-107.093333a42.666667 42.666667 0 0 1 0-85.333333z"/>
                <path d="M725.333333 469.333333m-42.666666 0a42.666667 42.666667 0 1 0 85.333333 0 42.666667 42.666667 0 1 0-85.333333 0Z"/>
              </svg>
            </button>
          </el-tooltip>

          <el-tooltip content="重置" placement="top">
            <button type="button" class="svg-icon-btn reset-btn" aria-label="重置" @click="onReset">
              <svg viewBox="0 0 1024 1024" width="24" height="24" aria-hidden="true">
                <path d="M377.856 856.576l-19.456 71.68c23.04 8.704 46.08 14.848 70.656 19.456l20.992-71.68c-25.088-4.096-49.152-10.752-72.192-19.456z m318.976-714.752V363.52h74.24v-115.712c68.096 67.072 111.104 160.256 111.104 263.68 0 204.8-165.376 370.176-370.176 370.176V955.904c244.736 0 443.904-199.168 443.904-443.904 0-113.664-43.52-217.6-114.688-295.936h77.312V141.824H696.832z m-101.376-65.536l-20.992 71.68c24.576 4.096 48.64 10.752 71.68 19.456l19.456-71.68c-23.04-8.704-46.08-14.848-70.144-19.456z m-83.456-8.192c-244.736 0-443.904 199.168-443.904 443.904 0 113.664 43.008 217.6 113.152 295.936h-76.288v74.24H326.656V660.48h-74.24v115.712c-68.096-67.072-111.104-160.256-111.104-263.68 0-204.8 165.376-370.176 370.176-370.176v-74.24z"/>
              </svg>
            </button>
          </el-tooltip>
        </div>
      </form>
    </div>

    <el-card shadow="never" class="table-card">
      <div class="table-band">
        <el-table
          :data="list"
          v-loading="loading"
          size="small"
          class="gold-table"
          :header-cell-class-name="() => 'gold-header-cell'"
        >
          <el-table-column prop="serial_number" label="序列号" width="220" fixed="left" show-overflow-tooltip />
          <el-table-column prop="receiver" label="领取人" width="180" />
          <el-table-column prop="item_name" label="物品名称" min-width="260" show-overflow-tooltip />
          <el-table-column prop="quantity" label="数量" width="140" align="center" />
          <el-table-column label="记录时间" width="190">
            <template #default="{ row }">{{ fmtFullTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right" align="center">
            <template #default="{ row }">
              <div class="row-actions">
                <el-tooltip content="编辑" placement="top">
                  <button type="button" class="svg-icon-btn edit" aria-label="编辑" @click="openEdit(row)">
                    <svg viewBox="0 0 1024 1024" width="18" height="18" aria-hidden="true">
                      <path d="M882.553 207.403l-66.652-66.652L894.352 62.3s67.244-1.399 67.244 65.845l-79.043 79.258z m-727.882 34.214v627.609H782.28V443.348l89.658-89.658v515.536c0 49.518-40.14 89.658-89.658 89.658H154.671c-49.518 0-89.658-40.14-89.658-89.658V241.617c0-49.518 40.14-89.658 89.658-89.658h515.536l-89.658 89.658H154.671zM378.817 645.08v-67.244l33.622-33.622 67.199 67.199-33.578 33.667h-67.243z m458.965-392.789L502.021 588.967 434.853 521.8l336.219-336.219 66.71 66.71z"/>
                    </svg>
                  </button>
                </el-tooltip>
                <el-tooltip content="二维码" placement="top">
                  <button type="button" class="svg-icon-btn qr" aria-label="二维码" @click="openQr(row)">
                    <svg viewBox="0 0 1024 1024" width="28" height="28" aria-hidden="true">
                      <path d="M597.333333 597.333333h85.333334v-85.333333h85.333333v128h-85.333333v42.666667h-85.333334v-42.666667h-85.333333v-128h85.333333v85.333333z m-384-85.333333h256v256H213.333333v-256z m85.333334 85.333333v85.333334h85.333333v-85.333334H298.666667zM213.333333 213.333333h256v256H213.333333V213.333333z m85.333334 85.333334v85.333333h85.333333V298.666667H298.666667z m213.333333-85.333334h256v256h-256V213.333333z m85.333333 85.333334v85.333333h85.333334V298.666667h-85.333334z m85.333334 384h85.333333v85.333333h-85.333333v-85.333333z m-170.666667 0h85.333333v85.333333h-85.333333v-85.333333z"/>
                    </svg>
                  </button>
                </el-tooltip>
                <el-popconfirm
                  title="确定删除该物资记录？"
                  :icon="null"
                  :hide-icon="true"
                  popper-class="confirm-inline-popconfirm"
                  @confirm="onDelete(row)"
                >
                  <template #reference>
                    <button type="button" class="svg-icon-btn del del-color" aria-label="删除">
                      <svg viewBox="0 0 1024 1024" width="20" height="20" aria-hidden="true">
                        <path d="M862.6176 172.1344H633.856c-4.4032-58.7776-53.4528-105.1136-113.3568-105.1136h-16.9984c-59.904 0-108.9536 46.336-113.3568 105.1136H161.3824c-20.0704 0-36.3008 16.2816-36.3008 36.3008s16.2816 36.3008 36.3008 36.3008h701.2352a36.3008 36.3008 0 0 0 0-72.6016zM686.6944 950.3744H337.3056c-98.2528 0-177.92-79.6672-177.92-177.92V316.3136c0-14.9504 12.1344-27.0848 27.0848-27.0848h651.0592c14.9504 0 27.0848 12.1344 27.0848 27.0848v456.1408c0 98.2528-79.616 177.92-177.92 177.92z" fill="#F7264E"/>
                        <path d="M678.6048 917.3504h-346.112c-83.3024 0-150.8352-67.5328-150.8352-150.8352V329.3184c0-10.5984 8.6016-19.2 19.2-19.2h609.3312c10.5984 0 19.2 8.6016 19.2 19.2v437.1968c0.0512 83.3024-67.4816 150.8352-150.784 150.8352z" fill="#F92B5C"/>
                        <path d="M642.0992 882.8416H350.8224c-83.3024 0-150.8352-67.5328-150.8352-150.8352V344.9856c0-9.9328 8.0896-18.0224 18.0224-18.0224h556.9024c9.9328 0 18.0224 8.0896 18.0224 18.0224v386.9696c0 83.3536-67.5328 150.8864-150.8352 150.8864z" fill="#FC4C66"/>
                        <path d="M336.9984 800.3072c-25.856 0-46.848-20.992-46.848-46.848v-166.3488c0-25.856 20.992-46.848 46.848-46.848 25.856 0 46.848 20.992 46.848 46.848v166.3488c0 25.856-20.992 46.848-46.848 46.848zM684.6976 800.3072c-25.856 0-46.848-20.992-46.848-46.848v-166.3488c0-25.856 20.992-46.848 46.848-46.848 25.856 0 46.848 20.992 46.848 46.848v166.3488c0 25.856-20.992 46.848-46.848 46.848zM510.8224 800.3072c-25.856 0-46.848-20.992-46.848-46.848v-273.408c0-25.856 20.992-46.848 46.848-46.848 25.856 0 46.848 20.992 46.848 46.848v273.408c0 25.856-20.9408 46.848-46.848 46.848z" fill="var(--theme-surface-muted, #f9f1e8)"/>
                        <path d="M336.9984 786.2272a32.768 32.768 0 0 1-32.768-32.768v-166.3488a32.768 32.768 0 1 1 65.536 0v166.3488a32.768 32.768 0 0 1-32.768 32.768zM684.6976 786.2272a32.768 32.768 0 0 1-32.768-32.768v-166.3488a32.768 32.768 0 1 1 65.536 0v166.3488c0 18.0736-14.6944 32.768-32.768 32.768zM510.8224 786.2272a32.768 32.768 0 0 1-32.768-32.768v-273.408a32.768 32.768 0 1 1 65.536 0v273.408c0.0512 18.0736-14.6432 32.768-32.768 32.768z" fill="#FFFFFF"/>
                      </svg>
                    </button>
                  </template>
                </el-popconfirm>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <el-pagination
        style="margin-top: 12px; justify-content: flex-end; display: flex"
        background
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :page-sizes="[10, 20, 50, 100]"
        @current-change="loadList"
        @size-change="loadList"
      />
    </el-card>

    <SupplyQrDialog v-model="qrVisible" :record="qrRecord" />

    <el-dialog
      v-model="dialogVisible"
      :title="editing ? '编辑物资记录' : '新增物资记录'"
      width="520px"
      align-center
      destroy-on-close
      class="supply-edit-dialog"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="序列号">
          <el-input
            v-model="form.serial_number"
            :placeholder="serialPreviewLoading ? '生成中...' : '系统自动生成'"
            disabled
          />
        </el-form-item>
        <el-form-item label="领取人" prop="receiver">
          <el-input v-model.trim="form.receiver" maxlength="64" />
        </el-form-item>
        <el-form-item label="物品名称" prop="item_name">
          <el-input v-model.trim="form.item_name" maxlength="128" />
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number v-model="form.quantity" :min="1" :max="999999" controls-position="right" />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="onSubmit">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessageBox } from 'element-plus'
import {
  createSupply,
  deleteSupply,
  listSupplies,
  previewNextSupplySerial,
  updateSupply,
} from '../api/supplies'
import SupplyQrDialog from '../components/SupplyQrDialog.vue'
import { toast } from '../utils/toast'

const keywordLabel = computed(() => Array.from('AI Search'))
const loading = ref(false)
const list = ref([])
const total = ref(0)
const dialogVisible = ref(false)
const editing = ref(null)
const saving = ref(false)
const formRef = ref(null)
const serialPreviewLoading = ref(false)
const qrVisible = ref(false)
const qrRecord = ref(null)

const query = reactive({
  page: 1,
  page_size: 10,
  keyword: '',
})

const form = reactive({
  serial_number: '',
  receiver: '',
  item_name: '',
  quantity: 1,
})

const rules = {
  receiver: [{ required: true, message: '请输入领取人', trigger: 'blur' }],
  item_name: [{ required: true, message: '请输入物品名称', trigger: 'blur' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'change' }],
}

function resetForm(row = null) {
  Object.assign(form, {
    receiver: row?.receiver || '',
    item_name: row?.item_name || '',
    quantity: row?.quantity || 1,
    serial_number: row?.serial_number || '',
  })
}

async function loadList() {
  loading.value = true
  try {
    const params = { ...query }
    Object.keys(params).forEach((key) => {
      if (params[key] === '' || params[key] == null) delete params[key]
    })
    const res = await listSupplies(params)
    list.value = res.items || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

function showComingSoon() {
  ElMessageBox.alert('待开放', '提示', {
    confirmButtonText: '确定',
  }).catch(() => {})
}

async function loadNextSerial() {
  serialPreviewLoading.value = true
  try {
    const res = await previewNextSupplySerial()
    form.serial_number = res.serial_number || ''
  } catch {
    form.serial_number = '保存后生成'
  } finally {
    serialPreviewLoading.value = false
  }
}

function openQr(row) {
  qrRecord.value = row
  qrVisible.value = true
}

function onSearch() {
  query.page = 1
  loadList()
}

function onReset() {
  query.keyword = ''
  query.page = 1
  loadList()
}

function openCreate() {
  editing.value = null
  resetForm()
  dialogVisible.value = true
  loadNextSerial()
}

function openEdit(row) {
  editing.value = row
  resetForm(row)
  dialogVisible.value = true
}

async function onSubmit() {
  await formRef.value?.validate()
  saving.value = true
  try {
    const payload = {
      receiver: form.receiver,
      item_name: form.item_name,
      quantity: Number(form.quantity || 1),
    }
    if (editing.value) {
      await updateSupply(editing.value.id, payload)
      toast.success('物资记录已更新')
    } else {
      await createSupply(payload)
      toast.success('物资记录已新增')
    }
    dialogVisible.value = false
    await loadList()
  } finally {
    saving.value = false
  }
}

async function onDelete(row) {
  await deleteSupply(row.id)
  toast.success('物资记录已删除')
  await loadList()
}

function fmtFullTime(value) {
  if (!value) return '—'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return '—'
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

onMounted(() => {
  loadList()
})
</script>

<style scoped>
.supplies-page {
  display: flex;
  flex-direction: column;
  gap: 0;
  min-height: calc(100% + 40px);
  margin: -20px -24px;
  padding: 20px 24px;
  background: var(--bg-card, #ffffff);
  font-family: 'HarmonyOS Sans SC', 'Noto Sans SC', 'PingFang SC',
    'Microsoft YaHei UI', 'Microsoft YaHei', -apple-system,
    BlinkMacSystemFont, 'Helvetica Neue', sans-serif;
  letter-spacing: 0.3px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  animation: page-fade-in 0.45s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.filter-bar {
  display: flex;
  margin: -12px 0 8px;
  padding: 0;
  background: transparent;
  animation: section-rise 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
  animation-delay: 0.06s;
}

.filter-row {
  display: flex;
  width: 100%;
  justify-content: space-between;
  align-items: flex-end;
  gap: 14px;
  padding: 0 6px;
}

.actions-left,
.actions-right {
  display: inline-flex;
  align-items: flex-end;
  gap: 14px;
}

.actions-left {
  margin-left: 12px;
}

.actions-left .svg-icon-btn {
  transform: translateY(2px);
}

.actions-left .svg-icon-btn,
.actions-right .svg-icon-btn {
  padding-bottom: 6px;
}

.form-control {
  position: relative;
  margin: 0;
  width: 200px;
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

.table-card {
  --asset-table-band-y: 16px;
  margin-top: 0;
  background: transparent;
  border: none;
  border-radius: 0 !important;
  box-shadow: none;
  isolation: isolate;
  overflow: visible !important;
  position: relative;
  animation: section-rise 0.55s cubic-bezier(0.22, 1, 0.36, 1) both;
  animation-delay: 0.16s;
}

.table-band {
  position: relative;
  isolation: isolate;
}

.table-band::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 0;
  background: var(--bg-page, #fafaf8);
  pointer-events: none;
}

.table-band :deep(.gold-table) {
  position: relative;
  z-index: 1;
}

.table-card :deep(.el-card__body) {
  padding: var(--asset-table-band-y) 18px !important;
  background: transparent;
}

.gold-table {
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid var(--theme-border, #ecdfc9);
  border-left: 0;
  border-right: 0;
}

.gold-table :deep(.gold-header-cell),
.gold-table :deep(.el-table__fixed-header-wrapper th.gold-header-cell),
.gold-table :deep(.el-table__fixed-right .gold-header-cell),
.gold-table :deep(.el-table__fixed .gold-header-cell) {
  background-color: #ffffff !important;
  color: var(--theme-primary-deep, #8a7355) !important;
  font-weight: 600;
  font-size: 16px;
  letter-spacing: 1.3px;
  height: 60px;
  border-bottom: 2px solid var(--theme-primary-light-3, #d4b89a) !important;
  border-right: none !important;
}

.gold-table :deep(.gold-header-cell .cell) {
  color: var(--theme-primary-deep, #8a7355) !important;
  font-size: 17px;
  letter-spacing: 1.5px;
  font-weight: 700;
}

.gold-table :deep(.el-table__header-wrapper thead tr) {
  background-color: #ffffff !important;
}

.gold-table :deep(.el-table__row td) {
  background-color: #ffffff !important;
  border-bottom: 1px solid var(--theme-table-line, #f3ece0) !important;
  border-right: none !important;
  padding: 14px 0 !important;
  font-size: 13.5px;
}

.gold-table :deep(.el-table__body tr:hover > td.el-table__cell) {
  background-color: var(--theme-surface, #faf4e9) !important;
}

.row-actions {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

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

.svg-icon-btn.edit svg {
  fill: var(--theme-primary-deep, #8a7355);
}

.svg-icon-btn.edit:hover svg {
  fill: var(--theme-text-hover, #6e5a40);
}

.svg-icon-btn.qr svg {
  fill: #333;
}

.svg-icon-btn.qr:hover svg {
  fill: #000;
}

.svg-icon-btn.qr {
  transform: translateY(1px);
}

html.dark .svg-icon-btn.qr svg {
  fill: #ffffff;
}

html.dark .svg-icon-btn.qr:hover svg {
  fill: #f0f0f0;
}

.svg-icon-btn.del svg {
  fill: initial;
}

.svg-icon-btn.del:hover svg {
  filter: brightness(1.05) saturate(1.1);
}

.svg-icon-btn.search-btn,
.svg-icon-btn.reset-btn,
.svg-icon-btn.add-btn,
.svg-icon-btn.import-btn {
  padding: 6px;
}

.svg-icon-btn.search-btn svg,
.svg-icon-btn.reset-btn svg,
.svg-icon-btn.add-btn svg,
.svg-icon-btn.import-btn svg {
  fill: var(--theme-primary-deep, #8a7355);
}

.svg-icon-btn.search-btn:hover svg,
.svg-icon-btn.reset-btn:hover svg,
.svg-icon-btn.add-btn:hover svg,
.svg-icon-btn.import-btn:hover svg {
  fill: var(--theme-text-hover, #6e5a40);
}

.svg-icon-btn.import-btn svg {
  transform: translateY(-1px);
  transition: transform 0.38s cubic-bezier(0.34, 1.56, 0.64, 1);
  animation: import-btn-breath 3.6s ease-in-out infinite;
  will-change: transform;
}

.svg-icon-btn.import-btn:hover svg {
  transform: translateY(-1px) scale(1.18) translateX(2px);
  animation: none;
}

.svg-icon-btn.import-btn:active svg {
  transform: translateY(-1px) scale(0.92);
  transition-duration: 0.1s;
  animation: none;
}

.svg-icon-btn.reset-btn svg {
  transition: transform 0.45s cubic-bezier(0.22, 1, 0.36, 1);
}

.svg-icon-btn.reset-btn:hover svg {
  transform: rotate(-180deg);
}

.svg-icon-btn.add-btn svg {
  transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.svg-icon-btn.add-btn:hover svg {
  transform: rotate(90deg);
}

.svg-icon-btn.search-btn:hover svg {
  animation: search-bounce 0.5s ease;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.supply-edit-dialog .el-dialog) {
  border-radius: 10px;
}

@keyframes page-fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes section-rise {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes import-btn-breath {
  0%, 100% { transform: translateY(-1px) translateX(0); }
  50% { transform: translateY(-1px) translateX(1.5px); }
}

@keyframes search-bounce {
  0%, 100% { transform: translateY(0); }
  40% { transform: translateY(-3px) scale(1.05); }
  70% { transform: translateY(0) scale(0.98); }
}

@media (max-width: 720px) {
  .filter-row,
  .actions-right {
    align-items: stretch;
    flex-direction: column;
  }

  .actions-left {
    align-self: flex-start;
  }

  .form-control {
    width: 100%;
  }

}
</style>

<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
const enabled = ref(true)
const extra = ref(1)
const saved = ref(false)
const error = ref('')

onMounted(async () => {
  const s = await getJSON('/api/settings')
  enabled.value = !!s.damp_rule_enabled
  extra.value = s.damp_extra_rolls
})
async function save() {
  saved.value = false; error.value = ''
  try {
    const r = await postJSON('/api/settings', {
      damp_rule_enabled: enabled.value,
      damp_extra_rolls: Number(extra.value),
    })
    enabled.value = r.damp_rule_enabled
    extra.value = r.damp_extra_rolls
    saved.value = true
  } catch (e) { error.value = String(e.message || e) }
}
</script>
<template><div class="page"><h1>设置</h1>
  <div class="card">
    <h2>潮湿空间加损规则</h2>
    <label class="row"><input type="checkbox" v-model="enabled"> 启用潮湿加卷（潮湿墙面订货时在基础卷数上另加固定卷数）</label>
    <label class="row">加卷枚数：
      <input type="number" min="0" step="1" v-model.number="extra" :disabled="!enabled"> 卷
    </label>
    <div class="row"><button @click="save">保存设置</button></div>
    <p v-if="saved" class="ok">已保存。停用规则后，新测算回到基础卷数；历史记录保持写入时的订货卷数不变。</p>
    <p v-if="error" class="warn">{{ error }}</p>
  </div>
</div></template>

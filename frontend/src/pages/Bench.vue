<script setup>
import { computed, onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
import DropStripBar from '../components/DropStripBar.vue'
const walls = ref([]); const rolls = ref([]); const wallId = ref(1); const rollId = ref(1); const out = ref(null)
onMounted(async () => {
  walls.value = (await getJSON('/api/walls')).items.filter(w => w.data_quality==='clean')
  rolls.value = (await getJSON('/api/rolls')).items.filter(r => r.data_quality==='clean')
  if (walls.value.length) wallId.value = walls.value[0].id
  if (rolls.value.length) rollId.value = rolls.value[0].id
})
const selectedWall = computed(() => walls.value.find(w => w.id === wallId.value))
async function run(save) {
  out.value = save ? await postJSON('/api/estimate', { wall_id: wallId.value, roll_id: rollId.value, save: true }) : await getJSON(`/api/estimate?wall_id=${wallId.value}&roll_id=${rollId.value}`)
}
</script>
<template>
  <div class="page"><h1>算卷工作台</h1>
  <select v-model.number="wallId"><option v-for="w in walls" :key="w.id" :value="w.id">{{ w.name }}</option></select>
  <span :class="['tag', selectedWall?.space_type === 'damp' ? 'tag-damp' : 'tag-normal']">
    {{ selectedWall?.space_type === 'damp' ? '潮湿' : '普通' }}
  </span>
  <select v-model.number="rollId"><option v-for="r in rolls" :key="r.id" :value="r.id">{{ r.name }}</option></select>
  <button @click="run(false)">试算</button><button @click="run(true)">保存</button>
  <table v-if="out" class="kv">
    <tr><th>墙面类型</th><td>{{ out.space_type === 'damp' ? '潮湿' : '普通' }}</td></tr>
    <tr><th>条带</th><td>{{ out.drops }} 条 · 每条 {{ out.drop_len_m }}m</td></tr>
    <tr><th>基础卷数</th><td>{{ out.rolls }} 卷</td></tr>
    <tr><th>订货卷数</th><td><strong>{{ out.order_rolls }} 卷</strong>
      <span v-if="out.damp_rule_applied" class="damp-note">（潮湿加损 +{{ out.damp_extra_rolls }}）</span>
    </td></tr>
  </table>
  <div v-if="out"><DropStripBar :drops="out.drops" :drop-len="out.drop_len_m" :rolls="out.rolls" /></div>
  </div>
</template>

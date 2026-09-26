<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, patchJSON } from '../api'
const props = defineProps({ id: String })
const wall = ref(null)
const runs = ref([])
const error = ref('')
async function load() {
  wall.value = await getJSON(`/api/walls/${props.id}`)
  runs.value = (await getJSON(`/api/runs?wall_id=${props.id}`)).items
}
onMounted(load)
async function setType(space_type) {
  error.value = ''
  try {
    wall.value = await patchJSON(`/api/walls/${props.id}/space-type`, { space_type })
  } catch (e) { error.value = String(e.message || e) }
}
</script>
<template>
  <div class="page" v-if="wall"><h1>{{ wall.name }}</h1>
  <p v-if="wall.data_quality==='dirty'" class="warn">{{ wall.note }}</p>
  <p>周长 {{ wall.perimeter }} m，墙高 {{ wall.height }} m</p>
  <p>墙面类型：
    <span :class="['tag', wall.space_type === 'damp' ? 'tag-damp' : 'tag-normal']">
      {{ wall.space_type === 'damp' ? '潮湿' : '普通' }}
    </span>
  </p>
  <p>
    <button :disabled="wall.space_type === 'normal'" @click="setType('normal')">标为普通</button>
    <button :disabled="wall.space_type === 'damp'" @click="setType('damp')">标为潮湿</button>
    <span v-if="error" class="warn">{{ error }}</span>
  </p>

  <h2>本墙测算记录</h2>
  <p v-if="!runs.length" class="muted">暂无记录，可到算卷工作台试算并保存。</p>
  <table v-else class="kv">
    <tr><th>时间</th><th>类型</th><th>基础卷数</th><th>订货卷数</th></tr>
    <tr v-for="r in runs" :key="r.id">
      <td>{{ r.created_at?.replace('T', ' ').slice(0, 16) }}</td>
      <td><span :class="['tag', r.result?.space_type === 'damp' ? 'tag-damp' : 'tag-normal']">
        {{ r.result?.space_type === 'damp' ? '潮湿' : '普通' }}
      </span></td>
      <td>{{ r.result?.rolls }}</td>
      <td><strong>{{ r.result?.order_rolls ?? r.result?.rolls }}</strong>
        <span v-if="r.result?.damp_rule_applied" class="damp-note">（+{{ r.result?.damp_extra_rolls }}）</span></td>
    </tr>
  </table>
  </div>
</template>

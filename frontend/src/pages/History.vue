<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
onMounted(async () => { items.value = (await getJSON('/api/runs')).items })
</script>
<template>
  <div class="page"><h1>记录</h1>
  <table class="kv">
    <tr><th>墙面</th><th>类型</th><th>基础卷数</th><th>订货卷数</th></tr>
    <tr v-for="r in items" :key="r.id">
      <td>{{ r.wall_name }}</td>
      <td><span :class="['tag', r.result?.space_type === 'damp' ? 'tag-damp' : 'tag-normal']">
        {{ r.result?.space_type === 'damp' ? '潮湿' : '普通' }}
      </span></td>
      <td>{{ r.result?.rolls }}</td>
      <td><strong>{{ r.result?.order_rolls ?? r.result?.rolls }}</strong>
        <span v-if="r.result?.damp_rule_applied" class="damp-note">（潮湿 +{{ r.result?.damp_extra_rolls }}）</span></td>
    </tr>
  </table>
  <p class="muted">类型、基础卷数与订货卷数均为写入时快照，不随后续设置变更。</p>
  </div>
</template>

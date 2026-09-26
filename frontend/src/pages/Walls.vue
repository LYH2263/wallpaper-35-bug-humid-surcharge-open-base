<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
onMounted(async () => { items.value = (await getJSON('/api/walls')).items })
</script>
<template>
  <div class="page"><h1>墙面列表</h1>
  <table class="kv">
    <tr><th>名称</th><th>周长</th><th>类型</th><th></th></tr>
    <tr v-for="w in items" :key="w.id">
      <td>{{ w.name }}</td><td>{{ w.perimeter }}m</td>
      <td><span :class="['tag', w.space_type === 'damp' ? 'tag-damp' : 'tag-normal']">
        {{ w.space_type === 'damp' ? '潮湿' : '普通' }}
      </span></td>
      <td><router-link :to="`/walls/${w.id}`">详情</router-link></td>
    </tr>
  </table>
  </div>
</template>

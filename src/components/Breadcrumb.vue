<template>
  <li v-for="(item, index) in stack.stack" :index="index" class="breadcrumb-item">
    <a v-if="index != stack.stack.length-1" :href="item.uri" v-on:click.prevent="$emit('changePath', item)">{{ item.name }}</a>
    <span class="active" v-if="index == stack.stack.length-1">{{ item.name }}</span>
  </li>
</template>
<script>
import { defineComponent } from 'vue';

export default defineComponent({
    props: [ 'stack', 'isGit' ],
    data() {
        return {}
    },
})
</script>

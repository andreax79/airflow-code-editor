<template>
  <li v-for="(item, index) in stack.stack" :index="index" class="breadcrumb-item">
    <a v-if="index != stack.stack.length-1" :href="item.uri" v-on:click.prevent="click(index, item)">{{ item.name }}</a>
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
    methods: {
        normalize(path) {
            if (path[0] != '/') {
                path = '/' + path;
            }
            return path.split(/[/]+/).join('/');
        },
        updateLocation() {
            // Update href hash
            const self = this;
            if (!self.isGit) {
                document.location.hash = self.normalize('files' + (self.stack.last().object || '/'));
            }
        },
        click(index, item) {
            // Breadcrumb action
            const self = this;
            self.stack.slice(index + 1);
            // Update href hash
            self.updateLocation();
            return false;
        },
    }
})
</script>

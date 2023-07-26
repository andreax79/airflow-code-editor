<template>
    <div class="search-view">
        <div v-for="item in items" class="search-result">
            <div class="search-title">{{ item.path }}</div>
            <div class="search-context" v-html="item.context"></div>
        </div>
    </div>
</template>
<style>
.search-view {
    flex: 1 1 0;
    -webkit-flex: 1 1 0;
    flex-direction: column;
    -webkit-flex-direction: column;
    background-color: #fff;
    display: flex;
    display: -webkit-flex;
    min-height: 0;
    min-width: 0;
    height: 100%;
    overflow-y: auto;
}
.search-result {
    background-color: #fff;
}

.search-context table {
    width: 100%;
}

.search-title {
    height: 3rem;
    padding-top: 0.85rem;
    padding-left: 1rem;
    font-size: 1rem;
}

</style>
<script>
import axios from 'axios';
import { defineComponent } from 'vue';
import { basename, normalize, prepareHref } from '../commons';
import { Stack } from '../stack';
import Icon from './Icon.vue';

export default defineComponent({
    components: {
        'icon': Icon,
    },
    props: [ 'config', 'target', 'uuid' ],
    data() {
        return {
            items: [], // tree items (blobs/trees)
        }
    },
    methods: {
        changePath(item) {
            // Show File
            this.$emit('changePath', item);
        },
        async refresh() {
            console.log("Search.refresh");
            const response = await axios.get(prepareHref('search'), { 'params': { 'query': this.target.query }});
            this.items = response.data.map(e => {
                e.stack = new Stack();
                e.stack.updateStack(e.path, 'blob');
                return e;
            });
        },
        update(target) {
            console.log("Search.update");
            console.log(target);
        },
        isChanged() {
            return false;
        }
    },
    mounted() {
        this.refresh();
    }
})
</script>

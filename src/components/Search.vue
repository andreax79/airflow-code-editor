<template>
    <div class="search-view">
        <spinner v-show="loading"/>
        <div v-for="item in items" class="search-result">
            <ol class="breadcrumb">
                <breadcrumb @changePath="changePath" :stack="item.stack" :isGit="false" :lastIsActive="true"></breadcrumb> : {{ item.row_number }}
            </ol>
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

.search-view .breadcrumb {
    padding: 0.5rem 1rem 0.5rem 1rem;
    margin-bottom: 0;
    border-radius: 0px;
}
.search-view .breadcrumb li {
    margin-top: 0.6rem;
    margin-bottom: 0.6rem;
}
.search-view .breadcrumb a {
    text-decoration: none;
    cursor: pointer;
}
.search-view .breadcrumb-buttons {
    float: right;
}
.search-view .breadcrumb-buttons .btn {
    margin-left: 0.5em;
}
.search-view .search-context pre {
    background-color: #fff;
}
</style>
<script>
import axios from 'axios';
import { defineComponent } from 'vue';
import { basename, normalize, prepareHref } from '../commons';
import { Stack } from '../stack';
import Icon from './Icon.vue';
import Breadcrumb from './Breadcrumb.vue';
import Spinner from './Spinner.vue';

export default defineComponent({
    components: {
        'icon': Icon,
        'breadcrumb': Breadcrumb,
        'spinner': Spinner,
    },
    props: [ 'config', 'target', 'uuid' ],
    data() {
        return {
            items: [], // tree items (blobs/trees)
            loading: false,
        }
    },
    methods: {
        changePath(item) {
            // Show File
            this.$emit("show", { id: 'files', path: item.object, type: item.type, line: item.line });
        },
        async refresh() {
            console.log("Search.refresh");
            this.loading = true;
            const response = await axios.get(prepareHref('search'), { 'params': { 'query': this.target.query }});
            this.items = response.data.map(e => {
                e.stack = new Stack(e.path, 'blob', e.row_number);
                return e;
            });
            this.loading = false;
        },
        update(target) {
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

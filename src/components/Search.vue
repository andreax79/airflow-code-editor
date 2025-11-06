<template>
    <div class="search-view">
        <spinner v-show="loading"/>
        <div v-show="!loading && items.length === 0" class="search-no-results">
            <i class="material-icons search-no-results-icon">search_off</i>
            <div class="search-no-results-text">No results found</div>
          <div class="search-input-container">
              <input type="text" class="form-control search-input" placeholder="Search here" v-model="target.query" @keyup.enter="refresh" />
              <i class="material-icons">search</i>
          </div>
        </div>
        <div v-for="item in items" class="search-result" v-show="!loading"
            @contextmenu.prevent.stop="showMenu($event, null)">
            <ol class="breadcrumb">
                <breadcrumb @changePath="changePath" :stack="item.stack" :isGit="false" :lastIsActive="true"></breadcrumb> : {{ item.row_number }}
            </ol>
            <div class="search-context" v-html="item.context"></div>
        </div>
        <vue-simple-context-menu
            :element-id="'search-menu-' + uuid"
            :options="options"
            ref="searchMenu"
            @option-clicked="menuOptionClicked"
        />
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
.search-view .search-no-results {
    text-align: center;
    padding: 10%;
}
.search-view .search-no-results-icon {
    font-size: 20rem;
}
.search-view .search-no-results-text {
    font-size: 2rem;
    margin-top: 1rem;
    margin-bottom: 2rem;
}
.search-view .search-input-container {
    display: inline-flex;
    position: relative;
    vertical-align: middle;
}
.search-view .search-input {
    font-family: "Roboto Flex", roboto, system-ui, -apple-system, blinkmacsystemfont, "Segoe UI", helvetica, arial, ubuntu, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
    border-radius: 1.25rem;
    border: 0;
    width: 200px;
    box-shadow: none;
    border: 1px solid #ccc;
    height: 30px;
    vertical-align: middle;
    padding-left: 32px;
}
.search-view .search-input-container i {
    position: absolute;
    left: 10px;
    top: 6px;
    color: #999;
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
.search-view .search-context .linenodiv {
    width: 5rem;
}
</style>
<script>
import axios from 'axios';
import { defineComponent } from 'vue';
import VueSimpleContextMenu from 'vue-simple-context-menu';
import { basename, normalize, prepareHref, showNotification, parseErrorResponse } from '../commons';
import { Stack } from '../stack';
import Icon from './Icon.vue';
import Breadcrumb from './Breadcrumb.vue';
import Spinner from './Spinner.vue';

export default defineComponent({
    components: {
        'icon': Icon,
        'breadcrumb': Breadcrumb,
        'spinner': Spinner,
        'vue-simple-context-menu': VueSimpleContextMenu,
    },
    props: [ 'config', 'target', 'uuid' ],
    data() {
        return {
            items: [], // tree items (blobs/trees)
            loading: false,
            options: [ // menu options
                {
                    name: '<span class="material-icons">refresh</span> Refresh',
                    slug: 'refresh'
                }
            ]
        }
    },
    methods: {
        changePath(item) {
            // Show File
            this.$emit("show", { id: 'files', path: item.object, type: item.type, line: item.line });
        },
        async refresh() {
            console.log("Search.refresh");
            console.log(this.target);

            try {
                this.loading = true;
                const response = await axios.get(prepareHref('search'), { 'params': { 'query': this.target.query, 'context': true }});
                this.items = response.data.value.map(e => {
                    e.stack = new Stack(e.path, 'blob', e.row_number);
                    return e;
                });
                this.loading = false;
            } catch(error) {
                this.loading = false;
                const message = parseErrorResponse(error, 'Search error');
                showNotification({ message: message, title: 'Search' });
            };
        },
        showMenu(event, item) {
            // Show menu
            this.$refs.searchMenu.showMenu(event, item);
        },
        menuOptionClicked(event) {
            if (event.option.slug == 'refresh') {
                this.refresh();
            }
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

<template>
    <div class="history-view">
        <div ref="logView" class="log-view list-group"><svg xmlns="http://www.w3.org/2000/svg"></svg><div></div></div>
        <div class="commit-view">
            <ul class="nav nav-tabs">
              <li role="presentation" :class="tab == 'commit' ? 'active' : ''" ><a href="#" @click.prevent="tab = 'commit'" >Commit</a></li>
              <li role="presentation" :class="tab == 'tree' ? 'active' : ''" ><a href="#" @click.prevent="tab = 'tree'">Tree</a></li>
            </ul>
            <div class="diff-view-container panel panel-default" v-show="tab == 'commit'">
                <commit ref="commit" :commit="commit"></commit>
            </div>
            <div class="tree-view" v-show="tab == 'tree'">
                <container ref="container" :config="config" :is-git="true"></container>
            </div>
        </div>
    </div>
</template>
<style>
.history-view {
    display: flex;
    display: -webkit-flex;
    min-height: 0;
    min-width: 0;
    flex: 1 1 0;
    -webkit-flex: 1 1 0;
    background-color: #eee;
}
.commit-view {
    display: flex;
    display: -webkit-flex;
    min-height: 0;
    min-width: 0;
    flex-direction: column;
    -webkit-flex-direction: column;
    flex: 1 1 0;
    -webkit-flex: 1 1 0;
    background-color: #fff;
}
.commit-view .commit-view-header {
    border: solid #dddddd;
    border-width: 0 0 1px 0;
    padding: 1em;
    text-align: right
}
.commit-view .commit-view-content {
    display: flex;
    display: -webkit-flex;
    min-height: 0;
    min-width: 0;
    flex: 1 1 0;
    -webkit-flex: 1 1 0;
    flex-direction: column;
    -webkit-flex-direction: column;
}
.commit-view .nav-tabs {
    padding-top: 1em;
    padding-left: 1em;
}
.commit-view .nav-tabs a:hover {
    color: #000;
}
.log-view {
    flex: 1 1 0;
    -webkit-flex: 1 1 0;
    overflow-y: auto;
    cursor: default;
    margin-bottom: 0;
    position: relative;
    background-color: #fff;
}
.log-view svg {
    position: absolute;
    top: 0;
    left: 0;
}
.log-view svg path {
    stroke-width: 2;
    fill: none;
}
.log-view svg circle {
    stroke: none;
    fill: #555555;
}
.log-view .log-entry {
    padding: 5px 10px;
    background-color: transparent;
    margin: 0;
    border-width: 0 0 1px 0;
    border-radius: 0;
}
.log-view .log-entry:hover {
    background-color: rgba(244, 244, 244, 0.9);
}
.log-view .log-entry.active {
    background-color: rgba(244, 244, 244, 0.9);
    border-color: #ccc;
    color: #000;
}
.log-view .log-entry.active header h6 a {
    color: #ffffff;
}
.log-view .log-entry header {
    display: flex;
    display: -webkit-flex;
    min-height: 0;
    min-width: 0;
    align-items: baseline;
    -webkit-align-items: baseline;
}
.log-view .log-entry header h6 {
    font-weight: bold;
    margin-top: 0;
}
.log-view .log-entry header h6 a {
    color: #777777;
}
.log-view .log-entry header .badge {
    font-family: Menlo, Monaco, Consolas, "Courier New", monospace;
}
.log-view .log-entry header .log-entry-date {
    margin-left: auto;
    font-size: 0.8em;
    margin-right: 1em;
}
.log-view .log-entry .list-group-item-text {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    color: inherit;
}
.log-view .log-entry-more {
    padding: 10px 16px;
}
.log-view .log-entry-more a {
    display: block;
    text-align: center;
}
</style>
<script>
import { defineComponent, ref } from 'vue';
import { LogView } from "../log";
import FilesEditorContainer from './FilesEditorContainer.vue';
import ShowCommit from './ShowCommit.vue';

export default defineComponent({
    components: {
        'container': FilesEditorContainer,
        'commit': ShowCommit,
    },
    props: [ 'config' ],
    data() {
        return {
            tab: 'commit', // active tab
            logView: null, // LogView instance
            name: null, // reference
            commit: null // commit object
        }
    },
    methods: {
        update(target) {
            if (this.name != target.name) {
                this.name = target.name;
                this.logView.update(this.name);
                this.updateCommit({ commit: this.name });
            }
        },
        updateCommit(commit) {
            this.commit = commit;
            this.$refs.commit.refresh();
            this.$refs.container.updateStack(this.commit.commit, 'tree');
        },
        initViews() {
            // Init views
            this.logView = new LogView(this.$refs.logView, this);
        },
    },
    mounted() {
        // Init
        console.log('HistoryView.mounted');
        this.initViews();
    }
})
</script>

<template>
    <div id="history-view">
        <div id="log-view" class="list-group"><svg xmlns="http://www.w3.org/2000/svg"></svg><div></div></div>
        <div id="commit-view">
            <div class="commit-view-header">
                <div class="btn-group" role="group" aria-label="...">
                  <button type="button" :class="tab == 'commit' ? 'btn btn-primary' : 'btn btn-default'" @click="tab = 'commit'">Commit</button>
                  <button type="button" :class="tab == 'tree' ? 'btn btn-primary' : 'btn btn-default'" @click="tab = 'tree'">Tree</button>
                </div>
            </div>
            <div class="diff-view-container panel panel-default" v-show="tab == 'commit'">
                <commit :commit="historyState.commit"></commit>
            </div>
            <div class="tree-view" v-show="tab == 'tree'">
                <container :stack="historyState.stack" :config="config" :is-git="true"></container>
            </div>
        </div>
    </div>
</template>
<script>
import { defineComponent } from 'vue';
import { LogView } from "../log";
import FilesEditorContainer from './FilesEditorContainer.vue';
import ShowCommit from './ShowCommit.vue';

export default defineComponent({
    components: {
        'container': FilesEditorContainer,
        'commit': ShowCommit,
    },
    props: [ 'historyState', 'config' ],
    data() {
        return {
            tab: 'commit',
            logView: null,
            name: null,
            commit: null
        }
    },
    watch: {
        historyState: {
            handler(val, preVal) {
                const self = this;
                console.log('HistoryView.watch historyState');
                if (self.name != self.historyState.item.name) {
                    self.name = self.historyState.item.name;
                    self.logView.update(self.name);
                    self.commit = null;
                }
                if ((self.historyState.commit != null) && (self.commit != self.historyState.commit.commit)) {
                    self.commit = self.historyState.commit.commit;
                    // self.diffView.update(self.commit);
                }
            },
            deep: true
        }
    },
    methods: {
        initViews() {
            // Init views
            const self = this;
            self.logView = new LogView('#log-view', self.historyState);
            // self.diffView = new DiffView('#commit-view .diff-view-container', false, false, null);
        },
    },
    mounted() {
        // Init
        console.log('HistoryView.mounted');
        const self = this;
        self.initViews();
    }
})
</script>

<template>
  <div class="show-commit">
    <div v-for="line in lines">
      <div :class="line.classes" v-if="!line.skip">{{ line.line }}</div>
    </div>
  </div>
</template>
<style>
.show-commit {
    font-family: monospace;
    overflow: auto;
    line-height: 1.2em;
    margin-top: 1em;
}

.show-commit .diff-default {
    padding-left: 2em;
}

.show-commit .diff-header {
    padding-left: 1em;
    line-height: 1.4em;
    font-family: sans-serif;
}

.show-commit .badge {
    float: right;
    margin-top: 0.5em;
    margin-right: 0.5em;
}

.show-commit .font-weight-bold {
    font-weight: bold;
}

.show-commit .diff-file-header {
    font-weight: bold;
    line-height: 3em;
    padding-left: 1em;
    border-top: 1px solid #eee;
    border-bottom: 1px solid #eee;
    margin-top: 2em;
    margin-bottom: 1em;
    background-color: #f6f6f6;
    font-family: sans-serif;
}

.show-commit .diff-line-add {
    background-color: #e6ffec;
    padding-left: 1em;
}

.show-commit .diff-line-del {
    background-color: #ffebe9;
    padding-left: 1em;
}

.show-commit .diff-line-offset {
    background-color: #ddf4ff;
    line-height: 2em;
}
</style>
<script>
import { defineComponent, ref } from 'vue';
import { git_async } from "../commons";

export default defineComponent({
    props: [ 'linesOfContext' ],
    data() {
        return {
            'lines': ref([]),
        }
    },
    methods: {
        processLine(line) {
            const c = line[0];
            let classes = '';
            let skip = false;
            if (this.inHeader) { // global header
                if (line.startsWith('commit')) { // commit id
                    line = line.substring(7);
                    classes = "badge";
                } else if (line.startsWith('diff --git')) { // end of global header
                    skip = true;
                    this.inHeader = false;
                    this.inFileHeader = true;
                } else {
                    classes = "diff-header";
                    if (line.startsWith('Author:')) {
                        classes += " font-weight-bold";
                    } else if (line.startsWith('Date:')) {
                        classes += " font-weight-bold";
                    }
                }
            } else if ((!this.inFileHeader) && (line.startsWith('diff --git'))) {
                skip = true;
                this.inFileHeader = true;
            } else if (this.inFileHeader) { // file header
                skip = true;
                if (line.startsWith('+++ ')) { // filename
                    classes += " diff-file-header";
                    line = line.substring(5);
                    if (line.startsWith('dev/null')) {
                        line = this.last.substring(5);
                    }
                    if (line[0] == '/') {
                        line = line.substring(1);
                    }
                    skip = false;
                    this.inFileHeader = false;
                }
            } else {
                if (c == '+') {
                    classes += " diff-line-add";
                } else if (c == '-') {
                    classes += " diff-line-del";
                } else if (c == '@') {
                    classes += " diff-line-offset";
                }
                if (!classes) {
                    classes = "diff-default";
                }
            }
            this.last = line;
            return { classes: classes, line: line, skip: skip };
        },
        parseDiff(data) {
            console.log('loaded ' + this.commit.commit);
            this.inHeader = true; // git diff header
            this.inFileHeader = false; // file header
            this.last = null;
            this.lines = data.split("\n").map(this.processLine);
            this.$emit('loaded');
        },
        async refresh(commit) {
            if (commit) {
                this.commit = commit;
            }
            if (this.commit) {
                console.log('loading');
                const cmd = [ 'show', '--unified=' + this.linesOfContext, this.commit.commit ];
                const data = await git_async(cmd);
                if (data) {
                    this.parseDiff(data);
                }
            }
        },
    },
    async mounted() {
        // Init
        this.refresh();
    }
})
</script>

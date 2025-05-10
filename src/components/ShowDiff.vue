<template>
  <div class="show-diff-container">
    <div class="show-diff">
      <div v-for="line in lines">
        <div :class="line.classes" v-if="!line.skip">{{ line.line }}</div>
      </div>
    </div>
  </div>
</template>
<style>
.show-diff-container {
    display: block;
    flex: 1;
    overflow: auto;
    background-color: #f2f2f2;
    padding-top: 1em;
}
.show-diff {
    font-family: monospace;
    line-height: 1.2em;
}
.show-diff .diff-default {
    padding-left: 2em;
}
.show-diff .diff-file-header {
    padding-left: 1em;
    font-family: monospace;
}
.show-diff .diff-filename{
    font-weight: bold;
}
.show-diff .diff-line-add {
    background-color: #e6ffec;
    padding-left: 1em;
}
.show-diff .diff-line-del {
    background-color: #ffebe9;
    padding-left: 1em;
}
.show-diff .diff-line-offset {
    background-color: #ddf4ff;
    line-height: 2em;
}
</style>
<script>
import axios from 'axios';
import { defineComponent, ref } from 'vue';
import { prepareHref, showNotification, parseErrorResponse } from '../commons';
import { git_async } from "../commons";

export default defineComponent({
    props: [ 'linesOfContext' ],
    data() {
        return {
            'lines': ref([])
        }
    },
    methods: {
        processLine(line) {
            const c = line[0];
            let classes = '';
            let skip = false;
            if ((!this.inFileHeader) && (line.startsWith('diff --git'))) {
                //skip = true;
                this.inFileHeader = true;
            } else if (this.inFileHeader) { // file header
                //skip = true;
                this.inFileHeader = true;
                classes += " diff-file-header";
                if (line.startsWith('+++ ')) { // filename
                    classes += " diff-filename";
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
            this.inFileHeader = true; // file header
            this.last = null;
            this.lines = data.split("\n").map(this.processLine);
            this.$emit('loaded', true);
        },
        async showDiff() {
            // Show git diff
            const cmd = [
                'diff',
                '--unified=' + this.linesOfContext,
                (this.target.kind == 'staged') ? '--cached' : null,
                '--',
                this.target.name
            ];
            const data = await git_async(cmd);
            if (data) {
                this.parseDiff(data);
            }
        },
        parseUntrackedFileResponse(response) {
            // Show an untracked file mimic git diff format
            const data = response.data;
            this.inFileHeader = true; // file header
            this.last = null;
            const content = data.split("\n").map(x => '+' + x);
            const header = [
                'diff --git a/dev/null b/' + this.target.name,
                'index ...',
                '--- a/dev/null',
                '+++ b/' + this.target.name,
                '@@ -0,0 +1,' + content.length + ' @@'
            ];
            this.lines = header.concat(content).map(this.processLine);
            this.$emit('loaded', true);
        },
        async showUntrackedFile(data) {
            // Show an untracked file mimic git diff format
            try {
                const response = await axios.get(prepareHref('files/' + this.target.name),
                    { transformResponse: res => res });
                return this.parseUntrackedFileResponse(response);
            } catch(error) {
                this.$emit('loaded', false); // close the spinner
                const message = parseErrorResponse(error, 'Error loading file');
                showNotification({ message: message, title: 'Load' });
            };
        },
        async refresh(target) {
            this.target = target;
            if (this.target && this.target.name) {
                if (this.target.status == 'untracked') {
                    this.showUntrackedFile();
                } else {
                    this.showDiff();
                }
            } else {
                this.$emit('loaded', true); // close the spinner
            }
        },
    }
})
</script>

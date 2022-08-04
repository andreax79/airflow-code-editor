<template>
  <div class="show-commit">
  <div v-for="line in lines">
    <div :class="line.classes" v-if="!line.skip">{{ line.line }}</div>
  </div>
  </div>
</template>
<script>
import { defineComponent } from 'vue';
import { git } from "../commons";

export default defineComponent({
    props: [ 'commit' ],
    data() {
        return {
            'lines': []
        }
    },
    methods: {
        processLine(line) {
            const self = this;
            const c = line[0];
            let classes = '';
            let skip = false;
            if (self.inHeader) { // global header
                if (line.startsWith('commit')) { // commit id
                    line = line.substring(7);
                    classes = "badge";
                } else if (line.startsWith('diff --git')) { // end of global header
                    skip = true;
                    self.inHeader = false;
                    self.inFileHeader = true;
                } else {
                    classes = "diff-header";
                    if (line.startsWith('Author:')) {
                        classes += " font-weight-bold";
                    } else if (line.startsWith('Date:')) {
                        classes += " font-weight-bold";
                    }
                }
            } else if ((!self.inFileHeader) && (line.startsWith('diff --git'))) {
                skip = true;
                self.inFileHeader = true;
            } else if (self.inFileHeader) { // file header
                skip = true;
                if (line.startsWith('+++ ')) { // filename
                    classes += " diff-file-header";
                    line = line.substring(5);
                    if (line.startsWith('dev/null')) {
                        line = self.last.substring(5);
                    }
                    if (line[0] == '/') {
                        line = line.substring(1);
                    }
                    skip = false;
                    self.inFileHeader = false;
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
            self.last = line;
            return { classes: classes, line: line, skip: skip };
        },
        parseDiff(diff) {
            const self = this;
            self.inHeader = true; // git diff header
            self.inFileHeader = false; // file header
            self.last = null;
            self.lines = diff.split("\n").map(self.processLine);
        },
        refresh() {
            const self = this;
            const cmd = [ 'show', '--unified=3', self.commit.commit ];
            git(cmd, self.parseDiff);
        },
    },
    watch: {
        'commit': {
            handler(val, preVal) {
                const self = this;
                console.log('ShowCommit.watch commit');
                self.refresh();
            },
            deep: true
        }
    },
})
</script>

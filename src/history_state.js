import { ref } from "vue";
import { Stack } from './stack';

export class HistoryState {
    constructor() {
        const self = this;
        self.stack = new Stack();
        self.item = ref(null); // item, e.g. - { id: "local-branches", name: "master" }
        self.commit = ref(null); // commit, e.g. { message: "Initial commit", commit: "85fa94c5f17bef8a6469cf5bf59c968cbcd102ca", tree: "ebb8346b56072b363258505cf99f8b49cdb55b43", author: {...}, committer: {...},... }
    }

    update(item) {
        const self = this;
        self.item = item;
        self.commit = { commit: item.name };
        self.stack.updateStack(item.name, 'tree');
        document.location.hash = item.id + '/' + item.name;
    }

    updateCommit(commit) {
        const self = this;
        self.commit = commit;
        self.stack.updateStack(commit.tree, 'tree');
    }
}

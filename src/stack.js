import { ref } from "vue";

export class Stack {
    constructor() {
        console.log('stack');
        const self = this;
        self.stack = ref([ { name: 'root', object: undefined } ]);
    }

    updateStack(path, type) {
        const self = this;
        console.log('Stack.updateStack path:' + path + ' type: ' + type);
        // path: absolute path (local file) or ref/path (git)
        // type: last item type (tree or blob)
        self.stack.length = 0;
        let fullPath = null;
        if (path == '/' || !path) {
            path = '';
        }
        path.split('/').forEach((part, index) => {
            if (index === 0 && !part) {
                self.stack.push({ name: 'root', object: undefined });
                fullPath = '';
            } else {
                if (fullPath === null) {
                    fullPath = part;
                    part = 'root';
                } else {
                    fullPath += '/' + part;
                }
                if (part[0] == '~') {
                    part = part.substring(1);
                }
                self.stack.push({
                    name: part,
                    object: fullPath,
                    uri: encodeURI((fullPath !== undefined && fullPath.startsWith('/')) ? ('#files' + fullPath) : null),
                    type: 'tree'
                });
            }
        });
        if (type == 'blob') {
            self.stack[self.stack.length - 1].type = 'blob';
        }
    }

    last() {
        // Return last stack element
        const self = this;
        return self.stack[self.stack.length - 1];
    }

    parent() {
        // Return stack - 2 element
        const self = this;
        return self.stack.length > 1 ? self.stack[self.stack.length - 2] : undefined;
    }

    isGit() {
        // Return true if last is a git ref
        const self = this;
        return (self.last().object !== undefined && !self.last().object.startsWith('/'));
    }

    pop() {
        const self = this;
        return self.stack.pop();
    }

    push(item) {
        const self = this;
        return self.stack.push(item);
    }

    slice(index) {
        const self = this;
        self.stack = self.stack.slice(0, index);
    }

};

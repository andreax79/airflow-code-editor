import { ref } from "vue";

export class Stack {
    constructor() {
        this.stack = [ { name: 'root', object: undefined } ];
    }

    updateStack(path, type) {
        console.log('Stack.updateStack path:' + path + ' type: ' + type);
        // path: absolute path (local file) or ref/path (git)
        // type: last item type (tree or blob)
        this.stack.length = 0;
        let fullPath = null;
        if (path == '/' || !path) {
            path = '';
        }
        path.split('/').forEach((part, index) => {
            if (index === 0 && !part) {
                this.stack.push({ name: 'root', object: undefined });
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
                this.stack.push({
                    name: part,
                    object: fullPath,
                    uri: encodeURI((fullPath !== undefined && fullPath.startsWith('/')) ? ('#files' + fullPath) : null),
                    type: 'tree'
                });
            }
        });
        if (type == 'blob') {
            this.stack[this.stack.length - 1].type = 'blob';
        }
    }

    last() {
        // Return last stack element
        return this.stack[this.stack.length - 1];
    }

    parent() {
        // Return stack - 2 element
        return this.stack.length > 1 ? this.stack[this.stack.length - 2] : undefined;
    }

    isGit() {
        // Return true if last is a git ref
        return (this.last().object !== undefined && !this.last().object.startsWith('/'));
    }

    pop() {
        return this.stack.pop();
    }

    push(item) {
        return this.stack.push(item);
    }

    slice(index) {
        this.stack = this.stack.slice(0, index);
    }

};

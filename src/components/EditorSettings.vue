<template>
    <div class="modal fade settings-modal" tabindex="-1" role="dialog">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal"><span>&times;</span><span class="sr-only">Close</span></button>
                    <h4 class="modal-title">Settings</h4>
                </div>
                <div class="modal-body">
                    <span style="min-width: 8em; display: inline-block">Theme:</span>
                    <select v-model="config.theme">
                        <option v-for="theme in themes">
                        {{ theme }}
                        </option>
                    </select>
                    <br/>
                    <span style="min-width: 8em; display: inline-block">Mode:</span>
                    <select v-model="config.mode">
                        <option selected>default</option>
                        <option>emacs</option>
                        <option>sublime</option>
                        <option>vim</option>
                    </select>
                    <hr/>
                </div>
            </div>
        </div>
    </div>
</template>
<script>

import themes from "../themes";

export default {
    props: [ 'config' ],
    data() {
        return {
            themes: themes, // themes list from "themes.js"
            codeMirrorOptions: { // code mirror options
                lineNumbers: true,
                foldGutter: true,
                tabSize: 4,
                indentUnit: 4,
                indentWithTabs: false,
                gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
                extraKeys: {
                    "Alt-F": "findPersistent",
                    "Tab": "indentMore"
                }
            }
        }
    }
}
</script>

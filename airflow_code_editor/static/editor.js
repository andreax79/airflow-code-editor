
jQuery(document).ready(function(){
    window.editor = CodeMirror.fromTextArea(document.getElementById('code'), {
    	lineNumbers: true,
        mode: 'python',
        foldGutter: true,
        gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"]
    });
    window.editor.on('change', function(editor) {
        document.forms.editor_form.code.value = editor.getValue();
    });
});

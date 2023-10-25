<template>
  <modal v-model="show" :close="close">
    <div :class="cssClass">
      <h1>{{ title }}</h1>
      <label>{{ message }}</label>
      <div class="dialog-buttons">
        <button @click="close" class="btn btn-primary">Dismiss</button>
      </div>
    </div>
  </modal>
</template>
<style>
.airflow-code-editor-modal-terminal {
    width: 95%;
}
.airflow-code-editor-modal-terminal label {
    white-space: pre;
    overflow: auto;
}
</style>
<script>
import { defineComponent } from 'vue';

export default defineComponent({
    props: [],
    data() {
        return {
            message: '',
            title: '',
            type: 'error',
            cssClass: 'airflow-code-editor-modal',
            show: false,
        }
    },
    methods: {
        showDialog(options) {
            return new Promise((resolve, reject) => {
                this.message = options.message;
                this.type = options.type;
                this.show = true;
                this.resolve = resolve;
                this.reject = reject;
                switch (options.type) {
                    case 'error':
                        this.title = options.title || 'Error';
                        this.cssClass = 'airflow-code-editor-modal';
                        break;
                    case 'warning':
                        this.title = options.title || 'Warning';
                        this.cssClass = 'airflow-code-editor-modal';
                        break;
                    case 'terminal':
                        this.title = options.title || '';
                        this.cssClass = 'airflow-code-editor-modal airflow-code-editor-modal-terminal';
                        break;
                }
            });
        },
        close() {
            this.show = false;
            this.resolve();
        },
    }
})
</script>

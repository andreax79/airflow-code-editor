<template>
  <modal v-model="show" :close="close">
    <div class="airflow-code-editor-modal airflow-code-editor-modal-error">
      <h1>{{ type == 'warning' ? 'Warning' : 'Error' }}</h1>
      <label>{{ message }}</label>
      <div class="dialog-buttons">
        <button @click="close" class="btn btn-primary">Dismiss</button>
      </div>
    </div>
  </modal>
</template>
<script>
import { defineComponent } from 'vue';

export default defineComponent({
    props: [],
    data() {
        return {
            message: '',
            type: 'errror',
            show: false,
        }
    },
    methods: {
        showDialog(message) {
            return new Promise((resolve, reject) => {
                this.message = message.message;
                this.type = message.type;
                this.show = true;
                this.resolve = resolve;
                this.reject = reject;
            });
        },
        close() {
            this.show = false;
            this.resolve();
        },
    }
})
</script>

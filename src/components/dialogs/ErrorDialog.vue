<template>
  <modal v-model="show" :close="close">
    <div :class="'airflow-code-editor-modal airflow-code-editor-modal-' + type">
      <icon icon="warning"/>
      <span class="message-text">{{ message }}</span>
      <button @click="close" class="btn btn-primary">Dismiss</button>
    </div>
  </modal>
</template>
<style>
.airflow-code-editor-modal {
    width: 400px;
    padding: 0;
    box-sizing: border-box;
    background-color: #fff;
    font-size: 1.5em;
    text-align: center;
}
.airflow-code-editor-modal-error .material-icons,
.airflow-code-editor-modal-warning .material-icons {
    color: #f65656;
    font-size: 4em;
    margin-top: 0.5em;
    margin-bottom: 0.25em;
    display: inline-block;
}
.airflow-code-editor-modal-warning .material-icons {
    color: #fb641f;
}
.airflow-code-editor-modal-error .message-text,
.airflow-code-editor-modal-warning .message-text {
    margin: 1em 1em 2em 1em;
    display: block;
}
.airflow-code-editor-modal-error .btn,
.airflow-code-editor-modal-warning .btn {
    background-color: #f65656;
    width: inherit;
    border: 0px solid #f65656;
    border-radius: 0;
}
.airflow-code-editor-modal-warning .btn {
    background-color: #fb641f;
    border: 0px solid #fb641f;
}
</style>
<script>
import { defineComponent } from 'vue';
import Icon from '../Icon.vue';

export default defineComponent({
    components: {
        'icon': Icon,
    },
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

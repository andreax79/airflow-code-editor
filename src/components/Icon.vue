<template>
  <span class="material-icons">{{ effectiveIcon }}</span>
</template>
<style>
</style>
<script>
import { defineComponent } from 'vue';

export default defineComponent({
    props: [ 'icon', 'state' ],
    computed: {
        effectiveIcon() {
            if (this.icon == 'file') {
                return 'insert_drive_file';
            } else if (this.icon == 'check_box') {
                if (this.state) {
                    return 'check_box';
                } else {
                    return 'check_box_outline_blank';
                }
            } else {
                return this.icon;
            }
        }
    },
    data() {
        return {}
    },
})
</script>

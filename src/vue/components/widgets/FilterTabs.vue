<template>
    <div class="filter-tabs">
        <!-- Bootstrap's Button Group -->
        <div class="btn-group"
             role="group">

            <!-- Filter Items -->
            <button v-for="item in props.items"
                    type="button"
                    class="btn btn-light text-2"
                    :class="{active:_isItemSelected(item)}"
                    @click="_selectItem(item)">
                <!-- Item Label -->
                {{item}}
            </button>
        </div>
    </div>
</template>

<script setup>
import {ref} from "vue"

const props = defineProps({
    items: Array
})

const emit = defineEmits(['selected'])
const selectedItemId = ref(null)

const _isItemSelected = (item) => {
    if(selectedItemId.value === null && props.items && props.items.length > 0) {
        _selectItem(props.items[0])
    }

    return selectedItemId.value === item
}

const _selectItem = (item) => {
    selectedItemId.value = item
    emit('selected', item)
}
</script>

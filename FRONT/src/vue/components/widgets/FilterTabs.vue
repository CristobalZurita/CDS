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

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";

div.btn-group {
    margin: 0 auto;
    width: 50%;
    @include media-breakpoint-down(lg) {
        width: 100%;
        max-width: 600px;
    }
}

button.btn {
    @include generate-dynamic-styles-with-hash((
        xxxl: (padding: 0.3rem 2rem),
        sm: (padding: 0.3rem 0)
    ));

    opacity: 0.8;
    border-radius: 30px;
    background-color: darken($light, 5%);

    &.active, &:hover {
        background-color: darken($light, 5%);
        border-color: $light;
        color: $primary;
    }

    &.active {
        background-color: $primary;
        color: $text-normal-contrast;
        opacity: 1;
    }
}
</style>
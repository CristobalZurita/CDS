<template>
    <div class="filter-tabs">
        <!-- Bootstrap's Button Group -->
        <div class="btn-group-custom" :style="groupStyles"
             role="group">

            <!-- Filter Items -->
            <button v-for="item in props.items"
                    type="button"
                    class="btn btn-light filter-btn"
                    :class="{active:_isItemSelected(item)}"
                    :style="buttonStyles"
                    @click="_selectItem(item)">
                <!-- Item Label -->
                {{item}}
            </button>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from "vue"
import { useResponsive } from "@/composables/useResponsive"

const props = defineProps({
    items: Array
})

const emit = defineEmits(['selected'])
const selectedItemId = ref(null)
const { windowWidth } = useResponsive()

const groupStyles = computed(() => {
    const w = windowWidth.value
    return {
        margin: '0 auto',
        width: w >= 992 ? '50%' : '100%',
        maxWidth: w < 992 ? '600px' : 'none'
    }
})

const buttonStyles = computed(() => {
    const w = windowWidth.value
    // AUMENTADO: de 0.3rem a 0.75rem para mejor legibilidad
    const padding = w >= 1600 ? '0.75rem 2rem' : '0.75rem 0.5rem'

    return {
        padding,
        opacity: '0.8',
        borderRadius: '30px',
        backgroundColor: '#c5c2b8', // darken($light, 5%)
        fontSize: '1rem', // AUMENTADO para mejor legibilidad
        fontWeight: '500' // AUMENTADO de 400 a 500 para mejor legibilidad
    }
})

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

<style scoped>
.filter-btn.active,
.filter-btn:hover {
    background-color: #c5c2b8 !important; /* darken($light, 5%) */
    border-color: #d3d0c3 !important; /* $light */
    color: #ec6b00 !important; /* $primary */
}

.filter-btn.active {
    background-color: #ec6b00 !important; /* $primary */
    color: #ffffff !important; /* $text-normal-contrast */
    opacity: 1 !important;
    font-weight: 600 !important; /* MÁS BOLD para texto activo */
}
</style>

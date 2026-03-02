<template>
    <div class="foxy-project-info">
        <!-- Logo Wrapper -->
        <div class="foxy-project-info-logo-wrapper"
             :class="shrinkImage ? `foxy-project-info-logo-wrapper-shrink` : ``">
            <ImageView :src="props.image"
                       alt="Logo"
                       :spinner-enabled="true"/>
        </div>

        <div class="foxy-project-info-content">
            <slot/>
        </div>
    </div>
</template>

<script setup>
import ImageView from "/src/vue/components/generic/ImageView.vue"

const props = defineProps({
    image: String,
    shrinkImage: Boolean
})
</script>

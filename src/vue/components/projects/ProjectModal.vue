<template>
    <div class="modal modal-xl fade foxy-project-modal"
         id="foxy-project-modal"
         tabindex="-1"
         aria-labelledby="foxy-project-modal-label">
        <div class="modal-dialog modal-dialog-centered">
            <!-- Modal Content -->
            <div class="modal-content">
                <!-- Close Button -->
                <button class="close-button"
                        data-bs-dismiss="modal"
                        aria-label="Close">
                    <i class="fa fa-close"/>
                </button>

                <!-- Banner -->
                <div class="modal-body py-5 py-lg-4">
                    <ProjectInfo v-if="project"
                                 :image="project.image"
                                 :shrink-image="true">
                        <ProjectInfoContent :title="project.title"
                                            :tags="project.tags"
                                            :description="project.description"
                                            :links="project.links"/>
                    </ProjectInfo>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import {onMounted, ref, watch} from "vue"
import {useLayout} from "/src/composables/layout.js"
import Modal from '/node_modules/bootstrap/js/src/modal'
import ProjectInfo from "/src/vue/components/projects/ProjectInfo.vue"
import ProjectInfoContent from "/src/vue/components/projects/ProjectInfoContent.vue"

const _layout = useLayout()

const props = defineProps({
    project: Object
})

const emit = defineEmits(['close'])

const bsModal = ref(null)

onMounted(() => {
    const elModal = document.getElementById("foxy-project-modal")
    bsModal.value = new Modal(elModal, {})
    elModal.addEventListener('hide.bs.modal', _onWillHide)
    elModal.addEventListener('hidden.bs.modal', _onHidden)
})

watch(() => props.project, () => {
    if(!bsModal.value)
        return

    if(props.project)
        bsModal.value.show()
    else
        bsModal.value.hide()
})

const _onWillHide = () => {
    if (document.activeElement) {
        document.activeElement.blur()
    }
}

const _onHidden = () => {
    emit("close")
}
</script>

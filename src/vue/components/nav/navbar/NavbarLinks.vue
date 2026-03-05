<template>
    <div class="foxy-navbar-links-wrapper">
        <ul class="foxy-navbar-links" :class="`${collapsed ? 'collapsed' : ''}`">
            <li v-for="link in parsedLinks">
                <Link :url="link.path">
                    <button class="foxy-nav-link"
                            @click="_onLinkClicked"
                            :class="link.buttonClass">
                        <i v-if="link.faIcon"
                           :class="link.faIcon"
                           class="foxy-nav-link-icon"/>

                        <span>
                            {{link.label}}
                        </span>
                    </button>
                </Link>
            </li>
        </ul>
    </div>
</template>

<script setup>
import {computed, onMounted, ref, watch} from "vue"
import {useRouter} from "vue-router"
import Link from "/src/vue/components/generic/Link.vue"

const router = useRouter()
const props = defineProps({
    items: Array,
    collapsed: Boolean
})
const emit = defineEmits(['linkClicked'])

const transitionLinks = ref([])

const parsedLinks = computed(() => {
    return props.items.map((item, index) => ({
        path: item.path,
        label: item.label,
        faIcon: item.faIcon,
        buttonClass: {
            active: item.isActive,
            hidden: transitionLinks.value.indexOf(index) === -1
        }
    }))
})

onMounted(() => {
    _executeTransition(props.collapsed)
})

watch(() => props.collapsed, (newVal) => {
    _executeTransition(newVal)
})

const _executeTransition = (collapsed) => {
    transitionLinks.value = []
    if (collapsed) return

    parsedLinks.value.forEach((_, i) => {
        setTimeout(() => {
            transitionLinks.value.push(i)
        }, 50 * i)
    })
}

const _onLinkClicked = () => {
    emit('linkClicked')
}
</script>

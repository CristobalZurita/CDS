<template>
    <div :style="wrapperStyles">
        <ul :style="linksStyles" :class="{ collapsed: collapsed }">
            <li v-for="link in parsedLinks">
                <Link :url="link.path">
                    <span class="nav-link"
                          role="link"
                          tabindex="0"
                          @click="_onLinkClicked"
                          :class="link.buttonClass">
                        <i v-if="link.faIcon"
                           :class="link.faIcon"
                           class="nav-link-icon"/>

                        <span>
                            {{link.label}}
                        </span>
                    </span>
                </Link>
            </li>
        </ul>
    </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue"
import { useResponsive } from "@/composables/useResponsive"
import Link from "/src/vue/components/generic/Link.vue"

const { windowWidth } = useResponsive()

const props = defineProps({
    items: Array,
    collapsed: Boolean
})
const emit = defineEmits(['linkClicked'])

const transitionLinks = ref([])

// Wrapper styles
const wrapperStyles = computed(() => ({
    marginLeft: windowWidth.value >= 992 ? '2rem' : '0'
}))

// Links list styles
const linksStyles = computed(() => {
    const baseStyles = {
        listStyle: 'none',
        margin: '0',
        padding: '0',
        display: 'flex',
        flexWrap: 'nowrap'
    }

    if (windowWidth.value < 992) {
        return {
            ...baseStyles,
            flexDirection: 'column',
            margin: '2px 0 15px'
        }
    }

    return baseStyles
})

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

<style scoped>
.nav-link {
    background-color: transparent;
    border: 0;
    padding: 0 0 0 1.2rem;
    white-space: nowrap;
    display: inline-flex;
    align-items: center;
    cursor: pointer;
    font-family: inherit;
    color: #dee2e6;
    text-transform: uppercase;
    font-weight: 600;
    letter-spacing: 0.03em;
    font-size: 1.1rem;
}

@media (max-width: 1199px) {
    .nav-link {
        padding: 0 0 0 0.9rem;
    }
}

@media (max-width: 991px) {
    .nav-link {
        padding: 0 !important;
        min-width: 160px;
        text-align: left;
        margin-left: 12px;
        margin-bottom: 8px;
        font-size: 1rem;
        transition: 0.2s ease-in margin-left, 0.2s ease-in opacity;
    }

    ul.collapsed {
        display: none;
    }
}

@media (max-height: 400px) {
    .nav-link {
        margin-bottom: 4px;
    }
}

.nav-link-icon {
    display: none;
    min-width: 1.4rem;
    margin-right: 10px;
    color: #6c757d;
    transition: color 0.4s;
}

@media (max-width: 991px) {
    .nav-link-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }
}

.nav-link.hidden {
    opacity: 0;
    margin-left: 80px;
}

@media (min-width: 992px) {
    .nav-link.hidden {
        opacity: 1;
        margin-left: 0;
    }
}

.nav-link:hover,
.nav-link.active {
    color: #f07519;
}

.nav-link:hover .nav-link-icon,
.nav-link.active .nav-link-icon {
    color: #faa967;
}
</style>

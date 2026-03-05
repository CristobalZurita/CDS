<template>
    <!-- Inline Link List -->
    <ul
        class="inline-link-list"
    >
        <!-- List Header (for small screens) -->
        <li class="inline-link-list-item inline-link-list-header">
            ━ <i class="fa fa-circle-nodes"/> ━
        </li>

        <!-- List Items -->
        <li
            v-for="link in parsedLinks"
            class="inline-link-list-item"
        >
            <a v-if="link.isRouterLink"
               :href="link.href"
               target="_blank"
               class="text-2 inline-link-list-link">
                <i v-if="link.faIcon"
                   :class="link.faIcon"
                   class="inline-link-list-icon"/>
                {{link.label}}
            </a>

            <router-link v-else
                         :to="link.href"
                         class="text-2 inline-link-list-link"
                         :class="link.classList">
                <i v-if="link.faIcon"
                   :class="link.faIcon"
                   class="inline-link-list-icon"/>
                {{link.label}}
            </router-link>
        </li>
    </ul>
</template>

<script setup>
import {useRoute} from "vue-router"
import {computed} from "vue"

const route = useRoute()

const props = defineProps({
    items: Array
})

const parsedLinks = computed(() => {
    return props.items.map(item => ({
        href: item.href || '/',
        label: item.label || '---',
        faIcon: item.faIcon || null,
        isRouterLink: item.href.charAt(0) !== '/',
        classList: {
            'inline-link-list-link-active': route.path === item.href
        }
    }))
})
</script>

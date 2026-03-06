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

<style scoped>
.inline-link-list {
    position: relative;
    list-style: none;
    padding: 0;
    margin: 0;
    color: #e9ecef; /* $light-5 */
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    align-items: center;
    gap: 0.45rem 0.75rem;
}

.inline-link-list-item {
    display: inline-flex;
    align-items: center;
    width: auto;
    padding-bottom: 0.1rem;
    padding-left: 0.3rem;
    padding-right: 0.3rem;
    font-size: 1rem; /* AUMENTADO para mejor legibilidad */
}

.inline-link-list-item:not(:last-child)::after {
    content: "·";
    color: #e9ecef; /* $light-5 */
    margin-left: 0.6rem;
}

@media (max-width: 576px) {
    .inline-link-list-item {
        display: block;
        padding-bottom: 0.05rem;
    }

    .inline-link-list-item:after {
        display: none;
    }
}

.inline-link-list-header {
    margin-top: 0.2rem;
    margin-bottom: 0.2rem;
    font-size: 1.1rem;
}
</style>

<template>
    <!-- Inline Link List -->
    <ul class="inline-link-list">
        <!-- List Header (for small screens) -->
        <li class="inline-link-list-item inline-link-list-header">
            ━ <i class="fa fa-circle-nodes"/> ━
        </li>

        <!-- List Items -->
        <li v-for="link in parsedLinks" class="inline-link-list-item">
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

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";

ul.inline-link-list {
    position: relative;
    list-style: none;
    padding: 0;
    margin: 0;
    color: $light-5;
}

li.inline-link-list-item {
    display: inline-block;
    padding-bottom: 0.1rem;
    padding-left: 0.3rem;
    padding-right: 0.3rem;

    &:not(:last-child)::after {
        content: "·";
        color: $light-5;
        margin-left: 0.6rem;
    }

    @include media-breakpoint-down(sm) {
        display: block;
        padding-bottom: 0.05rem;
        &:after {
            display: none;
        }
    }
}

li.inline-link-list-header {
    margin-top: 0.2rem;
    margin-bottom: 0.2rem;
    color: $light-5;
    font-size: 0.5rem;
    @include media-breakpoint-up(sm) {
        display: none;
    }
}

.inline-link-list-link {
    text-decoration: none;
    color: $light-6;

    i.inline-link-list-icon {
        min-width: 22px;
        color: $light-5;
        @include media-breakpoint-down(md) {
            min-width: 20px;
        }
    }
}

.inline-link-list-link:hover {
    color: lighten($primary, 15%);
    i.inline-link-list-icon {
        color: $light-2;
    }
}

.inline-link-list-link-active {
    color: lighten($primary, 20%);
}
</style>
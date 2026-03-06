<template>
    <div class="col-12 col-lg-4" :style="colStyles">
        <!-- Column Title -->
        <h5 :style="titleStyles">
            <i v-if="props.faIcon"
               :class="props.faIcon"/>

            <span>{{props.title}}</span>
        </h5>

        <!-- Description -->
        <div v-if="props.description.length > 0"
             :style="itemStyles">
            <div :style="descriptionStyles">
                <p v-for="descriptionItem in props.description" class="m-0" v-html="descriptionItem"/>
            </div>
        </div>

        <!-- Circle Links -->
        <div v-if="props.links.length > 0 && props.displayLinksAsButtons"
             class="mt-3"
             :style="itemStyles">
            <SocialLinks :items="props.links"
                         variant="dark"
                         size="4"/>
        </div>

        <!-- Inline Links -->
        <div v-if="props.links.length > 0 && !props.displayLinksAsButtons"
             class="mt-2 mt-lg-1"
             :style="itemStyles">
            <ul class="footer-inline-links">
                <li v-for="(link, index) in props.links" :key="index" class="footer-inline-link-item">
                    <a v-if="link.href && !link.href.startsWith('/')"
                       :href="link.href"
                       target="_blank"
                       rel="noopener noreferrer"
                       class="footer-inline-link">
                        {{ link.label }}
                    </a>
                    <router-link v-else
                                 :to="link.href"
                                 class="footer-inline-link">
                        {{ link.label }}
                    </router-link>
                </li>
            </ul>
        </div>
    </div>
</template>

<script setup>
import { computed } from "vue"
import { useResponsive, COLORS, getResponsiveValue } from "@/composables/useResponsive"
import SocialLinks from "/src/vue/components/widgets/SocialLinks.vue"

const props = defineProps(({
    title: String,
    faIcon: String,
    description: Array,
    links: Array,
    displayLinksAsButtons: Boolean
}))

const { windowWidth } = useResponsive()

// Column wrapper styles (responsive padding and border)
const colStyles = computed(() => {
    const w = windowWidth.value

    if (w < 992) {
        return {
            paddingTop: '1.5rem',
            paddingBottom: '2rem',
            textAlign: 'center'
        }
    }

    return {
        textAlign: 'left'
    }
})

// Title styles
const titleStyles = computed(() => ({
    color: COLORS.light1,
    textTransform: 'uppercase',
    fontWeight: '700',
    letterSpacing: '0.08em'
}))

// Item styles (responsive padding and alignment)
const itemStyles = computed(() => {
    const paddingTop = getResponsiveValue({
        xxxl: '0.5rem',
        lg: '0.3rem',
        md: '0.3rem',
        sm: '0.3rem'
    }, windowWidth.value)

    const w = windowWidth.value

    if (w >= 992) {
        return {
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'flex-start',
            paddingTop,
            margin: '0',
            maxWidth: '620px'
        }
    }

    return {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        paddingTop,
        margin: '0 auto',
        maxWidth: '520px'
    }
})

// Description styles
const descriptionStyles = computed(() => {
    const w = windowWidth.value

    return {
        display: 'flex',
        flexDirection: 'column',
        alignItems: w >= 992 ? 'flex-start' : 'center',
        justifyContent: 'start'
    }
})
</script>

<style scoped>
.footer-inline-links {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-start;
    align-items: center;
    gap: 1.1rem;
    white-space: normal;
}

.footer-inline-link-item {
    display: inline-flex;
    align-items: center;
}

.footer-inline-link-item:not(:last-child)::after {
    content: "·";
    color: #eaeaea;
    margin-left: 0.6rem;
}

.footer-inline-link {
    text-decoration: none;
    color: #eaeaea;
    font-weight: 700;
    white-space: nowrap;
}

.footer-inline-link:hover {
    color: #f89d4d;
}
</style>

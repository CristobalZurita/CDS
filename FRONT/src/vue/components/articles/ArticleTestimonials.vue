<template>
    <article class="foxy-testimonials">
        <!-- Swiper -->
        <swiper
            class="foxy-testimonials-swiper px-1"
            :slidesPerView="3"
            :spaceBetween="20"
            :pagination="{clickable: true}"
            :modules="[Pagination]"
            :grab-cursor="true"
            :prevent-clicks-propagation="true"
            :breakpoints = "{
                0:    {slidesPerView: 1},
                768:  {slidesPerView: 2},
                1200: {slidesPerView: 3}
            }">

            <template v-if="$slots.default">
                <swiper-slide v-for="(slide, index) in $slots.default()"
                              :key="index">
                    <component :is="slide" />
                </swiper-slide>
            </template>
        </swiper>
    </article>
</template>

<script setup>
import { Swiper, SwiperSlide } from 'swiper/vue'
import 'swiper/css'
import 'swiper/css/pagination'
import { Pagination } from 'swiper/modules'
</script>

<style lang="scss" scoped>
@import "/src/scss/_theming.scss";

.swiper {
    height: 100%;

    .swiper-slide {
        margin-bottom: 40px;
        height: auto!important;
    }
}
</style>
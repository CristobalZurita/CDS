<template>
    <!-- Loader Wrapper -->
    <div v-if="visible && currentStep"
         id="foxy-loader"
         class="foxy-loader"
         :class="{
            'foxy-loader-tween-in': currentStep === Steps.WILL_ENTER,
            'foxy-loader-tween-out': currentStep === Steps.LEAVING
         }">
        <!-- Loader Content -->
        <div class="foxy-loader-content">
            <ImageView src="/images/logo/logo_square_004.webp"
                       alt="Logo"
                       class="image-view-logo"
                       :class="{
                          'image-view-logo-animated': currentStep >= Steps.ANIMATING_LOGO
                       }"
                       @completed="_onLogoLoaded"
                       :spinner-enabled="false"/>

            <div class="foxy-loader-progress-display"
                 :class="{
                    'foxy-loader-progress-display-hidden': currentStep <  Steps.ANIMATING_PROGRESS,
                    'transition-none': currentStep < Steps.ANIMATING_PROGRESS
                 }">
                <p class="percentage text-2"
                   v-html="`${percentage}%`"/>

                <ProgressBar class="foxy-loader-progress-bar"
                             :percentage="percentage"/>
            </div>
        </div>
    </div>
</template>

<script setup>
import {onMounted, watch, ref} from "vue"
import {useUtils} from "/src/composables/utils.js"
import {useLayout} from "/src/composables/layout.js"
import {useScheduler} from "/src/composables/scheduler.js"
import ImageView from "/src/vue/components/generic/ImageView.vue"
import ProgressBar from "/src/vue/components/widgets/ProgressBar.vue"

const utils = useUtils()
const layout = useLayout()
const scheduler = useScheduler()

const props = defineProps({
    visible: Boolean,
    refreshCount: Number,
    smoothTransitionEnabled: Boolean
})

const Steps = {
    NONE: 0,
    WILL_ENTER: 1,
    ENTERING: 2,
    LOADING_LOGO: 3,
    ANIMATING_LOGO: 4,
    ANIMATING_PROGRESS: 5,
    WAITING_FOR_COMPLETION: 6,
    LEAVING: 7
}

const emit = defineEmits(['rendered', 'ready', 'leaving', 'completed'])

const schedulerTag = "loader"
const didLoadLogo = ref(false)
const didEmitReady = ref(false)
const currentStep = ref(Steps.NONE)
const percentage = ref(0)
const loadingTime = ref(0)

onMounted(() => {
    scheduler.clearAllWithTag(schedulerTag)
    _performTransition()
})

watch(() => props.visible, () => {
    scheduler.clearAllWithTag(schedulerTag)
    _performTransition()
})

watch(() => props.refreshCount, () => {
    scheduler.clearAllWithTag(schedulerTag)
    percentage.value = 0
    currentStep.value = Steps.NONE
    _executeAnimatingLogoStep()
})

const _onLogoLoaded = () => {
    didLoadLogo.value = true
}

const _performTransition = () => {
    if(!props.visible)
        return

    percentage.value = 0
    currentStep.value = Steps.NONE

    if(props.smoothTransitionEnabled)
        _executeEnteringStep()
    else
        _executeAnimatingLogoStep()
}

const _executeEnteringStep = () => {
    currentStep.value = Steps.WILL_ENTER

    scheduler.schedule(() => {
        currentStep.value = Steps.ENTERING
    }, 30, schedulerTag)

    scheduler.schedule(() => {
        _executeAnimatingLogoStep()
    }, 350, schedulerTag)
}

const _executeAnimatingLogoStep = () => {
    emit('rendered')
    currentStep.value = Steps.LOADING_LOGO
    layout.setBodyScrollEnabled(false)

    if(!didLoadLogo.value) {
        scheduler.schedule(() => {
            _executeAnimatingLogoStep()
        }, 100, schedulerTag)
        return
    }

    currentStep.value = Steps.ANIMATING_LOGO
    scheduler.schedule(() => {
        _executeAnimatingProgressStep()
    }, 300, schedulerTag)
}

const _executeAnimatingProgressStep = () => {
    currentStep.value = Steps.ANIMATING_PROGRESS
    scheduler.schedule(() => {
        _executeWaitingForCompletionStep()
    }, 500, schedulerTag)
}

const _executeWaitingForCompletionStep = () => {
    currentStep.value = Steps.WAITING_FOR_COMPLETION

    const dt = 1000 / 31
    loadingTime.value = 0
    didEmitReady.value = false

    scheduler.interval(() => {
        _updateProgress(dt)
    }, dt, schedulerTag)
}

const _updateProgress = (dt) => {
    const isPageLoaded = Boolean(document.querySelector('#app')?.children.length > 0)


    loadingTime.value += isPageLoaded ?
        dt :
        dt / 16

    const imageLoadPercentage = _getImageLoadPercentage()
  const minTimePercentage = utils.clamp(loadingTime.value*100/1500, 0, 100)


    const currentPercentage = (imageLoadPercentage + minTimePercentage)/2
    _incrementDisplayPercentage(currentPercentage)
}

const _getImageLoadPercentage = () => {
    const imageElements = document.querySelectorAll(".image")
    const imageLoadProgress = {loaded: 0, total: 0}
    Array.from(imageElements).map(item => {
        imageLoadProgress.total++
const st = item.getAttribute('load-status')
if (st === "loaded" || st === "error")
    imageLoadProgress.loaded++

    })

    if(imageLoadProgress.total <= 0)
        return 0
    return utils.clamp(imageLoadProgress.loaded*100/imageLoadProgress.total, 0, 100)
}

const _incrementDisplayPercentage = (currentPercentage) => {
    let diff = currentPercentage - percentage.value
    if (diff < 0) diff = 0

    if (diff <= 0) return  // ← Aquí debe ir la condición

    const step = didEmitReady.value ?
        8 :
        Math.round(4 + Math.random() * 4)

    const smootheningPercentageIncrement = diff > step ? step : Math.round(diff)
    percentage.value += smootheningPercentageIncrement
    percentage.value = utils.clamp(percentage.value, 0, 100)

    if(percentage.value > 12 && !didEmitReady.value) {
        emit('ready')
        didEmitReady.value = true
    }

    if(percentage.value === 100 || loadingTime.value >= 8000) {
        _onLoadingComplete()
    }
}


const _onLoadingComplete = () => {
    scheduler.schedule(() => {
        percentage.value = 100
        _executeLeavingStep()
    }, 300, schedulerTag)
}

const _executeLeavingStep = () => {
    layout.setBodyScrollEnabled(true)
    emit('leaving')

    if(window.location.hash) {
        scheduler.schedule(() => {
            currentStep.value = Steps.LEAVING
        }, 200, schedulerTag)
    }
    else {
        currentStep.value = Steps.LEAVING
    }

    scheduler.schedule(() => {
        emit('completed')
    }, 900, schedulerTag)
}
</script>

<template>

    <Head>
        <!-- Modern SVG Favicon (For Chrome, Firefox, Edge) -->
        <link rel="icon" type="image/svg+xml" href="/images/favicon.svg">
        <div v-if="false">
            <!-- PNG Fallbacks (For browsers that don't support SVG favicons) -->
            <link rel="icon" type="image/png" sizes="32x32" href="/images/favicon-32x32.png">
            <link rel="icon" type="image/png" sizes="16x16" href="/images/favicon-16x16.png">

            <!-- ICO Favicon (For older browsers like IE, Windows) -->
            <link rel="shortcut icon" href="/images/favicon.ico">

            <!-- Apple Touch Icon (For iOS devices - iPhones, iPads) -->
            <link rel="apple-touch-icon" sizes="180x180" href="/images/apple-touch-icon.png">

            <!-- Android/Chrome Icons -->
            <link rel="icon" type="image/png" sizes="192x192" href="/images/android-chrome-192x192.png">
            <link rel="icon" type="image/png" sizes="512x512" href="/images/android-chrome-512x512.png">

            <!-- Manifest for Progressive Web Apps (PWA) -->
            <link rel="manifest" href="/images/site.webmanifest">

            <!-- Safari Pinned Tab Icon -->
            <link rel="mask-icon" href="/images/safari-pinned-tab.svg" color="#5bbad5">

            <!-- Windows Tile Icon (For Windows 8/10 Start Menu) -->
            <meta name="msapplication-TileColor" content="#ffffff">
            <meta name="msapplication-TileImage" content="/images/mstile-150x150.png">

            <!-- Theme Color (For Chrome, Android) -->
            <meta name="theme-color" content="#ffffff">
        </div>
    </Head>
</template>
<script setup>
import { Head } from '@inertiajs/vue3';
</script>

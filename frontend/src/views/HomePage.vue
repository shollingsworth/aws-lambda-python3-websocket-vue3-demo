<script setup lang="ts">
import Grid from '@/components/Grid.vue'
</script>

<template>
    <div class="about">
        <Grid />
    </div>
</template>

<style>
@media (min-width: 1024px) {
    .about {
        min-height: 100vh;
        display: flex;
        align-items: center;
    }
}
</style>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import AuthState from '@/lib/auth'
import type { UserState } from '@/lib/auth'
import { ref } from 'vue'

var us = ref<UserState>(AuthState.getDefault())

AuthState.getState().then((v) => {
    us.value = v
})

</script>
<template>
    <v-app>
        <v-main>
            <v-tabs fixed-tabs>
                <v-tab to="/">Home</v-tab>
                <v-tab to="/profile">{{ us.linkname }}</v-tab>
            </v-tabs>
            <RouterView />
        </v-main>
    </v-app>
</template>

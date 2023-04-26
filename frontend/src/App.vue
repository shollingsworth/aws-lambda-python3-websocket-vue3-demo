<script setup lang="ts">
import { RouterView } from 'vue-router'
import AuthState, { type UserState } from '@/lib/auth'
import AppConfig from '@/lib/config'
import { ref } from 'vue'

var us = ref<UserState>(AuthState.getDefault())

AuthState.getState().then((v) => {
    us.value = v
})

const config = ref(AppConfig)

</script>
<template>
    <v-app>
        <v-main>
            <v-app-bar app>
                <v-toolbar-title>
                Griddle
                <v-chip>{{ config.stage }}</v-chip>
                </v-toolbar-title>
                <v-spacer></v-spacer>
                <v-btn text>Test</v-btn>
            </v-app-bar>
            <v-tabs fixed-tabs>
                <v-tab to="/">Home</v-tab>
                <v-tab to="/profile">{{ us.linkname }}</v-tab>
            </v-tabs>
            <RouterView />
        </v-main>
    </v-app>
</template>

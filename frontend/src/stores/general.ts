import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useGeneralStore = defineStore('general', () => {
    const connectionId = ref('disconnected')
    const isConnected = ref(false)
    const color = ref('red')

    const resetConnectionId = () => {
        connectionId.value = 'disconnected'
        isConnected.value = false
        color.value = 'red'
    }

    const isConnecting = () => {
        connectionId.value = 'connecting'
        isConnected.value = false
        color.value = 'blue'
    }

    const setConnectionId = (id: string) => {
        connectionId.value = id
        isConnected.value = true
        color.value = 'green'
    }

    return {
        isConnecting,
        isConnected,
        connectionId,
        resetConnectionId,
        setConnectionId,
        color
    }
})

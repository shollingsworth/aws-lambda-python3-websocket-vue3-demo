<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { CanvasGrid } from '@/lib/grid'
import AuthState, { type UserState } from '@/lib/auth'
import Config from '@/lib/config'

const gridelement = ref()
const x = ref(0)
const y = ref(0)

const grid = reactive(new CanvasGrid())

const rando = () => {
    grid.randomActiveCell()
}

const setactive = () => {
    grid.addActiveCell(x.value, y.value)
}

onMounted(() => {
    grid.setup(gridelement.value, 50, 50)
    AuthState.getState().then((state: UserState) => {
        if (!state.idJwtToken) {
            console.log("no jwt token")
            return
        }
        const ws = new WebSocket(Config.wsUrl(state.idJwtToken))
        ws.onopen = () => {
            console.log("ws open")
        }
        ws.onmessage = (msg) => {
            console.log("ws message", msg)
        }
        ws.onclose = () => {
            console.log("ws close")
        }
        ws.onerror = (err) => {
            console.log("ws error", err)
        }
    })
})
</script>

<template>
    <v-container>
        <v-row>
            <v-col>
                <v-btn @click="grid.clearAll()">Clear Board</v-btn>
            </v-col>
            <v-col>
                x: {{ grid.hovercell?.x || 'n/a' }} y: {{ grid.hovercell?.y || 'n/a' }} state:
                {{ grid.mousestate }}
            </v-col>
        </v-row>
        <v-row>
            <v-col>
                <v-text-field v-model="x" label="X" />
            </v-col>
            <v-col>
                <v-text-field v-model="y" label="Y" />
            </v-col>
            <v-col>
                <v-btn @click="setactive" color="green">Active</v-btn>
                <v-btn @click="rando" color="red">Random</v-btn>
            </v-col>
        </v-row>
        <v-row>
            <v-col>
                <canvas ref="gridelement"></canvas>
            </v-col>
            <v-col>
                <v-card>
                    <v-card-title>Active Cells</v-card-title>
                    <v-card-text>
                        <v-list>
                            <v-list-item>
                                <v-list-item-title>Title</v-list-item-title>
                                <v-list-item-subtitle>Subtitle</v-list-item-subtitle>
                                hello
                            </v-list-item>
                        </v-list>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

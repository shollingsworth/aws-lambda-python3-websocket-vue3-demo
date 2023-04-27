import type { Cell, AlertBox } from '@/lib/types'
import { useAuthStore } from '@/stores/auth'
import { useGeneralStore } from '@/stores/general'

enum MouseState {
    down = 'down',
    longdown = 'longdown',
    up = 'up'
}

interface ActiveCell {
    x: number
    y: number
}

interface SelectBox {
    x1: number
    y1: number
    x2: number
    y2: number
}

const gridSize = 50
const ElementSize = 12
const ColorAlertBox = 'orange'
const ColorAlertCell = 'red'
const ColorActiveCell = 'blue'
const ColorSelectFill = 'rgba(255, 255, 0, 0.5)'
const ColorBackground = 'white'
const ColorGrid = 'black'

export class CanvasGrid {
    hovercell: Cell | null = null
    width: number = 0
    height: number = 0
    alertBoxes: AlertBox[] = []
    selectBox: SelectBox | null = null
    canvas: HTMLCanvasElement | null = null
    ctx: CanvasRenderingContext2D | null = null
    mousepos: { x: number; y: number } | null = { x: 0, y: 0 }
    mousedownpos: { x: number; y: number } = { x: 0, y: 0 }
    mouseuppos: { x: number; y: number } = { x: 0, y: 0 }
    mousestate: MouseState = MouseState.up
    mouseTimeout: NodeJS.Timeout | null = null
    grid: Cell[][] = []
    websocket: WebSocket | null = null

    setup(canvas: HTMLCanvasElement) {
        const auth = useAuthStore()
        this.websocket = new WebSocket(auth.wsUrl)
        this.canvas = canvas
        this.ctx = this.canvas.getContext('2d')
        this.width = gridSize
        this.height = gridSize
        this.canvas.width = this.width * ElementSize
        this.canvas.height = this.height * ElementSize
        this.initGrid()
        this.draw()
        this.listen()
        this.listenWebSocket()
    }

    private send_action(action: string, data: any) {
        if (this.websocket) {
            const dat = { action: action, message: data }
            console.log('sending action', dat)
            this.websocket.send(JSON.stringify(dat))
        }
    }

    private process_action(event: MessageEvent) {
        const data = JSON.parse(event.data)
        console.log('process action', data)
        switch (data.action) {
            case 'alert_boxes':
                this.alertBoxes = data.message
                console.log('alert boxes', this.alertBoxes)
                this.draw()
                break
            case 'all_active_cells':
                this.setAllActiveCells(data.message)
                break
            case 'connection_id':
                const gen = useGeneralStore()
                gen.setConnectionId(data.message)
                break
            default:
                console.log('unknown action', data.action, data)
        }
    }

    private setAllActiveCells(cells: ActiveCell[]) {
        this.grid.forEach((row) => {
            row.forEach((cell) => {
                cell.active = false
            })
        })
        cells.forEach((cell) => {
            this.grid[cell.x][cell.y].active = true
        })
        this.draw()
    }

    public listenWebSocket() {
        const gen = useGeneralStore()
        gen.isConnecting()
        this.websocket?.addEventListener('open', (event: Event) => {
            console.log('websocket opened', event)
            this.send_action('send_alert_boxes', {})
            this.send_action('send_all_active_cells', {})
            this.send_action('send_connection_id', {})
        })

        this.websocket?.addEventListener('message', (event: MessageEvent) => {
            console.log('message received', event.data)
            this.process_action(event)
        })

        this.websocket?.addEventListener('close', (event: CloseEvent) => {
            gen.resetConnectionId()
            console.log('websocket closed', event)
        })

        this.websocket?.addEventListener('error', (event: Event) => {
            console.log('websocket error', event)
        })
    }

    // listen for changes and redraw
    public listen() {
        this.canvas?.addEventListener('mousedown', (event: MouseEvent) => this.onMouseDown(event))
        this.canvas?.addEventListener('mouseup', (event: MouseEvent) => this.onMouseUp(event))
        this.canvas?.addEventListener('mousemove', (event: MouseEvent) => this.onMouseMove(event))
        this.canvas?.addEventListener('mouseout', (event: MouseEvent) => this.onMouseOut(event))
    }

    public close() {
        this.websocket?.close()
    }

    private initGrid() {
        for (let x = 0; x < this.width; x++) {
            this.grid[x] = []
            for (let y = 0; y < this.height; y++) {
                this.grid[x][y] = {
                    x: x,
                    y: y,
                    active: false
                }
            }
        }
    }

    public draw() {
        if (this.canvas) {
            this.ctx?.clearRect(0, 0, this.canvas.width, this.canvas.height)
            for (let x = 0; x < this.width; x++) {
                for (let y = 0; y < this.height; y++) {
                    this.drawCell(this.grid[x][y])
                }
            }
            // draw outside border
            if (this.ctx) {
                this.ctx.strokeStyle = ColorGrid
                this.ctx.strokeRect(0, 0, this.canvas.width, this.canvas.height)
            }
            // draw alert boxes
            this.alertBoxes.forEach((box) => {
                this.drawAlertBox(box)
            })
            // draw select box
            if (this.mousestate == MouseState.longdown) {
                this.drawSelectBox()
            }
        }
    }

    public drawAlertBox(box: AlertBox) {
        if (this.ctx) {
            this.ctx.beginPath()
            this.ctx.strokeStyle = ColorAlertBox
            this.ctx.lineWidth = 3
            this.ctx.rect(
                box.x1 * ElementSize,
                box.y1 * ElementSize,
                (box.x2 - box.x1) * ElementSize,
                (box.y2 - box.y1) * ElementSize
            )
            this.ctx.stroke()
        }
    }

    public drawSelectBox() {
        if (this.ctx && this.selectBox) {
            this.ctx.beginPath()
            this.ctx.fillStyle = ColorSelectFill
            this.ctx.fillRect(
                this.selectBox.x1 * ElementSize,
                this.selectBox.y1 * ElementSize,
                (this.selectBox.x2 - this.selectBox.x1) * ElementSize,
                (this.selectBox.y2 - this.selectBox.y1) * ElementSize
            )
            this.ctx.stroke()
        }
    }

    private drawCell(cell: Cell) {
        if (this.ctx) {
            this.ctx.beginPath()
            this.ctx.strokeStyle = ColorGrid
            this.ctx.lineWidth = 1
            this.ctx.strokeRect(
                cell.x * ElementSize,
                cell.y * ElementSize,
                ElementSize,
                ElementSize
            )
            this.ctx.rect(cell.x * ElementSize, cell.y * ElementSize, ElementSize, ElementSize)
            this.ctx.fillStyle = this.isAlertCell(cell)
                ? ColorAlertCell
                : cell.active
                ? ColorActiveCell
                : ColorBackground
            this.ctx.fill()
            this.ctx.closePath()
        }
    }

    public isAlertCell(cell: Cell) {
        if (this.alertBoxes.length > 0) {
            return this.alertBoxes.some((box) => {
                return (
                    cell.x >= box.x1 &&
                    cell.x < box.x2 &&
                    cell.y >= box.y1 &&
                    cell.y < box.y2 &&
                    cell.active
                )
            })
        }
        return false
    }

    public getCellbyPos(x: number, y: number) {
        return this.grid[Math.ceil(x / ElementSize)][Math.ceil(y / ElementSize)]
    }

    public addActiveCell(x: number, y: number) {
        this.grid[x][y].active = true
        this.draw()
    }

    public randomActiveCell() {
        const x = Math.floor(Math.random() * this.width)
        const y = Math.floor(Math.random() * this.height)
        this.grid[x][y].active = true
        this.draw()
    }

    public clearAll() {
        this.alertBoxes = []
        this.initGrid()
        this.draw()
    }

    private mousePos(event: MouseEvent) {
        return { x: event.offsetX, y: event.offsetY }
    }

    private reset() {
        if (this.mouseTimeout) {
            clearTimeout(this.mouseTimeout)
        }
        this.mousestate = MouseState.up
        this.mousedownpos = { x: 0, y: 0 }
        this.mouseuppos = { x: 0, y: 0 }
        this.selectBox = null
        this.hovercell = null
        this.draw()
    }

    // Mouse events
    public onMouseDown(event: MouseEvent) {
        this.mousestate = MouseState.down
        if (this.mouseTimeout) {
            clearTimeout(this.mouseTimeout)
            this.selectBox = null
        }
        this.mouseTimeout = setTimeout(() => {
            this.mousestate = MouseState.longdown
        }, 250)
        this.mousedownpos = this.mousePos(event)
    }

    public onMouseUp(_: MouseEvent) {
        this.mousestate = MouseState.up
        if (this.mouseTimeout) {
            clearTimeout(this.mouseTimeout)
        }
        if (this.selectBox) {
            this.alertBoxes.push({
                name: 'Alert',
                x1: Math.floor(this.mousedownpos.x / ElementSize),
                y1: Math.floor(this.mousedownpos.y / ElementSize),
                x2: Math.ceil(this.mouseuppos.x / ElementSize),
                y2: Math.ceil(this.mouseuppos.y / ElementSize)
            })
            // copy selectbox
            const box = JSON.parse(JSON.stringify(this.selectBox))
            this.selectBox = null
            this.send_action('save_alert_box', box)
        }
    }

    public onMouseMove(event: MouseEvent) {
        this.mousepos = this.mousePos(event)
        this.hovercell = this.getCellbyPos(this.mousepos.x, this.mousepos.y)
        if (this.mousestate == MouseState.longdown) {
            this.mouseuppos = this.mousePos(event)
            this.selectBox = {
                x1: Math.floor(this.mousedownpos.x / ElementSize),
                y1: Math.floor(this.mousedownpos.y / ElementSize),
                x2: Math.ceil(this.mouseuppos.x / ElementSize),
                y2: Math.ceil(this.mouseuppos.y / ElementSize)
            }
            this.draw()
        }
    }

    public onMouseOut(_: MouseEvent) {
        this.reset()
    }
}

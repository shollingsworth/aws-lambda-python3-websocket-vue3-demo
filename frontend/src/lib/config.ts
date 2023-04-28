//console.log("meta env", import.meta.env)

class AppConfig {
    public stage: string
    constructor() {
        this.stage = import.meta.env.DEV ? 'local' : import.meta.env.VITE_STAGE
        // console.log("stage", this.stage)
    }

    public get redirectUrl(): string {
        const url = this.stage === 'local'
            ? 'http://localhost:8080'
            : 'https://' + import.meta.env.VITE_FQDN
        // console.log("redirectUrl", url)
        return url
    }

    public wsUrl(token: string): string {
        const url = this.stage === 'local'
            ? 'ws://localhost:3001/ws?token=' + token
            : import.meta.env.VITE_WEBSOCKET + '?token=' + token
        // console.log("wsUrl", url)
        return url
    }
}

export default AppConfig

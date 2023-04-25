class AppConfig {
    public stage: string
    constructor() {
        this.stage = import.meta.env.VITE_STAGE
    }

    public get redirectUrl(): string {
        return this.stage === 'local'
            ? 'http://localhost:8080'
            : this.stage === 'dev'
            ? 'https://sh-ws-demo-dev.stev0.me'
            : 'https://sh-ws-demo.stev0.me'
    }
}

export default new AppConfig()

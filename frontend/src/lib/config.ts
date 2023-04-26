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

    public wsUrl(token: string): string {
        return this.stage === 'local'
            ? 'ws://localhost:3001/ws?token=' + token
            : this.stage === 'dev'
            ? 'wss://xbbv6yjs83.execute-api.us-east-2.amazonaws.com/dev/ws?token=' + token
            : 'wss://yrmpqpmbf7.execute-api.us-east-2.amazonaws.com/prod/ws?token=' + token
    }
}

export default new AppConfig()

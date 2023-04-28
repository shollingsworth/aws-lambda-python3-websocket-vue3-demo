interface ImportMetaEnv {
    readonly VITE_STAGE: string
    readonly VITE_AWS_REGION: string
    readonly VITE_USER_POOL_ID: string
    readonly VITE_CLIENT_ID: string
    readonly VITE_FQDN: string
    readonly VITE_WEBSOCKET: string
    readonly VITE_COGNITO_DOMAIN: string
}

interface ImportMeta {
    readonly env: ImportMetaEnv
}

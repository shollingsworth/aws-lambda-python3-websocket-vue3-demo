interface ImportMetaEnv {
  readonly VITE_COGNITO_CLIENT_ID: string
  readonly VITE_COGNITO_POOL_ID: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

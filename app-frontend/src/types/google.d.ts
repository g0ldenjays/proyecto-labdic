export {}

declare global {
  interface Window {
    google: {
      accounts: {
        id: {
          initialize: (options: {
            client_id: string
            callback: (response: { credential: string }) => void
          }) => void
          renderButton: (
            parent: HTMLElement | null,
            options: {
              theme?: string
              size?: string
              width?: number
              text?: string
            },
          ) => void
        }
      }
    }
  }
}
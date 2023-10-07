import React from "react"
import { createRoot } from "react-dom/client"

import { NextUIProvider } from "@nextui-org/react"
import App from "./App"
import "./i18n"
import "./index.css"

const container = document.getElementById("root") as HTMLElement
const root = createRoot(container)

root.render(
   <React.StrictMode>
      <NextUIProvider>
         <React.Suspense fallback="loading">
            <App />
         </React.Suspense>
      </NextUIProvider>
   </React.StrictMode>
)

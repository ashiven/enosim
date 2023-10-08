"use client"
import { ModeToggle } from "@components/ui/toggle"
import Image from "next/image"

export default function Navbar() {
   return (
      <header>
         <nav>
            <ul className="flex items-center justify-between">
               <li>
                  <a href="/">
                     <Image
                        src="/images/logo.svg"
                        alt="Logo"
                        width={50}
                        height={50}
                     />
                  </a>
               </li>
               <li>
                  <a href="/">Home</a>
               </li>
               <li>
                  <a href="/about">About</a>
               </li>
               <li>
                  <ModeToggle />
               </li>
            </ul>
         </nav>
      </header>
   )
}

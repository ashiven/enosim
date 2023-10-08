"use client"
import { ModeToggle } from "@/components/ui/toggle"
import Image from "next/image"

export default function Navbar() {
   return (
      <header>
         <nav>
            <ul className="p-5 flex items-center justify-between">
               <div className="flex items-center justify-items-start">
                  <li>
                     <a href="/">
                        <Image
                           src="/icon.svg"
                           alt="Logo"
                           width={50}
                           height={50}
                        />
                     </a>
                  </li>
                  <li>
                     <a href="/about" className="ml-3 text-4xl font-bold">
                        EnoSimulator
                     </a>
                  </li>
               </div>
               <li>
                  <ModeToggle />
               </li>
            </ul>
         </nav>
      </header>
   )
}

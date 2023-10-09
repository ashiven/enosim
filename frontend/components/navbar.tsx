"use client"
import { ModeToggle } from "@/components/ui/toggle"
import Image from "next/image"

import {
   NavigationMenu,
   NavigationMenuItem,
   NavigationMenuList,
   NavigationMenuTrigger,
} from "@/components/ui/navigation-menu"

export default function Navbar() {
   return (
      <header>
         <nav className="shadow">
            <ul className="p-5 flex items-center justify-between">
               {/* Logo */}
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
                        EnoSim
                     </a>
                  </li>
               </div>
               {/* Navigation Menu and theme mode toggle*/}
               <div className="flex flex-row gap-4 justify-center items-center">
                  <NavigationMenu>
                     <NavigationMenuList>
                        <NavigationMenuItem>
                           <NavigationMenuTrigger>
                              <span className="text-[20px]">Website</span>
                           </NavigationMenuTrigger>
                        </NavigationMenuItem>
                        <NavigationMenuItem>
                           <NavigationMenuTrigger>
                              <span className="text-[20px]">About</span>
                           </NavigationMenuTrigger>
                        </NavigationMenuItem>
                        <NavigationMenuItem>
                           <NavigationMenuTrigger>
                              <span className="text-[20px]">Docs</span>
                           </NavigationMenuTrigger>
                        </NavigationMenuItem>
                     </NavigationMenuList>
                  </NavigationMenu>
                  <li>
                     <ModeToggle />
                  </li>
               </div>
            </ul>
         </nav>
      </header>
   )
}

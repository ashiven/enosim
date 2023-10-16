"use client"
import { ModeToggle } from "@/components/ui/toggle"
import Image from "next/image"
import Link from "next/link"

import {
   NavigationMenu,
   NavigationMenuItem,
   NavigationMenuLink,
   NavigationMenuList,
   navigationMenuTriggerStyle,
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
                     <a href="/" className="ml-3 text-4xl font-bold">
                        EnoSim
                     </a>
                  </li>
               </div>
               {/* Navigation Menu and theme mode toggle*/}
               <div className="flex flex-row gap-4 justify-center items-center">
                  <NavigationMenu>
                     <NavigationMenuList>
                        <NavigationMenuItem>
                           <Link href="/about" legacyBehavior passHref>
                              <NavigationMenuLink
                                 className={navigationMenuTriggerStyle()}
                              >
                                 <span className="text-[20px]">About</span>
                              </NavigationMenuLink>
                           </Link>
                        </NavigationMenuItem>
                        <NavigationMenuItem>
                           <Link
                              href="https://github.com/ashiven/enosimulator"
                              legacyBehavior
                              passHref
                           >
                              <NavigationMenuLink
                                 className={navigationMenuTriggerStyle()}
                              >
                                 <span className="text-[20px]">GitHub</span>
                              </NavigationMenuLink>
                           </Link>
                        </NavigationMenuItem>
                        <NavigationMenuItem>
                           <Link
                              href="https://github.com/ashiven/enosimulator/blob/main/docs/README.md"
                              legacyBehavior
                              passHref
                           >
                              <NavigationMenuLink
                                 className={navigationMenuTriggerStyle()}
                              >
                                 <span className="text-[20px]">
                                    Documentation
                                 </span>
                              </NavigationMenuLink>
                           </Link>
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

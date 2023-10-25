"use client"

import { Button } from "@/components/ui/button"
import { BarChart3, Container, Users } from "lucide-react"
import Link from "next/link"

import { usePathname } from "next/navigation"

export default function Sidebar() {
   const pathname = usePathname()
   return (
      <div className="flex flex-col h-screen p-4  shadow w-60">
         <div className="space-y-3">
            {/* Overview heading */}
            <div className="flex items-center ml-1">
               <h2 className="text-xl font-bold">Dashboard</h2>
            </div>
            {/* Tabs */}
            <div className="flex-1">
               <ul className="pt-2 pb-4 space-y-1 text-sm">
                  {/* Overview Tab */}
                  <li className="rounded-sm p-1">
                     <Button
                        variant={pathname === "/" ? "default" : "secondary"}
                     >
                        <BarChart3 className="w-6 h-6" size={24} />
                        <Link
                           href="/"
                           className="flex items-center p-2 space-x-3 rounded-md"
                        >
                           <span className="w-24">Overview</span>
                        </Link>
                     </Button>
                  </li>
                  {/* Services Tab */}
                  <li className="rounded-sm p-1">
                     <Button
                        variant={
                           pathname === "/services" ? "default" : "secondary"
                        }
                     >
                        <Container className="w-6 h-6" size={24} />
                        <Link
                           href="/services"
                           className="flex items-center p-2 space-x-3 rounded-md"
                        >
                           <span className="w-24">Services</span>
                        </Link>
                     </Button>
                  </li>
                  {/* Teams Tab */}
                  <li className="rounded-sm p-1">
                     <Button
                        variant={
                           pathname === "/teams" ? "default" : "secondary"
                        }
                     >
                        <Users className="w-6 h-6" size={24} />
                        <Link
                           href="/teams"
                           className="flex items-center p-2 space-x-3 rounded-md"
                        >
                           <span className="w-24">Teams</span>
                        </Link>
                     </Button>
                  </li>
               </ul>
            </div>
         </div>
      </div>
   )
}

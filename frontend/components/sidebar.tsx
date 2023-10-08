"use client"

import { Button } from "@/components/ui/button"
import { BarChart3, Container, Settings, Users } from "lucide-react"
import Link from "next/link"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { usePathname } from "next/navigation"

export default function Sidebar() {
   const pathname = usePathname()
   return (
      <div className="flex">
         {/* Sidebar */}
         <div className="flex flex-col h-screen p-3  shadow w-60">
            <div className="space-y-3">
               {/* Overview heading */}
               <div className="flex items-center">
                  <h2 className="text-xl font-bold">Dashboard</h2>
               </div>
               {/* Tabs */}
               <div className="flex-1">
                  <ul className="pt-2 pb-4 space-y-1 text-sm">
                     {/* Overview Tab */}
                     <li className="rounded-sm">
                        <Button
                           variant={pathname === "/" ? "default" : "secondary"}
                        >
                           <BarChart3 className="w-6 h-6" size={24} />
                           <Link
                              href="/"
                              className="flex items-center p-2 space-x-3 rounded-md"
                           >
                              <span>Overview</span>
                           </Link>
                        </Button>
                     </li>
                     {/* Services Tab */}
                     <li className="rounded-sm">
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
                              <span>Services</span>
                           </Link>
                        </Button>
                     </li>
                     {/* Teams Tab */}
                     <li className="rounded-sm">
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
                              <span>Teams</span>
                           </Link>
                        </Button>
                     </li>
                     {/* Settings Tab */}
                     <li className="rounded-sm">
                        <Button
                           variant={
                              pathname === "/settings" ? "default" : "secondary"
                           }
                        >
                           <Settings className="w-6 h-6" size={24} />
                           <Link
                              href="/settings"
                              className="flex items-center p-2 space-x-3 rounded-md"
                           >
                              <span>Settings</span>
                           </Link>
                        </Button>
                     </li>
                  </ul>
               </div>
            </div>
         </div>
         {/* A group of cards displaying some info */}
         <div className="container mx-auto mt-12">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
               {/* Revenue card */}
               <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                     <CardTitle className="text-sm font-medium">
                        Total Revenue
                     </CardTitle>
                     <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        className="h-4 w-4 text-muted-foreground"
                     >
                        <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
                     </svg>
                  </CardHeader>
                  <CardContent>
                     <div className="text-2xl font-bold">$45,231.89</div>
                     <p className="text-xs text-muted-foreground">
                        +20.1% from last month
                     </p>
                  </CardContent>
               </Card>
               {/* Revenue card */}
               <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                     <CardTitle className="text-sm font-medium">
                        Subscriptions
                     </CardTitle>
                     <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        className="h-4 w-4 text-muted-foreground"
                     >
                        <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                        <circle cx="9" cy="7" r="4" />
                        <path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
                     </svg>
                  </CardHeader>
                  <CardContent>
                     <div className="text-2xl font-bold">+2350</div>
                     <p className="text-xs text-muted-foreground">
                        +180.1% from last month
                     </p>
                  </CardContent>
               </Card>
               {/* Subscriptions card */}
               <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                     <CardTitle className="text-sm font-medium">
                        Sales
                     </CardTitle>
                     <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        className="h-4 w-4 text-muted-foreground"
                     >
                        <rect width="20" height="14" x="2" y="5" rx="2" />
                        <path d="M2 10h20" />
                     </svg>
                  </CardHeader>
                  <CardContent>
                     <div className="text-2xl font-bold">+12,234</div>
                     <p className="text-xs text-muted-foreground">
                        +19% from last month
                     </p>
                  </CardContent>
               </Card>
               {/* Sales card */}
               <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                     <CardTitle className="text-sm font-medium">
                        Active Now
                     </CardTitle>
                     <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        className="h-4 w-4 text-muted-foreground"
                     >
                        <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
                     </svg>
                  </CardHeader>
                  <CardContent>
                     <div className="text-2xl font-bold">+573</div>
                     <p className="text-xs text-muted-foreground">
                        +201 since last hour
                     </p>
                  </CardContent>
               </Card>
            </div>
         </div>
      </div>
   )
}

import Image from "next/image"
import Link from "next/link"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function Sidebar() {
   return (
      <div className="flex">
         <div className="flex flex-col h-screen p-3 bg-white shadow w-60">
            <div className="space-y-3">
               <div className="flex items-center">
                  <h2 className="text-xl font-bold">Dashboard</h2>
               </div>
               <div className="flex-1">
                  <ul className="pt-2 pb-4 space-y-1 text-sm">
                     {/* Overview Tab */}
                     <li className="rounded-sm">
                        <Link
                           href="/"
                           className="flex items-center p-2 space-x-3 rounded-md"
                        >
                           <Image
                              src="/chart.svg"
                              className="w-6 h-6"
                              alt="Logo"
                              width={30}
                              height={30}
                           />
                           <span>Overview</span>
                        </Link>
                     </li>
                     {/* Services Tab */}
                     <li className="rounded-sm">
                        <Link
                           href="/mails"
                           className="flex items-center p-2 space-x-3 rounded-md"
                        >
                           <Image
                              src="/docker.svg"
                              className="w-6 h-6"
                              alt="Logo"
                              width={30}
                              height={30}
                           />
                           <span>Services</span>
                        </Link>
                     </li>
                     {/* Teams Tab */}
                     <li className="rounded-sm">
                        <Link
                           href="/products"
                           className="flex items-center p-2 space-x-3 rounded-md"
                        >
                           <Image
                              src="/users.svg"
                              className="w-6 h-6"
                              alt="Logo"
                              width={30}
                              height={30}
                           />
                           <span>Teams</span>
                        </Link>
                     </li>
                     {/* Settings Tab */}
                     <li className="rounded-sm">
                        <Link
                           href="setting"
                           className="flex items-center p-2 space-x-3 rounded-md"
                        >
                           <svg
                              xmlns="http://www.w3.org/2000/svg"
                              className="w-6 h-6"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                              strokeWidth={2}
                           >
                              <path
                                 strokeLinecap="round"
                                 strokeLinejoin="round"
                                 d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                              />
                              <path
                                 strokeLinecap="round"
                                 strokeLinejoin="round"
                                 d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                              />
                           </svg>
                           <span>Settings</span>
                        </Link>
                     </li>
                  </ul>
               </div>
            </div>
         </div>
         {/* A group of cards displaying some info */}
         <div className="container mx-auto mt-12">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
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

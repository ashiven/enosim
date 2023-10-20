"use client"

import VMChart from "@/components/overview/vmchart"
import { Button } from "@components/ui/button"
import {
   DropdownMenu,
   DropdownMenuContent,
   DropdownMenuItem,
   DropdownMenuTrigger,
} from "@components/ui/dropdown-menu"

import { useState } from "react"

export default function VMSelect({ vmList, vmData }: any) {
   const [selectedVm, setSelectedVm] = useState(vmList[0])

   return (
      <div>
         <DropdownMenu>
            <DropdownMenuTrigger>
               <Button variant="outline">{selectedVm}</Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
               {vmList.map((vmName: string) => (
                  <DropdownMenuItem
                     key={vmName}
                     onSelect={() => setSelectedVm(vmName)}
                  >
                     {vmName}
                  </DropdownMenuItem>
               ))}
            </DropdownMenuContent>
         </DropdownMenu>

         <div>
            <VMChart data={vmData[selectedVm]} />
         </div>
      </div>
   )
}

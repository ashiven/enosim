"use client"

import VMChart from "@/components/overview/vmchart"
import { Button } from "@components/ui/button"
import {
   DropdownMenu,
   DropdownMenuContent,
   DropdownMenuLabel,
   DropdownMenuRadioGroup,
   DropdownMenuRadioItem,
   DropdownMenuSeparator,
   DropdownMenuTrigger,
} from "@components/ui/dropdown-menu"

import { useState } from "react"

export default function VMSelect({ vmList, vmData }: any) {
   if (vmList.length == 0) {
      return <div></div>
   }

   const [selectedVm, setSelectedVm] = useState(vmList[0])

   return (
      <div>
         <DropdownMenu>
            <DropdownMenuTrigger>
               <Button variant="outline">Select VM</Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
               <DropdownMenuLabel>VM Statistics</DropdownMenuLabel>
               <DropdownMenuSeparator />
               <DropdownMenuRadioGroup
                  value={selectedVm}
                  onValueChange={setSelectedVm}
               >
                  {vmList.map((vmName: string) => (
                     <DropdownMenuRadioItem value={vmName}>
                        {vmName}
                     </DropdownMenuRadioItem>
                  ))}
               </DropdownMenuRadioGroup>
            </DropdownMenuContent>
         </DropdownMenu>

         <div>
            <VMChart data={vmData[selectedVm]} />
         </div>
      </div>
   )
}

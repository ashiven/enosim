"use client"

import ContainerChart from "@/components/overview/vmchart"
import { Button } from "@components/ui/button"
import {
   DropdownMenu,
   DropdownMenuContent,
   DropdownMenuItem,
   DropdownMenuTrigger,
} from "@components/ui/dropdown-menu"

import { useState } from "react"

export default function ContainerSelect({ containerList, containerData }: any) {
   const [selectedContainer, setSelectedContainer] = useState(containerList[0])

   return (
      <div>
         <DropdownMenu>
            <DropdownMenuTrigger>
               <Button variant="outline">{selectedContainer}</Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
               {containerList.map((containerName: string) => (
                  <DropdownMenuItem
                     key={containerName}
                     onSelect={() => setSelectedContainer(containerName)}
                  >
                     {containerName}
                  </DropdownMenuItem>
               ))}
            </DropdownMenuContent>
         </DropdownMenu>

         <div>
            <ContainerChart data={containerData[selectedContainer]} />
         </div>
      </div>
   )
}

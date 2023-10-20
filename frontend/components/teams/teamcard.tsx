import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
   HoverCard,
   HoverCardContent,
   HoverCardTrigger,
} from "@/components/ui/hover-card"
import {
   Popover,
   PopoverContent,
   PopoverTrigger,
} from "@/components/ui/popover"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"

import * as React from "react"

interface TeamData {
   name: string
   id: number
   subnet: string
   address: string
   experience: string
   points: number
   gain: number
   exploiting: any
   patched: any
}
interface TeamCardProps {
   data: TeamData
}

function extractStrings(data: any) {
   const strings = []
   for (const parentKey in data) {
      const subObject = data[parentKey]
      for (const subKey in subObject) {
         if (subObject[subKey] === true) {
            strings.push(`${parentKey}-${subKey}`)
         }
      }
   }
   return strings
}

export default function TeamCard(props: TeamCardProps) {
   const exploitStrings = extractStrings(props.data.exploiting)
   const patchedStrings = extractStrings(props.data.patched)

   return (
      <HoverCard>
         <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
               <CardTitle className="text-sm font-medium">
                  <HoverCardTrigger>{props.data.name}</HoverCardTrigger>
               </CardTitle>
               <Popover>
                  <PopoverTrigger>
                     <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        strokeWidth="2"
                        stroke="#000000"
                        fill="none"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        className="h-4 w-4 text-muted-foreground"
                     >
                        <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                        <path d="M9 5h-2a2 2 0 0 0 -2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2 -2v-12a2 2 0 0 0 -2 -2h-2" />
                        <path d="M9 3m0 2a2 2 0 0 1 2 -2h2a2 2 0 0 1 2 2v0a2 2 0 0 1 -2 2h-2a2 2 0 0 1 -2 -2z" />
                        <path d="M9 17v-5" />
                        <path d="M12 17v-1" />
                        <path d="M15 17v-3" />
                     </svg>
                  </PopoverTrigger>
                  <PopoverContent>
                     <ScrollArea className="h-[200px] rounded-md border p-4 mb-1">
                        <h4 className="mb-4 text-sm font-medium leading-none">
                           Exploiting
                        </h4>
                        {exploitStrings.map((item, index) => (
                           <React.Fragment>
                              <div className="text-sm" key={index}>
                                 {item}
                              </div>
                              <Separator className="my-2" />
                           </React.Fragment>
                        ))}
                     </ScrollArea>
                     <ScrollArea className="h-[200px] rounded-md border p-4 mt-1">
                        <h3 className="mb-4 text-sm font-medium leading-none">
                           Patched
                        </h3>
                        {patchedStrings.map((item, index) => (
                           <React.Fragment>
                              <div className="text-sm" key={index}>
                                 {item}
                              </div>
                              <Separator className="my-2" />
                           </React.Fragment>
                        ))}
                     </ScrollArea>
                  </PopoverContent>
               </Popover>
            </CardHeader>
            <CardContent>
               <div className="text-2xl font-bold ">+{props.data.points}</div>
               <div className="text-xs text-muted-foreground">
                  +{props.data.gain} since last round
               </div>
            </CardContent>
         </Card>
         <HoverCardContent>
            <Badge>Id: {props.data.id}</Badge>
            <Badge>Team Subnet: {props.data.subnet}</Badge>
            <Badge>Address: {props.data.address}</Badge>
            <Badge>Experience Level: {props.data.experience}</Badge>
         </HoverCardContent>
      </HoverCard>
   )
}

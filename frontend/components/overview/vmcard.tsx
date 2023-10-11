import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
   Popover,
   PopoverContent,
   PopoverTrigger,
} from "@/components/ui/popover"

interface VMData {
   name: string
   status: string
   cpu: string
   memory: number
   disk: number
   uptime: number
   ip: string
}

interface VMCardProps {
   data: VMData
}

export default function VMCard(props: VMCardProps) {
   return (
      <Card>
         <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
               {props.data.name}
            </CardTitle>
            <Popover>
               <PopoverTrigger>
                  <svg
                     xmlns="http://www.w3.org/2000/svg"
                     className="h-4 w-4 text-muted-foreground"
                     viewBox="0 0 24 24"
                     stroke-width="1.5"
                     stroke="#000000"
                     fill="none"
                     stroke-linecap="round"
                     stroke-linejoin="round"
                  >
                     <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                     <path d="M5 5m0 1a1 1 0 0 1 1 -1h12a1 1 0 0 1 1 1v12a1 1 0 0 1 -1 1h-12a1 1 0 0 1 -1 -1z" />
                     <path d="M9 9h6v6h-6z" />
                     <path d="M3 10h2" />
                     <path d="M3 14h2" />
                     <path d="M10 3v2" />
                     <path d="M14 3v2" />
                     <path d="M21 10h-2" />
                     <path d="M21 14h-2" />
                     <path d="M14 21v-2" />
                     <path d="M10 21v-2" />
                  </svg>
               </PopoverTrigger>
               <PopoverContent>
                  <span className="font-bold">CPU: </span>
                  <span>{props.data.cpu}</span>
                  <br />
                  <span className="font-bold">Memory: </span>
                  <span>{props.data.memory} GB</span>
                  <br />
                  <span className="font-bold">Disk size: </span>
                  <span>{props.data.disk} GB</span>
                  <br />
                  <span className="font-bold">IP Address: </span>
                  <span>{props.data.ip}</span>
               </PopoverContent>
            </Popover>
         </CardHeader>
         <CardContent>
            <div className="flex flex-row items-center space-x-2">
               <Badge
                  variant={
                     props.data.status === "online" ? "default" : "secondary"
                  }
               >
                  {props.data.status}
               </Badge>
               <p className="text-xs text-muted-foreground">
                  {props.data.status === "online"
                     ? `up for ${props.data.uptime} min`
                     : ""}
               </p>
            </div>
         </CardContent>
      </Card>
   )
}

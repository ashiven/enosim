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
            <div className="text-2xl font-bold">{props.data.status}</div>
            <p className="text-xs text-muted-foreground">
               up for {props.data.uptime} minutes
            </p>
         </CardContent>
      </Card>
   )
}

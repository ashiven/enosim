import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
   HoverCard,
   HoverCardContent,
   HoverCardTrigger,
} from "@/components/ui/hover-card"

interface ServiceCardProps {
   name: string
   id: number
   flagsPerRound: number
   noisesPerRound: number
   havocsPerRound: number
   weightFactor: number
}

export default function ServiceCard(props: ServiceCardProps) {
   return (
      <HoverCard>
         <HoverCardTrigger>
            <Card>
               <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                     {props.name}
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
               </CardContent>
            </Card>
         </HoverCardTrigger>
         <HoverCardContent>
            <span className="font-bold">id: </span>
            <span>{props.id}</span>
            <br />
            <span className="font-bold">flags per round: </span>
            <span>{props.flagsPerRound}</span>
            <br />
            <span className="font-bold">noises per round: </span>
            <span>{props.noisesPerRound}</span>
            <br />
            <span className="font-bold">havocs per round: </span>
            <span>{props.havocsPerRound}</span>
            <br />
            <span className="font-bold">weight factor: </span>
            <span>{props.weightFactor}</span>
            <br />
         </HoverCardContent>
      </HoverCard>
   )
}

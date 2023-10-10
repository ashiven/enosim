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
         <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
               <CardTitle className="text-sm font-medium">
                  <HoverCardTrigger>{props.name}</HoverCardTrigger>
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
         <HoverCardContent>
            <span className="font-bold">Id: </span>
            <span>{props.id}</span>
            <br />
            <span className="font-bold">Flags per Round: </span>
            <span>{props.flagsPerRound}</span>
            <br />
            <span className="font-bold">Noises per Round: </span>
            <span>{props.noisesPerRound}</span>
            <br />
            <span className="font-bold">Havocs per Round: </span>
            <span>{props.havocsPerRound}</span>
            <br />
            <span className="font-bold">Weight Factor: </span>
            <span>{props.weightFactor}</span>
            <br />
         </HoverCardContent>
      </HoverCard>
   )
}

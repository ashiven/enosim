import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
   HoverCard,
   HoverCardContent,
   HoverCardTrigger,
} from "@/components/ui/hover-card"

interface TeamCardProps {
   TeamName: string
   TeamId: string
   TeamSubnet: string
   TeamAddress: string
   TeamExperience: string
}

export default function TeamCard(data: TeamCardProps) {
   return (
      <HoverCard>
         <HoverCardTrigger>
            <Card>
               <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                     {data.TeamName}
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
            <span>{data.TeamId}</span>
            <br />
            <span className="font-bold">team subnet: </span>
            <span>{data.TeamSubnet}</span>
            <br />
            <span className="font-bold">address: </span>
            <span>{data.TeamAddress}</span>
            <br />
            <span className="font-bold">experience level: </span>
            <span>{data.TeamExperience}</span>
         </HoverCardContent>
      </HoverCard>
   )
}
